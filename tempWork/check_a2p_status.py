"""Temporary, disposable: polls Twilio's A2P campaign compliance status
and logs any change. NOT part of the main safehouse app -- exists only
until the campaign clears review, then gets torn down. See this repo's
root CLAUDE.md, "tempWork" section, for what "torn down" means here.

Run via a cron entry (/etc/cron.d/safehouse-a2p-check), not a systemd
service -- deliberately the simplest possible thing for something meant
to be short-lived and easy to remove. Does NOT need Claude/coordinator
involvement at all -- this is routine system polling, not a judgment
call, so it stays a plain script on a timer.

    ./venv/bin/python tempWork/check_a2p_status.py
"""
import base64
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import twilio_client as tc  # noqa: E402

HERE = Path(__file__).parent
STATE_PATH = HERE / "a2p_status_state.json"
LOG_PATH = HERE / "a2p_status_changes.log"

MESSAGING_SERVICE_SID = "MGfd44b828f67d2d61ef30485c0170ec81"


def _get(url: str, auth: str) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {auth}")
    return json.loads(urllib.request.urlopen(req, timeout=15).read())


def check_once() -> str:
    api_key_sid, api_key_secret = tc._load_keys()
    auth = base64.b64encode(f"{api_key_sid}:{api_key_secret}".encode()).decode()
    resp = _get(
        f"https://messaging.twilio.com/v1/Services/{MESSAGING_SERVICE_SID}/Compliance/Usa2p", auth
    )
    compliance = resp.get("compliance") or [{}]
    current_status = compliance[0].get("campaign_status")

    last_status = None
    if STATE_PATH.exists():
        last_status = json.loads(STATE_PATH.read_text(encoding="utf-8")).get("campaign_status")

    now = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(
        json.dumps({"campaign_status": current_status, "checked_at": now}, indent=2),
        encoding="utf-8",
    )

    if current_status != last_status:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{now}  {last_status!r} -> {current_status!r}\n")
        print(f"STATUS CHANGED: {last_status!r} -> {current_status!r}")
    else:
        print(f"no change ({current_status!r})")

    return current_status


if __name__ == "__main__":
    check_once()
