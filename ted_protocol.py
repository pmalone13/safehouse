"""Ted Protocol v3 -- Ted's send/receive side of the encrypted-attachment
command channel to Bayhouse ("Bill"). v1 spec issued 2026-10-11, v2
issued 2026-10-13, v3 issued 2026-10-14 by Bayhouse (all logged in
projects/engineering/secure-agent-communication/CLAUDE.md). Crypto
construction confirmed against the matching reference script
(send_side_reference.py, from ted_protocol_package_v1.zip) live with
Paul 2026-10-12; every later package (v2, v3) confirms the crypto/key/
transport are byte-for-byte unchanged from v1 -- the key
(ted_key.txt) is unchanged since v1 too.

v2 added exactly one new capability, purely on Bayhouse's receiving
side: a message that doesn't start with one of the five fixed command
words is no longer an error -- Bayhouse reads it as a genuine
free-form question or piece of project work and replies directly.
Nothing on Ted's sending side had to change for that: encrypt_command()/
send_command() already accept any text, fixed command or not. The one
real consequence was timing -- a free-form reply can take "up to a
couple of minutes" per Bayhouse's spec, well past v1's fixed-command
round trips (observed ~14-30s) -- see poll_for_reply()'s bumped
default timeout below.

v3 adds one more capability: sending a real FILE (not just text) to
Bayhouse, to be saved into a project. Same construction as a command/
message (gzip then Fernet-encrypt) but skipping the UTF-8-encode step
since a file's bytes are already raw -- see encrypt_file()/send_file()
below. Bayhouse tells a file apart from a command/message purely by
whether the decrypted-and-decompressed bytes decode as UTF-8 (fails ->
file); the attachment's own filename must be set to the file's real
original name so Bayhouse knows what to call it once saved (unlike a
command/message attachment, whose filename is never interpreted).
Files are capped at 20MB on Bayhouse's end. This is inbound-only --
Bayhouse cannot send Ted a file back yet, so decrypt_reply() is
unaffected (a reply is always text). Also new in v3: if a single email
carries free-form text and/or files together, Bayhouse answers with
ONE combined reply for all of it, not one reply per attachment --
irrelevant to this module today since send_command()/send_file() each
send one attachment per email, but worth knowing if that ever changes.

Plain-English description (per the queue-id-237 rule that every
artifact needs one): this module's purpose is to send a fixed command
(PING, STATUS, LIST, RUN <pairing>, HELP), a free-form English
question/task (as of v2), or a real file (as of v3) to Bayhouse, and
decrypt its replies. Its data structure is a single gzip-then-Fernet-
encrypted blob per command/message/file or reply, carried as a raw
email attachment with a meaningless subject/body (Bayhouse never reads
those fields). Its disposition: this is standing protocol code, not a
one-off script -- it persists on disk and in git for as long as the
Ted<->Bill channel is in use. Its cost: ordinary Gmail API send/read
quota on the account already in use for everything else; no
additional expense.

ted_key.txt (sibling file in this same directory) is the shared Fernet
secret that authenticates Ted to Bayhouse on this channel. It is
gitignored (matched by the repo's default-deny .gitignore rule, no
explicit allow-line added for it) and excluded from drive_sync.py's
EXCLUDE_NAMES -- never log it, print it in full, commit it, or let it
reach Drive.
"""
import gzip
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

import google_client

KEY_PATH = Path(__file__).parent / "ted_key.txt"
BAYHOUSE_ADDRESS = "psmalone13@gmail.com"


def load_key() -> bytes:
    return KEY_PATH.read_text().strip().encode("utf-8")


def encrypt_command(command_text: str, key: bytes = None) -> bytes:
    """command_text -> gzip -> Fernet-encrypt. Order matters: compress
    before encrypt (PROTOCOL_SPEC.md Section 4) -- encrypted bytes are
    high-entropy and don't compress."""
    key = key or load_key()
    compressed = gzip.compress(command_text.encode("utf-8"))
    return Fernet(key).encrypt(compressed)


def encrypt_file(file_bytes: bytes, key: bytes = None) -> bytes:
    """New in v3. Same construction as encrypt_command(), just skipping
    the UTF-8-encode step since file_bytes is already raw bytes, not
    text (PROTOCOL_SPEC.md v3 Section 3.2). Pair with send_file() below
    rather than calling this directly, so the attachment's own filename
    is set correctly -- Bayhouse uses that filename (not this function's
    output) to decide what to call the file once saved."""
    key = key or load_key()
    compressed = gzip.compress(file_bytes)
    return Fernet(key).encrypt(compressed)


def send_file(service, file_bytes: bytes, filename: str, key: bytes = None) -> str:
    """New in v3. Encrypts file_bytes and emails it to Bayhouse with the
    attachment's own filename set to `filename` (the file's real
    original name) -- unlike send_command(), where the attachment
    filename never matters. Returns the sent message id. Capped at 20MB
    on Bayhouse's end; an oversized file is dropped there with a note
    in the reply, not rejected here."""
    attachment_bytes = encrypt_file(file_bytes, key)
    return google_client.send_message_with_attachment(
        service, BAYHOUSE_ADDRESS, subject="", body_text="",
        attachment_bytes=attachment_bytes, filename=filename,
    )


def send_file_with_message(service, message_text: str, file_bytes: bytes, filename: str,
                            key: bytes = None) -> str:
    """New in v3. Sends a free-form message and a file together in ONE
    email, each independently encrypted as its own attachment -- the
    pattern PROTOCOL_SPEC.md v3 Section 5.2 describes for telling
    Bayhouse which project a file belongs to (say so in the
    accompanying text). Bayhouse answers both with a single combined
    reply, not one per attachment. Returns the sent message id."""
    key = key or load_key()
    text_attachment = encrypt_command(message_text, key)
    file_attachment = encrypt_file(file_bytes, key)
    return google_client.send_message_with_attachments(
        service, BAYHOUSE_ADDRESS, subject="", body_text="",
        attachments=[
            {"bytes": text_attachment, "filename": "message.bin"},
            {"bytes": file_attachment, "filename": filename},
        ],
    )


def decrypt_reply(attachment_bytes: bytes, key: bytes = None) -> str:
    """Exact inverse of encrypt_command(). Raises ValueError on any
    failure (wrong key, corrupted bytes, or a valid decrypt that isn't
    valid gzip/UTF-8) -- Bayhouse's own side treats all of these
    identically too (no reply at all for an attachment that fails to
    decrypt)."""
    key = key or load_key()
    try:
        compressed = Fernet(key).decrypt(attachment_bytes)
        return gzip.decompress(compressed).decode("utf-8")
    except (InvalidToken, OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"failed to decrypt/decompress attachment: {exc}") from exc


def send_command(service, command_text: str, key: bytes = None) -> str:
    """Encrypts command_text and emails it to Bayhouse. Returns the sent
    message id. Subject/body are left empty -- Bayhouse never reads
    them (PROTOCOL_SPEC.md Section 2)."""
    attachment_bytes = encrypt_command(command_text, key)
    return google_client.send_message_with_attachment(
        service, BAYHOUSE_ADDRESS, subject="", body_text="",
        attachment_bytes=attachment_bytes, filename="command.bin",
    )


def poll_for_reply(service, key: bytes = None, timeout_seconds: int = 180,
                    interval_seconds: int = 5) -> str:
    """Polls the inbox for a message from Bayhouse carrying an
    attachment that decrypts cleanly with our key, and returns the
    decrypted reply text. Raises TimeoutError if nothing decryptable
    from Bayhouse shows up within timeout_seconds. An attachment that
    fails to decrypt is skipped rather than treated as the answer (not
    every attachment from that address is necessarily this protocol's
    reply -- be conservative about what counts).

    Default bumped from v1's 90s to 180s for v2: a free-form message
    (anything that isn't one of the five fixed commands) can take
    Bayhouse "up to a couple of minutes" to answer, per
    PROTOCOL_SPEC.md v2 Section 5.1 -- a fixed command still returns
    in well under a second once Bayhouse actually replies, so this
    only costs extra wait time in the genuine-no-reply case.

    Known bug, not fixed by this function (see root CLAUDE.md TODO,
    queue id 275): this only checks whether a decryptable attachment
    is new to this call's own seen_ids, never whether its timestamp is
    actually after the command was sent -- a stale old reply can be
    returned as if it answered the current send. Callers should still
    cross-check the message's own internalDate against their send
    time before trusting a reply, as every prior protocol turn has
    done by working around this here rather than inside it."""
    key = key or load_key()
    deadline = time.time() + timeout_seconds
    seen_ids = set()
    while time.time() < deadline:
        messages = google_client.list_new_messages(
            service, query=f"from:{BAYHOUSE_ADDRESS} has:attachment", max_results=10
        )
        for m in messages:
            mid = m["id"]
            if mid in seen_ids:
                continue
            seen_ids.add(mid)
            detail = google_client.get_message_detail(service, mid)
            for att in detail["attachments"]:
                raw = google_client.download_attachment(service, mid, att)
                try:
                    return decrypt_reply(raw, key)
                except ValueError:
                    continue
        time.sleep(interval_seconds)
    raise TimeoutError(f"no decryptable reply from {BAYHOUSE_ADDRESS} within {timeout_seconds}s")
