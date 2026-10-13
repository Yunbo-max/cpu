#!/usr/bin/env python3
"""Detached, bounded Linux command attempts for the simple runner.

An irreversible launch marker precedes Popen. If this worker disappears after
that marker, neither a missing receipt nor an expired process authorizes replay.
This is process supervision, not scientific validation or a command sandbox.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time

_CHILDREN = {}
_GRACE_SECONDS = 0.6


class ProcessError(ValueError):
    """Invalid or unverifiable attempt state."""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _process_stat(pid):
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
        fields = raw[raw.rfind(")") + 2:].split()
        return {"state": fields[0], "pgrp": int(fields[2]), "session": int(fields[3]),
                "start_ticks": int(fields[19])}
    except (OSError, ValueError, IndexError):
        return None


def _namespace_fields(pid):
    try:
        rows = Path(f"/proc/{pid}/status").read_text().splitlines()
        return {row.split(":", 1)[0]: [int(value) for value in row.split(":", 1)[1].split()]
                for row in rows if row.startswith(("NSpid:", "NSpgid:"))}
    except (OSError, ValueError):
        return {}


def _same_pid_namespace(pid):
    try:
        return os.stat(f"/proc/{pid}/ns/pid").st_ino == os.stat("/proc/self/ns/pid").st_ino
    except OSError:
        return False


def _local_pid(visible_pid):
    """Translate a /proc-visible PID for signalling in this PID namespace."""
    fields = _namespace_fields(visible_pid)
    if not _same_pid_namespace(visible_pid) or not fields.get("NSpid"):
        raise ProcessError("Process is not signal-addressable in the current PID namespace")
    return fields["NSpid"][-1]


def _visible_pid(local_pid):
    own_visible = int(Path("/proc/self/stat").read_text().split()[0])
    if local_pid == os.getpid():
        return own_visible
    if own_visible == os.getpid():
        return local_pid
    for item in Path("/proc").iterdir():
        if item.name.isdecimal():
            values = _namespace_fields(int(item.name)).get("NSpid", [])
            if values and values[-1] == local_pid and _same_pid_namespace(int(item.name)):
                return int(item.name)
    return None


def _visible_identity(pid):
    if type(pid) is not int or pid < 1:
        return None
    information = _process_stat(pid)
    if information is None:
        return None
    try:
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return None
    return {"pid": pid, "start_ticks": information["start_ticks"], "boot_id": boot_id}


def process_identity(pid=None):
    """Map a caller-local PID to durable /proc-visible PID/start ticks/boot ID.

    /proc can be mounted from an outer namespace (including Work sandboxes), so
    returned pid is intentionally not assumed equal to os.getpid()/Popen.pid.
    """
    pid = os.getpid() if pid is None else pid
    if type(pid) is not int or pid < 1:
        return None
    return _visible_identity(_visible_pid(pid))


def identity_alive(identity):
    """Reject recycled PIDs, previous boots, and exited/zombie processes."""
    if not isinstance(identity, dict) or _visible_identity(identity.get("pid")) != identity:
        return False
    information = _process_stat(identity["pid"])
    return information is not None and information["state"] not in {"Z", "X", "x"}


def atomic_json(path, obj):
    """Durably replace JSON using a same-directory rename and directory fsync."""
    path = Path(path)
    data = (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".write-", delete=False) as output:
            temporary = output.name
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            os.unlink(temporary)


def _bound_paths(root, attempt_dir):
    root = Path(root).expanduser().resolve(strict=True)
    directory = Path(attempt_dir)
    if not directory.is_absolute():
        raise ProcessError("Attempt directory must be absolute")
    expected = root / ".research-autopilot" / "runner" / "attempts" / directory.name
    if directory != expected or directory.resolve(strict=True) != expected:
        raise ProcessError("Attempt directory is not the bound project attempt path")
    if not root.is_dir() or not directory.is_dir():
        raise ProcessError("Project root and attempt directory must exist")
    for path in (directory, *directory.relative_to(root).parents):
        # Resolved equality above excludes symlink redirection; explicitly reject
        # even links whose final target happens to have the same spelling.
        candidate = path if path.is_absolute() else root / path
        if candidate.is_symlink():
            raise ProcessError("Attempt state may not use symlinks")
    return root, directory


def _relative(value, allow_dot=False):
    if allow_dot and value == ".":
        return value
    if (not isinstance(value, str) or not value or value.startswith("/") or "\\" in value
            or "\x00" in value or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ProcessError("Paths must be safe project-relative paths")
    return value


def _read_json(path):
    if path.is_symlink():
        raise ProcessError(f"State file may not be a symlink: {path.name}")
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ProcessError(f"Cannot read {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProcessError(f"{path.name} must be an object")
    return value


def _contract(root, directory, expected_sha256=None):
    path = directory / "attempt.json"
    if path.is_symlink():
        raise ProcessError("Attempt contract may not be a symlink")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ProcessError("Attempt contract hash changed")
    try:
        contract = json.loads(raw)
    except ValueError as exc:
        raise ProcessError("Attempt contract is not valid JSON") from exc
    if not isinstance(contract, dict) or contract.get("schema_version") != 1:
        raise ProcessError("Unsupported attempt contract")
    if contract.get("root") != str(root) or contract.get("attempt_id") != directory.name:
        raise ProcessError("Attempt contract project or attempt identity mismatch")
    if not isinstance(contract.get("task_id"), str) or not contract["task_id"].strip():
        raise ProcessError("Attempt requires task_id")
    if contract.get("kind") not in {"task", "agent"}:
        raise ProcessError("Attempt kind must be task or agent")
    argv = contract.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or "\x00" in arg for arg in argv) or not argv[0]:
        raise ProcessError("Attempt argv must be a nonempty string array")
    _relative(contract.get("cwd"), allow_dot=True)
    for field in ("timeout_seconds", "deadline_epoch"):
        value = contract.get(field)
        if type(value) not in {int, float} or not math.isfinite(value) or value <= 0:
            raise ProcessError(f"{field} must be finite and positive")
    inputs, outputs = contract.get("input_refs"), contract.get("outputs")
    if not isinstance(inputs, list) or not isinstance(outputs, list):
        raise ProcessError("Attempt input_refs and outputs must be arrays")
    for ref in inputs:
        if (not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
                or not isinstance(ref["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"])):
            raise ProcessError("Pinned inputs require path and lowercase SHA256")
        _relative(ref["path"])
    for name in outputs:
        _relative(name)
    if len(set(outputs)) != len(outputs) or len({ref["path"] for ref in inputs}) != len(inputs):
        raise ProcessError("Duplicate input or output paths")
    return contract, digest


def _file_ref(root, name):
    """Hash a regular file through no-follow directory descriptors."""
    _relative(name)
    descriptors = []
    try:
        descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(descriptor)
        parts = name.split("/")
        for part in parts[:-1]:
            descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            descriptors.append(descriptor)
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ProcessError(f"Not a regular file: {name}")
        digest = hashlib.sha256()
        while block := os.read(descriptor, 1024 * 1024):
            digest.update(block)
        after = os.fstat(descriptor)
        signature = lambda information: (information.st_dev, information.st_ino, information.st_size,
                                          information.st_mtime_ns, information.st_ctime_ns)
        if signature(before) != signature(after):
            raise ProcessError(f"File changed while hashing: {name}")
        return {"path": name, "sha256": digest.hexdigest()}, signature(after)
    except OSError as exc:
        raise ProcessError(f"Cannot safely read {name}: {exc}") from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _verify_inputs(root, refs):
    for ref in refs:
        actual, _ = _file_ref(root, ref["path"])
        if actual != ref:
            raise ProcessError(f"Pinned input hash changed: {ref['path']}")


def _group_members(identity, known_members=()):
    if not isinstance(identity, dict):
        return []
    pid = identity.get("pid")
    leader = _visible_identity(pid)
    if leader is not None and leader != identity:
        return []
    if leader != identity and not any(identity_alive(member) for member in known_members):
        return []
    members = []
    for item in Path("/proc").iterdir():
        if not item.name.isdecimal():
            continue
        member_pid = int(item.name)
        information = _process_stat(member_pid)
        if (information is not None and information["pgrp"] == pid and information["session"] == pid
                and information["state"] not in {"Z", "X", "x"}
                and information["start_ticks"] >= identity["start_ticks"]):
            member = _visible_identity(member_pid)
            if member is not None and member["boot_id"] == identity["boot_id"]:
                members.append(member)
    return members


def _terminate_group(identity, known_members=()):
    """Bound the identified session's group, including surviving grandchildren."""
    members = _group_members(identity, known_members)
    if not members:
        return []
    for number in (signal.SIGTERM, signal.SIGKILL):
        # Revalidate identities immediately before signalling the process group.
        members = _group_members(identity, members)
        if not members:
            return []
        try:
            representative = members[0]["pid"]
            if not _same_pid_namespace(representative):
                return members
            groups = _namespace_fields(representative).get("NSpgid", [])
            if not groups:
                return members
            os.killpg(groups[-1], number)
        except ProcessLookupError:
            return []
        deadline = time.monotonic() + _GRACE_SECONDS
        while time.monotonic() < deadline:
            members = _group_members(identity, members)
            if not members:
                return []
            time.sleep(.025)
    return _group_members(identity, members)


def _reap_workers():
    for pid, child in list(_CHILDREN.items()):
        if child.poll() is not None:
            del _CHILDREN[pid]


def _cleanup_owned_child(child, identity, members):
    """Clean up after ordinary worker errors even if /proc itself is failing.

    This fallback is restricted to this worker's unreaped Popen child. Keeping
    the child unreaped fences its local PID/process-group ID against reuse; it
    must never be applied to an identity recovered from another process.
    """
    if child.returncode is not None:
        return
    try:
        identity = identity or process_identity(child.pid)
        if identity is None:
            raise ProcessError("Command identity unavailable during cleanup")
        if _terminate_group(identity, members):
            raise ProcessError("Command group could not be inspected or bounded")
        child.wait(timeout=_GRACE_SECONDS)
        return
    except Exception:
        if child.returncode is not None:
            return
    # Do not call poll()/wait() between these signals: reaping the leader would
    # release the PID fence while descendants might still need termination.
    for number, grace in ((signal.SIGTERM, _GRACE_SECONDS), (signal.SIGKILL, .05)):
        try:
            os.killpg(child.pid, number)
        except ProcessLookupError:
            break
        time.sleep(grace)
    try:
        child.wait(timeout=_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        pass  # The retained launch marker still requires honest reconciliation.


def inspect_attempt(root, attempt_dir):
    """Observe files and exact process identities; never infer permission to replay."""
    _reap_workers()
    try:
        root, directory = _bound_paths(root, attempt_dir)
        contract, digest = _contract(root, directory)
        if (directory / "receipt.json").exists():
            receipt = _read_json(directory / "receipt.json")
            if (receipt.get("root") != str(root) or receipt.get("attempt_id") != directory.name
                    or receipt.get("task_id") != contract["task_id"] or receipt.get("contract_sha256") != digest):
                raise ProcessError("Receipt identity does not match the current immutable contract")
            return {"state": "completed", "reason": "Terminal worker receipt is present", "receipt": receipt}
        worker = _read_json(directory / "worker.json") if (directory / "worker.json").exists() else {}
        if identity_alive(worker.get("identity")):
            return {"state": "running", "reason": "The same detached worker is alive"}
        if (directory / "launch.json").exists():
            return {"state": "reconcile_required", "reason": "Irreversible launch marker exists but its worker is no longer alive; do not relaunch"}
        return {"state": "absent", "reason": "No command launch marker or live worker; the same wrapper may be dispatched"}
    except (OSError, ValueError) as exc:
        return {"state": "reconcile_required", "reason": str(exc)}


def launch_worker(root, attempt_dir, expected_sha256):
    """Detach one wrapper. Duplicate wrappers serialize on its durable attempt lock."""
    root, directory = _bound_paths(root, attempt_dir)
    _contract(root, directory, expected_sha256)
    observation = inspect_attempt(root, directory)
    if observation["state"] in {"completed", "reconcile_required"}:
        return None
    if observation["state"] == "running":
        return _read_json(directory / "worker.json")["identity"]
    log_descriptor = os.open(directory / "worker-stderr.txt", os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "worker", "--root", str(root),
                                  "--attempt-dir", str(directory), "--contract-sha256", expected_sha256],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=log_descriptor,
                                 start_new_session=True, close_fds=True)
    finally:
        os.close(log_descriptor)
    _CHILDREN[child.pid] = child
    return process_identity(child.pid)


def cancel_attempt(root, attempt_dir, reason):
    """Request cancellation; orphan cleanup is best effort and never forges a receipt."""
    root, directory = _bound_paths(root, attempt_dir)
    if not isinstance(reason, str) or not reason.strip():
        raise ProcessError("Cancellation requires an explicit reason")
    observation = inspect_attempt(root, directory)
    if observation["state"] == "completed":
        return observation
    atomic_json(directory / "cancel.json", {"schema_version": 1, "root": str(root),
                "attempt_id": directory.name, "reason": reason, "requested_at": _now()})
    if observation["state"] == "reconcile_required" and (directory / "command.json").exists():
        command = _read_json(directory / "command.json")
        _terminate_group(command.get("identity"), command.get("members", []))
    return inspect_attempt(root, directory)


def _working_directory(root, relative):
    path = root
    if relative != ".":
        for part in relative.split("/"):
            path = path / part
            if path.is_symlink() or not path.is_dir():
                raise ProcessError("Working directory must be a real project directory")
    return path


def _worker(root, attempt_dir, expected_sha256):
    root, directory = _bound_paths(root, attempt_dir)
    lock = os.open(directory / "worker.lock", os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        if (directory / "receipt.json").exists() or (directory / "launch.json").exists():
            return 0
        contract, digest = _contract(root, directory, expected_sha256)
        worker_identity = process_identity()
        atomic_json(directory / "worker.json", {"identity": worker_identity, "contract_sha256": digest})
        started_at, start = _now(), time.monotonic()
        status, error, exit_code = None, None, None
        command_identity, child, members = None, None, []
        output_refs, previous_outputs = [], {}
        log_handles = []
        try:
            for name in ("stdout.txt", "stderr.txt"):
                descriptor = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
                log_handles.append(os.fdopen(descriptor, "wb", buffering=0))
            try:
                _verify_inputs(root, contract["input_refs"])
                working_directory = _working_directory(root, contract["cwd"])
            except (OSError, ValueError) as exc:
                status, error = "invalid_inputs", str(exc)
            for name in contract["outputs"]:
                try:
                    _, previous_outputs[name] = _file_ref(root, name)
                except (OSError, ValueError):
                    previous_outputs[name] = None
            if status is None and (directory / "cancel.json").exists():
                status, error = "cancelled", "Cancellation was requested before launch"
            if status is None and time.time() >= contract["deadline_epoch"]:
                status, error = "timed_out", "Persisted attempt deadline expired before command launch"
            if status is None:
                # The marker is durable before the side effect. An ambiguous
                # failure after this point must never authorize another Popen.
                atomic_json(directory / "launch.json", {"schema_version": 1, "root": str(root),
                    "attempt_id": directory.name, "task_id": contract["task_id"], "contract_sha256": digest,
                    "worker_identity": worker_identity, "marked_at": _now()})
                try:
                    child = subprocess.Popen(contract["argv"], cwd=working_directory, stdin=subprocess.DEVNULL,
                        stdout=log_handles[0], stderr=log_handles[1], start_new_session=True, close_fds=True)
                except OSError as exc:
                    status, error = "launch_failed", f"Command Popen failed: {exc}"
                if child is not None:
                    command_identity = process_identity(child.pid)
                    if command_identity is None:
                        raise ProcessError("Cannot establish the launched command's Linux identity")
                    atomic_json(directory / "command.json", {"identity": command_identity, "members": [command_identity]})
                    previous_members = None
                    while True:
                        members = _group_members(command_identity, members)
                        member_ids = {(member["pid"], member["start_ticks"]) for member in members}
                        if member_ids != previous_members:
                            atomic_json(directory / "command.json", {"identity": command_identity, "members": members})
                            previous_members = member_ids
                        # Keep an exited leader unreaped until group cleanup, so
                        # its identity still fences its surviving descendants.
                        exited = os.waitid(os.P_PID, child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
                        if (directory / "cancel.json").exists():
                            status, error = "cancelled", "Cancellation requested while command was active"
                            break
                        if time.monotonic() - start >= contract["timeout_seconds"] or time.time() >= contract["deadline_epoch"]:
                            status, error = "timed_out", "Command exceeded its attempt timeout or persisted deadline"
                            break
                        if exited is not None:
                            break
                        time.sleep(.025)
                    remaining = _terminate_group(command_identity, members)
                    if remaining:
                        raise ProcessError("Controlled command group remains alive after TERM/KILL; reconciliation required")
                    exit_code = child.wait(timeout=_GRACE_SECONDS)
                    if status is None:
                        status = "succeeded" if exit_code == 0 else "failed"
                        if exit_code != 0:
                            error = f"Command exited with status {exit_code}"
            if child is not None:
                try:
                    _verify_inputs(root, contract["input_refs"])
                except (OSError, ValueError) as exc:
                    error = f"{error + '; ' if error else ''}{exc}"
                    if status == "succeeded":
                        status = "invalid_inputs"
                for name in contract["outputs"]:
                    try:
                        ref, signature = _file_ref(root, name)
                        if signature == previous_outputs[name]:
                            raise ProcessError(f"Declared output was not produced or changed by this attempt: {name}")
                        output_refs.append(ref)
                    except (OSError, ValueError) as exc:
                        error = f"{error + '; ' if error else ''}{exc}"
                        if status == "succeeded":
                            status = "invalid_outputs"
        except BaseException:
            # Ordinary persistence/inspection errors must not abandon an active
            # command. Hard worker death is handled conservatively by inspect.
            if child is not None:
                _cleanup_owned_child(child, command_identity, members)
            raise
        finally:
            for handle in log_handles:
                handle.flush()
                os.fsync(handle.fileno())
                handle.close()
        stdout_ref, _ = _file_ref(root, (directory / "stdout.txt").relative_to(root).as_posix())
        stderr_ref, _ = _file_ref(root, (directory / "stderr.txt").relative_to(root).as_posix())
        receipt = {"schema_version": 1, "root": str(root), "attempt_id": directory.name,
            "task_id": contract["task_id"], "contract_sha256": digest, "status": status,
            "exit_code": exit_code, "started_at": started_at, "finished_at": _now(),
            "elapsed_seconds": time.monotonic() - start, "worker_identity": worker_identity,
            "command_identity": command_identity, "stdout_ref": stdout_ref, "stderr_ref": stderr_ref,
            "output_refs": output_refs, "input_refs": contract["input_refs"], "error": error}
        atomic_json(directory / "receipt.json", receipt)
        return 0
    finally:
        os.close(lock)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["worker"])
    parser.add_argument("--root", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        return _worker(args.root, args.attempt_dir, args.contract_sha256)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "attempt_dir": args.attempt_dir}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
