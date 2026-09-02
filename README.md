# safehouse

What you get:

A phone number and an email address which are linked to an AI LLM
(Claude right now) in which 100% of your interaction is buffered
through an auditing and tracking layer plus a native language
interaction for managing multiple projects.


-------------------------------------------------------------------
A queue-driven personal AI assistant. Messages (email today, Twilio text
once approved) land on a FIFO queue; a coordinator spawns or resumes a
Claude Code session to handle each one, with the session's identity and
workflow defined entirely in `CLAUDE.md` — no separate app framework.
Runs on a single small Linux VM.  System benefits:

*  LLM interaction with full messaging and file audit trail because Claude.MD
   files and working folders are locally stored on VM, not LLM service.

*  Logging and auditing at FISMA Moderate level and complient with NIST 800-53.
   Cloud resident with native redundancy and backups under your personal account.

*  LLM tuned to managed multiple projects using natural language, "Start
   project 'trip to greece' and begin organizing a 10 day stay at x, y, z..."

*  All Project files are also mirrored to Google Drive for your access and
   review.

## Use cases

*  Use as companion to capture work on projects for home or the office.  Email it,
   Text it, send it attachments

*  Use it as a companion to a W2 'Position' and have employees perform work
   with this assistent only.  When staff changes occur, the safehouse stays
   with the position

*  Any "AI+Human" work in which there is an interest to understand how much
   insight and creativity came from the AI vs the Human.  Such as a piece of
   music or any other art and the work is pursuing Trademark or other special
   consideration.


## How it works

- `email_monitor.py` / Twilio webhook → `queue_db.py` (SQLite FIFO)
- `coordinator.py` claims each message and runs `claude -p`, resuming
  the same session (`--resume`) if the last one is still within its
  idle window — no process stays resident between messages
- `CLAUDE.md` is read fresh every turn and defines what the assistant
  actually does, including its own checkpoint (commit + push + Drive
  sync) at the end of every turn
- `drive_sync.py` mirrors the whole repo to Google Drive (one-way) so
  you can see what it's doing without SSH access
- `google_client.py` / `twilio_client.py` — Gmail, Drive, and SMS

## Setup

1. **VM**: any small Linux box with SSH + sudo (this was built on a
   414MB RAM instance + a 1GB swapfile — genuinely tiny is fine).

2. **Node.js 22+ and Claude Code CLI**:
   ```
   curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
   sudo apt-get install -y nodejs
   sudo npm install -g @anthropic-ai/claude-code
   ```

3. **Clone and set up the venv**:
   ```
   git clone <this repo> safehouse && cd safehouse
   python3 -m venv venv && venv/bin/pip install -r requirements.txt
   ```

4. **Claude auth** — put an API key from console.anthropic.com in `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

5. **Gmail** — create a Google Cloud project, enable the Gmail API,
   create a Desktop-app OAuth client, download it as
   `.gmail_api_client_secret.json`. Then, on a machine with a browser
   (not the VM):
   ```
   python authorize_once.py
   ```
   Copy the resulting `.gmail_api_token.json` to the VM.

6. **Drive** (optional) — same Cloud project, enable the Drive API, run
   `python authorize_drive_once.py` locally the same way, copy
   `.drive_api_token.json` to the VM.

7. **Twilio texting** (optional) — put your API Key SID (line 1) and
   Secret (line 2) in `~/.keys/twilioKeys`, and
   `TWILIO_ACCOUNT_SID=...` / `TWILIO_PHONE_NUMBER=...` in
   `~/.keys/twilioConfig`.

8. **Install and start the services**:
   ```
   sudo cp systemd/*.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now safehouse-logging-server safehouse-email-monitor safehouse-coordinator
   ```

9. **Write your own root `CLAUDE.md`** — who the assistant is, what
   tools it has, and its per-turn checkpoint contract. Use this repo's
   own `CLAUDE.md` as the reference shape.

10. Email the assistant's Gmail address. Check `queue.db` / the logs /
    the Drive mirror to see it work.

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and redistribute.
