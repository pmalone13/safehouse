"""safehouse's coordinator: the one process that turns queued messages
into Claude Code sessions.

Design (redesigned with Paul 2026-10-30, live session; supersedes the
2026-08-31 "resume ticket" design -- see this repo's own history for
that prior discussion, not duplicated here):

  - Entrypoint for Claude is always a message pulled off queue_db's FIFO.
  - One spawn at a time, serially -- never two running at once. This
    file stays genuinely dumb: claim the oldest unclaimed message, spawn
    one `claude -p` turn for it (always fresh, never --resume), wait for
    it to finish, repeat.
  - What used to be the coordinator's job (deciding whether to resume a
    prior session across separate spawns) is now entirely inside the
    turn itself. A single spawn is expected to stay alive and keep
    self-claiming further messages as they arrive -- via the same
    claim_next()/mark_done() this file uses -- for as long as its own
    CLAUDE.md-documented stay-alive protocol says to (bounded by an idle
    window, a forced-restart ceiling, a daily reset, or Paul explicitly
    asking it to exit). Because of that, SPAWN_TIMEOUT_SECONDS has to be
    generous -- it's now a true "something is stuck" tripwire, not a
    normal per-message ceiling.
  - Consequence: there is no session_state table anymore, no resume
    ticket, no wrap-up turn spawned by this file. Once a turn decides to
    stop, the next message -- whenever it arrives -- always starts a
    brand-new, empty-context session. Continuity within a busy stretch
    comes entirely from one process staying alive, never from this file
    remembering a session_id to resume later.
  - A message can end up stuck in 'claimed' if the process holding it
    (including one that self-claimed it mid-turn) dies before marking it
    done/failed/retry_pending -- requeue_stale_claimed() recovers that.
  - What each Claude turn actually does (read CLAUDE.md, decide how to
    respond, update its own state, commit + push, and now also: whether
    to keep watching for more messages before actually stopping) is NOT
    this file's concern -- that behavior contract lives in the repo's
    own CLAUDE.md, authored separately.

Run standalone, long-lived (systemd unit: safehouse-coordinator.service):
    python coordinator.py
"""
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import queue_db
import twilio_client
from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

REPO_DIR = Path(__file__).parent
CLAUDE_BIN = os.environ.get("SAFEHOUSE_CLAUDE_BIN", "claude")
PERMISSION_MODE = os.environ.get("SAFEHOUSE_PERMISSION_MODE", "bypassPermissions")
POLL_INTERVAL_SECONDS = float(os.environ.get("SAFEHOUSE_POLL_INTERVAL_SECONDS", "5"))

# These two govern the in-turn stay-alive protocol documented in root
# CLAUDE.md, not anything this file branches on directly -- they're
# defined here so there's one canonical place for the numbers, and
# inherited into the spawned `claude` subprocess's environment (default
# subprocess.run behavior) so the turn can read them back via `echo
# $SAFEHOUSE_IDLE_WINDOW_SECONDS` etc. instead of a hardcoded number in
# CLAUDE.md prose that could drift out of sync with reality.
IDLE_WINDOW_SECONDS = float(os.environ.get("SAFEHOUSE_IDLE_WINDOW_SECONDS", "3600"))  # 1 hour
FORCED_RESTART_SECONDS = float(os.environ.get("SAFEHOUSE_FORCED_RESTART_SECONDS", "14400"))  # 4 hours

# A single spawn can now legitimately stay alive for most of a day (see
# the stay-alive protocol above), so this is a true "something is stuck"
# tripwire, not a normal per-message ceiling -- set comfortably above the
# worst case (started just after the daily reset, runs until the next
# one, plus real working time).
SPAWN_TIMEOUT_SECONDS = float(os.environ.get("SAFEHOUSE_SPAWN_TIMEOUT_SECONDS", "90000"))  # ~25h

# Only recover a message stuck in 'claimed' once the spawn that could
# possibly still be holding it is certainly dead -- i.e. comfortably
# past SPAWN_TIMEOUT_SECONDS, never while a long-lived turn might still
# legitimately be mid-handling it.
STALE_CLAIM_SECONDS = SPAWN_TIMEOUT_SECONDS + 300

# Outage retry/notify config. A failed message used to just sit marked
# 'failed' forever -- no retry, no notification -- which is how six-plus
# Claude usage-limit outages in 2026-10 silently dropped messages for
# hours (see root CLAUDE.md's TODO section). The notification path below
# goes straight to Twilio, never through a Claude spawn, since the outage
# being reported might BE Claude's own usage limit.
NOTIFY_PHONE = os.environ.get("SAFEHOUSE_NOTIFY_PHONE", "+12026181308")
NOTIFY_THROTTLE_SECONDS = float(os.environ.get("SAFEHOUSE_NOTIFY_THROTTLE_SECONDS", "1800"))
MAX_RETRIES_OTHER = int(os.environ.get("SAFEHOUSE_MAX_RETRIES_OTHER", "5"))
MAX_RETRIES_USAGE_LIMIT = int(os.environ.get("SAFEHOUSE_MAX_RETRIES_USAGE_LIMIT", "15"))
RESET_BUFFER_SECONDS = 180  # cushion past the stated reset time, it's not always exact to the second
PROMPT_TOO_LONG_RETRY_SECONDS = 300
OTHER_BACKOFF_SECONDS = [120, 600, 1800, 3600, 3600]

# Matches the "resets 11pm (UTC)" / "resets 4:20am (UTC)" shape actually
# seen in Claude Code's own session/weekly-limit error text.
_RESET_TIME_RE = re.compile(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(UTC\)", re.IGNORECASE)


@dataclass
class SpawnResult:
    session_id: str
    result_text: Optional[str]
    raw: dict


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def classify_error(error: str) -> str:
    """Buckets a spawn_claude failure into a retry strategy. The exact
    phrasing matched here ('session limit', 'weekly limit', 'Prompt is
    too long') comes from errors actually observed across the recurring
    outages logged in root CLAUDE.md -- not a general-purpose parser."""
    low = error.lower()
    if "session limit" in low or "weekly limit" in low:
        return "usage_limit"
    if "prompt is too long" in low:
        return "prompt_too_long"
    return "other"


def _parse_reset_time(error: str, now: datetime) -> Optional[datetime]:
    """Extracts the UTC time a usage-limit error says it resets at, as
    the next occurrence of that time (today if still ahead, else
    tomorrow). Returns None if the error text doesn't match."""
    m = _RESET_TIME_RE.search(error)
    if not m:
        return None
    hour = int(m.group(1)) % 12
    if m.group(3).lower() == "pm":
        hour += 12
    minute = int(m.group(2)) if m.group(2) else 0
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def compute_retry(error: str, retry_count: int) -> Optional[datetime]:
    """Decides whether a failed message should be retried and, if so,
    when. Returns None once retries for this error's class are
    exhausted -- caller should then treat the message as terminally
    failed. `retry_count` is the number of retries already made (0 on
    the first failure). Every retry is already a fresh spawn (this file
    never resumes a session across separate spawns anymore), so there's
    no "force a new session" distinction left to make here."""
    now = _now()
    kind = classify_error(error)

    if kind == "usage_limit":
        if retry_count >= MAX_RETRIES_USAGE_LIMIT:
            return None
        reset_at = _parse_reset_time(error, now)
        if reset_at is None:
            reset_at = now + timedelta(minutes=30)
        return reset_at + timedelta(seconds=RESET_BUFFER_SECONDS)

    if kind == "prompt_too_long":
        if retry_count >= MAX_RETRIES_OTHER:
            return None
        return now + timedelta(seconds=PROMPT_TOO_LONG_RETRY_SECONDS)

    if retry_count >= MAX_RETRIES_OTHER:
        return None
    delay = OTHER_BACKOFF_SECONDS[min(retry_count, len(OTHER_BACKOFF_SECONDS) - 1)]
    return now + timedelta(seconds=delay)


def _should_notify_outage() -> bool:
    notice = queue_db.get_outage_notice()
    if notice is None or not notice["last_notified_at"]:
        return True
    last = datetime.fromisoformat(notice["last_notified_at"])
    return (_now() - last) > timedelta(seconds=NOTIFY_THROTTLE_SECONDS)


def notify_outage(message_id: int, error: str, retry_count: int, next_retry_at: datetime) -> None:
    """Best-effort direct SMS, bypassing Claude entirely -- the outage
    being reported may well BE Claude's own usage limit, so this can't
    itself depend on a Claude spawn succeeding. Throttled so one outage
    that fails many queued messages in a row sends one text, not one
    per message (per Paul's own 'don't irritate' standing principle,
    root CLAUDE.md queue id 257)."""
    if not _should_notify_outage():
        return
    body = (
        f"Ted: hit an error processing message #{message_id} "
        f"(attempt {retry_count + 1}): {error[:200]}. "
        f"Will auto-retry around {next_retry_at.strftime('%H:%M UTC')}."
    )
    try:
        twilio_client.send_sms(NOTIFY_PHONE, body)
        queue_db.set_outage_notice(_now_iso())
    except Exception as e:
        log.error(f"failed to send outage notification SMS: {e}")


def notify_terminal_failure(message_id: int, error: str, retry_count: int) -> None:
    body = (
        f"Ted: message #{message_id} failed permanently after "
        f"{retry_count} attempts and needs a look: {error[:300]}"
    )
    try:
        twilio_client.send_sms(NOTIFY_PHONE, body)
    except Exception as e:
        log.error(f"failed to send terminal-failure SMS: {e}")


def notify_recovered(message_id: int, retry_count: int) -> None:
    if retry_count <= 0:
        return
    plural = "y" if retry_count == 1 else "ies"
    body = f"Ted: back up -- message #{message_id} went through after {retry_count} retr{plural}."
    try:
        twilio_client.send_sms(NOTIFY_PHONE, body)
    except Exception as e:
        log.error(f"failed to send recovery SMS: {e}")


def build_prompt(msg) -> str:
    return (
        f"A new message has arrived on channel '{msg['channel']}' from "
        f"'{msg['source']}' at {msg['received_at']} (queue id {msg['id']}).\n\n"
        f"Message body:\n{msg['body']}\n\n"
        "Read the root CLAUDE.md in this directory first to orient "
        "yourself (who you're helping, which project is currently "
        "active, and this session's own workflow contract), then handle "
        "this message."
    )


def spawn_claude(prompt: str, resume: Optional[str] = None) -> SpawnResult:
    """Runs one Claude Code turn, fresh or resumed. Raises RuntimeError on
    any failure (non-JSON output, is_error, or a missing session_id) --
    the caller is responsible for treating that as a failed message, not
    retrying blindly (a failed turn may have already partially acted)."""
    argv = [CLAUDE_BIN, "-p", "--output-format", "json", "--permission-mode", PERMISSION_MODE]
    if resume:
        argv += ["--resume", resume]

    # Prompt goes through a real temp file, never a CLI arg or subprocess
    # input= pipe -- a large prompt piped via input= can lose the race
    # against the CLI's own short stdin-wait window (a real failure mode
    # hit building this same pattern locally). A real file handle means
    # the child reads at its own pace, no race.
    fd, tmp_path = tempfile.mkstemp(suffix=".prompt.txt")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(prompt)
        with open(tmp_path, "r", encoding="utf-8") as stdin_fh:
            proc = subprocess.run(
                argv,
                stdin=stdin_fh,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(REPO_DIR),
                text=True,
                timeout=SPAWN_TIMEOUT_SECONDS,
            )
    finally:
        os.unlink(tmp_path)

    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"claude spawn produced non-JSON output (returncode={proc.returncode}): "
            f"stderr={proc.stderr!r} stdout={proc.stdout!r}"
        ) from e

    if parsed.get("is_error"):
        raise RuntimeError(f"claude spawn returned is_error=True: {parsed.get('result')!r}")

    session_id = parsed.get("session_id")
    if not session_id:
        raise RuntimeError(f"claude spawn produced no session_id: {parsed!r}")

    return SpawnResult(session_id=session_id, result_text=parsed.get("result"), raw=parsed)


def process_one(msg) -> None:
    prior_retries = msg["retry_count"] or 0
    log.info(f"processing message id={msg['id']} channel={msg['channel']} "
             f"source={msg['source']} prior_retries={prior_retries}")
    try:
        result = spawn_claude(build_prompt(msg))
    except (subprocess.TimeoutExpired, RuntimeError) as e:
        error = str(e)
        retry_count = prior_retries + 1
        log.warning(f"message id={msg['id']} failed (attempt {retry_count}): {error}")
        next_retry_at = compute_retry(error, prior_retries)
        if next_retry_at is None:
            queue_db.mark_failed(msg["id"], error)
            notify_terminal_failure(msg["id"], error, retry_count)
            return
        queue_db.mark_retry_pending(msg["id"], error, retry_count, next_retry_at.isoformat())
        notify_outage(msg["id"], error, retry_count, next_retry_at)
        return

    # The turn itself may have stayed alive handling (and marking done)
    # any number of further self-claimed messages before finally
    # returning -- this file only ever knows about, and only ever marks
    # done, the one message it originally spawned for.
    queue_db.mark_done(msg["id"])
    log.info(f"message id={msg['id']} done, session={result.session_id}")
    queue_db.clear_outage_notice()
    notify_recovered(msg["id"], prior_retries)


def main() -> None:
    queue_db.init_db()
    log.info("safehouse coordinator starting "
             f"(poll={POLL_INTERVAL_SECONDS}s, spawn_timeout={SPAWN_TIMEOUT_SECONDS}s)")

    while True:
        requeued = queue_db.requeue_due_retries()
        if requeued:
            log.info(f"requeued {requeued} message(s) whose retry delay elapsed")

        recovered = queue_db.requeue_stale_claimed(STALE_CLAIM_SECONDS)
        if recovered:
            log.warning(f"recovered {recovered} message(s) stuck in 'claimed' "
                        "(the spawn holding them must have died without finishing)")

        msg = queue_db.claim_next()
        if msg is not None:
            process_one(msg)
            continue  # check for more immediately, no sleep

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
