"""Thin wrapper around the real Gmail API (OAuth) for the tedassistent@gmail.com
account -- ported from bayhouse's gmail_api/client.py essentially unchanged,
since that pattern is already proven. Scopes: gmail.readonly (reading) +
gmail.send (sending replies) -- deliberately not gmail.modify.

One-time setup, MUST be done from a machine with a browser (this VM is
headless, so this step does not run here):
  1. Create/select a Google Cloud project, enable the Gmail API, create a
     "Desktop app" OAuth client, download its JSON.
  2. Place it as .gmail_api_client_secret.json next to this file's repo
     root (gitignored).
  3. Run `python authorize_once.py` LOCALLY (not on the VM) -- opens a
     browser, sign in as tedassistent@gmail.com, grants consent -- and
     writes .gmail_api_token.json (gitignored).
  4. Copy .gmail_api_token.json (only) to the same path on the VM. After
     that, this module refreshes it automatically; authorize_once.py
     never needs to run again unless the token is revoked or SCOPES
     changes.
"""
import base64
import os
import time
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

REPO_ROOT = Path(__file__).parent
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
CLIENT_SECRET_PATH = REPO_ROOT / ".gmail_api_client_secret.json"
TOKEN_PATH = REPO_ROOT / ".gmail_api_token.json"

# Cross-process refresh lock -- same real bug class bayhouse hit: more
# than one process (this poller, and later any MCP tool a spawned Claude
# session uses for live Gmail access) can land on "token expired" at the
# same moment and both call refresh() concurrently, corrupting the token
# file for everyone until a fresh interactive re-auth. Cheap insurance,
# no-op when uncontended.
TOKEN_LOCK_PATH = REPO_ROOT / ".gmail_api_token.lock"
_LOCK_STALE_SECONDS = 15.0
_LOCK_WAIT_TIMEOUT_SECONDS = 10.0


def _acquire_token_lock() -> None:
    deadline = time.monotonic() + _LOCK_WAIT_TIMEOUT_SECONDS
    while True:
        try:
            fd = os.open(str(TOKEN_LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            os.close(fd)
            return
        except FileExistsError:
            try:
                age = time.time() - TOKEN_LOCK_PATH.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > _LOCK_STALE_SECONDS:
                log.warning(f"gmail token lock is {age:.1f}s old -- assuming abandoned, taking it over")
                TOKEN_LOCK_PATH.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                log.info(f"gmail token lock held by another process past {_LOCK_WAIT_TIMEOUT_SECONDS:.0f}s wait -- proceeding without it")
                return
            time.sleep(0.2)


def _release_token_lock() -> None:
    TOKEN_LOCK_PATH.unlink(missing_ok=True)


def get_client():
    """Returns an authorized Gmail API service object. Raises a plain
    FileNotFoundError with a clear message if the one-time setup hasn't
    been completed yet."""
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(
            f"{TOKEN_PATH} not found -- complete the one-time OAuth consent "
            "flow locally (see this module's docstring) and copy the "
            "resulting token file here before starting email_monitor.py."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        _acquire_token_lock()
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                TOKEN_PATH.write_text(creds.to_json())
        finally:
            _release_token_lock()
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def list_new_messages(service, query: str = "in:inbox", max_results: int = 25) -> list:
    """Newest-first list of {"id", "threadId"}. No state-tracking of its
    own -- caller owns dedup (see email_monitor.py's seen_ids set)."""
    resp = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return resp.get("messages", [])


def _decode_body_data(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("utf-8") + b"===").decode("utf-8", errors="replace")


def _walk_parts_for_body(part: dict, body_chunks: list) -> None:
    mime_type = part.get("mimeType", "")
    body = part.get("body", {})
    if mime_type == "text/plain" and body.get("data"):
        body_chunks.append(_decode_body_data(body["data"]))
    elif mime_type == "text/html" and body.get("data") and not body_chunks:
        body_chunks.append(_decode_body_data(body["data"]))
    for sub_part in part.get("parts", []) or []:
        _walk_parts_for_body(sub_part, body_chunks)


def get_message_detail(service, message_id: str) -> dict:
    """Headers (from/subject/date) + plain-text body (falls back to raw
    HTML if no text/plain part exists). No attachment handling yet --
    not needed for the hello-world pipeline test; add if/when a real use
    case needs it."""
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
    body_chunks: list = []
    _walk_parts_for_body(msg.get("payload", {}), body_chunks)
    return {
        "message_id": message_id,
        "thread_id": msg.get("threadId"),
        "sender": headers.get("from", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
        "body_text": "\n".join(body_chunks),
    }


def send_message(service, to: str, subject: str, body_text: str) -> str:
    """Sends as whichever account the OAuth token belongs to (tedassistent@gmail.com)."""
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body_text)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info(f"sent message id={sent.get('id')} to={to!r} subject={subject!r}")
    return sent.get("id")
