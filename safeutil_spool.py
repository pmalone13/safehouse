"""Pure-Python diversion for Paul's "safeutil" app emails (location +
words, see projects/location-tracker/CLAUDE.md and projects/words/
CLAUDE.md). These never reach the Claude pipeline at all -- email_monitor.py
calls spool_message() for them instead of queue_db.enqueue(), so the
high-frequency location/words pings stop spawning a full Claude session
(each of which re-reads the entire root CLAUDE.md) per the queue id 675
cost/outage finding and the 2026-10-25 "just capture it, we'll post
process" request.

One file per UTC calendar day, newline-delimited JSON, append-only:
    projects/location-tracker/spool/YYYY-MM-DD.jsonl

Deliberately does zero parsing/reacting here -- not location extraction,
not a trigger-phrase scan, nothing. The whole point is this path costs
near-zero: one disk append, no Claude spawn, no root-file read. Whatever
happens with the spooled content (parsing lat/lon, reviewing words,
anything else) is a separate, later, manual or scripted pass -- not this
module's job.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

SPOOL_DIR = Path(__file__).parent / "projects" / "location-tracker" / "spool"


def is_safeutil_message(sender: str, subject: str) -> bool:
    """True for mail from Paul's own safeutil app family: his address,
    subject starting with "safeutil" -- covers the current "safeutil
    status" format and the earlier separate "safeutil location" /
    "safeutil my words" ones, in case either ever reappears. Case-
    insensitive on both checks."""
    return "pmalone13@gmail.com" in (sender or "").lower() and \
        (subject or "").strip().lower().startswith("safeutil")


def spool_message(detail: dict) -> Path:
    """Appends one email's full raw content as one JSON line to today's
    rotation file (created on first use each day). Returns the path
    written to, mainly so the caller can log it."""
    SPOOL_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = SPOOL_DIR / f"{today}.jsonl"
    record = {
        "message_id": detail.get("message_id"),
        "sender": detail.get("sender"),
        "subject": detail.get("subject"),
        "date_header": detail.get("date"),
        "spooled_at": datetime.now(timezone.utc).isoformat(),
        "body": detail.get("body_text"),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path
