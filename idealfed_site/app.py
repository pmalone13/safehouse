"""Standalone site for idealfed.com -- About / Privacy Policy / Terms of
Use. Separate from the safehouse assistant itself (different domain,
different purpose); lives in this repo purely because it runs on the
same VM. Privacy/Terms content is deliberately written to cover what
Twilio/carrier A2P 10DLC review looks for (explicit no-data-sharing
statement, opt-out/opt-in mechanics, consent language) -- edit the
placeholder business details, keep those specific clauses.

Run via systemd (idealfed-site.service), proxied by nginx on 80/443 --
this process itself only listens on localhost.
"""
from flask import Flask

app = Flask(__name__)

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
</style>
</head>
<body>
<nav><a href="/">About</a><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Use</a></nav>
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
<p>This policy covers information collected through
idealfed.com and any SMS text messaging service operated by Paul Malone.</p>

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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8091)
