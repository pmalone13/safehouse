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
          ip            TEXT,
          user_agent    TEXT,
          status        TEXT NOT NULL DEFAULT 'opted_in'
        )
        """
    )
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
  button {{ margin-top: 1.5rem; padding: 0.5rem 1.2rem; }}
</style>
</head>
<body>
<nav><a href="/">About</a><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Use</a><a href="/sms-optin">Text Updates</a></nav>
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


def _render_optin_form(name: str = "", phone: str = "", error: str = "") -> str:
    error_html = f'<p class="error">{error}</p>' if error else ""
    body = f"""
<h1>Get Text Updates</h1>
<p>Sign up to receive SMS reminders and updates from Paul Malone.</p>
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

    if not consented:
        return _render_optin_form(name=name, phone=phone_raw,
                                   error="You must check the consent box to sign up.")

    _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO optins (name, phone_e164, consent_text, consented_at, ip, user_agent) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            name,
            phone_e164,
            CONSENT_TEXT,
            datetime.now(timezone.utc).isoformat(),
            request.remote_addr,
            request.headers.get("User-Agent", ""),
        ),
    )
    conn.commit()
    conn.close()

    body = """
<h1>You're signed up</h1>
<p>Thanks -- you'll start receiving text updates at the number you provided.
Reply STOP at any time to opt out.</p>
"""
    return PAGE_SHELL.format(title="Signed Up", body=body)


_init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8091)
