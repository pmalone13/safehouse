"""One-way mirror: this whole repo -> a "safehouse" folder on Drive, so
Paul can see what's happening without SSH. Local filesystem stays the
one Claude actually writes to (fast, no API round-trip per file); this
walks the tree afterward and pushes whatever changed.

Deliberately one-way (local -> Drive only) -- pulling Paul's own Drive
edits back down is a real conflict-resolution problem not worth solving
until it's actually needed. For now, "read something from Drive" is a
one-off, explicit action a turn takes when asked (browse via
google_client.list_files/get_file_content), not an automatic pull.

Incremental via a manifest (.drive_sync_state.json, gitignored) mapping
local relpath -> {drive_file_id, sha256}, plus a directory relpath ->
drive_folder_id cache so repeated syncs don't re-walk/re-create folders
that already exist. Only files whose hash changed get re-uploaded.

Deletions are NOT mirrored -- if a local file disappears, its Drive copy
is left in place (logged as orphaned) rather than auto-deleted. Drive is
meant to be the more durable, human-visible copy; silently deleting from
it because a local file vanished is the wrong default here.

Run manually, or (normally) invoked as part of a turn's own checkpoint,
right after the git commit/push:
    ./venv/bin/python drive_sync.py
"""
import hashlib
import json
import os
from pathlib import Path

import google_client
from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

REPO_ROOT = Path(__file__).parent
MANIFEST_PATH = REPO_ROOT / ".drive_sync_state.json"
DRIVE_ROOT_FOLDER_NAME = "safehouse"

# Anything under these names is never synced -- credentials, git
# internals, the venv, caches, and the manifest/lock files that only
# make sense on this machine. Matched against any path component, not
# just the top level, so e.g. a nested __pycache__/ is still excluded.
#
# queue.db/logs.db are ALSO excluded here, not just their -wal/-shm
# sidecars: create_file()/update_file_content() only handle UTF-8 text
# today, and blindly reading a SQLite file as text would silently
# corrupt it (replacement characters in place of invalid byte
# sequences). Binary-file support (raw bytes, not forced text decode)
# is a real TODO if Paul wants these visible on Drive -- not built yet,
# excluding rather than uploading something broken.
EXCLUDE_NAMES = {
    ".git", "venv", "__pycache__", ".drive_sync_state.json",
    ".env", ".gmail_api_client_secret.json", ".gmail_api_token.json",
    ".gmail_api_token.lock", ".drive_api_client_secret.json",
    ".drive_api_token.json", ".drive_api_token.lock",
    "queue.db", "queue.db-wal", "queue.db-shm",
    "logs.db", "logs.db-wal", "logs.db-shm",
    "optins.db", "optins.db-wal", "optins.db-shm",
}
EXCLUDE_SUFFIXES = (".pyc",)


def _should_skip(name: str) -> bool:
    return name in EXCLUDE_NAMES or name.endswith(EXCLUDE_SUFFIXES)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"root_folder_id": None, "folders": {}, "files": {}}


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _ensure_drive_folder_path(service, manifest: dict, rel_dir: str) -> str:
    """Returns the Drive folder id for rel_dir (a '/'-joined relative
    path, '' for repo root), creating any missing folders along the way
    and caching ids in manifest["folders"]."""
    if rel_dir in manifest["folders"]:
        return manifest["folders"][rel_dir]

    if rel_dir == "":
        parent_id = manifest["root_folder_id"]
        folder_id = google_client.find_or_create_folder(service, DRIVE_ROOT_FOLDER_NAME, parent_id)
        manifest["root_folder_id"] = folder_id
        manifest["folders"][""] = folder_id
        return folder_id

    parent_rel, _, name = rel_dir.rpartition("/")
    parent_id = _ensure_drive_folder_path(service, manifest, parent_rel)
    folder_id = google_client.find_or_create_folder(service, name, parent_id)
    manifest["folders"][rel_dir] = folder_id
    return folder_id


def sync_all() -> dict:
    """Walks the whole repo and mirrors changed files to Drive. Returns
    a summary dict: {"created": N, "updated": N, "unchanged": N,
    "orphaned": [relpaths...]}."""
    service = google_client.get_drive_client()
    manifest = _load_manifest()
    summary = {"created": 0, "updated": 0, "unchanged": 0, "orphaned": []}
    seen_relpaths = set()

    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if not _should_skip(d)]
        rel_dir = os.path.relpath(dirpath, REPO_ROOT).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""

        for filename in filenames:
            if _should_skip(filename):
                continue
            local_path = Path(dirpath) / filename
            relpath = f"{rel_dir}/{filename}" if rel_dir else filename
            seen_relpaths.add(relpath)

            file_hash = _sha256(local_path)
            existing = manifest["files"].get(relpath)
            if existing and existing["sha256"] == file_hash:
                summary["unchanged"] += 1
                continue

            folder_id = _ensure_drive_folder_path(service, manifest, rel_dir)
            content = local_path.read_text(encoding="utf-8", errors="replace")

            if existing:
                google_client.update_file_content(service, existing["drive_file_id"], content)
                manifest["files"][relpath]["sha256"] = file_hash
                summary["updated"] += 1
            else:
                drive_file_id = google_client.create_file(service, filename, content, parent_id=folder_id)
                manifest["files"][relpath] = {"drive_file_id": drive_file_id, "sha256": file_hash}
                summary["created"] += 1

    for relpath in manifest["files"]:
        if relpath not in seen_relpaths:
            summary["orphaned"].append(relpath)
    if summary["orphaned"]:
        log.warning(f"{len(summary['orphaned'])} file(s) synced to Drive previously no longer "
                    f"exist locally (left in place, not deleted): {summary['orphaned']}")

    _save_manifest(manifest)
    log.info(f"drive sync done: {summary['created']} created, {summary['updated']} updated, "
             f"{summary['unchanged']} unchanged, {len(summary['orphaned'])} orphaned")
    return summary


if __name__ == "__main__":
    result = sync_all()
    print(json.dumps(result, indent=2))
