"""Minimal Twilio REST client -- send only, for now. No SDK dependency;
Twilio's Messages API is one Basic-Auth POST, not worth a whole package
on a box this memory-constrained.

Credentials are read fresh from disk on every call (same convention as
bayhouse's own .power_strip_credentials / .claude_system_token handling
-- never on a command line, never cached at import time):
  - ~/.keys/twilioKeys        line 1: API Key SID (starts "SK...")
                              line 2: API Key Secret
  - ~/.keys/twilioConfig      KEY=VALUE lines: TWILIO_ACCOUNT_SID,
                              TWILIO_PHONE_NUMBER (the sending number)

Neither file lives in this git repo -- both are under $HOME/.keys/,
outside the checkout, same as every other credential in this project.
"""
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

KEYS_PATH = Path.home() / ".keys" / "twilioKeys"
CONFIG_PATH = Path.home() / ".keys" / "twilioConfig"

API_BASE = "https://api.twilio.com/2010-04-01"


class TwilioError(Exception):
    pass


def _load_keys() -> tuple[str, str]:
    lines = KEYS_PATH.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise TwilioError(f"{KEYS_PATH} must have API Key SID on line 1, secret on line 2")
    return lines[0].strip(), lines[1].strip()


def _load_config() -> dict:
    config = {}
    for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()
    for required in ("TWILIO_ACCOUNT_SID", "TWILIO_PHONE_NUMBER"):
        if required not in config:
            raise TwilioError(f"{CONFIG_PATH} is missing {required}")
    return config


def send_sms(to: str, body: str) -> dict:
    """Sends one SMS via the Twilio Messages API. Returns the parsed JSON
    response (includes 'sid', 'status', etc.) on success; raises
    TwilioError on any non-2xx response or transport failure."""
    api_key_sid, api_key_secret = _load_keys()
    config = _load_config()

    account_sid = config["TWILIO_ACCOUNT_SID"]
    from_number = config["TWILIO_PHONE_NUMBER"]

    url = f"{API_BASE}/Accounts/{account_sid}/Messages.json"
    data = urllib.parse.urlencode({"To": to, "From": from_number, "Body": body}).encode("utf-8")

    auth = base64.b64encode(f"{api_key_sid}:{api_key_secret}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise TwilioError(f"Twilio send failed: HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise TwilioError(f"Twilio send failed: {e}") from e
