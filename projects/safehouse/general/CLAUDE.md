# safehouse/general

This is the catch-all bucket for anything that isn't a specific named
project — automated notifications worth a quick check (like the Google
security alert handled here), conversational messages from Paul, meta
questions about the system itself, one-off requests too small to deserve
their own project. Log what happened here; don't over-invest structure
into this sub-project since being the non-project bucket is its whole
point. If something that lands here turns out to be the start of real,
ongoing work, that's the signal to spin it out into its own
`projects/<name>/` instead of letting it accumulate here.

## Log

- **2026-09-01, session `6a2aefb8` (two messages).** Both predate this
  bucket existing, so the long-form write-ups live in the root
  `CLAUDE.md` test log; recording them here so the general log isn't
  misleadingly empty about work that belongs to it.
  * *Queue id 1 — Paul, "describe yourself in a reply."* Conversational,
    not an assignment. Answered by email (what I am, the episodic
    spawn/resume shape of a session and why the per-turn checkpoint is
    the only continuity, working vs. blocked capabilities, the metered-
    API-key billing caveat, my limits). Deliberately created nothing
    under `projects/` — correct call at the time, and the reason this
    catch-all bucket was invented shortly after.
  * *Queue id 2 — automated Google "Security alert: you allowed Safehouse
    access."* Exactly this bucket's stated use case. Treated as a
    verification job, not a message to answer: confirmed authentic from
    the raw headers (`dkim=pass @accounts.google.com`, `spf=pass`,
    `dmarc=pass` on `p=REJECT`), decoded the grant time from the epoch in
    the alert URL (`1788276241000` ms = 15:24:01Z), and established the
    grant had no effect on the VM because the token was still on Paul's
    laptop. Emailed him the one actionable thing (the `scp`) plus the
    `auth/drive` vs `drive.file` scope tradeoff while narrowing was still
    cheap.
  * *Resolved since, by later turns:* the Drive token did land (15:38)
    and was smoke-tested; Paul chose to keep full `auth/drive`. So the
    "Drive is dead here" statements in my turn-3 email and in the root
    log are now **stale** — Drive is live. Don't act on them.

- **2026-09-01 ~16:27 — session wrap-up (idle timeout, no new message).**
  Nothing pending: queue ids 1 and 2 both `done`, working tree clean.
  Sent no further email — Paul already knows Drive works (he placed the
  token himself), and the one question I'd asked twice, "what's the first
  real project," is now structurally handled by this bucket existing
  rather than being something to nag about. Ran the checkpoint (commit,
  push, `drive_sync.py`) mainly because the Drive mirror had gone stale:
  `.drive_sync_state.json` was from 15:48 but tempWork/ and utils/ landed
  at 16:17–16:24, so the mirror Paul reads was missing them.
  Open threads for whoever picks this up next: (1) no *named* project yet
  — wait for Paul, don't invent one; (2) A2P campaign still
  `IN_PROGRESS`, watcher running every 30 min, don't poll it by hand;
  (3) still no inbound text channel, pending the VPN-vs-public-port call.

- **2026-09-02 ~11:54 — queue id 3, automated Twilio A2P rejection.**
  Fresh session (the 2026-09-01 resume ticket had long expired). Another
  textbook case for this bucket: an automated notification that needed
  verifying and interpreting, not answering.
  * Verified the mail was really Twilio (`dkim=pass @twilio.com`,
    `spf=pass`, via Twilio's SendGrid), clicked no links.
  * Went past the single email: dug the two earlier rejections out of
    Gmail and read the campaign + brand objects from the Twilio API. The
    shape of it is that this is the **third** rejection and the **second**
    for error 30915 — a `SOLE_PROPRIETOR` brand with an LLC's identity
    visible to reviewers (this time on the website they pulled up:
    "Ideal Federal Technologies, LLC"). `campaign_status` is now `FAILED`.
  * Emailed Paul the decision, not a status update: two mutually exclusive
    paths (scrub the LLC and stay sole prop vs. register the LLC as a new
    STANDARD / LOW_VOLUME_STANDARD brand, which can't be done in place),
    my recommendation of the latter and why, plus two concrete defects in
    the current campaign he should fix while editing either way.
  * Did **not** edit or resubmit the registration despite holding working
    API credentials. Filing a business classification with carriers is
    Paul's representation to make; the whole question the rejection poses
    is one only he can answer. Worth remembering as the general shape:
    having the credentials to do a thing is not the same as it being mine
    to do.
  * Left the watcher running and amended the root file's teardown rule —
    it previously said to retire the watcher when status left
    `IN_PROGRESS`, which would have been wrong here. `FAILED` means
    another resubmission is coming; only `APPROVED` retires it. Also
    recorded the email-vs-API lag (email 11:53Z, API still `IN_PROGRESS`
    at the 11:30 tick, `FAILED` at 11:54Z).
  Open thread: waiting on Paul's A-vs-B answer. Until then texting stays
  blocked and there is nothing further to do on it from this VM.

- **2026-09-02 ~12:57 — session wrap-up (idle window elapsed, no new
  message).** Nothing pending and nothing to revise: queue id 3 handled,
  working tree clean at `7ff102b`, and one deliberate inbox read confirmed
  Paul hasn't answered the A-vs-B question yet (last inbound from him is
  still 2026-09-01). The watcher ticked at 12:00 and 12:30 and correctly
  logged nothing — status is stably `FAILED`, which is the expected
  resting state until Paul resubmits, so silence from it is the signal
  working, not the signal broken. Ran the checkpoint to carry the 12:30
  watcher-state files out to the Drive mirror.
  Open threads unchanged: (1) still no *named* project — wait for Paul;
  (2) A2P blocked on Paul's classification decision, watcher stays until
  `APPROVED`; (3) still no inbound text channel, pending the
  VPN-vs-public-port call.


- **2026-09-02 ~16:20 — queue id 4, automated Twilio "resubmission
  received."** Fresh session. On its face a no-action-needed
  acknowledgement; treating it that way would have missed the actual
  problem. Verified authentic (`dkim=pass @twilio.com`, `spf=pass`),
  clicked nothing.
  * **What Paul did between turns:** he never answered the A-vs-B email,
    he just went and executed **path A** — commit `89dcd6f` (16:04Z)
    added a standalone Flask site for idealfed.com (About/Privacy/Terms,
    gunicorn on 127.0.0.1:8091 behind nginx), deliberately free of LLC
    branding, then resubmitted the campaign with new Privacy/T&C URLs.
    API confirms: same brand `BN257b...1afc`, still `SOLE_PROPRIETOR`,
    `campaign_status` back to `IN_PROGRESS`, `errors` now empty. The
    scrub itself checks out — no "LLC"/"Ideal Federal" anywhere in
    `idealfed_site/`, description reads "Paul Malone of Tracys Landing MD".
  * **The finding: idealfed.com was unreachable from the internet.**
    Certbot issued a valid cert at 15:17Z and rewrote the `:80` server
    block to `return 301 https://...`, but inbound 443 is not open.
    Evidence chain: port 80 OPEN / port 443 times out (tested against the
    VM's own public IP 3.238.63.42); `curl --resolve idealfed.com:443:
    127.0.0.1 https://idealfed.com/privacy` returns **200**, so nginx and
    the cert are fine and only the packets are missing; `ufw` inactive and
    `iptables INPUT` an empty ACCEPT chain, so it's not the host — it's the
    AWS security group (instance `i-066d2ff2bfd9cf3c9`). No http fallback
    either, since :80 301s to the dead port. So every URL on the domain was
    a black hole starting ~the moment he resubmitted, and the reviewer who
    opens the privacy/terms URL gets a timeout — a near-certain 4th
    rejection after burning 1–3 business days.
  * **Did not fix it.** Opening a security-group port is an infrastructure
    change and lands on the wrong side of the hard boundary. Emailed Paul
    the diagnosis with the evidence, the one-line verification
    (`curl -sI https://idealfed.com/privacy | head -1`), and the SG names.
    Same principle as this morning's turn: holding the credentials to do a
    thing isn't the same as it being mine to do.
  * **Re-flagged, still unfixed:** "Fields updated" lists only the two URLs,
    and the API confirms `message_samples[2]` is still literally
    "Any message...." and `has_embedded_links`/`has_embedded_phone` are both
    true with no link or phone in any sample. Told him I don't know whether
    Twilio permits a mid-review edit vs. forcing submission #7 — that's a
    console question — but weighed against a guaranteed rejection.
  * Noted a red herring for future turns: both the email and the API report
    the campaign date as `2026-08-10T13:32:28Z`. That's the original
    creation date echoing through, **not** today's resubmission time.
  * Watcher untouched and still correct: 16:00 tick read `FAILED`, the
    16:30 tick will log `FAILED -> IN_PROGRESS`. Retire only on `APPROVED`.
  Open threads: (1) 443 closed — blocking, only Paul can clear it;
  (2) the two campaign defects, his call; (3) still no *named* project;
  (4) still no inbound text channel.
