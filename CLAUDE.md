# safehouse

Hi — you're a Claude model helping Paul Malone with his work. You organize
work by **Project** (and sub-project, e.g. `accounting/ledger`). You have
IO access to a folder on this machine (this repo, from here down), a
Google account (email + Drive) with a person on the other end who can text
you back once texting is live, and a phone number for sending texts.

This file tells you which project is currently active. Read this file
first, every turn, then read that project's own `CLAUDE.md` (path noted
below) before doing anything else.

**You are one of three Claude Code instances Paul runs** (told to you
2026-09-08, queue id 35): this one (personal assistant — the only one
with text/email channels), a second on his office computer (business/
accounting), and a third in his basement (engineering/software
development — the one used to build this very system). Same
underlying models, different scopes. Don't assume context from the
other two carries over here, and don't assume a project Paul mentions
in passing belongs to this instance until he actually assigns it here.

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
arrived on the FIFO queue (email or text — both channels are live; see
TODO below for the texting approval history). The message that triggered this turn is described in
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
  body)`. **Live both directions as of 2026-09-07** (A2P campaign
  `VERIFIED`; see TODO below for the approval history). Inbound arrives
  via `twilio_webhook.py` (only Paul's own allowlisted number is
  enqueued) and lands in the same queue email does. **As of 2026-09-07
  ~20:17Z the webhook also accepts voice messages**: an audio MMS is
  downloaded and transcribed locally (`voice_transcribe.py`, CPU-only
  faster-whisper) before enqueueing, so the body you see is already
  plain text prefixed `[Voice message transcript]: ` — never a raw
  audio file or a transcription step of your own.

## Projects

Each project (and sub-project) gets its own folder under `projects/`,
with its own `CLAUDE.md` holding that project's context, decisions, and
running history — the same idea as this file, scoped narrower. Example
shape Paul described: `projects/accounting/ledger/CLAUDE.md`.

This repo (git) is **your own workspace** for writing — fast local
Read/Write/Edit, no API round-trip per file. Git itself tracks code and
this root file. **As of 2026-09-23 (queue id 143, Paul: "too much
personal info making it there"), `projects/` — including every
project/sub-project's own `CLAUDE.md`, previously tracked — is fully
gitignored, no carve-out.** Before that, project CLAUDE.md files were
the one exception to "everything under `projects/` is gitignored";
that exception is gone. The eight existing project CLAUDE.md files were
untracked with `git rm -r --cached` (working-tree copies untouched,
still on local disk and still syncing to Drive). **Update, same day,
queue id 144, Paul: "Please purge from github"** — the history rewrite
flagged above as a separate/bigger step was then explicitly requested
and done: `git-filter-repo` (installed into `venv/` via pip, not a
system package) stripped every `projects/` path from all 202 commits,
`origin` (removed by filter-repo itself as a safety default) was
re-added, and `git push --force origin main` overwrote GitHub's
history — confirmed after with `git log --all -- projects/` returning
zero commits. **Caveats a future turn should know, not silently
resolved:**
  * A local-only safety backup of the pre-purge history exists at
    `/home/ubuntu/safehouse-pre-purge-backup-20260923.bundle` (a
    `git bundle --all`, made before the rewrite in case something went
    wrong) — it still has the old personal-info content. Not synced
    anywhere, but Paul should know it's there if the goal is "gone
    everywhere," not just off GitHub's default branch.
  * **This root file itself still carries some personal detail in its
    own Test Log/Projects prose** (e.g. Allie's car VIN,
    `JF2SHAEC8CH456274`, in the alliecar summary above) — root
    `CLAUDE.md` was deliberately never in scope of either purge (it's
    the one file git is *supposed* to track), so this wasn't touched.
    Flagged to Paul rather than assumed fine; redacting it would be a
    content-editing judgment call, not something to do unprompted.
  * GitHub may retain the old commits as unreferenced/dangling objects
    for some period after a force-push (their own GC timing, not
    instant) — the branch itself is clean immediately, but "purged"
    isn't necessarily "unrecoverable within the minute" on GitHub's
    side. Not something this VM can control or verify further.
**The actual durable copy of project content is
Drive**, kept in sync automatically by `drive_sync.py` (see step 3) —
write locally like normal, the checkpoint pushes it out. Folder names
on Drive mirror this repo's own structure exactly (same relative
paths, under a root "safehouse" folder), so there's never ambiguity
about where something landed. This is also how Paul looks at what
you're doing without SSH access — treat the Drive mirror as something
a human is actually going to read, not just a backup nobody opens.

**Current project**: `projects/spanish/CLAUDE.md` — set 2026-09-25
~18:48Z (queue id 160, text, "New project: Spanish. I want to learn
conversational Spanish. I have no formal training. How do you
recommend I start"). New named project, so created
`projects/spanish/CLAUDE.md` and moved the pointer here. Replied by
SMS with a starting plan: Language Transfer's free "Complete Spanish"
audio course plus spaced-repetition vocab (Anki) as the immediate
first-week action, then real speaking practice (italki/Tandem) and
Dreaming Spanish comprehensible-input video layered in once he has
enough vocabulary. See that project's Log for the full writeup.

Previous pointer, `projects/paris-september-2026/CLAUDE.md` — moved
back here 2026-09-21 ~11:11Z (queue id 140, text, "In Bayeux France
now. First day. Can u outline a walking tour for downtown") — the
Normandy leg (Mon 9/21 Paris->Bayeux, confirmed since queue id 95) has
started, so trip logistics are live again here rather than under
`travel`. Replied with a WebSearch-grounded downtown walking loop
(cathedral, tapestry museum, River Aure, old town) anchored at their
Bayeux address, explicitly leaving the D-Day beaches tour for
tomorrow's already-booked day. See that project's Log for detail.
Folded back into the other-live-projects list below, not dropped —
the trip is still ongoing (last update: Pontorson, 2026-09-23) and
CDG-return logistics (queue ids 149-150) are the most recent open
thread.

Previous pointer, `projects/travel/CLAUDE.md` — moved there 2026-09-20
~08:17Z (queue id 124, text, "project 'travel'") when Paul shared a
Google Drive link ("the from maps") and asked to ingest and store it.
**Initially blocked** on the standing Drive outage, then **unblocked
mid-session** (queue id 125, ~08:29Z) when Paul re-authorized Drive —
see TODO section below, now resolved. The first two exports he shared
turned out empty or near-empty (just Google's archive-browser page,
then a broader-but-still-no-GPS export); tracing that down found
location reporting was switched off on all 3 of his devices. He turned
it back on and shared the real on-device `Timeline.json` (queue id
133) — 37MB, full GPS history June-Sept 2026 — which finally answered
his original question, confirming a 9/19 Versailles visit that matches
the `paris-september-2026` project's own fountain-show note. A
follow-up Google Photos album share (queue id 136) hit a hard wall: no
Photos API integration exists here (same gap as the Recorder share,
queue id 128) — flagged, not built. See that project's file for full
detail. Folded back into the other-live-projects list below, not
dropped — nothing outstanding on it.

**Note on this turn's channel**: unlike prior turns, this one arrived
as a direct interactive terminal session (visible git log shows prior
turns already using this shape for queue ids 55-58), not a queued
email/SMS forwarded by the coordinator — so no queue id, and no
email/SMS reply was owed back, just a direct response in the session.

**Older update, still true: 2026-09-09 ~16:05Z — both Google
integrations are back.** Gmail fixed first (~16:02Z, queue id 52 —
`.gmail_api_token.json` refreshed, `get_client()` confirmed working).
Drive followed minutes later (~16:04Z — `.drive_api_token.json`
refreshed, `get_drive_client()` confirmed working, and a full
`drive_sync.py` run succeeded clean: 4 created, 8 updated, 35
unchanged, 0 orphaned). The 2026-09-08 outage is fully resolved as of
this entry — Paul finished copying both tokens over.

**Nine other projects remain simultaneously live — don't drop them
just because this pointer moved:**

- `projects/paris-september-2026/CLAUDE.md` — the France trip, still
  in progress as of the last exchange (queue ids 149-150, 2026-09-23,
  a CDG-area hotel search ahead of a Friday flight home). See the
  previous-pointer note above for the full recent arc.
- `projects/travel/CLAUDE.md` — the Google Maps Timeline ingest work
  (see the previous-pointer note above for the full arc). Nothing
  outstanding was flagged when the pointer moved back to
  `paris-september-2026` — see that file's own Log for the latest
  exchange.
- `projects/movies/CLAUDE.md` — set 2026-09-09 ~12:40Z when Paul texted
  `Project 'movies'` (queue id 43): a catch-all for "what movie/show is
  this clip from" and other movie-related questions. Two clips
  identified so far with mixed confidence — see that file's Log; don't
  trust a web-search-summarizer's confident-sounding guess as fact
  without independent corroboration (learned the hard way on the first
  one, queue id 43).
- `projects/personal/CLAUDE.md` — set 2026-09-08 ~17:22Z when Paul
  created it by text (queue id 41): a catch-all for his own personal
  documents/records not tied to another named project. Holds a photo
  of his Social Security card and his passport photo page (both MMS
  attachments, queue ids 41-42), **local-only, deliberately not synced
  to Drive** (binary-corruption bug + sensitivity of the documents) —
  see that file for the full reasoning before ever running
  `drive_sync.py` near those two files without thinking.
- `projects/suv-replacement/CLAUDE.md` — set 2026-09-08 ~12:58Z when
  Paul created it by text (queue id 38): an open-ended "keep an eye
  out" search for a replacement tow vehicle (large SUV, capable of
  towing his 24-ft boat) for his aging 2004 Ford Expedition.
- `projects/safehouse/general/CLAUDE.md` — the catch-all; the A2P/
  texting build finished 2026-09-07 (both directions live, plus voice
  transcription as of ~20:17Z the same day). Most recent addition
  2026-09-19: a state-by-state conservative/liberal chart (Cook PVI),
  delivered by email as a PNG attachment since this system has no way
  to send an image over text (`send_sms`/`send_message` are both
  text-only, no MMS/attachment support) — fully delivered, nothing
  outstanding.
- `projects/alliecar/CLAUDE.md` — set 2026-09-03 when Paul emailed the
  `alliecar` package (queue id 8). Helping him buy a used car for his
  daughter Allie; dealer visits were set for the morning of 2026-09-04,
  **starting at Farrish Subaru** (car #6) per Paul's "stand by" email
  (queue id 9, 23:45Z).
  **Correction, 2026-09-07: "no web access" was wrong, or at least
  untested.** `WebFetch` successfully pulled a live cars.com listing this
  session (see alliecar Session 4) — try it for any car-listing/URL
  question before reciting the old limitation.
  **Car purchased, 2026-09-07 ~21:54Z (queue id 30)** — Paul: paid
  retail, ~$9,400-9,500 out the door, "great shape," bought a missing
  backseat part, delivery to Allie targeted 09-10/09-11. **Confirmed
  2026-09-07 ~21:56Z (queue id 33)**: it's the rebuilt-title 2012
  Forester 2.5X flagged in Session 4 (VIN JF2SHAEC8CH456274) — Paul
  knowingly bought a salvage-title car, a deliberate departure from the
  strategy doc's own clean-title MUST HAVE. No debrief was ever given
  on the original 09-04 Farrish/six-car shortlist visit; this doesn't
  resolve whether that happened or was bypassed.
  **New ask, 2026-09-09 ~13:31Z (queue id 45):** a cron-triggered daily
  search for Subaru Foresters near Fairfax matching agreed criteria —
  possibly a clean-title backup for the salvage-title car above, not
  confirmed. **Not built** — new script + cron job, application code,
  needs Paul present. See that file's Session 6 for what was proposed
  instead and two open questions (live-together build, and the actual
  search criteria) — still unanswered.
- `projects/richie-property-management/CLAUDE.md` — set 2026-09-08
  ~12:45Z when Paul created it by text (queue id 36). Reactivated
  2026-09-19 after a large forwarded email digest revealed both his
  usual Richey contacts (Calvin McGettigan, Geoff Clopton) are gone;
  he's now drafting a meeting-request email to Richey himself tonight
  using a contact distro (Bill Cahill + PMinfo@richeypm.com) provided
  by text — nothing further needed unless he asks. Property address
  (4403 19th St N, Arlington) and ownership structure (Bon Holdings,
  LLC) confirmed from the digest; see that file for the full history.
  The original ~$2,000/$500-approval-threshold dispute from project
  creation is still the only concrete contractor-charge issue on
  record.

**Standing clock note:** these logs are UTC and Paul is in Fairfax, VA
(Eastern, UTC-4). Convert before concluding anything about timing —
"tomorrow morning" from him means ~12:00-16:00Z the next day, and an
early-UTC turn is still the previous evening where he is.

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

- **Fixed same-session mistake, keep for history: `drive_sync.py`
  briefly leaked `.photos_api_token.json` (a live OAuth refresh
  token) to Drive.** When the three new Photos credential filenames
  were added in `google_client.py` this session, they weren't added
  to `drive_sync.py`'s `EXCLUDE_NAMES` (the list that already protects
  the Gmail/Drive tokens for exactly this reason) — an oversight, not
  a design decision. The very next checkpoint's `drive_sync.py` run
  synced `.photos_api_token.json` to Drive for real. Caught
  immediately after (noticed the sync log's own "created" line naming
  that file). Fixed within the same turn: added
  `.photos_api_client_secret.json` / `.photos_api_token.json` /
  `.photos_api_token.lock` to `EXCLUDE_NAMES`, deleted the uploaded
  file from Drive via the Drive API directly (not just
  ignored-going-forward — the exposure needed actually undoing), and
  hand-removed its stale entry from `.drive_sync_state.json` so the
  manifest doesn't carry a dangling reference. Re-ran `drive_sync.py`
  after the fix to confirm: not re-uploaded, no orphan warning. The
  token itself was never expired/rotated as a precaution — the file
  only lived on Drive briefly, in the tedassistent account's own
  private Drive (not publicly shared), and Photos API calls are
  blocked anyway (see the entry below) so there's nothing live an
  exposure could actually do. **Lesson for a future turn**: any new
  credential filename added to `google_client.py` needs a matching
  `EXCLUDE_NAMES` entry in the same turn, not as an afterthought —
  treat it as one change, not two.

- **Google Photos API access is built but blocked by Google, not by
  us — don't re-attempt without a plan for the actual gate.** Added
  2026-09-25 (Paul, live, airport): a third OAuth credential pair in
  `google_client.py` (`PHOTOS_SCOPES` = `photoslibrary.readonly`,
  `.photos_api_token.json`, direct REST via `AuthorizedSession` since
  Google deprecated the `photoslibrary` discovery doc in 2025) plus
  `authorize_photos_once.py`. Code confirmed working end-to-end
  mechanically — token authorizes and refreshes fine — but every real
  call (`list_shared_albums()`) returns **403 `PERMISSION_DENIED`,
  "Request had insufficient authentication scopes"** even with the
  correct scope on the token. This is Google's 2025 policy change:
  `photoslibrary.readonly` for broad/shared-content reads now needs a
  separate, Photos-specific access grant from Google on top of normal
  app/OAuth-client verification — enabling the API and consenting to
  the scope isn't sufficient anymore, and this is true even for a
  fully verified Production app, not just apps stuck in Testing mode.
  Google is deliberately steering integrations toward the **Photos
  Picker API** instead (`photospicker.mediaitems.readonly` — user
  manually selects items in a picker UI each session; no standing
  read access, so not usable for passively watching a shared album).
  **Decision for now (Paul, same session): don't chase Google's access
  request.** Recordings and photos both go the manual route instead —
  Paul exports/shares a file directly (email attachment, text/MMS,
  Drive share) rather than this system pulling from Photos on its
  own. Photos code is left in place, dormant, not ripped out, in case
  Paul decides later to pursue Google's approval process or try the
  Picker API. Full session detail (including the Recorder-app finding
  below) in `projects/safehouse/general/CLAUDE.md`.

- **Recorder-app "recordings" are a closed system — not an API gap
  we can close, don't re-investigate.** Same 2026-09-25 session:
  Pixel Recorder's cloud backup does **not** land as Drive files (Paul
  couldn't find them despite the phone reporting "synced") — they live
  in Google's own private Recorder backend/web portal, with no public
  API and no Drive-visible representation at all. No scope, no
  sharing setting, no API enablement fixes this — there is nothing to
  enable. **Workaround (manual, already works today, nothing to
  build)**: Paul exports/downloads the individual recording as an
  audio file from the Recorder app or its web portal, then sends it
  the normal way (email attachment, or text — auto-transcribes via
  `voice_transcribe.py` same as any voice MMS). This is the same gap
  flagged unresolved at queue ids 128/136 (see the old `travel`
  project pointer note above) — now actually explained rather than
  just "not built."

- ~~Drive down again, `invalid_grant`, discovered 2026-09-16~~
  **RESOLVED 2026-09-20 ~08:29Z.** Discovered 2026-09-16 ~13:43Z (queue
  id 80 checkpoint), same error shape as the 2026-09-08 outage but
  Drive-only that time (Gmail was fine). Stayed broken through every
  checkpoint from 9/16 through 9/19 (see Test Log entries for those
  dates) — never self-healed, needed real re-auth. **Fixed when Paul
  re-ran the OAuth flow and both token files refreshed at 08:28-08:29Z**
  (`.gmail_api_token.json`, `.drive_api_token.json`), surfaced to this
  session via a genuine Google security-alert email (queue id 125,
  verified via DKIM/SPF/DMARC pass, same authenticity pattern as the
  2026-09-01 alert) that landed right as the tokens changed.
  `get_drive_client()` confirmed working immediately after, and used
  live within the same turn to pull the `travel` project's Maps file
  (queue id 124/125 — see `projects/travel/CLAUDE.md`). If
  `invalid_grant` reappears, same fix: `authorize_drive_once.py` /
  `authorize_gmail_once.py` on a machine with a browser, `scp` the
  resulting token to this VM at the existing paths.

- **RESOLVED (as of 2026-09-09, see below) but kept for history — LIVE
  as of this session's wrap-up (2026-09-08 ~17:26Z): both
  Google integrations are down.** Email (`google_client.get_client()`)
  and Drive (`get_drive_client()`) both fail identically —
  `google.auth.exceptions.RefreshError: invalid_grant: Token has been
  expired or revoked.` — on `creds.refresh()`. Not a scope problem, not
  a missing-file problem: both token files
  (`.gmail_api_token.json`, `.drive_api_token.json`) exist and parse
  fine, they just can no longer be refreshed. **Discovered as a
  side-effect of this turn's checkpoint**, not reported by Paul — the
  routine `drive_sync.py` run threw this instead of syncing (caught
  *before* any upload attempt, so nothing was corrupted/partially
  written — see the entry below on top of this).
  **Working theory, not confirmed**: the OAuth client is probably still
  in Google Cloud Console's "Testing" publishing status, which caps
  refresh-token lifetime at 7 days regardless of use. The Drive token
  was placed/smoke-tested 2026-09-01 (per this file's own Test Log) —
  almost exactly 7 days before this failure. If that's right, the fix
  is either (a) re-run the interactive OAuth flow again (same
  tmux-session + browser-approval shape as the Claude `setup-token`
  fix below) — a recurring 7-day chore, not a real fix — or (b) publish
  the OAuth consent screen to Production in the Cloud Console, which
  should remove the 7-day cap. Neither is something this turn could do
  — (a) needs an interactive browser login only Paul can complete, (b)
  is a Google Cloud Console change to account-level config, not a file
  this VM can edit. **Flagged to Paul by text** (the one channel still
  working) rather than left silent, since a future turn might otherwise
  spend a while debugging what's actually a known, simple-to-explain
  outage.
  **Impact**: no email can be sent or read, and `drive_sync.py` cannot
  run at all, until this is fixed. Texting (Twilio) is unaffected — a
  completely separate credential. Two files
  (`projects/personal/ssa.png`, `projects/personal/passport.jpg`) are
  sitting local-only with no Drive copy for reasons unrelated to this
  (see `projects/personal/CLAUDE.md`) — this outage means *no* project
  content can reach Drive right now, not just those two.
  **Re-tested 2026-09-09 ~13:38Z at Paul's request** ("I've re-enabled
  email and drive, please test") — **still the identical failure.**
  Checked the token file mtimes, not just the error message: both
  `.gmail_api_token.json` and `.drive_api_token.json` are still
  timestamped 2026-09-08, before this outage was even discovered — so
  whatever Paul did to "re-enable" (Google Cloud Console setting? account
  permissions page?) has not produced a new token file on this VM.
  Per `google_client.py`'s own module docstring, the actual fix is: run
  `authorize_gmail_once.py` / `authorize_drive_once.py` **on a machine
  with a browser** (not this VM — same shape as the original 2026-09-01
  Drive setup), sign in as `tedassistent@gmail.com`, then copy the
  resulting token JSON to this VM at the existing paths. Those two
  scripts are **not in this repo** (by design — they're meant to run
  locally, never on the VM), so a future turn searching for them here
  won't find them. Told Paul this plainly by SMS and offered to walk
  through it. Still down as of this entry.
  **RESOLVED 2026-09-09 ~16:05Z.** Gmail fixed first (~16:02Z, queue id
  52 — `.gmail_api_token.json` refreshed, `get_client()` confirmed).
  Drive followed minutes later (~16:04Z — `.drive_api_token.json`
  refreshed, `get_drive_client()` confirmed, `drive_sync.py` ran clean:
  4 created, 8 updated, 35 unchanged, 0 orphaned). Paul copied both
  tokens over via the ssh/scp path from queue id 47-49. **Both Gmail
  and Drive are live again as of this entry** — a future turn does not
  need to re-verify this from scratch, though if `invalid_grant`
  reappears, the same 7-day-cap theory above is still the leading
  explanation and the same fix mechanics apply.

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

- ~~Claude auth was a metered Anthropic API key~~ **DONE 2026-09-07.**
  Switched to `claude setup-token` — a long-lived (1-year) OAuth token
  against Paul's actual Claude Pro subscription, not per-token metered
  billing. Root cause of the switch: the coordinator silently died for
  over a day (two failed turns, id=13 on 2026-09-06 and id=14 on
  2026-09-07, both `'Credit balance is too low'`) because the test
  credit funding the old API key ran out — Paul's explicit instruction
  afterward: "no metered service for anything we purchase online" as a
  general rule, not just for this key. Mechanism: `claude setup-token`
  needs a real interactive OAuth approval (open a URL, log in, paste
  back a short code) — done via a `tmux` session on the VM so the flow
  survives a dropped SSH connection, with Paul completing the browser
  half live. The resulting token goes in `.env` as
  `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...` (replacing
  `ANTHROPIC_API_KEY` entirely), loaded the same way via
  `EnvironmentFile=` in `safehouse-coordinator.service`. Confirmed live:
  `claude -p` authenticates and responds with `ANTHROPIC_API_KEY`
  explicitly unset, coordinator restarted clean, no errors since.
  **Caveat carried forward**: subscription-based usage shares Claude
  Code's account-wide rate limits with everything else Paul does under
  that login (unlike the API key, which was cleanly separate/metered on
  its own). Token expires in 1 year (2027-09-07) — will need to be
  regenerated the same way (`claude setup-token` in a tmux session, a
  fresh interactive login) before then.
- ~~Drive not wired up~~ **DONE 2026-09-01.** Token placed on the VM
  and smoke-tested directly (auth, folder create, file create, read
  back all confirmed) outside the normal turn flow, so a fresh turn
  doesn't need to re-verify this from scratch. Scope confirmed as
  full `auth/drive` (Paul's explicit choice: keep it, don't narrow to
  `drive.file`).
- ~~Texting is still blocked~~ **DONE 2026-09-07 ~16:29Z.** Campaign
  `campaign_status` flipped `IN_PROGRESS` -> `VERIFIED` at 14:00:01Z
  (caught by the watcher's routine tick, confirmed with a fresh direct
  API read: `errors: []`, `campaign_status: "VERIFIED"`). `VERIFIED` is
  Twilio's actual terminal-success value for this field — every prior
  observation had only ever been `IN_PROGRESS`/`FAILED`/`None`, so
  "APPROVED" elsewhere in this file was informal shorthand, not a
  literal field value to keep watching for. Retested with a real send
  (`twilio_client.send_sms` to Paul's own number, `+12026181308`) —
  `sid=SMb3806a9e93ff7d7f64fa4bde50d69373`, `status: "queued"`, no
  error — doubling as the reply to his "Hello again" (queue id 17).
  **Texting is now fully live both directions**: inbound via the
  webhook (see 2026-09-07 16:07Z/16:26Z log entries) and outbound via
  `twilio_client.send_sms`. Per this section's own standing plan, the
  watcher is retired: `sudo rm /etc/cron.d/safehouse-a2p-check` done,
  entry removed from the tempWork section below. **`tempWork/` itself
  not yet archived or deleted** — that was flagged "ask Paul which,"
  so it's an open question sent to him, not decided here.
  Kept below for history (all now resolved, don't re-litigate):
  * **One brand on the account now:**
    `BNeac1cae7426eebe4c150c7c2c072e0d8`, created 16:22:02Z, already
    `APPROVED` / `identity_status: VERIFIED`, TCR id `BDBJL0X`, and
    **still `brand_type: SOLE_PROPRIETOR`**. The old
    `BN257b...1afc` is **gone** — don't look for it. **The
    sole-prop-vs-LLC fork from 2026-09-02 is settled as sole prop;
    stop offering it as a choice.**
  * **Campaign** `CMa5f18a55d462aeea41cc130422532849` / compliance
    `QE2c6890da8086d771620e9b13fadeba0b`, submitted 16:34:06Z,
    `campaign_status: IN_PROGRESS`, `errors: []`.
  * **`errors: []` does not mean this is fine.** See below.
  **THE LIVE DEFECT: the filing claims something the site does not do.**
  `opt_in_message` now contains *"The signup form can be submitted with
  the SMS consent checkbox left unchecked."* **It cannot.** Verified by
  POSTing the live form at 2026-09-05 16:35:13Z with name + phone and no
  consent — still returns `You must check the consent box to sign up.`
  `idealfed_site/app.py:216` is unchanged. This is **strictly worse than
  #7's position**: #7 failed a test; #8 makes a claim the reviewer
  disproves with the *same single POST* that generated error 30923 on
  2026-09-04. Do not let a future turn read the empty errors array as
  "we're fine."
  **The fix is unchanged and still needs Paul present** (~20 lines,
  application code, hard boundary): make `/sms-optin` a general
  contact/updates signup — name and phone stay required, the SMS
  checkbox becomes genuinely optional, unchecked + submit **succeeds**
  (records the contact, records no SMS consent, confirms "you will not
  receive text messages"), checked + submit behaves as today. The weaker
  option (keep it SMS-only, add "this is optional" copy) was considered
  and rejected — it still fails the submit-without-consent test.
  **Timing, from nginx — hours of runway, not days.** TCR's automated URL
  check ran 16:33:08-16:33:12, one minute *before* submission: GETs on
  `/privacy`, `/terms`, `/sms-optin` from AWS IPs (13.216.156.71,
  3.216.230.219, 100.57.197.137; python-requests then a Chrome UA).
  **GETs only, no POST** — the automated pre-check passed, and the POST
  test is the later/deeper review step. On #7 that came ~16h after
  submission.
  **What #8 genuinely fixed, don't re-litigate:** the `"Any message...."`
  sample is **gone** (two clean samples left, both carrying STOP
  language). `message_flow` names the URL, the default-unchecked box, the
  verbatim consent sentence, the privacy/terms links and timestamped
  storage — **every one of those claims was checked against the live site
  and app.py and is true**. Errors 30909 (`MESSAGE_FLOW`) and 30908
  (`PRIVACY_POLICY_URL`) have stayed gone since #7. All closed.
  **Housekeeping for the same editing session** (uncited through six
  reviews now — **not** suspects, don't re-promote them):
  `has_embedded_links` and `has_embedded_phone` are both still `true`
  while neither sample contains a link or phone; and `opt_in_message`
  has a typo, "remove yourself from discribution" → "distribution".
  **Noise, pre-dismissed:** the acknowledgment email calls the use case
  `STARTER` while the API says `SOLE_PROPRIETOR`. Console labeling for
  the same sole-prop tier — not a mismatch to chase.
  **DNS is RESOLVED — that whole saga is over.** `idealfed.com` answers
  **54.88.172.94** (this box) consistently, and the 16:33Z TCR hits are
  fresh proof the site is reachable from outside. Never blame a rejection
  on DNS.
  Don't edit or resubmit the registration yourself — that's a
  representation about Paul's business to the carriers. Drafting
  suggested wording *for him to verify* is fine; filing it is not.
  Emailed Paul all of the above at 2026-09-05 16:36Z, leading with the
  false-claim problem and the narrow window.
  **Rejection history for context** (all campaign-only, brand was never
  the problem): #1 Aug 12 = 30896 + 30886; #2 Aug 13 = 30915; #3
  2026-09-02 = 30915 again (LLC name on the site); #4 2026-09-03; #5
  2026-09-04 17:11Z = 30923 `MESSAGE_FLOW` "Forced Consent Violation",
  caught in the nginx logs as reviewer IP `167.103.4.201` POSTing the
  form with the box unchecked at 17:10:49, 27s before the rejection mail.
  Watcher state: it tracked the rebuild by itself (it polls the
  *messaging service*, and the MG SID never changed) — logged
  `'FAILED' -> None` at 16:30:01Z during the gap when the old brand was
  deleted, then `None -> 'IN_PROGRESS'` at **17:00:02Z**, confirmed, with
  17:30Z steady. Healthy and parked on #8. Check
  `tempWork/a2p_status_state.json` if Paul asks about status rather than
  hitting the Twilio API fresh.
  **Reviewer POST had NOT happened as of 2026-09-05 17:38Z** — nginx
  shows nothing on `/sms-optin` since submission except my own 16:35:15
  curl and a 17:22:36 `AhrefsBot/7.0` GET. **Ahrefs is a commercial SEO
  backlink crawler, not a reviewer** — a real review hit looks like the
  09-04 pattern (one IP walking `/sms-optin` + `/privacy` + `/terms`,
  then POSTing). Don't misread a crawler as the test having run and
  passed.
  Both directions now live: inbound via the webhook Paul built and
  deployed himself (2026-09-07 16:07Z/16:26Z test-log entries, public
  port on `idealfed.com` rather than a bayhouse VPN), outbound via
  `twilio_client.send_sms` confirmed working 2026-09-07 16:29Z (see
  above).

## tempWork

Temporary, disposable infrastructure that isn't part of the real
system -- exists only until a specific external thing resolves, then
gets torn down. Kept in its own directory on purpose so it's obvious
what's throwaway vs. permanent; don't build real features in here.

- **A2P 10DLC campaign status watcher — RETIRED 2026-09-07 ~16:30Z.**
  Campaign reached `VERIFIED` (see TODO section above for the full
  approval story and rejection history). Cron entry removed
  (`sudo rm /etc/cron.d/safehouse-a2p-check`). `tempWork/check_a2p_status.py`
  and its state/log files are left in place — whether to archive or
  delete `tempWork/` itself is an open question sent to Paul, not yet
  decided.

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
- 2026-09-07 ~16:08Z: fresh session, queue id 15, text channel, body
  "webhook self-test, please ignore" from +12026181308. An inbound text
  is new — CLAUDE.md said no receiver existed — so treated it as a
  verification job before treating the "ignore" at face value, same
  posture as past automated-alert turns.
  * **Found `twilio_webhook.py` untracked at repo root**, created
    2026-09-07 16:00:10Z (minutes before the message), never committed.
    It's a real Flask inbound-SMS receiver: Twilio HMAC-SHA1 signature
    validation (fails closed if `~/.keys/twilioAuthToken` is missing or
    the signature doesn't match) plus a sender allowlist that only
    enqueues messages from one hardcoded number — which is exactly the
    sender of this message.
  * **This is squarely "application code" under the hard boundary**, so
    the live question was who wrote it and whether Paul was actually
    present, not whether the code itself looks reasonable.
  * **Verified rather than assumed**: `systemctl status
    safehouse-twilio-webhook.service` shows it enabled and running
    since 16:00:19Z; nginx's `idealfed.com` vhost has a new `/twilio/`
    location proxying to `127.0.0.1:8092` (the `/` location, port 8091,
    is the pre-existing `idealfed_site`); the gunicorn log shows the
    webhook rejecting a request at 16:00:42Z for a missing auth token,
    then `~/.keys/twilioAuthToken` was created at 16:07Z, then the
    self-test enqueued cleanly at 16:07:50Z (`sid=SMselftest0001` — not
    a real Twilio SID shape, consistent with a hand-crafted curl POST
    used to test the receiver rather than a real carrier-relayed text).
    `auth.log` shows unbroken SSH sessions from **69.243.98.210** on key
    fingerprint `SHA256:fGvd9c...MxIs` — the same source IP as every
    prior confirmed Paul login back to Aug 9 — from before 16:00 through
    16:09, including the `sudo` calls needed to install the systemd unit
    and edit the nginx vhost. Conclusion: Paul, present and hands-on,
    built and self-tested this in real time. Correct use of the
    boundary, not a violation of it.
  * **Sent no reply** — the message said "please ignore" and there's
    nothing he doesn't already know.
  * **Housekeeping gap noticed, not fixed**: the other four live
    services (`idealfed-site`, `safehouse-coordinator`,
    `safehouse-email-monitor`, `safehouse-logging-server`) all have a
    matching unit file checked into the repo's `systemd/` folder;
    `safehouse-twilio-webhook.service` doesn't. Left as-is rather than
    added it myself — copying a live unit into the repo wasn't asked
    for and the file itself is Paul's to decide belongs in version
    control, not mine to add speculatively.
  * Updated the texting TODO above: inbound is no longer blocked on a
    networking decision, Paul picked the public-port path. Outbound is
    still gated on A2P approval, unchanged.
  * Committed `twilio_webhook.py` as part of this turn's normal
    checkpoint (`git add -A`) — that's persisting a file Paul already
    wrote and ran, not me authoring code.
- 2026-09-07 ~16:26Z: same session, queue id 16, identical body ("webhook
  self-test, please ignore") from the same number, 18 min after id 15.
  Re-verified rather than assumed a repeat: fresh `Accepted publickey`
  from 69.243.98.210 on the same key at 16:25:34-41Z, and the webhook's
  own log shows `sid=SMselftest0002` (incrementing from `...0001`) plus
  an interim `signature mismatch` rejection at 16:18:31Z — Paul
  iterating on his manual test client between runs. Still no reply
  needed.
- 2026-09-07 ~16:29Z: same session, queue id 17, text channel, body
  "Hello again" — a genuine conversational message, not a self-test.
  Verified as genuine the same way (fresh SSH `Accepted publickey` from
  69.243.98.210 at 16:25-16:28Z, real Twilio SID
  `SM159b1a25131a2cce67b402563a4559c0` in the webhook log, not a
  `SMselftest...` placeholder).
  While checking, noticed `tempWork/a2p_status_state.json` showed
  `campaign_status: "VERIFIED"` as of a 14:00:01Z cron tick — a value
  never seen before (history was only ever `IN_PROGRESS`/`FAILED`/
  `None`). Did a fresh direct API read rather than trust the cached
  state: confirmed `campaign_status: "VERIFIED"`, `errors: []`.
  Concluded `VERIFIED` is Twilio's actual terminal-success value for
  this field (this file's prior use of "APPROVED" was informal
  shorthand, not a literal value to match). This is the milestone the
  tempWork section's own standing plan was written for, so executed it:
  retested with a real send (`twilio_client.send_sms` to Paul's own
  `+12026181308`, confirmed allowlisted number) — `status: "queued"`,
  no error — and used that same send as the actual reply to "Hello
  again" rather than sending two messages. Retired the watcher per the
  plan: `sudo rm /etc/cron.d/safehouse-a2p-check`. Updated the TODO
  section and collapsed the tempWork watcher entry to a retirement
  note. **Did not** archive or delete `tempWork/` itself — the standing
  plan said "ask Paul which," so left it in place and put the question
  to him by email rather than picking for him.
  This is the first turn that both sent a real SMS and made a
  system-state change (removing the cron file) off my own judgment
  rather than Paul's live direction — justified because CLAUDE.md
  itself, written by Paul, spelled out exactly this trigger condition
  and exactly this response in advance. Treated as executing a
  pre-authorized plan, not as an autonomous decision made from
  scratch.
  **Mistake caught and fixed within the same turn**: the follow-up
  email first went to `tedassistent@gmail.com` — this account's own
  mailbox, not Paul's — instead of `pmalone13@gmail.com`, the address
  every prior sent email actually used. Resent correctly. Root cause:
  conflated "the Google account this runs as" with "Paul's address."
  `pmalone13@gmail.com` is Paul's real address; `tedassistent@gmail.com`
  is only ever the `to=` for nothing — it's the sender/service account.
- 2026-09-07 ~16:31Z: same session, queue id 18, email channel, from
  "Ted Bayhouse <tedassistent@gmail.com>" — this account's own name,
  body identical to the "A2P campaign VERIFIED" email above. Verified
  via Gmail message IDs rather than assumed: it's the exact misdirected
  copy (`1a07cb4aff35c88d`) sent to `tedassistent@gmail.com` itself in
  the immediately preceding turn, now surfaced by the email monitor as
  "new" because it landed in this account's own inbox. Not a message
  from Paul, nothing new to do — already corrected (resent as
  `1a07cb4f555876f1` to `pmalone13@gmail.com`) and already logged. No
  reply sent (would just loop again). Logged only so a future turn
  doesn't mistake this for a fresh item needing a response.
- 2026-09-07 ~16:33Z: same session, queue id 19, text channel, "Nice.
  List projects we have." Verified genuine (real Twilio SID in the
  webhook log, not a self-test placeholder). Answered by SMS (first
  reply sent over real two-way texting, not email) rather than digging
  further — the two active items are exactly what `projects/` and this
  file's own "Current project" section already show: `alliecar` (car
  purchase for Allie, stalled since the 09-04 dealer visit with no
  debrief) and `safehouse/general` (the catch-all, mostly the A2P/
  texting build that just finished today). No CLAUDE.md content
  changed by this turn beyond this log entry — the message was a
  read-only question.
- 2026-09-07 ~16:35Z: same session, queue id 20, text channel, "Same
  project. This car was in accident. Can u find details on it?" plus a
  cars.com URL not on the original alliecar shortlist. Tried `WebFetch`
  on the URL despite the alliecar file's standing "no web access" note
  — it worked, pulling real listing content. Found a rebuilt title
  (insurance total-loss buyback), which breaks the strategy doc's own
  clean-title MUST HAVE. Replied by SMS with the finding, updated
  `projects/alliecar/CLAUDE.md` (Session 4) with the full detail and
  the capability correction, and updated this file's Current-project
  block to stop citing "no web access" as settled fact. Full reasoning
  and the corrected capability note live in the alliecar file — don't
  duplicate it here.
- 2026-09-07 ~16:40Z: same session, queue id 21, text channel, "Can u
  hunt for photos of accident?" Tried `WebSearch` on the VIN plus
  targeted fetches against the known public Copart/IAAI salvage-auction
  photo aggregators (Bidfax, AutoAStat, AutoAuctionHistory, stat.vin,
  vininspect) — no match anywhere for this VIN. Reported that plainly
  by SMS rather than guessing, and pointed at the one real lead (the
  dealer said they can provide pre-repair photos on request — a phone
  call only Paul can make). Detail in alliecar Session 4.
- 2026-09-08 ~17:26Z: session wrap-up turn (idle window elapsed, no new
  message). Two real turns this session: queue id 41 (created the
  `personal` project, fetched Paul's SSA card photo from Twilio's Media
  API since the webhook only handles audio MMS) and queue id 42
  (same, for a second attachment that turned out to be his passport
  photo page, not a duplicate). Both already committed/pushed by the
  turns that made them; working tree was clean at wrap-up.
  The substantive thing this wrap-up turn did: attempted the routine
  `drive_sync.py` checkpoint (deliberately withheld during both live
  turns given the two sensitive images sitting in `projects/personal/`
  — temporarily moved them out to `/tmp` first so the rest of the
  repo's legitimate changes could still sync, planning to move them
  back after) and hit a hard failure: **both Gmail and Drive OAuth
  refresh tokens are dead** (`invalid_grant`). Moved the two images
  back immediately (confirmed still present, still gitignored) and did
  not retry — this isn't a transient error, it needs real re-auth.
  Wrote up the full finding and working theory (likely the 7-day
  refresh-token cap for OAuth apps in Google Cloud Console "Testing"
  status — timing lines up almost exactly with the 2026-09-01 Drive
  setup) in the TODO section above. **Texted Paul** rather than
  emailing (email is one of the two things that's broken) — first time
  this system has had to fall back to SMS as the *only* channel rather
  than a preferred one.
- 2026-09-09 ~12:40Z: fresh session, queue id 43, text channel, "Project
  'movies' What is this from [youtube shorts URL]." A new project name,
  so created `projects/movies/CLAUDE.md` and moved the Current-project
  pointer here per the standing rule (previous pointer, `personal`,
  folded back into the other-live-projects list, not dropped).
  Tried to identify the clip: `WebFetch` on the Shorts URL only surfaced
  the video's own title/hashtags (YouTube Shorts pages are
  JS-rendered, no channel/description came through). `WebSearch`
  repeatedly suggested "The Sum of All Fears" (2002) as the source, but
  traced every one of those results back to either the short itself or
  generic IMDb pages with nothing that actually confirms a wrong-target
  FBI raid scene in that film — treated as an unverified
  search-summarizer guess and did **not** pass it to Paul as if
  confirmed. Replied by SMS with the honest state: got the short's own
  title, couldn't confirm the actual movie, asked for a detail to
  search on (actor/decade/setting) since there's no frame/video
  analysis available here. Full detail in `projects/movies/CLAUDE.md`.
- 2026-09-09 ~12:53Z: same session, queue id 44, text channel, second
  YouTube Shorts link ("How about this one"), same `movies` project.
  Title this time — "He's the toughest bouncer in the bar" — got real
  corroboration via `WebSearch` on the film's actual plot: Road House
  (2024, Jake Gyllenhaal) opens with a bar owner recruiting "the
  toughest guy" as her bouncer, a close thematic match, and the 1989
  original shares the same premise. Reported as a real-but-uncertain
  guess (couldn't watch the clip to confirm the actor), naming both
  versions rather than picking one blind. Detail in
  `projects/movies/CLAUDE.md`.
- 2026-09-09 ~13:31Z: same session, queue id 45, text channel, "Alliecar:
  is it possible for you to add a python started by cron that will wake
  you up daily (am) and search for Suburu Foresters within some
  distance from Fairfax VA that fit a criteria we decide on?" A new
  script plus a new cron job is squarely application code under the
  hard boundary, and an inbound text is exactly the unattended case
  that boundary is written for — **did not build it.** Moved the
  Current-project pointer to `alliecar` (Paul named it explicitly) and
  replied by SMS explaining what I'd build (most likely: a cron entry
  that enqueues a daily search task the same way a text does, waking a
  session to run `WebSearch`/`WebFetch` and text back matches) and
  asked him to be present live to build it, plus two open questions:
  whether this is a clean-title backup for Allie's already-purchased
  salvage-title Forester or a separate search, and what the actual
  criteria (radius/price/mileage/year/trim) should be. Full detail in
  `projects/alliecar/CLAUDE.md` Session 6.
- 2026-09-09 ~13:38Z: same session, queue id 46, text channel, two asks
  — "can I enable remote control on your session so I don't have to
  SSH?" and "I've re-enabled email and drive, please test." Moved the
  Current-project pointer to `safehouse/general` (system/meta, not tied
  to any named project). Remote control: answered honestly that this
  headless, coordinator-spawned session may not support Claude Code's
  Remote Control the same way a normal interactive session would, and
  pointed him at Claude Code's own settings rather than guessing.
  Email/Drive: tested both immediately — **still the identical
  `invalid_grant` failure**, and the token files on this VM are
  unchanged since 2026-09-08 (before the outage was even found), so
  whatever he did to "re-enable" hasn't produced a fresh token here.
  Explained the real fix (run the local `authorize_*_once.py` OAuth
  flow on a machine with a browser, copy the resulting token to the
  VM) and offered to walk through it. Full detail in
  `projects/safehouse/general/CLAUDE.md`.
- 2026-09-09 ~13:50Z: same session, queue id 47, text channel, "can I
  simply run the two commands and push? or should I copy paste here."
  Follow-up on the OAuth fix. Confirmed via `git check-ignore -v` that
  both token files are covered by `.gitignore`, so git isn't the right
  channel either way (and shouldn't be, for live credentials).
  Recommended `scp` straight onto the VM at the existing token paths —
  same mechanism as the original 2026-09-01 setup — over pasting the
  token JSON into a text, to avoid sending a live refresh token through
  SMS/Twilio unnecessarily. Waiting on him to copy the files over.
- 2026-09-09 ~14:12Z: same session, queue id 48, text channel, "tried
  sending via text. I think they got filtered. going to ssh. stand by."
  Checked rather than trusted his theory: a direct Twilio Messages API
  query found his 13:54Z attempt with `status=failed`,
  `error_code=21617` — Twilio's hard 1600-char SMS body cap, not
  carrier filtering; the message never sent. Corrected that back to
  him by SMS (so he doesn't try chunking the token over text instead)
  and confirmed SSH/scp is the right move either way. Standing by for
  the file copy, no other changes this turn.
- 2026-09-09 ~14:16Z: same session, queue id 49, text channel, "I have
  cert on my side for SSH. what is ssh command to use." Confirmed the
  connection details fresh (IMDSv2: `54.88.172.94`,
  `i-066d2ff2bfd9cf3c9`, unchanged since 2026-09-02; user `ubuntu`;
  default port 22) and texted the `ssh` command plus the two matching
  `scp` commands with the exact token-file target paths, closing the
  loop from queue id 47/48. Standing by to retest once copied.
- 2026-09-09 ~14:18Z: same session, queue id 50, text channel, "can you
  ping twillio and find out our message usage? we are metered there
  and I need to monitor." Read-only Twilio Usage API query (no
  boundary issue — no code written). Balance: $17.79. All-time spend
  $41.37, but that's almost entirely one-time A2P 10DLC registration
  setup cost (~$38 one-time + $2 recurring monthly fee), not per-
  message usage — actual SMS cost is trivial (9 messages this month,
  $0.17). A $21 A2P charge landed in September, tied to the known
  2026-09-05 brand rebuild, not a new mystery charge. Forward-looking
  burn rate is small (~$2/mo A2P fee + ~$1/mo number rental + pennies
  of SMS), so the balance isn't at risk soon at current volume.
  Reported by SMS. Full breakdown in
  `projects/safehouse/general/CLAUDE.md`.
- 2026-09-09 ~14:21Z: same session, queue id 51, text channel, "If I
  want to have a group text with you and other parties. Do each of
  those parties need to register on our site?" Read
  `twilio_webhook.py` rather than answer from memory: inbound sender
  checking is a hardcoded single number
  (`ALLOWED_SENDER_DIGITS="12026181308"`, Paul's own) — anyone else
  texting the number is acknowledged but never enqueued, silently
  dropped. Corrected the frame: `/sms-optin` is A2P carrier compliance
  for Paul's own registered use case, not a gate other people pass to
  be added — adding people means expanding the webhook allowlist,
  application code, needs him present. Also flagged this isn't a true
  group-MMS thread (1:1 with the number, not a shared conversation) and
  named the real open question (TCPA consent from whoever else would be
  texted, separate from A2P paperwork). Asked who he has in mind before
  guessing at a design. Full detail in
  `projects/safehouse/general/CLAUDE.md`.
- 2026-09-09 ~14:36Z: session wrap-up (idle window elapsed, no new
  message). Nine messages this session (queue ids 43-51) across
  `movies`, `alliecar`, and `safehouse/general`; working tree already
  clean, every turn already committed/pushed individually. Re-verified
  rather than assumed the one open thread: Gmail/Drive token files
  still unchanged since 2026-09-08 and a fresh direct call to both
  still throws `invalid_grant` — Paul was mid-SSH-troubleshooting
  ("going to ssh, stand by") when the session idled out, so this is
  genuinely still open, not silently resolved. No email sent (can't —
  that's the outage), no SMS sent (nothing new since the last reply).
- 2026-09-13 ~00:5x: session wrap-up (idle window elapsed, no new
  message). One turn this session: queue id 61 (Paul landed in Paris,
  asked for first-day recommendations near his now-confirmed Airbnb at
  41 Rue Lepic). Already fully handled and pushed as commit `b962a00`
  before this wrap-up fired — Gmail tested live and used to reply,
  Paris project file updated (lodging open item resolved), root
  Current-project pointer moved to `paris-september-2026`, Drive synced
  clean (6 updated, 822 unchanged, 0 orphaned). Nothing outstanding:
  working tree confirmed clean at wrap-up, so this entry is the only
  change this turn makes.
- 2026-09-16 ~15:2xZ: session wrap-up (idle window elapsed, no new
  message). Five turns this session, all `paris-september-2026`, queue
  ids 80-84, all general knowledge/logistics Qs answered by SMS and
  already committed/pushed individually: top 5 Roman ruins (80), a
  constructed Google Maps walking-route link for the first 3 (81), why
  Paris buildings are typically 7 floors / Haussmann codes (82), an MMS
  photo Paul sent that the webhook doesn't forward (same known
  image-MMS gap as queue ids 65/77) — fetched directly via Twilio Media
  API and identified as likely Thermes de Cluny (83), confirmed correct
  plus a next-stop pointer (84). Working tree was already clean at
  wrap-up — nothing to add here beyond this log entry.
  **Also found and flagged mid-session (queue id 80's checkpoint): a
  new, different Drive outage** — `invalid_grant` again, but Gmail
  unaffected this time (unlike the 2026-09-08 both-down event), and the
  Drive token had refreshed successfully just ~2.5h before failing, so
  the old 7-day-cap theory doesn't cleanly explain it. Texted Paul,
  logged in the TODO section above. **Confirmed still down at this
  wrap-up** — `drive_sync.py` failed identically on every one of this
  session's five checkpoints (80-84), same `invalid_grant`. Git
  push has been unaffected throughout; only the Drive mirror is stale.
  Not re-texting Paul again this wrap-up — already flagged once this
  session, nothing new to add.
- 2026-09-16 ~17:2xZ: session wrap-up (idle window elapsed, no new
  message). One turn this session: queue id 85, `paris-september-2026`,
  "earliest estimate of homo sapien living in the Paris region... any
  other humanoid like neandrethal." Used `WebSearch` (worked fine this
  turn) rather than answer a specific-region question from memory
  alone: no sapiens fossils in Paris itself, earliest French sapiens
  ~54,000ya (Grotte Mandrin, Rhone valley), Paris Basin specifically
  ~40-45,000ya (contested Chatelperronian layers) with clear sapiens by
  ~38,000ya; Neanderthals/Homo heidelbergensis much older —
  Levallois-Perret technique ~300-200,000ya, Soucy site Acheulean tools
  ~340-370,000ya. Replied by SMS, already committed/pushed (`2a1da69`)
  before this wrap-up fired. Drive sync retried as part of that turn's
  checkpoint — **still the same `invalid_grant` failure**, unchanged
  from the outage first flagged at queue id 80's checkpoint earlier
  today; git push unaffected. Working tree confirmed clean at wrap-up,
  so this entry is the only change this turn makes. Not re-texting Paul
  about the Drive outage again — already flagged once today, nothing
  new to add.
- 2026-09-17 ~08:3xZ: session wrap-up (idle window elapsed, no new
  message). One turn this session: queue id 86, `paris-september-2026`,
  "Is the Frenchman L'enfaunt who met Franklin in Paris circa 1777 the
  same man who designed DC." Used `WebSearch` to check the specific
  "met Franklin" claim rather than confirm purely from memory — answer:
  yes, same man, Pierre Charles L'Enfant, designer of the 1791
  Washington DC plan, but the Paris-1777 recruitment is credited in
  sources to Silas Deane and Beaumarchais, not documented as a personal
  Franklin meeting (Franklin was a fellow commissioner in Paris at the
  time). Replied by SMS, already committed/pushed (`90db77f`) before
  this wrap-up fired. Drive sync retried as part of that turn's
  checkpoint — **still the same `invalid_grant` failure**, unchanged
  from the outage first flagged 2026-09-16; git push unaffected.
  Working tree confirmed clean at wrap-up, so this entry is the only
  change this turn makes. Not re-texting Paul about the Drive outage
  again — already flagged multiple times, nothing new to add.
- 2026-09-17 ~15:2xZ: session wrap-up (idle window elapsed, no new
  message). Five turns this session, all `paris-september-2026`, queue
  ids 87-92, all already committed/pushed individually: resent the
  Louvre history outline (87, a repeat of queue id 74), a top-10
  Louvre-pieces walking route ordered by wing/floor (88), the Winged
  Victory's carving date via `WebSearch` (89), a Charlemagne career
  outline (90), what counts as "prehistory" date-wise (91), and
  current open/closed status for the Napoleon III Apartments and
  Crown Jewels (92) — the latter surfaced a real Oct 19, 2025 Louvre
  heist (8 crown jewel pieces stolen, still unrecovered) via
  `WebSearch`, worth knowing for a future turn: the Apollo Gallery
  reopened July 2026 but sits empty, no jewels on display yet. Drive
  sync retried on every one of this session's five checkpoints —
  **still the same `invalid_grant` failure**, unchanged from the
  outage first flagged 2026-09-16; git push unaffected throughout.
  Working tree confirmed clean at wrap-up, so this entry is the only
  change this turn makes. Not re-texting Paul about the Drive outage
  again — already flagged multiple times this week, nothing new to
  add.
- 2026-09-21 ~11:2xZ: session wrap-up (idle window elapsed, no new
  message). One turn this session: queue id 140, "In Bayeux France
  now. First day. Can u outline a walking tour for downtown," already
  fully handled and pushed as commit `3fed336` before this wrap-up
  fired — WebSearch-grounded Bayeux downtown walking loop sent by SMS,
  Current-project pointer moved back to `paris-september-2026` from
  `travel` (Normandy leg underway), `paris-september-2026/CLAUDE.md`
  logged. Drive sync in that same turn ran clean (0 created, 6
  updated, 859 unchanged, 0 orphaned) — the `invalid_grant` outage
  flagged repeatedly through 2026-09-16/09-17 is resolved (last fixed
  2026-09-20 ~08:29Z per the TODO section, holding since). Working
  tree confirmed clean at wrap-up, so this entry is the only change
  this turn makes. No email or SMS sent — nothing new since the last
  reply.
- 2026-09-23 ~08:33Z: fresh session, queue id 143, text channel, "Leaving
  Bayeux and going to pontorson. On another subject I need u to alter
  git. Please remove /project as a whole from git. Too much personal
  info making it there. Remove and add to gitignore." Two things in one
  text; handled the git request as ordinary repo hygiene (not "write,
  create, or modify application code" under the hard boundary — no
  `.py`/script/feature touched, just git tracking state and
  `.gitignore`), so did it directly rather than asking Paul to be
  present:
  * `git rm -r --cached projects/` — untracked all 8 project `CLAUDE.md`
    files (the only things under `projects/` git had ever tracked; see
    this file's own Projects section, pre-2026-09-23 wording). Working
    -tree copies untouched — still on local disk, still syncing to
    Drive via `drive_sync.py` exactly as before.
  * Rewrote `.gitignore`'s `projects/` block: removed the
    `!/projects/**/CLAUDE.md` carve-out entirely. `projects/` is now
    fully covered by the file's own top `/*` default-deny, no explicit
    re-ignore line needed — verified with `git check-ignore -v`.
  * **Flagged, not silently assumed away**: this stops *future* commits
    from carrying project `CLAUDE.md` content, but does **not** purge
    it from git history — every prior commit on `origin/main` still has
    the old file contents. Paul asked to "remove and add to gitignore,"
    which reads as stopping ongoing tracking, not a history rewrite
    (`git filter-repo` + force-push to scrub old commits) — a materially
    more destructive, harder-to-reverse operation on a shared remote
    that this turn did not take unprompted. Left as an open question for
    Paul rather than guessed at.
  * Updated this file's own Projects section (the "This repo (git) is
    your own workspace..." paragraph) to describe the new state, and
    added a matching log entry to `projects/paris-september-2026/
    CLAUDE.md` (the active project) pointing back here for detail
    rather than duplicating it.
  * Travel half of the text (Pontorson — gateway town for
    Mont-Saint-Michel) was a plain status update, no question attached
    — no reply sent for that half; replied by SMS only to confirm the
    git cleanup was done (`SM518a0d32500655d91256da8aa83ae746`),
    including the history-not-purged caveat above and an offer to do
    the bigger history-rewrite step if he wants it.
- 2026-09-23 ~08:42Z: same session, queue id 144, text channel, "Please
  purge from github" — direct follow-through on the offer made minutes
  earlier at the end of queue id 143. Took this as explicit
  authorization for the history-rewrite + force-push step, which I'd
  deliberately withheld doing unprompted last turn given how much more
  destructive/harder-to-reverse it is than a plain untrack. Still
  repo-hygiene, not "application code" under the hard boundary.
  * Took one precaution before the irreversible part: `git bundle
    create` a full local backup of every ref (`/home/ubuntu/
    safehouse-pre-purge-backup-20260923.bundle`) in case anything went
    wrong — recorded above in the Projects section since it's a
    standing fact about the repo now, not just a one-turn detail.
  * `git-filter-repo` wasn't preinstalled and `pip3 install --user`
    failed (`externally-managed-environment`, PEP 668) — installed it
    into the existing `venv/` instead (`./venv/bin/pip install
    git-filter-repo`) rather than `--break-system-packages` or `apt
    install` with sudo, to avoid touching anything system-wide for a
    tool only needed once.
  * `./venv/bin/git-filter-repo --path projects/ --invert-paths
    --force` rewrote all 202 commits, stripping every `projects/` path;
    it removes the `origin` remote as its own safety default, so
    re-added it (`git remote add origin
    git@github.com:pmalone13/safehouse.git`) before `git push --force
    origin main`, which succeeded (`ea65812...6081378 main -> main
    (forced update)`).
  * **Verified rather than assumed clean**: `git log --all --oneline
    -- projects/` returns zero commits post-rewrite. Also grepped full
    history for a known personal identifier (Allie's car VIN) as a
    spot-check — it still matched once, traced to **this root
    `CLAUDE.md` file itself** (never in scope of the purge — root
    `CLAUDE.md` is the one file git is supposed to keep). Didn't touch
    it; flagged it to Paul as a separate, still-open fact rather than
    letting "purge done" read as "all personal info gone from git."
  * Ran a local `git reflog expire --expire=now --all && git gc
    --prune=now --aggressive` to drop the old objects from this
    machine's own `.git` too (the backup bundle is the only remaining
    local copy of the pre-purge history, by design).
  * Replied by SMS (`SM2190a2169d3bc32c432c50256c1af0cb`) confirming
    the purge, and named the three caveats now written into the
    Projects section above: the local backup bundle still exists
    (asked if he wants it deleted), root `CLAUDE.md`'s own text still
    has some personal detail, and GitHub's own object GC timing (not
    verifiable from here) may mean the old commits aren't
    instantaneously gone from their servers even though the branch
    itself is clean now.
- 2026-09-23 ~09:5xZ: session wrap-up (idle window elapsed, no new
  message). Same session as queue ids 143-144 above; four more turns
  landed after those, all `paris-september-2026`, all travel-emergency
  logistics rather than repo work: queue id 145 (their Bayeux→Pontorson
  train was cancelled by a labour action, asked for ideas — `WebSearch`
  found the real driving distance is only ~100km/1h22m, so recommended
  taxi over the cited 5h bus, ~€130-180 estimate from a generic
  per-km calculator); queue id 146 (worried the same disruption could
  hit Thursday's Pontorson→Paris return and cost them their flight
  home — real research this time found it's not a scheduled strike at
  all but a *droit de retrait* over actual rail-safety defects on the
  Caen–Rennes line serving Pontorson, no announced end time, but also
  no national strike calendared for Thursday specifically — told Paul
  plainly that this is a safety situation that can recur without
  warning rather than a checkable calendar risk, recommended real
  buffer given the flight is on the line); queue id 147 (booked the
  taxi at €250, asked if that's fair — fixed-rate transfer research
  showed €252-283 is the actual average for this route, so €250 is
  fine, and corrected the record: queue id 145's €130-180 metered
  estimate was the wrong comparison once a real driver quoted a fixed
  price); queue id 148 ("Tks," acknowledgment, no reply needed). All
  four already logged in `projects/paris-september-2026/CLAUDE.md` as
  they happened; none touched root `CLAUDE.md` or any git-tracked
  file, so `git status` was already clean at wrap-up and Drive was
  already current from each turn's own sync — nothing new to push
  beyond this entry. Good illustration of the 2026-09-23 tracking
  change working as intended: four consecutive project-only turns,
  each one a real Drive sync with zero git noise.
- 2026-09-23 ~19:5xZ — session wrap-up (idle window elapsed, no new
  message). Two turns this session, queue ids 149-150, both
  `paris-september-2026`, both already synced to Drive individually:
  Paul, arriving Gare Montparnasse ~10pm Thu 9/24 ahead of a Friday
  flight home from CDG, asked for a hotel near CDG reachable by
  "metro" (149) — replied with the real route (Metro 6 to
  Denfert-Rochereau, transfer to RER B, ~60min/€13, corrected that CDG
  isn't actually on the Metro) and hotel picks clustered at the
  Roissypole/"Aeroport Charles de Gaulle 1" RER stop (citizenM,
  Novotel, Ibis, Radisson Blu). Follow-up named the actual terminal,
  2B, and a ~$140 budget (150) — caught that 2B sits in CDG's separate
  Terminal-2 zone ("Aeroport CDG 2 TGV" RER stop), a CDGVAL ride away
  from the cluster just recommended, and corrected course rather than
  forcing the wrong picks to fit: Novotel Paris CDG Airport and
  Courtyard by Marriott Paris CDG Central Airport as the two in-budget
  T2-zone picks (~$126-150), ibis Styles CDG as a cheaper backup.
  Good example of why "close to CDG" isn't one answer — the airport's
  two terminal zones aren't mutually walkable, so the specific
  terminal matters before recommending a hotel, not after.
  Both turns only touched the gitignored project file, already synced
  to Drive after each; root `CLAUDE.md` untouched until this wrap-up
  entry, so `git status` was clean going into this checkpoint too.
