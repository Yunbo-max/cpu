#!/usr/bin/env python3
"""Verify and restore one immutable CPU research archive without running it."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile


PROJECT_ID = "autopilot-3d-20261011"
PROJECT_DIR = "autopilot_3d"
CHUNK = 1024 * 1024
INVENTORY_NAMES = {"ARCHIVE_INVENTORY.json", "CHECKPOINT_INVENTORY.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(value, label="path"):
    require(isinstance(value, str) and value, f"Invalid {label}")
    require("\\" not in value and "\x00" not in value, f"Unsafe {label}: {value!r}")
    p = PurePosixPath(value)
    require(not p.is_absolute() and all(x not in ("", ".", "..") for x in value.split("/")),
            f"Unsafe {label}: {value!r}")
    require(str(p) == value, f"Noncanonical {label}: {value!r}")
    return p


def size_hash(record, label):
    require(isinstance(record, dict), f"Invalid {label}")
    size = record.get("bytes")
    digest = record.get("sha256")
    require(type(size) is int and size >= 0, f"Invalid byte count: {label}")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
            f"Invalid SHA256: {label}")
    return size, digest


def raw_url(repo, commit, path):
    safe_path(path, "repository path")
    # Quote each path component; a manifest cannot inject a query or another host.
    from urllib.parse import quote
    return f"https://raw.githubusercontent.com/{repo}/{commit}/" + quote(path, safe="/")


def open_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "cpu-archive-restore/1"})
    response = urllib.request.urlopen(request, timeout=60)
    require(response.status == 200, f"Unexpected HTTP status {response.status}")
    return response


def fetch_manifest(url):
    with open_url(url) as response:
        raw = response.read(16 * CHUNK + 1)
    require(len(raw) <= 16 * CHUNK, "Manifest exceeds 16 MiB")
    return json.loads(raw)


def select_archive(manifest, kind):
    require(isinstance(manifest, dict) and manifest.get("schema_version") == 1,
            "Unsupported manifest schema")
    require(manifest.get("project_id") == PROJECT_ID, "Manifest project identity mismatch")
    archives = manifest.get("archives")
    require(isinstance(archives, list) and archives, "No archives in manifest")
    names = []
    for archive in archives:
        require(isinstance(archive, dict), "Invalid archive record")
        name = archive.get("name")
        safe_path(name, "archive name")
        require(len(PurePosixPath(name).parts) == 1, "Archive name must be a basename")
        names.append(name)
    require(len(names) == len(set(names)), "Duplicate archive names in manifest")
    selected = [a for a in archives if a.get("kind") == kind]
    require(len(selected) == 1, f"Expected exactly one {kind!r} archive")
    archive = selected[0]
    expected_size, _ = size_hash(archive, "archive")
    parts = archive.get("parts")
    require(isinstance(parts, list) and parts, "Archive has no parts")
    part_records = {}
    total = 0
    for part in parts:
        part_size, _ = size_hash(part, "part")
        safe_path(part.get("path"), "part path")
        identity = (part_size, part["sha256"])
        require(part["path"] not in part_records or part_records[part["path"]] == identity,
                "Conflicting identities for one part path")
        part_records[part["path"]] = identity
        total += part_size
    require(total == expected_size, "Part sizes do not sum to archive size")
    return archive


def download_archive(repo, commit, archive, target):
    whole_hash = hashlib.sha256()
    whole_size = 0
    with target.open("xb") as output:
        for part in archive["parts"]:
            expected_size, expected_hash = size_hash(part, "part")
            digest = hashlib.sha256()
            count = 0
            with open_url(raw_url(repo, commit, part["path"])) as response:
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    count += len(chunk)
                    require(count <= expected_size, f"Part exceeds declared size: {part['path']}")
                    digest.update(chunk)
                    whole_hash.update(chunk)
                    output.write(chunk)
            require(count == expected_size and digest.hexdigest() == expected_hash,
                    f"Part size/SHA256 mismatch: {part['path']}")
            whole_size += count
        output.flush()
        os.fsync(output.fileno())
    require(whole_size == archive["bytes"] and whole_hash.hexdigest() == archive["sha256"],
            "Combined archive size/SHA256 mismatch")


def validate_zip(path):
    """All member reads check ZIP CRC in addition to inventory size/SHA256."""
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [m.filename for m in members]
        require(len(names) == len(set(names)), "Duplicate ZIP member names")
        regular = {}
        for member in members:
            name = member.filename[:-1] if member.is_dir() else member.filename
            p = safe_path(name, "ZIP member")
            mode = member.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            require(file_type in (0, stat.S_IFREG, stat.S_IFDIR),
                    f"Symlink or special ZIP member rejected: {name}")
            require(not (member.flag_bits & 1), f"Encrypted ZIP member rejected: {name}")
            if member.is_dir():
                require(file_type in (0, stat.S_IFDIR), f"ZIP directory type mismatch: {name}")
                require(p.parts[0] == PROJECT_DIR, f"Unexpected ZIP directory: {name}")
                require(member.file_size == 0, f"Nonempty ZIP directory: {name}")
            else:
                require(file_type != stat.S_IFDIR, f"ZIP regular-file type mismatch: {name}")
                if name not in INVENTORY_NAMES:
                    require(len(p.parts) > 1 and p.parts[0] == PROJECT_DIR,
                            f"Unexpected ZIP file outside project: {name}")
                regular[name] = member
        inventory_names = INVENTORY_NAMES.intersection(regular)
        require(len(inventory_names) == 1, "Expected exactly one root inventory")
        inventory_name = next(iter(inventory_names))
        require(regular[inventory_name].file_size <= 64 * CHUNK, "Inventory exceeds 64 MiB")
        inventory = json.loads(archive.read(inventory_name))
        require(isinstance(inventory, dict) and isinstance(inventory.get("files"), list),
                "Invalid archive inventory")
        inventory_files = {}
        for record in inventory["files"]:
            expected_size, expected_hash = size_hash(record, "inventory file")
            relative = safe_path(record.get("path"), "inventory path")
            name = PROJECT_DIR + "/" + str(relative)
            require(name not in inventory_files, f"Duplicate inventory path: {name}")
            inventory_files[name] = (expected_size, expected_hash)
        require(set(inventory_files) == set(regular) - {inventory_name},
                "Inventory does not exactly cover all archived regular files")
        for name, (expected_size, expected_hash) in inventory_files.items():
            require(regular[name].file_size == expected_size, f"ZIP header size mismatch: {name}")
            digest = hashlib.sha256()
            count = 0
            with archive.open(name) as source:
                while True:
                    chunk = source.read(CHUNK)
                    if not chunk:
                        break
                    digest.update(chunk)
                    count += len(chunk)
            require(count == expected_size and digest.hexdigest() == expected_hash,
                    f"Inventory size/SHA256 mismatch: {name}")
        # Explicit test also covers directory entries, while regular files were
        # already streamed above (ZipExtFile checks CRC at end of each member).
        require(archive.testzip() is None, "ZIP CRC check failed")
        return len(inventory_files), inventory_name


def extract_verified(path, destination):
    destination = Path(os.path.abspath(destination))
    require(not destination.is_symlink(), "Destination must not be a symlink")
    if destination.exists():
        require(destination.is_dir() and not any(destination.iterdir()),
                "Destination must be an empty directory")
    else:
        destination.mkdir(parents=True)
    project = destination / PROJECT_DIR
    require(not project.exists() and not project.is_symlink(), "Extracted project path already exists")
    with tempfile.TemporaryDirectory(prefix=".verified-extract-", dir=destination) as work:
        root = Path(work)
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                relative = PurePosixPath(member.filename.rstrip("/"))
                output = root.joinpath(*relative.parts)
                if member.is_dir():
                    output.mkdir(parents=True, exist_ok=True)
                    continue
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, output.open("xb") as target:
                    shutil.copyfileobj(source, target, CHUNK)
                mode = (member.external_attr >> 16) & 0o777
                if mode:
                    os.chmod(output, mode)
        require((root / PROJECT_DIR).is_dir(), "Archive contains no project directory")
        # Rename only after every verified file has been extracted successfully.
        require(not project.exists() and not project.is_symlink(), "Project appeared during extraction")
        (root / PROJECT_DIR).rename(project)
        for name in INVENTORY_NAMES:
            if (root / name).exists():
                require(not (destination / name).exists(), "Inventory path appeared during extraction")
                (root / name).rename(destination / name)
    return str(project)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True, help="Immutable, full 40-character Git commit SHA")
    parser.add_argument("--repo", default="Yunbo-max/cpu")
    parser.add_argument("--manifest", default=f"projects/{PROJECT_ID}/archive-manifest.json")
    parser.add_argument("--kind", choices=("active", "history"), default="active")
    parser.add_argument("--destination", help="Empty target parent; restored project goes in autopilot_3d/")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    require(re.fullmatch(r"[0-9a-fA-F]{40}", args.commit) is not None,
            "--commit must be a full immutable 40-character hexadecimal SHA")
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo) is not None,
            "Invalid GitHub owner/repository")
    require(args.verify_only or args.destination, "--destination is required unless --verify-only")
    if args.destination and not args.verify_only:
        destination = Path(args.destination)
        require(not destination.is_symlink(), "Destination must not be a symlink")
        require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())),
                "Destination must be an empty directory")
    commit = args.commit.lower()
    manifest = fetch_manifest(raw_url(args.repo, commit, args.manifest))
    archive = select_archive(manifest, args.kind)
    with tempfile.TemporaryDirectory(prefix="cpu-verified-download-") as temp:
        target = Path(temp) / "archive.zip"
        download_archive(args.repo, commit, archive, target)
        count, inventory = validate_zip(target)
        restored = None if args.verify_only else extract_verified(target, args.destination)
    print(json.dumps({"status": "verified" if args.verify_only else "restored", "project_id": PROJECT_ID,
                      "repo": args.repo, "commit": commit, "kind": args.kind,
                      "archive": archive["name"], "bytes": archive["bytes"], "sha256": archive["sha256"],
                      "parts_verified": len(archive["parts"]), "files_verified": count,
                      "inventory": inventory, "zip_crc": "passed", "destination": restored}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, urllib.error.URLError) as error:
        print(f"restore failed: {error}", file=sys.stderr)
        sys.exit(1)
