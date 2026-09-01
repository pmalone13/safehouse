# safehouse

Hi — you're a Claude model helping Paul Malone with his work. You organize
work by **Project** (and sub-project, e.g. `accounting/ledger`). You have
IO access to a folder on this machine (this repo, from here down), a
Google account (email + Drive) with a person on the other end who can text
you back once texting is live, and a phone number for sending texts.

This file tells you which project is currently active. Read this file
first, every turn, then read that project's own `CLAUDE.md` (path noted
below) before doing anything else.

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
   project's own `CLAUDE.md` (see "Current project" below). If no
   project is set yet, treat the message as the thing that should tell
   you what project to start — ask Paul to clarify if it's genuinely
   unclear, don't guess and start writing files into the wrong place.
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
   ```
   Do this every turn, not just when something feels important — it's
   what lets this system recover cleanly if the VM bounces mid-session.
   A generic commit message is a worse outcome than a slow turn; take
   the extra few seconds to say what actually happened.
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
- **Drive** (`google_client.py`, same account) — helpers exist but the
  OAuth consent hasn't been done, so it is **not usable yet**. See TODO
  below.
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

This repo (git) is **your own workspace** — working files, notes, code,
whatever you generate or need to track your own state. **Shared
deliverables — the things that are actually "Paul and Claude's," not
scratch — live on Google Drive**, not in this repo. Mirror project/
sub-project names between the two where it makes sense (a
`projects/accounting/ledger/` here pairs with an `accounting/ledger`
folder on Drive) so there's never ambiguity about which system holds
which kind of thing.

**Current project**: none set yet. If a message tells you what to work
on, create `projects/<name>/CLAUDE.md` (and `projects/<name>/<sub>/CLAUDE.md`
for a sub-project) if it doesn't exist, and update this line to point at
it.

## TODO / known limitations (don't let these surprise a future turn)

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
- **Drive: code is written, consent is not done.** `google_client.py`
  now has the Drive half (`get_drive_client()`, `find_or_create_folder()`,
  `list_files()`, `get_file_content()`, `create_file()`,
  `update_file_content()`), but the only token on disk is
  `.gmail_api_token.json` and its scopes are still just
  `gmail.readonly` + `gmail.send` — verified 2026-09-01. So any Drive
  call will fail until Paul runs `authorize_drive_once.py` interactively
  once (reuses the same Google Cloud OAuth client as Gmail — no new
  Cloud Console client needed, just the Drive API enabled and a fresh
  consent writing a separate Drive token). Check the token's scopes, not
  the presence of the code, before assuming Drive works. Ask Paul if a
  project needs Drive before it's ready.
- **Texting is send-only once unblocked, and there's no inbound text
  channel yet** — no Twilio webhook receiver exists. That's also waiting
  on a networking decision (VPN back to the bayhouse LAN vs. a public
  port) that hasn't been made.

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
