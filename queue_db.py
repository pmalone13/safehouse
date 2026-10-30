"""SQLite-backed FIFO message queue for the safehouse coordinator.

Two tables:
  - messages: one row per inbound event (text, email, whatever channel
    comes later). status flows unclaimed -> claimed -> done|failed.
    claim_next() uses a BEGIN IMMEDIATE claim-oldest-unclaimed pattern
    (same convention bayhouse itself uses in analyzeBirdClips.py /
    assistant_queue/db.py) so it stays safe even if something ever claims
    concurrently, though today's coordinator is single-process/serial.
  - outage_notice / retry columns on messages: see coordinator.py.

Session continuity (2026-10-30 redesign, see coordinator.py's own
docstring) now lives entirely *inside* one long-lived Claude turn, which
self-claims further messages via claim_next() as they arrive rather than
the coordinator resuming a new spawn per message -- there is no
session_state table anymore. One consequence: a message can land in
'claimed' and never reach 'done'/'failed'/'retry_pending' if the process
holding it dies mid-handling (crash, VM bounce, SPAWN_TIMEOUT_SECONDS
kill). requeue_stale_claimed() below is the recovery path for that -- a
'claimed' row older than any legitimate spawn could still be running is
flipped back to 'unclaimed' so claim_next() picks it up again.

Deliberately no multi-tenant capability/actor model here (unlike
bayhouse's own rules/pairings tables) -- this box is single-user by
design.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "queue.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    """Additive migration for a column that didn't exist in older copies
    of this DB -- lets existing queue.db files on disk pick up the new
    retry columns without a destructive rebuild."""
    cols = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                source TEXT NOT NULL,
                body TEXT NOT NULL,
                received_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unclaimed',
                claimed_at TEXT,
                error TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,
                next_retry_at TEXT
            )
            """
        )
        _ensure_column(conn, "messages", "retry_count", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "messages", "next_retry_at", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)")
        # Singleton row tracking the last time an outage SMS went out, so
        # one outage that fails many messages in a row (e.g. a usage-limit
        # window) triggers one text, not one per dropped message.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outage_notice (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_notified_at TEXT
            )
            """
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def enqueue(channel: str, source: str, body: str) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO messages (channel, source, body, received_at) VALUES (?, ?, ?, ?)",
            (channel, source, body, _now_iso()),
        )
        return cur.lastrowid


@contextmanager
def _immediate(conn: sqlite3.Connection):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def claim_next() -> Optional[sqlite3.Row]:
    """Claims the oldest unclaimed message, or None if the queue is empty."""
    conn = _connect()
    try:
        with _immediate(conn):
            row = conn.execute(
                "SELECT * FROM messages WHERE status = 'unclaimed' ORDER BY id ASC LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE messages SET status = 'claimed', claimed_at = ? WHERE id = ?",
                (_now_iso(), row["id"]),
            )
            row = conn.execute("SELECT * FROM messages WHERE id = ?", (row["id"],)).fetchone()
        return row
    finally:
        conn.close()


def has_pending() -> bool:
    with _connect() as conn:
        row = conn.execute("SELECT 1 FROM messages WHERE status = 'unclaimed' LIMIT 1").fetchone()
        return row is not None


def mark_done(message_id: int) -> None:
    with _connect() as conn:
        conn.execute("UPDATE messages SET status = 'done' WHERE id = ?", (message_id,))


def mark_failed(message_id: int, error: str) -> None:
    """Terminal failure -- retries (if any) are exhausted. Distinct from
    mark_retry_pending below, which is the normal landing spot for a
    failure that's still being retried automatically."""
    with _connect() as conn:
        conn.execute(
            "UPDATE messages SET status = 'failed', error = ? WHERE id = ?", (error, message_id)
        )


def mark_retry_pending(message_id: int, error: str, retry_count: int, next_retry_at: str) -> None:
    """Keeps a failed message out of 'failed' purgatory -- it's requeued
    automatically once next_retry_at passes (see requeue_due_retries),
    instead of being silently dropped the way every message failure was
    before this (the recurring outage gap logged across 2026-10, see
    root CLAUDE.md's TODO section)."""
    with _connect() as conn:
        conn.execute(
            """
            UPDATE messages
            SET status = 'retry_pending', error = ?, retry_count = ?, next_retry_at = ?
            WHERE id = ?
            """,
            (error, retry_count, next_retry_at, message_id),
        )


def requeue_due_retries() -> int:
    """Flips any retry_pending message whose next_retry_at has passed back
    to 'unclaimed' so claim_next() picks it up through the ordinary
    path -- deliberately not a separate claim mechanism, so done/failed
    handling etc. all stay exactly as they are for a normal message.
    Returns how many rows were flipped."""
    with _connect() as conn:
        cur = conn.execute(
            """
            UPDATE messages
            SET status = 'unclaimed'
            WHERE status = 'retry_pending' AND next_retry_at IS NOT NULL AND next_retry_at <= ?
            """,
            (_now_iso(),),
        )
        return cur.rowcount


def requeue_stale_claimed(staleness_seconds: float) -> int:
    """Recovers a message stuck in 'claimed' because the process handling
    it (or one it was self-claimed into, mid-turn) died before ever
    marking it done/failed/retry_pending -- otherwise such a row has no
    path back to being processed at all, since claim_next() only ever
    looks at 'unclaimed'. Pass a staleness_seconds comfortably above
    coordinator.py's SPAWN_TIMEOUT_SECONDS so this never touches a
    message that's still legitimately being worked on."""
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=staleness_seconds)).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            """
            UPDATE messages
            SET status = 'unclaimed', claimed_at = NULL
            WHERE status = 'claimed' AND claimed_at IS NOT NULL AND claimed_at <= ?
            """,
            (cutoff,),
        )
        return cur.rowcount


def get_outage_notice() -> Optional[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute("SELECT * FROM outage_notice WHERE id = 1").fetchone()


def set_outage_notice(ts_iso: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO outage_notice (id, last_notified_at) VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET last_notified_at = excluded.last_notified_at
            """,
            (ts_iso,),
        )


def clear_outage_notice() -> None:
    """Called once a delayed message finally succeeds, so the throttle
    only suppresses repeat texts within one ongoing outage -- a later,
    unrelated outage still gets its own prompt notification rather than
    inheriting whatever's left of the old throttle window."""
    with _connect() as conn:
        conn.execute("DELETE FROM outage_notice WHERE id = 1")
