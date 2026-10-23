"""safehouse's coordinator: the one process that turns queued messages
into Claude Code sessions.

Design (agreed with Paul 2026-08-31, see this repo's own history for the
full discussion -- not duplicated here since this file's docstring is
meant to stay short):

  - Entrypoint for Claude is always a message pulled off queue_db's FIFO.
  - One message at a time, serially -- never two spawns running at once.
  - Session continuity is a "resume ticket," not a resident process:
    after a successful turn, queue_db.session_state remembers the
    session_id and a deadline (now + SESSION_IDLE_TIMEOUT_SECONDS). A
    message arriving before the deadline resumes that same Claude
    session (`claude -p --resume <session_id>`) with full prior context;
    nothing costs anything while idle since no process stays resident.
  - Once the deadline passes with nothing new queued, a final wrap-up
    turn runs (giving the session a chance to checkpoint), then the
    ticket is cleared -- the next message starts a brand new session.
  - Two race windows are checked deliberately, mirroring a real bug
    bayhouse hit with this exact pattern locally: a message can land (1)
    in the gap between "idle timeout reached" and actually committing to
    the wrap-up turn, or (2) while the wrap-up turn itself is running (a
    real, possibly slow `claude -p --resume` call). Both are re-checked
    so a message never goes unnoticed just because it arrived at a bad
    moment.
  - What each Claude turn actually does (read CLAUDE.md, decide how to
    respond, update its own state, commit + push) is NOT this file's
    concern -- that behavior contract lives in the repo's own CLAUDE.md,
    authored separately. This coordinator only ever hands a message to a
    session and trusts the session to do its own bookkeeping.

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
SESSION_IDLE_TIMEOUT_SECONDS = float(os.environ.get("SAFEHOUSE_SESSION_IDLE_TIMEOUT_SECONDS", "3600"))
SPAWN_TIMEOUT_SECONDS = float(os.environ.get("SAFEHOUSE_SPAWN_TIMEOUT_SECONDS", "900"))

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

WRAPUP_PROMPT = (
    "No new messages have arrived and this session's idle window has "
    "elapsed. If your CLAUDE.md files or any other state need a final "
    "update before this session ends, do that now (the same checkpoint "
    "you do after every message: update project CLAUDE.md, update root "
    "CLAUDE.md, commit, push origin), then stop."
)


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


def compute_retry(error: str, retry_count: int) -> Optional[tuple[datetime, bool]]:
    """Decides whether a failed message should be retried and, if so,
    when, plus whether the retry should force a brand-new Claude
    session rather than resuming one. Returns None once retries for
    this error's class are exhausted -- caller should then treat the
    message as terminally failed. `retry_count` is the number of
    retries already made (0 on the first failure)."""
    now = _now()
    kind = classify_error(error)

    if kind == "usage_limit":
        if retry_count >= MAX_RETRIES_USAGE_LIMIT:
            return None
        reset_at = _parse_reset_time(error, now)
        if reset_at is None:
            reset_at = now + timedelta(minutes=30)
        return reset_at + timedelta(seconds=RESET_BUFFER_SECONDS), False

    if kind == "prompt_too_long":
        if retry_count >= MAX_RETRIES_OTHER:
            return None
        # A bloated resumed session is the near-certain cause (even
        # automatic compaction fails for lack of budget) -- retrying into
        # the same session would just fail the same way again.
        return now + timedelta(seconds=PROMPT_TOO_LONG_RETRY_SECONDS), True

    if retry_count >= MAX_RETRIES_OTHER:
        return None
    delay = OTHER_BACKOFF_SECONDS[min(retry_count, len(OTHER_BACKOFF_SECONDS) - 1)]
    return now + timedelta(seconds=delay), False


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


def _live_resume_id() -> Optional[str]:
    state = queue_db.get_session_state()
    if state is None or not state["session_id"] or not state["deadline"]:
        return None
    if state["deadline"] > _now_iso():
        return state["session_id"]
    return None


def process_one(msg) -> None:
    resume_id = _live_resume_id()
    prior_retries = msg["retry_count"] or 0
    log.info(f"processing message id={msg['id']} channel={msg['channel']} "
             f"source={msg['source']} resume={resume_id!r} prior_retries={prior_retries}")
    try:
        result = spawn_claude(build_prompt(msg), resume=resume_id)
    except (subprocess.TimeoutExpired, RuntimeError) as e:
        error = str(e)
        retry_count = prior_retries + 1
        log.warning(f"message id={msg['id']} failed (attempt {retry_count}): {error}")
        retry = compute_retry(error, prior_retries)
        if retry is None:
            queue_db.mark_failed(msg["id"], error)
            notify_terminal_failure(msg["id"], error, retry_count)
            return
        next_retry_at, force_fresh = retry
        if force_fresh:
            queue_db.clear_session_state()
        queue_db.mark_retry_pending(msg["id"], error, retry_count, next_retry_at.isoformat())
        notify_outage(msg["id"], error, retry_count, next_retry_at)
        return

    queue_db.mark_done(msg["id"])
    deadline = (_now() + timedelta(seconds=SESSION_IDLE_TIMEOUT_SECONDS)).isoformat()
    queue_db.set_session_state(result.session_id, deadline)
    log.info(f"message id={msg['id']} done, session={result.session_id} "
             f"resumable until {deadline}")
    queue_db.clear_outage_notice()
    notify_recovered(msg["id"], prior_retries)


def run_wrapup_turn(session_id: str) -> None:
    log.info(f"session {session_id} idle-timeout reached, running wrap-up turn")
    try:
        spawn_claude(WRAPUP_PROMPT, resume=session_id)
    except (subprocess.TimeoutExpired, RuntimeError) as e:
        log.warning(f"wrap-up turn for session {session_id} failed (session will still end): {e}")


def main() -> None:
    queue_db.init_db()
    log.info("safehouse coordinator starting "
             f"(idle_timeout={SESSION_IDLE_TIMEOUT_SECONDS}s, poll={POLL_INTERVAL_SECONDS}s)")

    while True:
        requeued = queue_db.requeue_due_retries()
        if requeued:
            log.info(f"requeued {requeued} message(s) whose retry delay elapsed")

        msg = queue_db.claim_next()
        if msg is not None:
            process_one(msg)
            continue  # check for more immediately, no sleep

        state = queue_db.get_session_state()
        now = _now_iso()

        if state is not None and state["deadline"] and state["deadline"] > now:
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if state is not None and state["deadline"] and state["deadline"] <= now:
            # Race window 1: something may have landed between the idle
            # check above and committing to the wrap-up turn.
            if queue_db.has_pending():
                continue
            run_wrapup_turn(state["session_id"])
            # Race window 2: something may have landed while the
            # (possibly slow) wrap-up turn itself was running.
            if queue_db.has_pending():
                log.info("new message arrived during wrap-up turn, session stays alive")
                continue
            queue_db.clear_session_state()
            log.info(f"session {state['session_id']} ended")
            continue

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
