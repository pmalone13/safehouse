# personal

Catch-all for Paul's own personal documents/records that aren't tied to
any other named project (car purchase, property management, trip
planning, etc). Created 2026-09-08 ~17:22Z by text (queue id 41).

## Contents

- `ssa.png` — a photo of Paul's Social Security card (or SSA
  correspondence), sent as an MMS attachment on queue id 41 ("create
  project called personal and store this pic. just my ssa."). Saved
  locally at `projects/personal/ssa.png`.
  **How it got here, since the normal inbound pipeline doesn't do
  this**: `twilio_webhook.py` only downloads and processes *audio*
  MMS attachments (voice messages) — non-audio media is explicitly
  left alone ("out of scope, not handled" per its own docstring). So
  the picture never reached this VM automatically; the queued message
  only carried the text body. Fetched it directly from Twilio's REST
  Media API instead (`Messages/{sid}/Media/{media_sid}`), using the
  same auth-token credential the webhook already uses for voice
  downloads — a one-off authenticated read via existing credentials,
  not a code change. Confirmed genuine: `image/png`, 1322x866, 101,845
  bytes, intact (`file` reports valid PNG, not corrupted).
  Source message: sid `MM3fcdd254b158c15dfa4170d66d4ddabc`, media sid
  `ME9820701ed71e93dc15e068f58471581c`, received 2026-09-08 17:21:58Z.

## Storage decision — deliberately NOT sent to Drive yet

Given what this document is (an SSN card / SSA record — about as
sensitive as personal data gets), two things this session's normal
checkpoint would otherwise do unthinkingly were both skipped on
purpose:

1. **Git**: not a concern — `projects/**` other than `CLAUDE.md` files
   is gitignored by design (confirmed with `git check-ignore`), so
   this file was never at risk of landing in git history or getting
   pushed to the remote.
2. **`drive_sync.py`**: **skipped this turn**, deviating from the
   normal "every checkpoint" rule in the root `CLAUDE.md`. Reason:
   `drive_sync.py` has a known, already-documented bug (see root
   `CLAUDE.md` TODO) — it reads every file as UTF-8 text
   (`errors="replace"`) and uploads as `text/plain`, silently
   corrupting any binary file. Proven on a `.docx` (11,425 replacement
   characters, unopenable). Running the standard sync on `ssa.png`
   would push a mangled-but-likely-still-partially-recoverable copy of
   an SSN document to Drive as an unprotected `text/plain` file — worse
   than not syncing it at all, not better. Following the same
   precedent the alliecar `.docx` situation set (flag it, don't
   silently assume the mirror has it).
   **Net effect: the only copy of this file right now is local to this
   VM**, at `projects/personal/ssa.png`. Told Paul this by text and
   asked how he wants it handled long-term — options include leaving
   it local-only, fixing `drive_sync.py`'s binary handling for real
   (application code, needs Paul present per the hard boundary), or
   moving it somewhere else entirely (e.g. he pulls it off the VM
   himself, or a dedicated secrets/document store rather than this
   general-purpose Drive mirror).

## Log

- 2026-09-08 ~17:24Z: project created, `ssa.png` fetched and saved per
  above. Replied by text confirming it's saved and flagging that Drive
  sync was deliberately skipped for this file, asking how he wants it
  stored longer-term.
