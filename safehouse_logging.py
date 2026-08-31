"""Centralized, log4j-style logging shared by every module in this repo.
Every module gets its own named logger; instead of writing log files or a
database directly, records are shipped over TCP (log4j SocketAppender
style) to a central logging server (logging_server.py), which is the one
process that actually writes files/DB -- no multi-process write contention,
one place to see everything.

Usage, at the top of any top-level script:
    from pathlib import Path
    from safehouse_logging import get_logger
    log = get_logger(Path(__file__).stem)

For a module inside a package, qualify with the package name so same-named
files across packages don't collide into one logger:
    log = get_logger(f"{Path(__file__).parent.name}.{Path(__file__).stem}")

log.info(...)  = normal, low-volume operational events.
log.debug(...) = high-volume tracing, off by default.
Default level is INFO; set SAFEHOUSE_LOG_LEVEL=DEBUG in the environment to
turn on debug-level tracing repo-wide without touching any code.

If logging_server.py isn't running, SocketHandler silently drops records
after failing to connect (by design -- a client must never crash because
the log server is down). A console handler is also attached so you still
see output locally even when the central server is unreachable.
"""
import logging
import logging.handlers
import os

LOG_SERVER_HOST = os.environ.get("SAFEHOUSE_LOG_HOST", "127.0.0.1")
LOG_SERVER_PORT = int(os.environ.get("SAFEHOUSE_LOG_PORT", "9020"))
LEVEL = os.environ.get("SAFEHOUSE_LOG_LEVEL", "INFO").upper()

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (pid=%(process)d): %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Idempotent: safe to call repeatedly for the same name (e.g. on
    module re-import) without stacking duplicate handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(LEVEL)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(console_handler)

    # SocketHandler pickles the raw record and ships it to logging_server.py;
    # formatting happens server-side, so no formatter is set here.
    socket_handler = logging.handlers.SocketHandler(LOG_SERVER_HOST, LOG_SERVER_PORT)
    logger.addHandler(socket_handler)

    return logger
