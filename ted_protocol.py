"""Ted Protocol v2 -- Ted's send/receive side of the encrypted-attachment
command channel to Bayhouse ("Bill"). v1 spec issued 2026-10-11, v2
issued by Bayhouse 2026-10-13 (both logged in
projects/engineering/secure-agent-communication/CLAUDE.md). Crypto
construction confirmed against the matching reference script
(send_side_reference.py, from ted_protocol_package_v1.zip) live with
Paul 2026-10-12; v2's package (ted_protocol_package_v2.zip) confirms
the crypto/key/transport are byte-for-byte unchanged from v1 -- no
code change was required here for that part.

v2 adds exactly one new capability, purely on Bayhouse's receiving
side: a message that doesn't start with one of the five fixed command
words is no longer an error -- Bayhouse now reads it as a genuine
free-form question or piece of project work and replies directly.
Nothing on Ted's sending side has to change to use this: encrypt_command()/
send_command() already accept any text, fixed command or not. The one
real consequence for this module is timing -- a free-form reply can
take "up to a couple of minutes" per Bayhouse's spec (PROTOCOL_SPEC.md
v2 Section 5.1), well past v1's fixed-command round trips (observed
~14-30s) -- see poll_for_reply()'s bumped default timeout below.

Plain-English description (per the queue-id-237 rule that every
artifact needs one): this module's purpose is to send either a fixed
command (PING, STATUS, LIST, RUN <pairing>, HELP) or, as of v2, a
free-form English question/task, to Bayhouse, and decrypt its replies.
Its data structure is a single gzip-then-Fernet-encrypted blob per
command/message or reply, carried as a raw email attachment with a
meaningless subject/body (Bayhouse never reads those fields). Its
disposition: this is standing protocol code, not a one-off script --
it persists on disk and in git for as long as the Ted<->Bill channel
is in use. Its cost: ordinary Gmail API send/read quota on the account
already in use for everything else; no additional expense.

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
