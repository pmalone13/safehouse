# safehouse

What you get:

A phone number and an email address which are linked to an AI LLM
(Claude right now) in which 100% of your interaction is buffered
through an auditing and tracking layer plus a native language
interaction for managing multiple projects.
-------------------------------------------------------------------

## Philosophy

I'm posting because I've spent a lot of time working with AI over the past years and honestly I wanted a place to write this down so I can refer folks when asked what I think.
In a nutshell, I believe that from now on, each one of us should build our "AI History" in detail under some secure storage that you own, or at least each of us should plan on collecting and archiving our AI interaction histories somewhere.   
AI History is the set of data owned by 3rd party companies, one for each "account" which captures the interaction between a human and an AI model.  When working with AI, periodically the model will 'summarize' your session to reduce its memory footprint and provide for a more optimized AI runtime environment.  The AI  memory is optimized for your specific work.  This is how many of use are using AI now.  
As I use AI, when I'm working on a project, I will go down many dead ends that didn't work for my goals.  When the AI summarizes, you loose the granularity of "how" did you get from inception to product creation.  In my humble opinion, keeping that detailed log is critical to understanding the dynamic betwee the AI model and the human.  Today the detailed logs do exist but they are not owned by the human if you are using one of the commone models.
As I write, Organizations are using AI in the workplace.  Individual contributors are given AI resources such as CoPilot or Claude or Grok or ChatGpt or some home grown AI models.  In all cases, the Organization "owns" the accounts/logs and the work product, however, you the Human own the  "Human AI Creation Experience" having been the Human side of the effort.  In practice, Organizations give AI Agents to Employees to do creative work.  All of which is owned by the Organization.  However, you, the human are creating with the AI and you are becoming better and better at collaborating with an AI model to do work, you are functioning as an "AI Conductor".
As a result, I have changed how I work in all cases.  In practice I am an enterprise scale software architect with mission critical applications running in several sectors.  This is what I'm doing for any given assignment:
1.  Understand the need enough to work with my Personal AI to develop/build/create, no data allowed to come over, all data is synthetic.  This process is lengthy, down many dead ends, back out, shuffles, resets, until, I get a good path using my AI Model (any AI model) that will get me from A->B where A is inception and B is pruduct ready.  I archive the entire history, dead ends and all.  This is the AI Conductor's work.
2.  I ask  my Personal AI to give me the shortest path to get From A->B and export.
3.  I import or I enter manually into my customer's environment.  
Any creative work when done by AI/Human "Conductor" will always face the question about insight or what is 'new'.  The answer can be discussed in more detail by examaining the detailed message history and work products over the creative process, including all the dead ends. Ten years from now, hiring managers may ask to see at least one "Human/AI Composition" from an applicant.  A copy of course.
For me this means that 100% of my individual work will be done with me and my personal AIs, never an AI from work.  At some point companies will force your hands to use their AIs, but it works in reverse.  Use the company AI's but keep your personal AI up to date with concepts you have strung together or created.  Never actual data. 
I am now working on ways to automaticly save history 
Using AI through text and email only and a private data store behind the AI model.  However I get it done I will archive my AI History.

-------------------------------------------------------------------
## What is system

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
