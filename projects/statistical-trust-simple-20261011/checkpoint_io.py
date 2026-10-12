#!/usr/bin/env python3
"""Verify/restore one GitHub CPU checkpoint; cleanup requires exact byte parity.

Use a freshly downloaded, commit-pinned repository checkout. No credentials,
network operations, experiment execution or global memory-cache controls here.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import zipfile

PROJECT = "statistical-trust-simple-20261011"
ROOT = Path("/workspace/scratch/a5c97e2248bf/statistical_trust_simple")
INDEX = Path("projects") / PROJECT / "LATEST.json"
MAX_BYTES = 1_000_000_000


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(524288), b""):
            h.update(b)
    return h.hexdigest()


def sqlite_backup_digest(path):
    # Packaging uses SQLite backup, not a raw copy. Repeat that same operation
    # so benign file-change counters do not masquerade as new records; pending
    # committed WAL content is included. Do not normalize or ignore any bytes.
    with tempfile.TemporaryDirectory(prefix="sts-db-parity-") as temp:
        snapshot = Path(temp) / "simple-loop.sqlite3"
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as src, sqlite3.connect(snapshot) as dst:
            src.backup(dst)
            if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Local SQLite integrity failure")
        return snapshot.stat().st_size, digest(snapshot)


def relative(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or "\\" in name or any(x in ("", ".", "..") for x in name.split("/")):
        raise ValueError("Unsafe archive path")
    return p


@contextlib.contextmanager
def assembled(repo):
    idx = json.loads((repo / INDEX).read_text())
    if idx["project_id"] != PROJECT or idx["restore_root"] != str(ROOT):
        raise ValueError("Wrong project/root")
    if not 0 < idx["archive_bytes"] <= MAX_BYTES:
        raise ValueError("Archive size outside safety bound")
    with tempfile.TemporaryDirectory(prefix="sts-remote-check-") as temp:
        arc = Path(temp) / "checkpoint.zip"
        with arc.open("xb") as out:
            for n, part in enumerate(idx["parts"]):
                if part["index"] != n:
                    raise ValueError("Nonsequential parts")
                p = repo / relative(part["path"])
                if p.is_symlink() or not p.resolve().is_relative_to(repo.resolve()):
                    raise ValueError("Symlink/escaping archive part")
                if p.stat().st_size != part["bytes"] or digest(p) != part["sha256"]:
                    raise ValueError("Part integrity mismatch")
                with p.open("rb") as inp:
                    shutil.copyfileobj(inp, out, 524288)
        if arc.stat().st_size != idx["archive_bytes"] or digest(arc) != idx["archive_sha256"]:
            raise ValueError("Archive integrity mismatch")
        with zipfile.ZipFile(arc) as z:
            prefix = ROOT.name + "/"
            members = z.infolist()
            if len(members) != idx["member_count"] or len({m.filename for m in members}) != len(members):
                raise ValueError("Wrong/duplicate member inventory")
            if sum(m.file_size for m in members) > MAX_BYTES:
                raise ValueError("Uncompressed archive exceeds safety bound")
            for m in members:
                relative(m.filename)
                if not m.filename.startswith(prefix) or m.is_dir() or stat.S_ISLNK(m.external_attr >> 16):
                    raise ValueError("Unexpected member type/root")
            raw_manifest = z.read(prefix + "MANIFEST.json")
            if hashlib.sha256(raw_manifest).hexdigest() != idx["manifest_sha256"]:
                raise ValueError("Manifest integrity mismatch")
            rows = json.loads(raw_manifest)["files"]
            expected = {prefix + r["path"] for r in rows} | {prefix + "MANIFEST.json"}
            if len(rows) != idx["manifest_files"] or len(expected) != len(rows) + 1 or expected != {m.filename for m in members}:
                raise ValueError("Manifest/member set mismatch")
            for row in rows:
                relative(row["path"])
                h = hashlib.sha256()
                size = 0
                with z.open(prefix + row["path"]) as f:
                    for b in iter(lambda: f.read(524288), b""):
                        h.update(b)
                        size += len(b)
                if size != row["bytes"] or h.hexdigest() != row["sha256"]:
                    raise ValueError("Payload integrity mismatch: " + row["path"])
            db = Path(temp) / "simple-loop.sqlite3"
            with z.open(prefix + ".research-autopilot/simple-loop.sqlite3") as inp, db.open("xb") as out:
                shutil.copyfileobj(inp, out, 524288)
            with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as c:
                if c.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("SQLite integrity failure")
            yield idx, rows, z


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("verify", "restore", "cleanup"))
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--apply", action="store_true", help="Required for cleanup; otherwise checks only")
    a = p.parse_args()
    with assembled(a.repo.resolve()) as (idx, rows, z):
        result = {"project_id": PROJECT, "archive_sha256": idx["archive_sha256"],
                  "verified_parts": len(idx["parts"]), "verified_payload_files": len(rows),
                  "sqlite_integrity": "ok", "action": a.action}
        if a.action == "restore":
            if ROOT.exists() or ROOT.is_symlink():
                raise ValueError("Refusing to overwrite an existing project")
            ROOT.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="sts-restore-", dir=ROOT.parent) as temp:
                staged = Path(temp) / ROOT.name
                staged.mkdir()
                for m in z.infolist():
                    dest = staged / PurePosixPath(m.filename).relative_to(ROOT.name)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(m) as inp, dest.open("xb") as out:
                        shutil.copyfileobj(inp, out, 524288)
                    dest.chmod((m.external_attr >> 16) & 0o777)
                if ROOT.exists():
                    raise ValueError("Project appeared during restore; preserve it")
                staged.rename(ROOT)
            result["restored_root"] = str(ROOT)
        elif a.action == "cleanup":
            if ROOT.is_symlink() or ROOT.resolve() != ROOT:
                raise ValueError("Unexpected local root")
            lock_path = ROOT / ".research-autopilot/runner/supervisor.lock"
            with lock_path.open("a+") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                raw = subprocess.check_output([sys.executable, str(ROOT / "runtime/scripts/simple_runner.py"),
                                               "--root", str(ROOT), "status"], timeout=20)
                state = json.loads(raw)
                if any(x["state"] != "terminal" for x in state["attempts"]):
                    raise ValueError("Active or unknown attempt; do not clean")
                if any(x["state"] not in ("succeeded", "failed", "cancelled") for x in state["tasks"]):
                    raise ValueError("Nonterminal task; do not clean")
                files = [f for f in ROOT.rglob("*") if f.is_file() or f.is_symlink()]
                expected = {r["path"]: r for r in rows}
                for f in files:
                    rel = f.relative_to(ROOT).as_posix()
                    if f.is_symlink():
                        raise ValueError("Unexpected local symlink")
                    if rel in expected:
                        r = expected[rel]
                        size, actual = (sqlite_backup_digest(f) if rel == ".research-autopilot/simple-loop.sqlite3"
                                        else (f.stat().st_size, digest(f)))
                        if size != r["bytes"] or actual != r["sha256"]:
                            raise ValueError("Local file is newer/different; keep it: " + rel)
                    elif not (rel == "MANIFEST.json" or "__pycache__" in f.parts or
                              rel == ".research-autopilot/runner/supervisor.lock" or
                              rel in (".research-autopilot/simple-loop.sqlite3-wal", ".research-autopilot/simple-loop.sqlite3-shm")):
                        raise ValueError("Unarchived file; keep it: " + rel)
                if set(expected) - {f.relative_to(ROOT).as_posix() for f in files}:
                    raise ValueError("Missing local payload; inspect before cleanup")
                result["local_files_checked"] = len(files)
                result["local_bytes"] = sum(f.stat().st_size for f in files)
                if a.apply:
                    # Only preverified individual files under this exact root.
                    for f in files:
                        if f != lock_path:
                            f.unlink()
                    for d in sorted((d for d in ROOT.rglob("*") if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
                        if d not in lock_path.parents:
                            d.rmdir()
                    lock_path.unlink()
                    for d in lock_path.parents:
                        if d == ROOT:
                            break
                        d.rmdir()
                    ROOT.rmdir()
                    result["local_copy_removed"] = True
                else:
                    result["local_copy_removed"] = False
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
