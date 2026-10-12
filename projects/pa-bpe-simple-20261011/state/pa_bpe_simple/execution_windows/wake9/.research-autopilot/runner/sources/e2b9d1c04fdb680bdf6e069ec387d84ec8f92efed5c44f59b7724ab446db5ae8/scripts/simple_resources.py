#!/usr/bin/env python3
"""Observe local CPU/RAM/NVIDIA resources; never authorize, lease or run work.

Linux procfs/cgroup data and nvidia-smi are best-effort observations. Unknown
values remain null. Visible hardware, instantaneous headroom and CUDA visibility
are not a user's allocation. State that allocation separately in the experiment
plan, then measure the workload with an authorized bounded pilot.
"""
import argparse
import csv
from datetime import datetime, timezone
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import socket
import subprocess
import tempfile
import time

DEFAULT_TIMEOUT_SECONDS = 3.0
MAX_TIMEOUT_SECONDS = 60.0
NVIDIA_QUERY = "index,uuid,name,memory.total,memory.free,utilization.gpu"
UNKNOWN_FIELDS = {"", "n/a", "[n/a]", "not supported", "[not supported]", "unknown"}


def _diagnostic(component, kind, message, **details):
    return {"component": component, "kind": kind, "message": message, **details}


def _read_text(path, diagnostics, optional=False):
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as handle:
            value = handle.read(1024 * 1024 + 1)
        if len(value) > 1024 * 1024:
            diagnostics.append(_diagnostic("cpu_memory", "source_too_large",
                "Resource source exceeded the bounded read size", source=str(path)))
            return None
        return value.strip()
    except OSError as error:
        if not optional or not isinstance(error, FileNotFoundError):
            diagnostics.append(_diagnostic("cpu_memory", "source_unavailable",
                error.strerror or type(error).__name__, source=str(path), errno=error.errno))
        return None


def parse_cpu_list(value):
    """Expand a kernel CPU list, refusing malformed or excessive ranges."""
    result = set()
    if not value.strip():
        return []
    for item in value.strip().split(","):
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", item.strip())
        if not match:
            raise ValueError("Invalid CPU list")
        first = int(match[1])
        last = int(match[2]) if match[2] is not None else first
        if last < first or last > 1048575 or last - first + len(result) >= 65536:
            raise ValueError("Invalid or excessively large CPU range")
        result.update(range(first, last + 1))
    return sorted(result)


def _unescape_mount(value):
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value)


def _cgroup_locations(proc_root, diagnostics):
    membership = _read_text(proc_root / "self/cgroup", diagnostics)
    mountinfo = _read_text(proc_root / "self/mountinfo", diagnostics)
    if membership is None or mountinfo is None:
        return [], False
    members = {}
    for line in membership.splitlines():
        fields = line.split(":", 2)
        if len(fields) == 3:
            for controller in fields[1].split(","):
                members[controller] = fields[2]
    locations, complete = [], True
    for line in mountinfo.splitlines():
        fields = line.split()
        try:
            separator = fields.index("-")
            filesystem = fields[separator + 1]
            if filesystem not in {"cgroup", "cgroup2"}:
                continue
            mount_root = PurePosixPath(_unescape_mount(fields[3]))
            mount_point = Path(_unescape_mount(fields[4]))
            controllers = set(fields[separator + 3].split(","))
            controllers.update(fields[separator + 2].split(","))
        except (ValueError, IndexError):
            complete = False
            continue
        if filesystem == "cgroup2":
            relevant = {"cpu", "memory", "cpuset"}
            member = members.get("")
            version = 2
        else:
            relevant = controllers & {"cpu", "memory", "cpuset"}
            member = next((members[name] for name in sorted(relevant) if name in members), None)
            version = 1
        if not relevant:
            continue
        try:
            if member is None or not mount_point.is_absolute() or not mount_root.is_absolute():
                raise ValueError("Missing cgroup membership")
            member_path = PurePosixPath(member)
            if not member_path.is_absolute() or ".." in member_path.parts or ".." in mount_root.parts:
                raise ValueError("Cgroup path cannot be safely mapped")
            relative = member_path.relative_to(mount_root)
            directory = mount_point.joinpath(*relative.parts)
        except ValueError:
            complete = False
            diagnostics.append(_diagnostic("cgroup", "unmapped_cgroup",
                "Membership could not be mapped to the visible mount; its constraints remain unknown",
                source=str(proc_root / "self/cgroup"), mount_point=str(mount_point)))
            continue
        locations.append({"version": version, "controllers": relevant,
                          "directory": directory, "mount_point": mount_point})
    if not locations:
        complete = False
        diagnostics.append(_diagnostic("cgroup", "unknown",
            "No mapped CPU/memory cgroup hierarchy was identified",
            source=str(proc_root / "self/mountinfo")))
    return locations, complete


def _visible_ancestors(directory, mount_point):
    """Only visit the mapped membership and its visible mounted ancestors."""
    while True:
        yield directory
        if directory == mount_point:
            break
        directory = directory.parent


def _cpu_observation(directory, version, controllers, diagnostics):
    result = {"version": version, "path": str(directory), "sources": [],
              "quota_us": None, "period_us": None, "quota_count": None,
              "quota_state": "unknown", "cpuset_ids": None}
    if "cpu" in controllers:
        paths = ([directory / "cpu.max"] if version == 2 else
                 [directory / "cpu.cfs_quota_us", directory / "cpu.cfs_period_us"])
        result["sources"].extend(str(path) for path in paths)
        texts = [_read_text(path, diagnostics, optional=True) for path in paths]
        try:
            if all(text is not None for text in texts):
                quota_text, period_text = texts[0].split() if version == 2 else texts
                period = int(period_text)
                unlimited = quota_text == "max" if version == 2 else quota_text == "-1"
                quota = None if unlimited else int(quota_text)
                if period <= 0 or (quota is not None and quota <= 0):
                    raise ValueError("CPU quota/period must be positive")
                result.update(quota_us=quota, period_us=period,
                              quota_count=None if unlimited else quota / period,
                              quota_state="unlimited" if unlimited else "observed")
        except (ValueError, OverflowError):
            diagnostics.append(_diagnostic("cpu.cgroup", "invalid_cpu_quota",
                "CPU quota or period could not be interpreted", sources=result["sources"].copy()))
    if "cpuset" in controllers:
        names = ["cpuset.cpus.effective"] if version == 2 else ["cpuset.effective_cpus", "cpuset.cpus"]
        for name in names:
            path = directory / name
            text = _read_text(path, diagnostics, optional=True)
            if text:
                result["sources"].append(str(path))
                try:
                    result["cpuset_ids"] = parse_cpu_list(text)
                except ValueError:
                    diagnostics.append(_diagnostic("cpu.cgroup", "invalid_cpuset",
                        "CPU set could not be interpreted", source=str(path)))
                break
    return result


def _memory_observation(directory, version, diagnostics):
    limit_path = directory / ("memory.max" if version == 2 else "memory.limit_in_bytes")
    current_path = directory / ("memory.current" if version == 2 else "memory.usage_in_bytes")
    limit_text = _read_text(limit_path, diagnostics, optional=True)
    current_text = _read_text(current_path, diagnostics, optional=True)
    result = {"version": version, "path": str(directory), "limit_bytes": None,
              "current_bytes": None, "headroom_bytes": None, "limit_state": "unknown",
              "raw_limit": limit_text, "sources": [str(limit_path), str(current_path)]}
    try:
        if limit_text is not None:
            if limit_text == "max" and version == 2:
                result["limit_state"] = "unlimited"
            else:
                limit = int(limit_text)
                if limit < 0:
                    raise ValueError("Negative memory limit")
                # v1 PAGE_COUNTER_MAX appears as a huge integer, not real RAM.
                if version == 1 and limit >= 2**60:
                    result["limit_state"] = "unlimited_or_kernel_sentinel"
                else:
                    result.update(limit_bytes=limit, limit_state="observed")
        if current_text is not None:
            current = int(current_text)
            if current < 0:
                raise ValueError("Negative memory usage")
            result["current_bytes"] = current
        if result["limit_bytes"] is not None and result["current_bytes"] is not None:
            result["headroom_bytes"] = max(0, result["limit_bytes"] - result["current_bytes"])
    except ValueError:
        diagnostics.append(_diagnostic("memory.cgroup", "invalid_memory_value",
            "Memory limit or usage could not be interpreted", sources=result["sources"]))
    return result


def _minimum(values):
    known = [value for value in values if value is not None]
    return min(known) if known else None


def collect_cpu_memory(proc_root=Path("/proc")):
    """Return CPU, memory and diagnostics from the local visible Linux sources."""
    proc_root = Path(proc_root)
    diagnostics = []
    logical_count = os.cpu_count()
    affinity = {"status": "unknown", "ids": None, "count": None, "source": "os.sched_getaffinity(0)"}
    try:
        ids = sorted(os.sched_getaffinity(0))
        affinity.update(status="observed", ids=ids, count=len(ids))
    except (AttributeError, OSError) as error:
        diagnostics.append(_diagnostic("cpu.affinity", "unknown", type(error).__name__, source=affinity["source"]))

    locations, complete = _cgroup_locations(proc_root, diagnostics)
    cpu_observations, memory_observations, visited = [], [], set()
    for location in locations:
        for directory in _visible_ancestors(location["directory"], location["mount_point"]):
            key = (str(directory), location["version"], tuple(sorted(location["controllers"])))
            if key in visited:
                continue
            visited.add(key)
            if location["controllers"] & {"cpu", "cpuset"}:
                cpu_observations.append(_cpu_observation(directory, location["version"],
                                                        location["controllers"], diagnostics))
            if "memory" in location["controllers"]:
                memory_observations.append(_memory_observation(directory, location["version"], diagnostics))
    quota_count = _minimum(item["quota_count"] for item in cpu_observations)
    cpusets = [set(item["cpuset_ids"]) for item in cpu_observations if item["cpuset_ids"] is not None]
    cpuset_ids = sorted(set.intersection(*cpusets)) if cpusets else None
    affinity_cpuset_count = None
    if cpuset_ids is not None:
        affinity_cpuset_count = len(set(cpuset_ids) & set(affinity["ids"])) if affinity["ids"] is not None else len(cpuset_ids)
    cpu = {
        "logical_count": logical_count,
        "affinity": affinity,
        "cgroup": {"cpu_quota_count_upper_bound": quota_count, "cpuset_ids": cpuset_ids,
                   "observations": cpu_observations, "hierarchy_complete": complete,
                   "scope": "Mapped membership through visible mount roots; hidden ancestors may impose tighter limits"},
        "capacity_upper_bound": _minimum([logical_count, affinity["count"], quota_count, affinity_cpuset_count]),
        "sources": {"logical_count": "os.cpu_count()",
                    "capacity_upper_bound": "Minimum of known logical count, affinity, intersected cpusets and ancestor quota/period"},
        "note": "An observed upper bound, not dedicated cores, current idle capacity or authorization; unknown constraints may lower it",
    }

    meminfo_path = proc_root / "meminfo"
    meminfo = _read_text(meminfo_path, diagnostics)
    physical, available = None, None
    if meminfo is not None:
        values = dict(re.findall(r"^(MemTotal|MemAvailable):\s+(\d+)\s+kB\s*$", meminfo, flags=re.MULTILINE))
        physical = int(values["MemTotal"]) * 1024 if "MemTotal" in values else None
        available = int(values["MemAvailable"]) * 1024 if "MemAvailable" in values else None
    physical_source = str(meminfo_path) + ":MemTotal"
    if physical is None:
        try:
            pages, page_size = os.sysconf("SC_PHYS_PAGES"), os.sysconf("SC_PAGE_SIZE")
            if pages > 0 and page_size > 0:
                physical = pages * page_size
                physical_source = "os.sysconf(SC_PHYS_PAGES) * os.sysconf(SC_PAGE_SIZE)"
        except (AttributeError, ValueError, OSError):
            pass
    limit = _minimum(item["limit_bytes"] for item in memory_observations)
    headroom = _minimum(item["headroom_bytes"] for item in memory_observations)
    memory = {
        "mem_total_bytes": physical, "mem_available_bytes": available,
        "cgroup_limit_bytes": limit, "cgroup_headroom_bytes": headroom,
        "effective_total_bytes_upper_bound": _minimum([physical, limit]),
        "observed_headroom_bytes": _minimum([available, headroom]),
        "cgroup_observations": memory_observations,
        "sources": {"mem_total_bytes": physical_source,
                    "mem_available_bytes": str(meminfo_path) + ":MemAvailable",
                    "cgroup_limit_bytes": "Minimum known limit in cgroup_observations",
                    "cgroup_headroom_bytes": "Minimum max(0, limit-current) in cgroup_observations",
                    "effective_total_bytes_upper_bound": "Minimum known MemTotal and cgroup limit",
                    "observed_headroom_bytes": "Minimum known MemAvailable and current cgroup headroom"},
        "note": "MemTotal may describe host RAM; cgroup headroom is instantaneous and shared, excludes future reclaim, and is not reserved memory",
    }
    return cpu, memory, diagnostics


def _metric(value, name, row_number, diagnostics, maximum=None):
    value = value.strip()
    try:
        if value.lower() in UNKNOWN_FIELDS:
            raise ValueError("Unavailable metric")
        number = float(value)
        if not math.isfinite(number) or number < 0 or (maximum is not None and number > maximum):
            raise ValueError("Invalid metric")
        return int(number) if number.is_integer() else number
    except ValueError:
        diagnostics.append(_diagnostic("nvidia_gpus", "metric_unknown",
            "Metric unavailable or outside its expected range", row=row_number, field=name))
        return None


def parse_nvidia_csv(output):
    """Parse only the requested inventory fields; do not infer CUDA device IDs."""
    devices, diagnostics = [], []
    seen = set()
    try:
        rows = csv.reader(io.StringIO(output), skipinitialspace=True, strict=True)
        for number, row in enumerate(rows, 1):
            if not row or not any(field.strip() for field in row):
                continue
            try:
                if len(row) != 6:
                    raise ValueError("Unexpected field count")
                index = int(row[0])
                if index < 0 or index in seen:
                    raise ValueError("Invalid or duplicate device index")
            except ValueError:
                diagnostics.append(_diagnostic("nvidia_gpus", "invalid_inventory_row",
                    "Inventory row was not a unique six-field GPU record", row=number))
                continue
            seen.add(index)
            uuid, model = row[1].strip(), row[2].strip()
            if uuid.lower() in UNKNOWN_FIELDS or model.lower() in UNKNOWN_FIELDS:
                diagnostics.append(_diagnostic("nvidia_gpus", "identity_partial",
                    "GPU UUID or model was unavailable", row=number))
            total = _metric(row[3], "memory_total_mib", number, diagnostics)
            free = _metric(row[4], "memory_free_mib", number, diagnostics, maximum=total)
            utilization = _metric(row[5], "utilization_gpu_percent", number, diagnostics, maximum=100)
            devices.append({"index": index, "uuid": None if uuid.lower() in UNKNOWN_FIELDS else uuid,
                            "model": None if model.lower() in UNKNOWN_FIELDS else model,
                            "memory_total_mib": total, "memory_free_mib": free,
                            "utilization_gpu_percent": utilization})
    except csv.Error:
        diagnostics.append(_diagnostic("nvidia_gpus", "invalid_csv", "Inventory was not valid CSV"))
    if not devices:
        diagnostics.append(_diagnostic("nvidia_gpus", "unknown_inventory",
            "No interpretable device record; this does not establish that the host has zero GPUs"))
    return {"status": "unknown" if not devices else "partial" if diagnostics else "observed",
            "devices": devices or None, "diagnostics": diagnostics}


def _timeout(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("timeout_seconds must be a finite positive number") from None
    if not math.isfinite(number) or not 0 < number <= MAX_TIMEOUT_SECONDS:
        raise ValueError(f"timeout_seconds must be greater than 0 and at most {MAX_TIMEOUT_SECONDS:g}")
    return number


def probe_nvidia(timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    """A bounded, read-only local inventory query; failure leaves GPUs unknown."""
    timeout_seconds = _timeout(timeout_seconds)
    raw_visibility = os.environ.get("CUDA_VISIBLE_DEVICES")
    result = {"status": "unknown", "devices": None,
              "source": {"tool": "nvidia-smi", "query": NVIDIA_QUERY, "timeout_seconds": timeout_seconds},
              "visibility": {"cuda_visible_devices_raw": raw_visibility, "mapping_status": "unknown",
                             "reason": "CUDA_VISIBLE_DEVICES expresses visibility, not authorization; nvidia-smi indices are not confirmed CUDA ordinals. CUDA/MIG runtime mapping is not probed"},
              "diagnostics": []}
    executable = shutil.which("nvidia-smi")
    if executable is None:
        result["diagnostics"].append(_diagnostic("nvidia_gpus", "missing_tool",
            "nvidia-smi was not found; GPU inventory remains unknown and CPU work can continue"))
        return result
    result["source"]["executable"] = executable
    argv = [executable, "--query-gpu=" + NVIDIA_QUERY, "--format=csv,noheader,nounits"]
    started = time.monotonic()
    try:
        command = subprocess.run(argv, capture_output=True, text=True, errors="replace",
                                 timeout=timeout_seconds, check=False)
        if command.returncode:
            # Never dump arbitrary command output or the inherited environment.
            # Keep the failure identity plus a recognized driver diagnostic.
            stderr = command.stderr.lower()
            detail = ("NVML initialization/query failure" if "nvml" in stderr else
                      "Driver communication failure" if "driver" in stderr else
                      "Permission denied" if "permission" in stderr else
                      "nvidia-smi query failed")
            result["diagnostics"].append(_diagnostic("nvidia_gpus", "command_failed", detail,
                returncode=command.returncode, stderr_present=bool(command.stderr)))
        else:
            result.update(parse_nvidia_csv(command.stdout))
    except subprocess.TimeoutExpired:
        result["diagnostics"].append(_diagnostic("nvidia_gpus", "timeout",
            "nvidia-smi exceeded its timeout; GPU inventory remains unknown", timeout_seconds=timeout_seconds))
    except OSError as error:
        result["diagnostics"].append(_diagnostic("nvidia_gpus", "tool_unavailable",
            error.strerror or type(error).__name__, errno=error.errno))
    result["source"]["query_elapsed_seconds"] = time.monotonic() - started
    return result


def collect_resources(timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    """Create one timestamped local snapshot, with no credential or remote reads."""
    timeout_seconds = _timeout(timeout_seconds)
    collected_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    cpu, memory, diagnostics = collect_cpu_memory()
    return {
        "schema_version": 1, "collected_at_utc": collected_at,
        "host": {"hostname": socket.gethostname(), "system": platform.system(), "machine": platform.machine()},
        "scope": {"local_only": True, "authorizes_execution": False, "reserves_resources": False,
                  "resource_lease": False,
                  "note": "Observation only; declare the user's allocation separately and measure an authorized workload pilot. No research task is launched"},
        "cpu": cpu, "memory": memory, "nvidia_gpus": probe_nvidia(timeout_seconds),
        "diagnostics": diagnostics,
    }


def write_snapshot(output, snapshot):
    """Atomically replace a JSON file; a failed write preserves its predecessor."""
    payload = json.dumps(snapshot, indent=2, sort_keys=True, allow_nan=False) + "\n"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="." + output.name + ".", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
        try:
            directory = os.open(output.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Atomically write the local JSON observation here")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS,
                        help="nvidia-smi timeout in seconds (default: 3, maximum: 60)")
    args = parser.parse_args(argv)
    try:
        timeout_seconds = _timeout(args.timeout_seconds)
        snapshot = collect_resources(timeout_seconds=timeout_seconds)
        write_snapshot(args.output, snapshot)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"output": str(args.output), "gpu_status": snapshot["nvidia_gpus"]["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
