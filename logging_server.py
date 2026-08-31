"""Central logging server -- every module in this repo ships its log
records here over TCP (safehouse_logging.get_logger's SocketHandler)
instead of writing log files or logs.db directly. One process, one writer:
avoids multi-process SQLite write contention and gives one place to tail
or query activity across the whole system.

Per-logger-name output: rotating file at ./logs/<name>.log (5MB x 5
backups) plus a row in ./logs.db (log_entries table) plus an echo to this
server's own console for live tailing.

Run standalone, long-lived:
    python logging_server.py                # listens on 127.0.0.1:9020
"""
import argparse
import logging
import pickle
import socketserver
import sqlite3
import struct
import threading
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
DB_PATH = Path(__file__).parent / "logs.db"
_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (pid=%(process)d): %(message)s"
_formatter = logging.Formatter(_FORMAT)

_file_handlers: dict[str, RotatingFileHandler] = {}
_file_handlers_lock = threading.Lock()
_db_lock = threading.Lock()


def _get_file_handler(logger_name: str) -> RotatingFileHandler:
    with _file_handlers_lock:
        handler = _file_handlers.get(logger_name)
        if handler is None:
            LOG_DIR.mkdir(exist_ok=True)
            handler = RotatingFileHandler(
                LOG_DIR / f"{logger_name}.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
            )
            handler.setFormatter(_formatter)
            _file_handlers[logger_name] = handler
        return handler


def _init_db() -> None:
    conn = sqlite3.connect(str(DB_PATH), timeout=30, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS log_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            logger_name TEXT NOT NULL,
            level TEXT NOT NULL,
            pid INTEGER NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_log_logger ON log_entries(logger_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_log_level ON log_entries(level)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_log_ts ON log_entries(ts)")
    conn.close()


def _write_db(record: logging.LogRecord) -> None:
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH), timeout=30, isolation_level=None)
        try:
            conn.execute(
                "INSERT INTO log_entries (ts, logger_name, level, pid, message) VALUES (?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), record.name, record.levelname,
                 record.process, record.getMessage()),
            )
        finally:
            conn.close()


def _process(record: logging.LogRecord) -> None:
    _get_file_handler(record.name).emit(record)
    _write_db(record)
    print(_formatter.format(record))


class LogRecordHandler(socketserver.StreamRequestHandler):
    """Standard stdlib logging-cookbook socket receiver: 4-byte length
    prefix + pickled LogRecord.__dict__, repeated per connection."""

    def handle(self) -> None:
        while True:
            length_bytes = self.connection.recv(4)
            if len(length_bytes) < 4:
                break
            data_len = struct.unpack(">L", length_bytes)[0]
            data = self.connection.recv(data_len)
            while len(data) < data_len:
                data += self.connection.recv(data_len - len(data))
            obj = pickle.loads(data)
            record = logging.makeLogRecord(obj)
            _process(record)


class LogServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9020)
    args = ap.parse_args()

    _init_db()
    server = LogServer((args.host, args.port), LogRecordHandler)
    print(f"Central logging server listening on {args.host}:{args.port} "
          f"(db={DB_PATH}, logs dir={LOG_DIR})")
    server.serve_forever()


if __name__ == "__main__":
    main()
