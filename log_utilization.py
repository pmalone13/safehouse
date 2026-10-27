"""Snapshot this session's own Claude Code token usage and append one
line to utilizationSpool.log, so a later turn can answer "what's our
utilization" by reading a local file instead of guessing or trying
(and failing -- see CLAUDE.md's TODO history, queue ids 694/695) to
query it live.

Standing step added to the root CLAUDE.md checkpoint (step 3), just
before the git commit, per Paul's request 2026-10-27 (direct follow-
through on the proposal floated at queue id 696, confirmed at queue
id 697). Run every cycle, not just when something feels notable --
same philosophy as the commit-message rule one line up in CLAUDE.md.

Mechanism: $CLAUDE_CODE_SESSION_ID names this session's own transcript
at ~/.claude/projects/-home-ubuntu-safehouse/<session_id>.jsonl. Every
assistant message line in it carries a real `usage` object (input/
output/cache token counts, model name) -- but the same logical message
gets written to the transcript more than once as it streams (confirmed
by inspecting a real transcript: identical usage values recur under
the same message.id a few hundred ms apart), so lines are deduped by
message.id before summing or they'd double-count.

Caveat carried over from the original investigation (queue id 695):
this is raw per-message token cost, not a running percentage against
the actual session/weekly rate-limit cap -- that cap only ever
surfaces as literal error text when a limit is actually hit. Treat the
numbers here as "how much this session has spent," not "how close to
the limit."

Run manually, or (normally) invoked as part of a turn's own checkpoint,
right before `git add -A && git commit`:
    ./venv/bin/python log_utilization.py
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent
SPOOL_PATH = REPO_ROOT / "utilizationSpool.log"
TRANSCRIPT_DIR = Path.home() / ".claude" / "projects" / "-home-ubuntu-safehouse"


def summarize_transcript(transcript_path: Path) -> dict | None:
    """Sum deduped per-message usage across one transcript file."""
    by_message_id = {}
    model = None
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "assistant":
                continue
            msg = entry.get("message", {})
            msg_model = msg.get("model")
            if not msg_model or msg_model == "<synthetic>":
                # Synthetic entries are local error messages (e.g. a
                # rate-limit notice), not real model responses -- no
                # real token cost, skip rather than let them pollute
                # totals or overwrite the real model name.
                continue
            msg_id = msg.get("id")
            if not msg_id:
                continue
            by_message_id[msg_id] = msg.get("usage", {})
            model = msg_model

    if not by_message_id:
        return None

    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    for usage in by_message_id.values():
        for key in totals:
            totals[key] += usage.get(key, 0) or 0

    return {
        "model": model,
        "assistant_messages": len(by_message_id),
        **totals,
    }


def main():
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": session_id,
    }

    if not session_id:
        record["error"] = "CLAUDE_CODE_SESSION_ID not set in environment"
    else:
        transcript_path = TRANSCRIPT_DIR / f"{session_id}.jsonl"
        if not transcript_path.exists():
            record["error"] = f"transcript not found: {transcript_path}"
        else:
            summary = summarize_transcript(transcript_path)
            if summary is None:
                record["error"] = "no real (non-synthetic) assistant usage found yet"
            else:
                record.update(summary)

    with open(SPOOL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
