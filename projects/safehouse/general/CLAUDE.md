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
