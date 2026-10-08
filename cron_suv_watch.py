"""Cron entrypoint for the suv-replacement Craigslist watch (built live
with Paul over SSH, 2026-10-08 -- see root CLAUDE.md's hard-boundary
section: this is the "Paul actively present and directing in real time"
case, not an unattended autonomous build).

What this does and does NOT do:
  - Does NOT search Craigslist itself. It just drops a message onto the
    same FIFO queue a text or email would, exactly the shape
    twilio_webhook.py / email_monitor.py already use
    (queue_db.enqueue(channel, source, body)). The coordinator is a
    long-running systemd service that polls that queue every 5s, so
    inserting the row IS the "wake it up" step -- nothing else is
    needed to "fire" processing.
  - The actual search happens when a live Claude session processes that
    message with its own WebFetch/WebSearch tools, the same as any
    other inbound text. Those tools can read Craigslist directly
    (confirmed 2026-10-08, queue id 194) where cars.com/CarGurus could
    not (unreliable filters / outright 403s, see suv-replacement
    project history) -- so the search logic deliberately lives in a
    live Claude turn, not in scraping code here.

Scheduling note -- why this runs hourly and checks the time itself
rather than being scheduled at exactly 9am/6pm in the crontab:
  This box's cron daemon runs on the system clock (Etc/UTC) and does
  NOT honor a per-job TZ= for scheduling -- confirmed via
  `man 5 crontab`: "Even if a user specifies the TZ environment
  variable in his crontab this will affect only the commands executed
  in the crontab, not the execution of the crontab tasks themselves."
  Hardcoding two UTC times would silently drift by an hour every time
  Eastern crosses a DST boundary (Nov/March) until someone edits the
  crontab by hand. Checking the real America/New_York wall-clock hour
  here, once an hour, survives DST forever with no crontab edits.
"""
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import queue_db

EASTERN = ZoneInfo("America/New_York")
RUN_HOURS = {9, 18}  # 9am and 6pm Eastern, per Paul's spec (queue-less live session, 2026-10-08)

MESSAGE_BODY = """suv-replacement project (automated cron watch, not a text/email from \
Paul directly -- but handle it exactly like one of his messages, same as \
any other queued item).

Search Craigslist for an older SUV, roughly pre-2012, with UNDER \
110,000 miles (changed 2026-10-08 -- Paul's original build spec said \
"high miles" and the first on-demand run searched min_auto_miles=100000 \
accordingly, but he corrected it same-day to a mileage CEILING, not a \
floor: he wants lower-mileage cars, not higher-mileage ones. Don't \
revert to the old "high miles" framing.). Washington DC \
and Annapolis are SEPARATE Craigslist regions, not one site with a \
sub-area -- search both: https://washingtondc.craigslist.org/search/cta \
and https://annapolis.craigslist.org/search/cta (confirmed via \
geo.craigslist.org/iso/us/md's own site list, 2026-10-08). Use a plain \
`curl`/`requests` fetch of that URL (not WebFetch's AI-summarized \
version -- it silently drops filters) with query params \
`max_auto_year=2012&max_auto_miles=110000&query=SUV`, then parse the \
`<script type="application/ld+json" id="ld_searchpage_results">` block \
in the raw HTML for name/price/location -- mileage and title status \
are NOT on the search-results page, only on each listing's own page \
(`class="attr auto_miles"` / `class="attr auto_title_status"`), so \
fetch individual listing pages for your shortlisted candidates before \
reporting a mileage/title-status number. All of this was worked out \
live on 2026-10-08 (the auto_year_max param doesn't exist and silently \
no-ops -- min_auto_year/max_auto_year/min_auto_miles/max_auto_miles \
are the real ones); don't rediscover it, just use it.

Before reporting anything, read \
projects/suv-replacement/craigslist_watch_results.md -- it holds every \
listing a prior run has already found. Only email/report about links \
NOT already in that file; don't re-alert on the same listing twice.

For any new (not-already-recorded) listing priced under $10,000, email \
pmalone13@gmail.com with the link and a short description (year/make/\
model, price, mileage, location).

Append every new listing found this run (regardless of price) to \
projects/suv-replacement/craigslist_watch_results.md with the date \
found, price, mileage, and link, so future runs can dedup against it. \
If nothing new was found this run, no email is needed -- just log that \
in this project's own CLAUDE.md as usual, and still do the normal \
checkpoint (project CLAUDE.md, root CLAUDE.md if anything there needs \
it, commit, push, drive_sync.py)."""


def main() -> None:
    now_eastern = datetime.now(EASTERN)
    if now_eastern.hour not in RUN_HOURS:
        return  # not a scheduled run time -- no-op, checked again next hour
    queue_db.enqueue("cron", "suv-replacement-watch", MESSAGE_BODY)


if __name__ == "__main__":
    main()
