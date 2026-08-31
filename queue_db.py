"""SQLite-backed FIFO message queue + session-continuity state for the
safehouse coordinator.

Two tables:
  - messages: one row per inbound event (text, email, whatever channel
    comes later). status flows unclaimed -> claimed -> done|failed.
    claim_next() uses a BEGIN IMMEDIATE claim-oldest-unclaimed pattern
    (same convention bayhouse itself uses in analyzeBirdClips.py /
    assistant_queue/db.py) so it stays safe even if something ever claims
    concurrently, though today's coordinator is single-process/serial.
  - session_state: a single row (id=1) holding the current resumable
    Claude session_id and the deadline past which it should be treated
    as expired. This is the "resume-ticket" -- no process stays resident
    between messages; the coordinator just remembers this ticket and
    resumes (`claude -p --resume <session_id>`) if a new message arrives
    before the deadline, otherwise starts fresh. Persisted (not just
    in-memory) specifically so a coordinator restart/bounce doesn't lose
    the ability to resume mid-window.

Deliberately no multi-tenant capability/actor model here (unlike
bayhouse's own rules/pairings tables) -- this box is single-user by
design.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "queue.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn


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
                error TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                session_id TEXT,
                deadline TEXT,
                updated_at TEXT
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
    with _connect() as conn:
        conn.execute(
            "UPDATE messages SET status = 'failed', error = ? WHERE id = ?", (error, message_id)
        )


def get_session_state() -> Optional[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute("SELECT * FROM session_state WHERE id = 1").fetchone()


def set_session_state(session_id: str, deadline_iso: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO session_state (id, session_id, deadline, updated_at)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                session_id = excluded.session_id,
                deadline = excluded.deadline,
                updated_at = excluded.updated_at
            """,
            (session_id, deadline_iso, _now_iso()),
        )


def clear_session_state() -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM session_state WHERE id = 1")
