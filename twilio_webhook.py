"""Inbound Twilio SMS webhook -- receives a text sent to the safehouse
number and enqueues it into queue_db, exactly the same shape
email_monitor.py already uses (channel, source, body). No SDK
dependency, same "plain Python over managed platforms" convention as
twilio_client.py.

Security model, both load-bearing:
  1. Signature validation (Twilio's own HMAC-SHA1-over-URL+sorted-params
     scheme) against the classic Account Auth Token in
     ~/.keys/twilioAuthToken (NOT the API Key/Secret twilio_client.py
     uses for outbound sends -- a different credential). Fails CLOSED:
     no token file on disk, or a signature mismatch, both reject the
     request outright (403) rather than trusting it. Validated against
     a hardcoded WEBHOOK_URL rather than anything derived from request
     headers, since that's the one fixed value we ourselves registered
     with Twilio as the SMS webhook -- no proxy-header trust needed.
  2. Sender allowlist: only a message from Paul's own registered number
     is ever enqueued for a real Claude turn. Anything else (a stray
     reply from the public opt-in list this same number also serves,
     a wrong number, an abuse attempt) is logged and acknowledged with
     an empty TwiML response, never queued -- this number's A2P
     registration is for opt-in business notifications, not open
     two-way assistant access.

Run standalone via gunicorn (systemd unit: safehouse-twilio-webhook.service):
    gunicorn --workers 1 --bind 127.0.0.1:8092 twilio_webhook:app
"""
import hashlib
import hmac
import base64
from pathlib import Path

from flask import Flask, request, Response

import queue_db
from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

app = Flask(__name__)

AUTH_TOKEN_PATH = Path.home() / ".keys" / "twilioAuthToken"
WEBHOOK_URL = "https://idealfed.com/twilio/inbound-sms"

# Paul's own number, the only sender this webhook will ever hand to the
# coordinator. Stored digits-only; compared after stripping everything
# but digits from the inbound "From" field so formatting differences
# (+1..., (xxx) xxx-xxxx, etc.) never cause a false negative.
ALLOWED_SENDER_DIGITS = "12026181308"

EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'


def _digits(s: str) -> str:
    return "".join(c for c in s if c.isdigit())


def _load_auth_token() -> str:
    return AUTH_TOKEN_PATH.read_text(encoding="utf-8").strip()


def _valid_signature(auth_token: str, url: str, params: dict, header_sig: str) -> bool:
    s = url + "".join(f"{k}{params[k]}" for k in sorted(params.keys()))
    digest = hmac.new(auth_token.encode("utf-8"), s.encode("utf-8"), hashlib.sha1).digest()
    computed = base64.b64encode(digest).decode("ascii")
    return hmac.compare_digest(computed, header_sig or "")


@app.route("/twilio/inbound-sms", methods=["POST"])
def inbound_sms():
    header_sig = request.headers.get("X-Twilio-Signature", "")
    params = request.form.to_dict()

    try:
        auth_token = _load_auth_token()
    except FileNotFoundError:
        log.warning("inbound SMS rejected: no twilioAuthToken on disk yet, failing closed")
        return Response(status=403)

    if not _valid_signature(auth_token, WEBHOOK_URL, params, header_sig):
        log.warning(f"inbound SMS rejected: signature mismatch from={params.get('From')!r}")
        return Response(status=403)

    from_number = params.get("From", "")
    body = params.get("Body", "")
    message_sid = params.get("MessageSid", "")

    if _digits(from_number) != ALLOWED_SENDER_DIGITS:
        log.info(f"inbound SMS from unrecognized number {from_number!r} (sid={message_sid}) -- "
                  f"acknowledged, not enqueued")
        return Response(EMPTY_TWIML, mimetype="text/xml")

    queue_db.enqueue("text", from_number, body)
    log.info(f"enqueued text from={from_number!r} sid={message_sid} len={len(body)}")
    return Response(EMPTY_TWIML, mimetype="text/xml")
