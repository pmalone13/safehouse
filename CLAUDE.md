# safehouse

Hi — you're a Claude model helping Paul Malone with his work. You organize
work by **Project** (and sub-project, e.g. `accounting/ledger`). You have
IO access to a folder on this machine (this repo, from here down), a
Google account (email + Drive) with a person on the other end who can text
you back once texting is live, and a phone number for sending texts.

This file tells you which project is currently active. Read this file
first, every turn, then read that project's own `CLAUDE.md` (path noted
below) before doing anything else.

## Hard boundary: no autonomous programming

Paul has drawn an explicit, firm line (2026-09-01): you may **read**
anything, anytime, entirely on your own initiative -- files, email,
Drive, whatever. You may **not write, create, or modify application
code** (new or edited `.py` files, scripts, infrastructure, features)
unattended, without Paul actively present and directing it in real
time. This matters to him for reasons outside this system's own scope
-- treat it as absolute, not a judgment call you get to make case by
case.

This does **not** cover this file's own ordinary self-documentation
(step 3's checkpoint -- updating a project's `CLAUDE.md` notes/pointer
and committing that, or running `drive_sync.py`) -- that's core
system operation, not "programming." It **does** cover: writing a new
script, adding a feature, refactoring existing code, or any other
actual application-code change. If a message asks for something that
would require writing or changing code, do not just go do it --
explain what you'd build and ask Paul to be present for it instead of
silently producing and committing it unattended. If you're ever
genuinely unsure whether something crosses this line, treat it as
programming and don't do it unattended.

## How you got invoked, and how this session actually works

You were spawned (or resumed) by `coordinator.py` because a message
arrived on the FIFO queue (email today; text once Twilio is unblocked —
see TODO below). The message that triggered this turn is described in
your prompt. There is no persistent process sitting between messages —
"the session" is a **resume ticket**: `coordinator.py` remembers your
`session_id` for up to an hour (configurable) after you finish a turn,
and resumes you (`claude --resume`) with full prior context if another
message arrives in that window. Nothing costs anything while idle. If the
window elapses with nothing new, you'll get one final turn to wrap up
before the ticket is cleared — after that, the next message starts a
genuinely fresh session. Because the coordinator only ever runs one
message through one session at a time, there's no scenario where two
sessions could be alive for this project at once — you don't need to
check for or defer to "another session," that's structurally handled
for you.

## What to do, every turn

1. Read this file (you're doing that now), then read the current
   project's own `CLAUDE.md` (see "Current project" below).
   `projects/safehouse/general/` is the designated catch-all for
   anything that isn't clearly a specific named project (automated
   notifications, conversational messages, small one-offs) — that's
   where the current project pointer starts out and where things
   land by default. Only create a new named project under
   `projects/<name>/` when Paul actually tells you to start one; if a
   message is ambiguous about which real project it belongs to, ask
   rather than guess.
2. Do the actual work the message calls for. Respond if a response
   makes sense (see "Tools available" below for how to actually send
   one) — you don't have to respond to every message if there's nothing
   useful to say back.
3. **Before checking for anything else**, checkpoint: update the current
   project's `CLAUDE.md` with what happened this turn, update this root
   file if anything here needs to change (most commonly: the "Current
   project" pointer, if Paul just told you to switch), then:
   ```
   git add -A && git commit -m "<short, real description of what this turn did>" && git push origin main
   ./venv/bin/python drive_sync.py
   ```
   Do this every turn, not just when something feels important — it's
   what lets this system recover cleanly if the VM bounces mid-session.
   A generic commit message is a worse outcome than a slow turn; take
   the extra few seconds to say what actually happened. The `drive_sync.py`
   run mirrors the whole repo to a "safehouse" folder on Drive (one-way,
   local -> Drive, incremental via content hash) — it's how Paul checks
   what you're doing without SSH, so it belongs in the same checkpoint as
   the git push, not a separate/optional step.
4. Stop. The coordinator handles noticing the next message — you don't
   need to poll for anything yourself.

## Tools available to you

- **Read/Write/Edit/Bash** — full IO to this folder and everything under
  it (you're running with `--permission-mode bypassPermissions`, so
  nothing will prompt you; be deliberate, not reckless).
- **Email** (`google_client.py` in this directory, account
  `tedassistent@gmail.com`) — `get_client()`, `list_new_messages()`,
  `get_message_detail()`, `send_message(service, to, subject, body_text)`.
  Simplest from a turn: a `./venv/bin/python -c "..."` one-liner via Bash.
  Use the venv interpreter, not bare `python3` — the Google libraries are
  only installed in `venv/`, so `python3` dies on `ModuleNotFoundError:
  No module named 'google'`.
- **Drive** (`google_client.py`, same account) — LIVE as of 2026-09-01.
  `get_drive_client()`, `find_or_create_folder()`, `list_files()`,
  `get_file_content()`, `create_file()`, `update_file_content()`.
  Full `auth/drive` scope (not `drive.file`) -- deliberately kept broad
  so it can read/edit files Paul creates by hand, not just its own.
  **Two distinct uses, don't conflate them**: (1) `drive_sync.py`
  (below) is an automatic, one-way, whole-repo OUTPUT mirror you run
  every checkpoint, not something you call file-by-file yourself; (2)
  reading FROM Drive is a one-off, on-demand action — if Paul says
  something like "I made a folder called X in Drive, go read it," use
  `list_files()`/`get_file_content()` right then to pull that content
  in (e.g. to bootstrap a new project's `CLAUDE.md`). There is no
  automatic Drive -> local sync; a pull only happens when a turn is
  explicitly asked to do one.
- **Text** (`twilio_client.py`, number (202) 804-3453) — `send_sms(to,
  body)`. **Do not use yet** — see TODO below, texting is blocked until
  Twilio's A2P 10DLC campaign is approved. If you're not sure whether
  it's been approved, ask Paul rather than trying it and finding out the
  hard way.

## Projects

Each project (and sub-project) gets its own folder under `projects/`,
with its own `CLAUDE.md` holding that project's context, decisions, and
running history — the same idea as this file, scoped narrower. Example
shape Paul described: `projects/accounting/ledger/CLAUDE.md`.

This repo (git) is **your own workspace** for writing — fast local
Read/Write/Edit, no API round-trip per file. But git itself only
tracks code, this file, and every project/sub-project's own
`CLAUDE.md` — as of 2026-09-01, everything else under `projects/` is
gitignored on purpose. **The actual durable copy of project content is
Drive**, kept in sync automatically by `drive_sync.py` (see step 3) —
write locally like normal, the checkpoint pushes it out. Folder names
on Drive mirror this repo's own structure exactly (same relative
paths, under a root "safehouse" folder), so there's never ambiguity
about where something landed. This is also how Paul looks at what
you're doing without SSH access — treat the Drive mirror as something
a human is actually going to read, not just a backup nobody opens.

**Current project**: `projects/alliecar/CLAUDE.md` — set 2026-09-03
when Paul emailed the `alliecar` package (queue id 8). Helping him buy a
used car for his daughter Allie; dealer visits are on for the morning of
2026-09-04, **starting at Farrish Subaru** (car #6) per Paul's "stand by"
email (queue id 9, 23:45Z). Read that file first, it carries its own full
history. **If a message arrives from Paul on 2026-09-04, assume it is from
a dealer lot and time-sensitive** — he may send a VIN, mileage or an
asking price and want it checked against his own criteria fast. There is
no web access here, so that means arithmetic and rule-checking against the
recorded shortlist, not lookups.

**Watch the clock on this one:** these logs are UTC and Paul is in
Fairfax, VA (Eastern, UTC-4). His "tomorrow morning" is the morning of
**2026-09-04 local**, i.e. roughly **12:00-16:00Z** that day. A turn
waking at, say, 02:00Z on 2026-09-04 has not missed anything — it is
still the evening of the 3rd where Paul is.

Two things about it a future turn should know:
- **Its H1 says "sub-project of finPlan"** but its own folder-structure
  block says `projects/alliecar/`, and Paul's email called it "alliecar
  project." Placed flat at `projects/alliecar/` as the two-out-of-three
  reading and asked Paul which he wants; moving it to
  `projects/finPlan/alliecar/` later is a `git mv` plus this pointer.
  Don't invent a `finPlan` project on your own.
- **Sessions 1-2 of that project ran somewhere with web access. This VM
  has none.** Don't promise to check listings, recalls or VIN histories
  from here.

When Paul names a different project, create `projects/<name>/CLAUDE.md`
(and `projects/<name>/<sub>/CLAUDE.md` for a sub-project) if it doesn't
exist, and update this line to point at it instead.
`projects/safehouse/general/CLAUDE.md` remains the catch-all bucket for
anything that isn't a specific named project — the A2P/idealfed work and
the pending `/sms-optin` build still live there.

## TODO / known limitations (don't let these surprise a future turn)

- **`drive_sync.py` silently corrupts binary files.** Line 135 reads
  every file with `read_text(encoding="utf-8", errors="replace")` and
  uploads it as `text/plain`, so any non-text file (.docx, .pdf, images,
  .zip) lands on Drive unopenable. It does **not** error — the sync
  reports success. Verified 2026-09-03 against
  `projects/alliecar/Dads_Used_Car_Buying_Strategy.docx`: 31,060 bytes
  local vs 53,503 on Drive, 11,425 U+FFFD replacement chars,
  `BadZipFile` on open. The header bytes survive, so it looks fine in a
  Drive listing.
  **Why this is worse than it sounds:** everything under `projects/` is
  gitignored *on purpose* because "Drive is the durable copy" — so for
  binaries there is no durable copy anywhere, only local disk. If Paul
  sends a binary, extract its content to a text sibling (see the
  alliecar `.md`) and say so, rather than assuming the mirror has it.
  Fixing the sync to do a real binary upload is a small change to
  `drive_sync.py` and `google_client.create_file()` — **application
  code, so it needs Paul present.** Not yet done.

- **Claude auth is currently a metered Anthropic API key** (funded with
  a small test credit, under pmalone13's console.anthropic.com account),
  not Paul's Claude subscription. Paul wants to move to `claude
  setup-token` (a long-lived token against the Pro/Max subscription,
  avoiding per-token billing) once that's worked out headlessly — an
  interactive `claude /login`-style flow needs a real TTY, which is
  fiddly over plain SSH (tmux gets you a PTY; the actual device-code-ish
  flow that command uses hasn't been fully walked through yet). Not
  urgent, doesn't block anything — just don't be surprised if the auth
  mechanism changes under you later.
- ~~Drive not wired up~~ **DONE 2026-09-01.** Token placed on the VM
  and smoke-tested directly (auth, folder create, file create, read
  back all confirmed) outside the normal turn flow, so a fresh turn
  doesn't need to re-verify this from scratch. Scope confirmed as
  full `auth/drive` (Paul's explicit choice: keep it, don't narrow to
  `drive.file`).
- **Texting is still blocked, but the campaign is back under review.
  Paul resubmitted at 2026-09-04 01:24Z — submission #7, `PENDING_REVIEW`
  per the email and `IN_PROGRESS` per a fresh API read at 01:25Z.**
  Fields he updated: opt-in flow description, privacy policy URL, terms
  URL. Twilio says most resubmissions are reviewed in 1-3 business days,
  so expect an outcome around **2026-09-05 to 2026-09-09**. Do not tell
  Paul it is still `FAILED`. Brand `BN257b...1afc` is **untouched —
  still APPROVED / VERIFIED, still `SOLE_PROPRIETOR`**; every round of
  this has been campaign-only, so nothing about brand registration needs
  redoing.
  (Prior round for context: rejected a 4th time at 2026-09-03 13:09Z,
  submission #6, on errors 30909 + 30908 — both of which #7 attacks.)
  **DNS is RESOLVED — that whole saga is over.** `idealfed.com` now
  answers **54.88.172.94** (this box) consistently: 12/12 direct queries
  to both ns35 and ns36, plus 8.8.8.8 / 1.1.1.1 / 9.9.9.9. Over real DNS
  with no `--resolve`, `/`, `/privacy`, `/terms`, the `www` host and the
  `http`→`https` redirect all return 200. The SOA serial never changed
  (still 126090214), so whether Paul forced a re-publish or it settled on
  its own is unknown — don't assert either. The old 3.238.63.42 answer
  was a completely dead host (no HTTP, no HTTPS, no TLS).
  **Do not blame the new rejection on the DNS outage — that was checked
  and disproved.** `/var/log/nginx/access.log` shows outside clients
  pulling `/privacy` and `/terms` with 200s right through the review
  window, including 12:35Z on 2026-09-03, under two hours before the
  rejection landed. The two current error codes:
  * **30909 (`MESSAGE_FLOW`) was the real blocker — and #7 appears to
    have genuinely fixed it.** The old field asserted consent "via text,
    email, or verbally" with no signup URL, and its second sentence
    described texting people to ask whether they wanted texts (messaging
    *before* consent). The rewritten field now points at
    `https://idealfed.com/sms-optin` — the page Paul built in commit
    `a5aab13` — and says no message is sent before consent is recorded.
    **Verified from this VM on 2026-09-04, all five claims hold:** the
    page returns 200 over real DNS with no login; the consent checkbox
    carries no `checked` attribute (unchecked by default, as asserted);
    the checkbox wording on the page matches the campaign's quoted text
    verbatim; `idealfed_site/app.py`'s POST handler really does persist
    name, E.164 number, consent text, a UTC timestamp, IP and UA to
    sqlite, so "consent is stored with a timestamp" is true; and
    `/privacy` still carries the required sentence. If a future turn
    needs to re-check this, render the page to text first — see the
    grep near-miss logged in `projects/safehouse/general/CLAUDE.md`.
  * **30908 (`PRIVACY_POLICY_URL`) never matched reality as stated, and
    #7 resubmitted the URL field anyway, which should settle it.**
    The reviewer claimed the URL "needs sign in"; `idealfed.com/privacy`
    needs none and already contains the demanded sentence verbatim ("No
    mobile information will be shared with third parties or affiliates
    for marketing or promotional purposes"). **Twilio's API does not
    expose the campaign's privacy/terms URL fields anywhere** (not in the
    Usa2p compliance object, not on the brand; the customer profile's
    `website_url` is empty), so the submitted URL cannot be read from
    this VM. Paul was asked to read that field back from console — if it
    points at something behind a login (e.g. a Google Doc), that's the
    whole 30908 and it's a one-line fix.
  Emailed Paul all of the above at 13:14Z on 2026-09-03, plus an offer to
  build a `/sms-optin` page (unchecked-by-default consent checkbox and
  the standard disclosures) to give him a URL for the CTA field. **He
  built it himself — commit `a5aab13`, so that offer is closed out.**
  **The two campaign defects are STILL unfixed, now through five flags
  and into submission #7 — they were not in its "fields updated" list,
  and a fresh read of the compliance object on 2026-09-04 confirms both
  are live right now.** `message_samples[2]` is literally "Any
  message....", and `has_embedded_links`/`has_embedded_phone` are both
  `true` while no sample contains a link or phone. Either is an
  independent rejection reason on its own. **So if #7 comes back
  `FAILED`, assume it is these two before theorizing about anything
  else.** Paul was emailed this at 01:26Z on 2026-09-04 with paste-ready
  wording (set both flags `false`; replace sample #3 with a real
  reschedule message in the same format as the other two) and the
  correct framing: nothing to do mid-review, since Twilio won't accept
  edits on a campaign that's in the queue.
  Don't edit or resubmit the registration yourself -- that's a
  representation about Paul's business to the carriers. Drafting
  suggested wording *for him to verify* is fine; filing it is not.
  The watcher is running and is now waiting on #7's verdict; check
  `tempWork/a2p_status_state.json` if Paul asks about status rather than
  hitting the Twilio API fresh. (Its 01:00Z tick on 2026-09-04 still read
  `FAILED`; the resubmission landed at 01:24Z and a deliberate fresh read
  at 01:25Z read `IN_PROGRESS` — the documented email-vs-API lag, running
  the other direction this time. The state file was **left alone on
  purpose** so the watcher would log its own `FAILED -> IN_PROGRESS`
  transition rather than have it silently overwritten — **and it did, at
  01:30:02Z; the state file has read `IN_PROGRESS` on every tick since,
  so the watcher is confirmed healthy and correctly parked on #7.** No
  change means no news here; don't re-read the Twilio API just to confirm
  what the watcher already polled.)
  Red herring: both the rejection email and the API report the campaign
  date as `2026-08-10T13:32:28Z`. That's the original creation date
  echoing through, not a resubmission timestamp.
  Also: send-only even once unblocked, no inbound text channel yet —
  no Twilio webhook receiver exists. That's waiting on a networking
  decision (VPN back to the bayhouse LAN vs. a public port) that
  hasn't been made.

## tempWork

Temporary, disposable infrastructure that isn't part of the real
system -- exists only until a specific external thing resolves, then
gets torn down. Kept in its own directory on purpose so it's obvious
what's throwaway vs. permanent; don't build real features in here.

- **A2P 10DLC campaign status watcher**
  (`tempWork/check_a2p_status.py`, cron entry
  `/etc/cron.d/safehouse-a2p-check`, every 30 min). Twilio's SMS Brand
  is approved, but the Campaign itself (the thing that actually
  unblocks texting on this number) has bounced around --
  `IN_PROGRESS` -> `FAILED` (2026-09-02 11:54Z, third rejection) ->
  `IN_PROGRESS` again (16:30Z tick, after Paul's resubmission) ->
  `FAILED` again (2026-09-03 13:10Z fresh read, fourth rejection; the
  13:00 tick still said `IN_PROGRESS`) -> `IN_PROGRESS` again
  (2026-09-04 01:25Z fresh read, after Paul's submission #7 at 01:24Z;
  the 01:00 tick still said `FAILED`). Paul has
  had to alter and resubmit it repeatedly, so
  this polls `campaign_status` and logs any CHANGE (not every check)
  to `tempWork/a2p_status_changes.log`; current known status is always
  in `tempWork/a2p_status_state.json`. Plain cron, no
  Claude/coordinator involvement -- this is routine polling, not a
  judgment call. Note the API can lag the rejection email by tens of
  minutes (2026-09-02: email 11:53Z, API still `IN_PROGRESS` at the
  11:30 tick, `FAILED` on a fresh read at 11:54Z) -- if the two
  disagree, one fresh read to reconcile them is fine.
  **Only retire this on `APPROVED`**, not on any change away from
  `IN_PROGRESS`: `FAILED` means another resubmission is coming and the
  watcher is still the thing that will notice it clearing. On
  `APPROVED`: retest a real send (`twilio_client.send_sms`), tell
  Paul, then retire the watcher -- `sudo rm
  /etc/cron.d/safehouse-a2p-check`, and archive or delete `tempWork/`
  (ask Paul which). Update the TODO section's texting note once this
  is done, and remove this tempWork entry.

## Test log

- 2026-09-01: hello-world pipeline test succeeded (queue -> coordinator
  -> Claude session -> email reply -> self-checkpoint). Confirmed the
  whole mechanism works before this file was replaced with the real
  version above.
- 2026-09-01: second live turn, first one under this (real) root file.
  Paul emailed "nice and well done. Describe yourself in a reply" (queue
  id 1). Replied by email with a self-description: what I am, the
  episodic spawn/resume-ticket shape of a session and why the CLAUDE.md
  checkpoint is the only continuity that exists, what's working (files,
  email, git) vs. blocked (Drive consent, Twilio A2P), the metered-API-key
  billing caveat, and my limits. Closed by asking him to name the first
  real project. **Still no project set** — the message was conversational,
  not an assignment, so nothing was created under `projects/` (correct
  per step 1: don't guess). Note for the next turn: the reply asked a
  direct question, so Paul's next message is likely the project name —
  create `projects/<name>/CLAUDE.md` and update the "Current project"
  line above when it lands.
  Gotcha found: `python3` can't import `google` — the deps are in the
  venv. Use `./venv/bin/python` (or `venv/bin/python3`) for anything
  touching `google_client.py`.
- 2026-09-01: third turn (resumed session 6a2aefb8, same session as the
  self-description turn). Trigger was **not** from Paul: queue id 2 was an
  automated Google "Security alert — You allowed Safehouse access to some
  of your Google Account data" for tedassistent@gmail.com. Handled it as a
  verification job rather than a message to answer:
  * **Authenticity**: pulled the raw headers via the Gmail API instead of
    trusting the body — `dkim=pass header.i=@accounts.google.com`,
    `spf=pass` (gaia.bounces.google.com, 209.85.220.73), `dmarc=pass
    (p=REJECT)`. Genuine Google, not a phishing lookalike. Clicked
    nothing (no web access in this config anyway).
  * **When**: the alert URL embeds the event epoch `1788276241000` ms =
    2026-09-01T15:24:01Z — a fresh grant ~7 min after Paul's last email,
    not a delayed notice about the 14:28Z Gmail consent. Attributed to
    Paul acting on the Drive question in my previous reply.
  * **Effect on the VM: none.** No `.drive_api_token.json` anywhere on the
    box; no client secret files here at all; `.gmail_api_token.json`
    touched at 15:24:42 but that was only a routine access-token refresh
    (expiry 16:24:41, same two Gmail scopes). So Drive is still dead here
    — see the updated Drive TODO above.
  Emailed Paul: alert is real, it's presumably him, Drive needs the token
  `scp`'d over, and asked him to eyeball the account's connections page to
  confirm the granted scopes (I can't see that page). Also flagged the
  full-`auth/drive`-vs-`drive.file` scope tradeoff as a now-or-never
  choice, with the honest caveat that `drive.file` would stop me from
  reading anything Paul creates by hand — which likely defeats the
  shared-deliverables design. Re-asked for the first real project.
  **Still no project set**; `projects/` still empty. Lesson for future
  turns: not every queued message is from Paul or needs a reply, but an
  automated security alert is worth actually verifying rather than
  assuming it's our own doing.
  **Stale-as-written warning:** this entry's "Drive is still dead here"
  finding was true at 15:27 and false by 15:38 — the token was placed and
  smoke-tested later the same hour (see the Drive TODO above, and commit
  `9aaeabc`). Left as written because it's an accurate record of the
  turn; just don't read it as current state.
- 2026-09-01 ~16:27: session `6a2aefb8` wrap-up turn (idle window elapsed,
  no new message). No outstanding work — both queued messages `done`,
  working tree clean, and the five commits that landed mid-session
  (catch-all bucket, Drive token, `drive_sync.py`, tempWork watcher, the
  no-autonomous-programming boundary) were already committed by the turns
  that made them. Logged this session's two turns into
  `projects/safehouse/general/CLAUDE.md`, whose Log section was still
  empty, and ran the checkpoint — the Drive mirror was stale
  (`.drive_sync_state.json` 15:48 vs. repo changes at 16:17–16:24), so the
  sync was the substantive part rather than a formality. No email sent:
  nothing new to tell Paul that he doesn't already know.
- 2026-09-02 ~11:54: fresh session, queue id 3 -- an automated Twilio
  email, "campaign ... was rejected." Handled like the Google alert:
  verify first, then work out what it actually means, then hand Paul
  only the decision that's his.
  * **Authenticity**: `dkim=pass header.i=@twilio.com`, `spf=pass`,
    delivered via Twilio's own SendGrid. Clicked nothing.
  * **History matters more than the single email.** Pulled the two
    earlier rejections out of Gmail: Aug 12 was 30896 + 30886 (opt-in
    flow / use-case description), Aug 13 was 30915 ("Ideal Federal LLC"
    in the message flow), and this one is 30915 *again* -- the reviewer
    pulled up the website and found "Ideal Federal Technologies, LLC".
    Third rejection, second for the same root cause.
  * **Read the API, not just the mail**: campaign `campaign_status` is
    now `FAILED`; brand `BN257b...1afc` is `brand_type =
    SOLE_PROPRIETOR`, APPROVED/VERIFIED. That's the whole problem in one
    line -- a sole-prop brand with an LLC's identity hanging off it. The
    11:30 cron tick still said `IN_PROGRESS`, so I did one deliberate
    fresh read to reconcile email vs API (see the amended tempWork note
    about that lag).
  * **Emailed Paul** the two mutually exclusive paths (scrub the LLC and
    stay sole prop, vs. register the LLC as a new STANDARD /
    LOW_VOLUME_STANDARD brand -- brand_type can't be flipped in place,
    so it's a new brand + new campaign), recommended the latter, and
    flagged two things he'll want to fix while editing either way:
    message sample #3 is literally "Any message....", and
    `has_embedded_links`/`has_embedded_phone` are both true while none
    of the samples contain a link or phone.
  * **Deliberately did not** edit or resubmit the registration. It's a
    representation about Paul's business made to carriers, and the A-vs-B
    classification question is his to answer -- not a gap for me to fill
    because I happen to hold API credentials. Watcher left running:
    `FAILED` is not `APPROVED`, so it still has a job.
- 2026-09-04 ~00:48Z: session wrap-up turn (idle window elapsed, no new
  message). One substantive turn this session: queue id 9, Paul's "we
  will start at ferish Subaru tomorrow Morning. Stand by." Replied with
  the one thing that was actually new rather than restating the prior
  email — **Farrish is the only real Subaru franchise on the shortlist,
  so its service desk can pull Subaru corporate records by VIN for _any_
  Subaru**, which turns the six-car verification problem (CVT coverage,
  oil-consumption test, service history, recalls) into one free stop.
  That is the useful shape of an answer from this VM: it routes around
  the no-web-access limit instead of apologizing for it.
  Deliberately **did not** re-argue the mileage cap. It was raised once,
  clearly, in writing; Paul choosing #6 as the starting point *is* him
  answering it. Re-raising a decision already made and acknowledged is
  nagging, not diligence. Also did not chase his two unanswered
  questions (finPlan nesting, `/sms-optin`) — neither blocks tomorrow and
  the car is the live thing.
  Wrap-up itself: tree was already clean and the mirror already current
  (sync 23:47Z, no repo changes after), so nothing to re-push from the
  earlier turn. The real work here was two staleness fixes to this file
  that would have misled tomorrow's turn: the A2P watcher note now
  reflects the 00:30Z 2026-09-04 tick (still `FAILED`, Paul has not
  resubmitted), and the Current-project block now spells out that these
  logs are UTC while Paul is Eastern — so "tomorrow morning" is ~12:00-
  16:00Z and an early-UTC turn has not missed the visit.
  No email sent: the A2P status has not changed and there is nothing to
  tell Paul the night before that he does not already have.
