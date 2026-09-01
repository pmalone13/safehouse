"""Polls tedassistent@gmail.com for new inbox mail and drops each one onto
queue_db's FIFO for the coordinator to pick up. Deliberately much simpler
than bayhouse's email_topic_monitor.py: this inbox is dedicated to one
purpose (this pipeline), so there's no wake-word/topic gating, no
per-sender permission tiers -- every new message is just a message.

First poll of the process's lifetime seeds the seen-ids baseline only
(same convention as every other detector in the bayhouse lineage) -- an
in-memory set, bounded, reset on restart. That's an accepted, honest
tradeoff for a single-purpose POC inbox, not a hidden gap.

Run standalone, long-lived (systemd unit: safehouse-email-monitor.service):
    python email_monitor.py
"""
import os
import time
from pathlib import Path

import google_client
import queue_db
from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

POLL_INTERVAL_SECONDS = float(os.environ.get("SAFEHOUSE_EMAIL_POLL_INTERVAL_SECONDS", "20"))
MAX_SEEN_IDS = 2000

_seen_ids: set[str] = set()
_seeded = False


def _poll_once(service) -> None:
    global _seeded
    messages = google_client.list_new_messages(service, query="in:inbox", max_results=25)
    new_ids = [m["id"] for m in messages if m["id"] not in _seen_ids]

    if not _seeded:
        # First poll: record the current inbox as the baseline, don't
        # enqueue anything already sitting there from before this
        # process started.
        _seen_ids.update(m["id"] for m in messages)
        _seeded = True
        log.info(f"seeded baseline with {len(messages)} existing message(s)")
        return

    for message_id in reversed(new_ids):  # oldest-of-the-new first
        detail = google_client.get_message_detail(service, message_id)
        body = f"Subject: {detail['subject']}\n\n{detail['body_text']}"
        queue_db.enqueue("email", detail["sender"], body)
        _seen_ids.add(message_id)
        log.info(f"enqueued email from={detail['sender']!r} subject={detail['subject']!r} "
                 f"message_id={message_id}")

    if len(_seen_ids) > MAX_SEEN_IDS:
        # Bounded, not precise -- fine, since Gmail message ids don't
        # recur and this only exists to stop unbounded memory growth.
        _seen_ids.clear()
        _seen_ids.update(new_ids[-100:])


def main() -> None:
    queue_db.init_db()
    log.info(f"email monitor starting (poll={POLL_INTERVAL_SECONDS}s)")
    while True:
        try:
            service = google_client.get_client()
            _poll_once(service)
        except FileNotFoundError as e:
            log.error(f"{e} -- sleeping and will retry")
        except Exception as e:
            log.warning(f"poll failed, will retry: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
