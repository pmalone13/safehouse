"""Standalone site for idealfed.com -- About / Privacy Policy / Terms of
Use / SMS opt-in. Separate from the safehouse assistant itself (different
domain, different purpose); lives in this repo purely because it runs on
the same VM. Privacy/Terms content is deliberately written to cover what
Twilio/carrier A2P 10DLC review looks for (explicit no-data-sharing
statement, opt-out/opt-in mechanics, consent language) -- edit the
placeholder business details, keep those specific clauses.

Run via systemd (idealfed-site.service), proxied by nginx on 80/443 --
this process itself only listens on localhost.
"""
import html
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, request

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "optins.db"

CONSENT_TEXT = (
    'I agree to receive SMS text messages from Paul Malone about '
    'appointments, reminders, and business updates at the number provided. '
    'Consent is not a condition of purchase. Msg &amp; data rates may apply. '
    'Msg frequency varies. Reply STOP to opt out, HELP for help. See our '
    '<a href="/privacy">Privacy Policy</a> and <a href="/terms">Terms of Use</a>.'
)


def _init_db() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS optins (
          id            INTEGER PRIMARY KEY AUTOINCREMENT,
          name          TEXT NOT NULL,
          phone_e164    TEXT NOT NULL,
          consent_text  TEXT NOT NULL,
          consented_at  TEXT NOT NULL,
          submitted_at  TEXT,
          ip            TEXT,
          user_agent    TEXT,
          status        TEXT NOT NULL DEFAULT 'opted_in'
        )
        """
    )
    # The table predates submitted_at; CREATE TABLE IF NOT EXISTS won't add it.
    columns = {row[1] for row in conn.execute("PRAGMA table_info(optins)")}
    if "submitted_at" not in columns:
        conn.execute("ALTER TABLE optins ADD COLUMN submitted_at TEXT")
    conn.commit()
    conn.close()


def _normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


PAGE_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Paul Malone</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
         max-width: 700px; margin: 3rem auto; padding: 0 1.5rem;
         line-height: 1.6; color: #222; }}
  nav a {{ margin-right: 1.2rem; color: #0645ad; text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
  h1 {{ font-size: 1.6rem; }}
  footer {{ margin-top: 3rem; color: #777; font-size: 0.85rem; }}
  label {{ display: block; margin-top: 1rem; }}
  input[type=text], input[type=tel] {{ width: 100%; max-width: 320px; padding: 0.4rem; }}
  .consent-row {{ display: flex; align-items: flex-start; gap: 0.5rem; margin-top: 1.2rem; }}
  .consent-row input {{ margin-top: 0.3rem; }}
  .error {{ color: #b00020; }}
  .optional-tag {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;
                   color: #555; border: 1px solid #bbb; border-radius: 3px;
                   padding: 0 0.35rem; margin-top: 0.25rem; white-space: nowrap; }}
  button {{ margin-top: 1.5rem; padding: 0.5rem 1.2rem; }}
</style>
</head>
<body>
<nav><a href="/">About</a><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Use</a><a href="/sms-optin">Text Updates</a><a href="/safehouse">Safehouse</a></nav>
{body}
<footer>&copy; 2026 Paul Malone. Contact: pmalone@idealfed.com</footer>
</body>
</html>"""


@app.route("/")
def about():
    body = """
<h1>Paul Malone</h1>
<p>Independent IT consultant providing technology services to clients --
systems, automation, and applications built around each client's actual
needs rather than off-the-shelf platforms.</p>
<p>Based in Tracys Landing, MD. For inquiries, contact
<a href="mailto:pmalone@idealfed.com">pmalone@idealfed.com</a>.</p>
"""
    return PAGE_SHELL.format(title="About", body=body)


@app.route("/privacy")
def privacy():
    body = """
<h1>Privacy Policy</h1>
<p><em>Last updated: September 2026</em></p>
<p>This Privacy Policy is issued by <strong>Paul Malone</strong> ("Paul Malone," "we," "us," or "our") and applies to idealfed.com and any SMS text messaging service operated by Paul Malone.</p>

<h2>Information Collected</h2>
<p>When you interact with our SMS service, we collect your phone number
and the content of messages exchanged, solely to provide the service you
signed up for (appointment reminders, confirmations, and related
business communications).</p>

<h2>How Information Is Used</h2>
<p>Your information is used only to send you the messages you have
consented to receive and to respond to your replies. We do not use your
phone number or message content for any other purpose.</p>

<h2>Data Sharing</h2>
<p><strong>No mobile information will be shared with third parties or
affiliates for marketing or promotional purposes.</strong> Information
sharing to subcontractors in support services, such as customer service,
is permitted where necessary to operate this service. All other use of
personal information, categories of mobile subscriber data or personally
identifiable information is prohibited.</p>

<h2>Opting Out</h2>
<p>You may opt out of SMS messages at any time by replying STOP to any
message. Reply HELP for assistance.</p>

<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:pmalone@idealfed.com">pmalone@idealfed.com</a>.</p>
"""
    return PAGE_SHELL.format(title="Privacy Policy", body=body)


@app.route("/terms")
def terms():
    body = """
<h1>Terms of Use</h1>
<p><em>Last updated: September 2026</em></p>
<p>These Terms of Use govern your use of services provided by <strong>Paul Malone</strong> ("Paul Malone," "we," "us," or "our"), including idealfed.com and any SMS messaging services.</p>

<h2>SMS Messaging Program</h2>
<p>By providing your phone number and opting in, you consent to receive
SMS text messages from Paul Malone related to appointments, reminders,
and business communications. Message frequency varies. Message and data
rates may apply.</p>

<p>Consent to receive SMS messages is not a condition of any purchase or
service.</p>

<h2>Opt-In / Opt-Out</h2>
<p>Reply START to opt in (or resubscribe), STOP to opt out at any time,
and HELP for assistance. Carriers are not liable for delayed or
undelivered messages.</p>

<h2>Supported Carriers</h2>
<p>This program is supported on major US carriers. Carriers are not
liable for delayed or undelivered messages.</p>

<h2>Site Use</h2>
<p>Content on this site is provided for general informational purposes.
Use of this site does not create a client relationship; contact
<a href="mailto:pmalone@idealfed.com">pmalone@idealfed.com</a> to
discuss actual services.</p>
"""
    return PAGE_SHELL.format(title="Terms of Use", body=body)


@app.route("/safehouse")
def safehouse_page():
    diagram_svg = """
<svg viewBox="0 0 700 380" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#444"/>
    </marker>
  </defs>
  <style>
    .box { fill: #f5f7fb; stroke: #0645ad; stroke-width: 1.2; }
    .lbl { font-size: 13px; fill: #222; }
    .sub { font-size: 10.5px; fill: #666; }
    .arr { stroke: #444; stroke-width: 1.4; fill: none; marker-end: url(#arrow); }
  </style>

  <rect class="box" x="20" y="20" width="150" height="55" rx="6"/>
  <text class="lbl" x="95" y="42" text-anchor="middle">Email / Text</text>
  <text class="sub" x="95" y="58" text-anchor="middle">Gmail poll / Twilio</text>

  <rect class="box" x="220" y="20" width="150" height="55" rx="6"/>
  <text class="lbl" x="295" y="42" text-anchor="middle">FIFO Queue</text>
  <text class="sub" x="295" y="58" text-anchor="middle">SQLite (queue_db.py)</text>

  <rect class="box" x="420" y="20" width="150" height="55" rx="6"/>
  <text class="lbl" x="495" y="42" text-anchor="middle">Coordinator</text>
  <text class="sub" x="495" y="58" text-anchor="middle">claims one at a time</text>

  <path class="arr" d="M170,47 L215,47"/>
  <path class="arr" d="M370,47 L415,47"/>
  <path class="arr" d="M495,75 L495,120"/>

  <rect class="box" x="270" y="120" width="450" height="0" style="display:none"/>
  <rect class="box" x="320" y="120" width="350" height="60" rx="6"/>
  <text class="lbl" x="495" y="145" text-anchor="middle">Claude session</text>
  <text class="sub" x="495" y="162" text-anchor="middle">spawned or --resume'd; reads CLAUDE.md fresh, every turn</text>

  <path class="arr" d="M495,180 L495,220"/>

  <rect class="box" x="270" y="220" width="150" height="55" rx="6"/>
  <text class="lbl" x="345" y="242" text-anchor="middle">Reply</text>
  <text class="sub" x="345" y="258" text-anchor="middle">email / SMS</text>

  <rect class="box" x="470" y="220" width="200" height="55" rx="6"/>
  <text class="lbl" x="570" y="242" text-anchor="middle">Checkpoint</text>
  <text class="sub" x="570" y="258" text-anchor="middle">git commit + push, Drive sync</text>

  <path class="arr" d="M495,180 C420,200 400,210 355,220"/>
  <path class="arr" d="M495,180 C540,200 555,210 565,220"/>

  <rect class="box" x="20" y="310" width="550" height="55" rx="6"/>
  <text class="lbl" x="295" y="332" text-anchor="middle">No standing process between messages</text>
  <text class="sub" x="295" y="349" text-anchor="middle">Session-continuity via a resume ticket, not a resident daemon -- nothing runs while idle</text>
</svg>
"""

    philosophy_summary = """
<p><em>Summary, pulled from this project's own README:</em> keep a
detailed, human-owned record of the actual path from idea to finished
work when collaborating with AI &mdash; not just the polished result,
but the dead ends, backtracks, and resets along the way. Most AI usage
today lives inside a company-owned account, where the interaction
history belongs to the organization, not the person who did the work.
Paul's practice: work through the messy, exploratory part of a project
with a personal AI on synthetic data only, then bring the shortest
clean path into the actual client or work environment &mdash; keeping
the full, granular history as his own. Safehouse is the practical,
running implementation of that idea: an AI collaborator whose entire
interaction history is captured, owned, and inspectable by the person
who directed it.</p>
"""

    philosophy_detail = """
<p>I'm posting because I've spent a lot of time working with AI over the past years and honestly I wanted a place to write this down so I can refer folks when asked what I think.
In a nutshell, I believe that from now on, each one of us should build our "AI History" in detail under some secure storage that you own, or at least each of us should plan on collecting and archiving our AI interaction histories somewhere.</p>

<p>AI History is the set of data owned by 3rd party companies, one for each "account" which captures the interaction between a human and an AI model. When working with AI, periodically the model will 'summarize' your session to reduce its memory footprint and provide for a more optimized AI runtime environment. The AI memory is optimized for your specific work. This is how many of us are using AI now.</p>

<p>As I use AI, when I'm working on a project, I will go down many dead ends that didn't work for my goals. When the AI summarizes, you lose the granularity of "how" did you get from inception to product creation. In my humble opinion, keeping that detailed log is critical to understanding the dynamic between the AI model and the human. Today the detailed logs do exist but they are not owned by the human if you are using one of the common models.</p>

<p>As I write, Organizations are using AI in the workplace. Individual contributors are given AI resources such as CoPilot or Claude or Grok or ChatGPT or some home grown AI models. In all cases, the Organization "owns" the accounts/logs and the work product, however, you the Human own the "Human AI Creation Experience" having been the Human side of the effort. In practice, Organizations give AI Agents to Employees to do creative work. All of which is owned by the Organization. However, you, the human are creating with the AI and you are becoming better and better at collaborating with an AI model to do work, you are functioning as an "AI Conductor".</p>

<p>As a result, I have changed how I work in all cases. In practice I am an enterprise scale software architect with mission critical applications running in several sectors. This is what I'm doing for any given assignment:</p>

<ol>
<li>Understand the need enough to work with my Personal AI to develop/build/create, no data allowed to come over, all data is synthetic. This process is lengthy, down many dead ends, back out, shuffles, resets, until, I get a good path using my AI Model (any AI model) that will get me from A&rarr;B where A is inception and B is product ready. I archive the entire history, dead ends and all. This is the AI Conductor's work.</li>
<li>I ask my Personal AI to give me the shortest path to get from A&rarr;B and export.</li>
<li>I import or I enter manually into my customer's environment.</li>
</ol>

<p>Any creative work when done by AI/Human "Conductor" will always face the question about insight or what is 'new'. The answer can be discussed in more detail by examining the detailed message history and work products over the creative process, including all the dead ends. Ten years from now, hiring managers may ask to see at least one "Human/AI Composition" from an applicant. A copy of course.</p>

<p>For me this means that 100% of my individual work will be done with me and my personal AIs, never an AI from work. At some point companies will force your hands to use their AIs, but it works in reverse. Use the company AI's but keep your personal AI up to date with concepts you have strung together or created. Never actual data.</p>
"""

    body = f"""
<h1>Safehouse</h1>
{philosophy_summary}

<p>
<a href="https://github.com/pmalone13/safehouse">Safehouse on GitHub</a>
&nbsp;&middot;&nbsp;
<a href="https://github.com/NateBJones-Projects/OB1/tree/main">Related: OB1</a>
</p>

<h2>How it works</h2>
{diagram_svg}

<h2>Philosophy, in full</h2>
{philosophy_detail}
"""
    return PAGE_SHELL.format(title="Safehouse", body=body)


def _render_optin_form(name: str = "", phone: str = "", error: str = "") -> str:
    error_html = f'<p class="error">{html.escape(error)}</p>' if error else ""
    name = html.escape(name, quote=True)
    phone = html.escape(phone, quote=True)
    body = f"""
<h1>Sign Up for Updates</h1>
<p>Enter your name and mobile number to be added to Paul Malone's contact
list.</p>
<p>Receiving SMS text messages is <strong>entirely optional and is not
required</strong> to sign up, to contact, or to hire Paul Malone. Leave the
box below unchecked and your signup will still go through -- you simply
will not receive any text messages.</p>
{error_html}
<form method="post" action="/sms-optin">
  <label>Name
    <input type="text" name="name" value="{name}" required>
  </label>
  <label>Mobile number
    <input type="tel" name="phone" value="{phone}" placeholder="(555) 555-5555" required>
  </label>
  <div class="consent-row">
    <input type="checkbox" name="consent" id="consent" value="yes">
    <span class="optional-tag">Optional</span>
    <label for="consent" style="margin-top:0;">{CONSENT_TEXT}</label>
  </div>
  <button type="submit">Sign up</button>
</form>
"""
    return PAGE_SHELL.format(title="Text Updates", body=body)


@app.route("/sms-optin", methods=["GET"])
def sms_optin_form():
    return _render_optin_form()


@app.route("/sms-optin", methods=["POST"])
def sms_optin_submit():
    name = (request.form.get("name") or "").strip()
    phone_raw = (request.form.get("phone") or "").strip()
    consented = request.form.get("consent") == "yes"

    if not name:
        return _render_optin_form(phone=phone_raw, error="Please enter your name.")

    phone_e164 = _normalize_phone(phone_raw)
    if not phone_e164:
        return _render_optin_form(name=name, phone=phone_raw,
                                   error="Please enter a valid 10-digit US mobile number.")

    _init_db()
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO optins (name, phone_e164, consent_text, consented_at, "
        "submitted_at, ip, user_agent, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            name,
            phone_e164,
            CONSENT_TEXT if consented else "NO SMS CONSENT GIVEN",
            now if consented else "",
            now,
            request.remote_addr,
            request.headers.get("User-Agent", ""),
            "opted_in" if consented else "contact_only",
        ),
    )
    conn.commit()
    conn.close()

    if consented:
        body = """
<h1>You're signed up</h1>
<p>Thanks -- you'll start receiving text updates at the number you provided.
Reply STOP at any time to opt out.</p>
"""
    else:
        body = """
<h1>You're signed up</h1>
<p>Thanks -- your contact details have been recorded.</p>
<p><strong>You will not receive text messages.</strong> You left the SMS
consent box unchecked, so no SMS consent was recorded and no text messages
will be sent to your number. If you change your mind, sign up again at any
time with the box checked.</p>
"""
    return PAGE_SHELL.format(title="Signed Up", body=body)


_init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8091)
