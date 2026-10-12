"""Content-addressed simple-runner source snapshots, without activation or updates.

Only the fixed executable/guidance inventory is copied. A snapshot identifies
bytes, not their scientific correctness. Adoption and quiet-boundary authority
belong to the runner; this helper never edits installed skills or old snapshots.
"""
from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import threading
import types
import uuid


class SourceError(ValueError):
    """A source pin cannot be captured or verified exactly."""


LEGACY_SOURCE_FILES = ("SKILL.md", "references/rsi-simple.md", "references/simple-runner.md",
                       "scripts/_simple_process.py", "scripts/_simple_source.py",
                       "scripts/simple_loop.py", "scripts/simple_runner.py")
PRE_COLLABORATION_SOURCE_FILES = LEGACY_SOURCE_FILES + (
    "references/simple-experiment-design.md", "scripts/simple_design.py", "scripts/simple_resources.py",
    "assets/templates/simple-experiment-plan.json", "assets/templates/simple-experiment-results.json")
SOURCE_FILES = PRE_COLLABORATION_SOURCE_FILES + (
    "references/simple-collaboration.md", "assets/templates/simple-delegation.json")
SOURCE_BASE = ".research-autopilot/runner/sources"
_MODULE_LOCK = threading.Lock()


def _encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


@contextmanager
def _directory(path, create=False):
    """Walk absolute directory components with NOFOLLOW, including the root."""
    path = Path(os.path.abspath(Path(path).expanduser()))
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=descriptor)
                    os.fsync(descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        yield path, descriptor
    finally:
        os.close(descriptor)


def _read(directory, relative):
    descriptors = []
    try:
        current = directory
        parts = relative.split("/")
        for part in parts[:-1]:
            current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            descriptors.append(current)
        handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current)
        descriptors.append(handle)
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode):
            raise SourceError(f"Source must be a regular file: {relative}")
        chunks = []
        while chunk := os.read(handle, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(handle)
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if identity(before) != identity(after):
            raise SourceError(f"Source changed while reading: {relative}")
        return b"".join(chunks)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _identity(contents):
    files = [{"path": name, "sha256": hashlib.sha256(contents[name]).hexdigest()} for name in SOURCE_FILES]
    digest = hashlib.sha256(_encoded({"format": "rsi-simple-source-v1", "files": files})).hexdigest()
    return {"digest": digest, "files": files}


def _capture_bytes(source_root):
    root = Path(__file__).parents[1] if source_root is None else source_root
    with _directory(root) as (_, directory):
        contents = {name: _read(directory, name) for name in SOURCE_FILES}
        # Refuse a mixed-generation capture if files change during the read.
        if any(_read(directory, name) != contents[name] for name in SOURCE_FILES):
            raise SourceError("Source changed during capture; retry from a quiet source tree")
    return contents


def current_source_identity(source_root=None):
    """Hash the current fixed source inventory; do not adopt or activate it."""
    try:
        return _identity(_capture_bytes(source_root))
    except OSError as exc:
        raise SourceError(f"Cannot inspect simple source: {exc}") from exc


def _validate_descriptor(descriptor):
    if not isinstance(descriptor, dict) or set(descriptor) != {"digest", "root", "files"}:
        raise SourceError("Source descriptor requires exactly digest, root and files")
    digest, files = descriptor["digest"], descriptor["files"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise SourceError("Source digest must be lowercase SHA256")
    if descriptor["root"] != f"{SOURCE_BASE}/{digest}":
        raise SourceError("Source snapshot root does not match its project-relative digest")
    if not isinstance(files, list):
        raise SourceError("Source file inventory must be an array")
    inventory = tuple(item.get("path") if isinstance(item, dict) else None for item in files)
    if inventory not in (LEGACY_SOURCE_FILES, PRE_COLLABORATION_SOURCE_FILES, SOURCE_FILES):
        raise SourceError("Source file inventory differs from the fixed current or historical inventory")
    for name, item in zip(inventory, files):
        if (not isinstance(item, dict) or set(item) != {"path", "sha256"}
                or item["path"] != name or not isinstance(item["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise SourceError("Source file inventory differs from the required simple files")
    actual = hashlib.sha256(_encoded({"format": "rsi-simple-source-v1", "files": files})).hexdigest()
    if actual != digest:
        raise SourceError("Source inventory digest mismatch")
    return inventory


def _inventory(directory, prefix=""):
    files, directories = set(), set()
    with os.scandir(directory) as entries:
        for entry in entries:
            name = prefix + entry.name
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                directories.add(name)
                child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                try:
                    nested_files, nested_directories = _inventory(child, name + "/")
                finally:
                    os.close(child)
                files.update(nested_files)
                directories.update(nested_directories)
            elif stat.S_ISREG(mode):
                files.add(name)
            else:
                raise SourceError(f"Snapshot contains a symlink or special file: {name}")
    return files, directories


def verify_snapshot(project_root, descriptor):
    """Verify descriptor, manifest, exact inventory and bytes; return pinned root."""
    inventory = _validate_descriptor(descriptor)
    expected_directories = {str(parent) for name in inventory for parent in Path(name).parents if str(parent) != "."}
    try:
        with _directory(project_root) as (project, _):
            destination = project / descriptor["root"]
            with _directory(destination) as (_, directory):
                files, directories = _inventory(directory)
                if files != set(inventory) | {"manifest.json"} or directories != expected_directories:
                    raise SourceError("Snapshot has missing or extra files/directories")
                manifest = {"schema_version": 1, "digest": descriptor["digest"], "files": descriptor["files"]}
                if _read(directory, "manifest.json") != _encoded(manifest):
                    raise SourceError("Snapshot manifest differs from the retained descriptor")
                for item in descriptor["files"]:
                    if hashlib.sha256(_read(directory, item["path"])).hexdigest() != item["sha256"]:
                        raise SourceError(f"Snapshot source hash changed: {item['path']}")
            return destination
    except OSError as exc:
        raise SourceError(f"Cannot verify source snapshot: {exc}") from exc


def _write(directory, relative, data):
    descriptors = []
    try:
        current = directory
        parts = relative.split("/")
        for part in parts[:-1]:
            try:
                os.mkdir(part, mode=0o700, dir_fd=current)
                os.fsync(current)
            except FileExistsError:
                pass
            current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            descriptors.append(current)
        handle = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=current)
        descriptors.append(handle)
        remaining = memoryview(data)
        while remaining:
            remaining = remaining[os.write(handle, remaining):]
        os.fchmod(handle, 0o444)
        os.fsync(handle)
        os.fsync(current)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def capture_source(project_root, source_root=None):
    """Atomically publish immutable source bytes, or verify an identical snapshot.

    Existing corrupt snapshots are refused, never repaired in place. A capture
    creates no adoption record and never repins historical attempts.
    """
    temporary = None
    try:
        contents = _capture_bytes(source_root)
        identity = _identity(contents)
        descriptor = {**identity, "root": f"{SOURCE_BASE}/{identity['digest']}"}
        with _directory(project_root) as (project, _):
            with _directory(project / SOURCE_BASE, create=True) as (base, directory):
                if os.path.lexists(base / identity["digest"]):
                    verify_snapshot(project, descriptor)
                    return descriptor
                temporary = ".capture-" + uuid.uuid4().hex
                os.mkdir(temporary, mode=0o700, dir_fd=directory)
                temporary_fd = os.open(temporary, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                try:
                    for name, data in contents.items():
                        _write(temporary_fd, name, data)
                    _write(temporary_fd, "manifest.json", _encoded({"schema_version": 1, **identity}))
                    os.fsync(temporary_fd)
                finally:
                    os.close(temporary_fd)
                try:
                    os.rename(temporary, identity["digest"], src_dir_fd=directory, dst_dir_fd=directory)
                    temporary = None
                    os.fsync(directory)
                except OSError as exc:
                    if exc.errno not in {errno.EEXIST, errno.ENOTEMPTY}:
                        raise
                    # Another capture published the identical address first.
                    verify_snapshot(project, descriptor)
                finally:
                    if temporary is not None:
                        shutil.rmtree(temporary, dir_fd=directory)
                        temporary = None
                verify_snapshot(project, descriptor)
        return descriptor
    except OSError as exc:
        raise SourceError(f"Cannot capture simple source: {exc}") from exc
    finally:
        # Clean up only this invocation's unpublished private temporary tree.
        if temporary is not None:
            with _directory(Path(project_root) / SOURCE_BASE) as (_, directory):
                shutil.rmtree(temporary, dir_fd=directory)


def load_process_module(project_root, descriptor):
    """Load the verified pinned worker without adding bytecode to its snapshot."""
    root = verify_snapshot(project_root, descriptor)
    path = root / "scripts/_simple_process.py"
    with _directory(root) as (_, directory):
        raw = _read(directory, "scripts/_simple_process.py")
    expected = next(item["sha256"] for item in descriptor["files"] if item["path"] == "scripts/_simple_process.py")
    if hashlib.sha256(raw).hexdigest() != expected:
        raise SourceError("Pinned process helper changed before loading")
    name = "_rsi_simple_process_" + hashlib.sha256(str(path).encode()).hexdigest()
    with _MODULE_LOCK:
        if name not in sys.modules:
            module = types.ModuleType(name)
            module.__file__ = str(path)
            module.__package__ = ""
            exec(compile(raw, str(path), "exec"), module.__dict__)
            sys.modules[name] = module
        return sys.modules[name]
