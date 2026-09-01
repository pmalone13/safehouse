"""Thin wrapper around Google APIs (OAuth) for the tedassistent@gmail.com
account. Two independent credential pairs, deliberately NOT merged into
one combined-scope token: Gmail was already consented to once (asking
Paul to redo that just to add Drive would mean making him repeat a
manual multi-step process he explicitly didn't want to do twice). Drive
gets its own separate token instead -- one new consent, not a redo of
the old one. Both reuse the SAME underlying Google Cloud OAuth client
(no new Cloud Console client needed for Drive, just the Drive API
enabled on that project and a fresh consent run).

GMAIL, live since 2026-09-01. Scopes: gmail.readonly + gmail.send
(deliberately not gmail.modify -- sending is all this needs).

DRIVE, not live yet -- see authorize_drive_once.py's docstring for the
one-time setup. Scope: full `drive` (not the narrower `drive.file`) --
deliberate choice, since Claude needs to read/edit files Paul already
created on Drive, not just files it creates itself. Revisit if that
proves too broad in practice.

One-time setup for EITHER, MUST be done from a machine with a browser
(this VM is headless):
  1. Create/select a Google Cloud project, enable the relevant API
     (Gmail API / Drive API), create a "Desktop app" OAuth client,
     download its JSON.
  2. Place it at the matching *_CLIENT_SECRET_PATH below (gitignored).
  3. Run the matching authorize_*_once.py script LOCALLY (not on the
     VM) -- opens a browser, sign in as tedassistent@gmail.com, grants
     consent -- and writes the matching *_TOKEN_PATH file (gitignored).
  4. Copy that one token file to the same path on the VM. After that,
     this module refreshes it automatically.
"""
import base64
import io
import os
import time
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

REPO_ROOT = Path(__file__).parent

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
GMAIL_CLIENT_SECRET_PATH = REPO_ROOT / ".gmail_api_client_secret.json"
GMAIL_TOKEN_PATH = REPO_ROOT / ".gmail_api_token.json"
GMAIL_TOKEN_LOCK_PATH = REPO_ROOT / ".gmail_api_token.lock"

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_CLIENT_SECRET_PATH = REPO_ROOT / ".drive_api_client_secret.json"
DRIVE_TOKEN_PATH = REPO_ROOT / ".drive_api_token.json"
DRIVE_TOKEN_LOCK_PATH = REPO_ROOT / ".drive_api_token.lock"

_LOCK_STALE_SECONDS = 15.0
_LOCK_WAIT_TIMEOUT_SECONDS = 10.0


def _acquire_lock(lock_path: Path) -> None:
    deadline = time.monotonic() + _LOCK_WAIT_TIMEOUT_SECONDS
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            os.close(fd)
            return
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > _LOCK_STALE_SECONDS:
                log.warning(f"{lock_path.name} is {age:.1f}s old -- assuming abandoned, taking it over")
                lock_path.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                log.info(f"{lock_path.name} held by another process past {_LOCK_WAIT_TIMEOUT_SECONDS:.0f}s wait -- proceeding without it")
                return
            time.sleep(0.2)


def _release_lock(lock_path: Path) -> None:
    lock_path.unlink(missing_ok=True)


def _get_client(token_path: Path, lock_path: Path, scopes: list, api: str, version: str):
    if not token_path.exists():
        raise FileNotFoundError(
            f"{token_path} not found -- complete the one-time OAuth consent "
            f"flow locally (see google_client.py's docstring) and copy the "
            f"resulting token file here first."
        )
    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if creds.expired and creds.refresh_token:
        _acquire_lock(lock_path)
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json())
        finally:
            _release_lock(lock_path)
    return build(api, version, credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------- Gmail --

def get_client():
    """Returns an authorized Gmail API service object."""
    return _get_client(GMAIL_TOKEN_PATH, GMAIL_TOKEN_LOCK_PATH, GMAIL_SCOPES, "gmail", "v1")


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
    HTML if no text/plain part exists)."""
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


# ---------------------------------------------------------------- Drive --

def get_drive_client():
    """Returns an authorized Drive API service object. Not live until
    the separate Drive OAuth consent has been done -- see
    authorize_drive_once.py."""
    return _get_client(DRIVE_TOKEN_PATH, DRIVE_TOKEN_LOCK_PATH, DRIVE_SCOPES, "drive", "v3")


def find_or_create_folder(service, name: str, parent_id: str = None) -> str:
    """Returns the folder's id, creating it (under parent_id, or Drive
    root if None) if it doesn't already exist. Matching is by name only
    within the given parent -- Drive allows duplicate names, this
    returns the first match rather than guarding against that (fine at
    the scale this is used at)."""
    parent_clause = f"and '{parent_id}' in parents" if parent_id else "and 'root' in parents"
    query = (
        f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false {parent_clause}"
    )
    resp = service.files().list(q=query, fields="files(id, name)").execute()
    existing = resp.get("files", [])
    if existing:
        return existing[0]["id"]

    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    log.info(f"created Drive folder {name!r} (id={folder['id']})")
    return folder["id"]


def list_files(service, parent_id: str = None, query: str = None, max_results: int = 50) -> list:
    """Returns [{"id", "name", "mimeType"}], optionally scoped to one
    folder and/or an additional Drive query-language filter."""
    clauses = ["trashed = false"]
    if parent_id:
        clauses.append(f"'{parent_id}' in parents")
    if query:
        clauses.append(query)
    resp = service.files().list(
        q=" and ".join(clauses), fields="files(id, name, mimeType)", pageSize=max_results
    ).execute()
    return resp.get("files", [])


def get_file_content(service, file_id: str) -> str:
    """Downloads a file's content as text. Google Docs get exported as
    plain text; anything else is downloaded raw and decoded as UTF-8
    (best-effort -- not meant for binary files)."""
    meta = service.files().get(fileId=file_id, fields="mimeType").execute()
    mime_type = meta["mimeType"]
    buf = io.BytesIO()
    if mime_type == "application/vnd.google-apps.document":
        request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    else:
        request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue().decode("utf-8", errors="replace")


def create_file(service, name: str, content: str, parent_id: str = None,
                 mime_type: str = "text/plain") -> str:
    """Creates a new file with the given text content. Returns the new
    file's id."""
    metadata = {"name": name}
    if parent_id:
        metadata["parents"] = [parent_id]
    media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")), mimetype=mime_type)
    created = service.files().create(body=metadata, media_body=media, fields="id").execute()
    log.info(f"created Drive file {name!r} (id={created['id']})")
    return created["id"]


def update_file_content(service, file_id: str, content: str, mime_type: str = "text/plain") -> None:
    """Overwrites an existing file's content in place."""
    media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")), mimetype=mime_type)
    service.files().update(fileId=file_id, media_body=media).execute()
    log.info(f"updated Drive file id={file_id}")
