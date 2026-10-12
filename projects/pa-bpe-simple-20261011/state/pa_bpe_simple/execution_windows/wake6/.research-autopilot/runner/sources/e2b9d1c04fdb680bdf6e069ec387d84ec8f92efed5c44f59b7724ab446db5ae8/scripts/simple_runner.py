#!/usr/bin/env python3
"""Current-host, finite command supervisor with durable agent decisions.

Commands execute with shell=False. Exit zero is an execution observation, never
scientific acceptance. No provider or unattended platform host is installed here.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import sys
import time
import uuid

# A pinned checkout is immutable; ordinary CLI recovery must not write pycache
# into it before source verification.
sys.dont_write_bytecode = True
import _simple_process as process
import _simple_source as source
from simple_loop import SimpleLoop, LoopError, PHASES, _json

_IMPORTED_SOURCE_IDENTITY = source.current_source_identity(Path(__file__).resolve().parents[1])


class RunnerError(ValueError):
    pass


class DecisionRefresh(RunnerError):
    """The immutable decision snapshot was overtaken by concrete new state."""


ACTIVE = {"reserved", "dispatched", "running", "reconcile_required"}
TERMINAL = {"succeeded", "failed", "timed_out", "cancelled", "invalid_inputs", "invalid_outputs", "launch_failed", "invalid_evidence", "blocked"}
RESERVATION_GRACE = 3.0
CONTINUATION_REASONS = {"max_tokens", "max_turn_requests", "context_limit", "timeout", "interrupted", "partial"}
ISSUE_KINDS = {"cpu_unavailable", "gpu_unavailable", "resource_unavailable", "runtime_issue"}
ALERT_ACTIONS = {
    "task_result": "Inspect the referenced receipt and logs; repair or reconcile this attempt before replacement",
    "reconcile_required": "Reconcile the retained attempt identity and receipt before replacing it",
    "receipt_unreadable": "Restore or inspect the retained receipt; preserve its reservation until reconciliation",
    "cancellation_unresolved": "Inspect the retained command identity and reconcile cancellation",
    "dependency_blocked": "Repair the failed dependency and explicitly rebuild affected descendants",
    "task_contract_stale": "Create a versioned task for the current idea and revision",
    "budget_fit": "Choose work that fits the retained budget or request an explicitly authorized allocation revision",
    "decision_error": "Inspect the agent receipt and repair its configuration or answer the existing inbox",
    "decision_refresh": "Read the current decision snapshot and address the recorded validation error",
    "journal_rejected": "Inspect the rejected event and repair its evidence or contract",
    "source_adoption_required": "Reconcile active work, adopt authorized source at a quiet boundary, then restart",
}


def _summary(value):
    """A bounded single-line diagnostic, never a copy of payloads or log files."""
    return " ".join(str(value).splitlines()[0:1])[:600]


def _invalid_json_constant(value):
    raise RunnerError(f"Nonfinite diagnostic JSON constant: {value}")


def _name(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}", value):
        raise RunnerError(f"{label} must be a nonempty stable identifier")
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise RunnerError(f"{label} must be a nonempty string")
    return value


def _number(value, label, integer=False):
    if type(value) not in {int, float} or not math.isfinite(value) or value <= 0 or (integer and type(value) is not int):
        raise RunnerError(f"{label} must be a positive finite {'integer' if integer else 'number'}")
    return value


def _require_quiet_command_group(identity):
    """Observe every retained group candidate without granting signal ownership.

    The worker's last members snapshot can predate a child fork. The signalling
    helper intentionally needs an identity anchor; absence of that anchor is not
    evidence that the old group is empty. Reconciliation therefore scans /proc
    directly, retaining the reservation if inspection cannot establish quiet.
    """
    if (not isinstance(identity, dict) or type(identity.get("pid")) is not int
            or identity["pid"] < 1 or type(identity.get("start_ticks")) is not int
            or identity["start_ticks"] < 0 or not isinstance(identity.get("boot_id"), str)
            or not identity["boot_id"]):
        raise RunnerError("Retained command group identity cannot be established")
    try:
        if Path("/proc/sys/kernel/random/boot_id").read_text().strip() != identity["boot_id"]:
            return  # A prior boot cannot retain live members on this host.
        for entry in Path("/proc").iterdir():
            if not entry.name.isdecimal():
                continue
            try:
                raw = (entry / "stat").read_text()
            except (FileNotFoundError, ProcessLookupError):
                continue  # A process may exit during observation.
            fields = raw[raw.rfind(")") + 2:].split()
            if (int(fields[2]) == identity["pid"] and int(fields[3]) == identity["pid"]
                    and fields[0] not in {"Z", "X", "x"}
                    and int(fields[19]) >= identity["start_ticks"]):
                raise RunnerError("The retained command group still has live members")
    except (OSError, ValueError, IndexError) as exc:
        raise RunnerError(f"Retained command group needs reconciliation: {exc}") from exc


class SimpleRunner:
    """Persistent queue and decision inbox, sharing the journal's transaction."""

    def __init__(self, root, source_root=None):
        self.loop = SimpleLoop(root)
        self.root = self.loop.root
        self.directory = self.root / ".research-autopilot" / "runner"
        self.source_root = Path(source_root).resolve() if source_root is not None else Path(__file__).resolve().parents[1]
        self._process_modules = {}
        self._health_record = None
        self._reported_error = None
        self._exported_alerts = set()

    @contextmanager
    def _diagnostic_directory(self, create=False, alerts=False):
        """Use directory descriptors so neither reads nor writes follow symlinks."""
        descriptor = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parts = [".research-autopilot", "runner", "diagnostics"] + (["alerts"] if alerts else [])
            for part in parts:
                if create:
                    try:
                        os.mkdir(part, mode=0o700, dir_fd=descriptor)
                        os.fsync(descriptor)
                    except FileExistsError:
                        pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
            yield descriptor
        finally:
            os.close(descriptor)

    @staticmethod
    def _read_diagnostic(descriptor, name):
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        with os.fdopen(handle, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 1024 * 1024:
                raise RunnerError("Diagnostic must be a bounded regular JSON file")
            raw = stream.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise RunnerError("Diagnostic grew beyond its read limit")
            record = json.loads(raw, parse_constant=_invalid_json_constant)
        if not isinstance(record, dict):
            raise RunnerError("Diagnostic record must be a JSON object")
        return record

    def _write_diagnostic(self, name, record, alerts=False):
        """Atomic, durable write; alert IDs are immutable and create-once."""
        with self._diagnostic_directory(create=True, alerts=alerts) as directory:
            if alerts:
                try:
                    existing = self._read_diagnostic(directory, name)
                except FileNotFoundError:
                    pass
                else:
                    if existing.get("event_id") != record["event_id"]:
                        raise RunnerError("Alert identity conflicts with its retained file")
                    return existing
            else:
                try:
                    if not stat.S_ISREG(os.stat(name, dir_fd=directory, follow_symlinks=False).st_mode):
                        raise RunnerError("Health record must be a regular file")
                except FileNotFoundError:
                    pass
            temporary = ".write-" + uuid.uuid4().hex
            try:
                descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    json.dump(record, stream, sort_keys=True, allow_nan=False)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                if alerts:
                    try:
                        os.link(temporary, name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
                    except FileExistsError:
                        return self._read_diagnostic(directory, name)
                else:
                    os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
                os.fsync(directory)
                return record
            finally:
                try:
                    os.unlink(temporary, dir_fd=directory)
                except FileNotFoundError:
                    pass

    @staticmethod
    def _diagnostic_fallback(reason, error):
        try:
            print(json.dumps({"diagnostic_persistence_failed": _summary(error), "reason": _summary(reason),
                              "user_notified": False}), file=sys.stderr, flush=True)
        except Exception:
            pass  # A broken stderr must not replace the original runtime error.

    def _emit_alert(self, event_id, kind, reason, next_action, evidence=None, **identifiers):
        if event_id in self._exported_alerts and not event_id.startswith("host-issue:"):
            return {"event_id": event_id, "delivery_state": "local_pending_report", "user_notified": False}
        record = {"schema_version": 1, "root": str(self.root), "event_id": event_id, "kind": kind,
                  "observed_at": process._now(), "reason": _summary(reason), "next_action": _summary(next_action),
                  "evidence": evidence or [], "delivery_state": "local_pending_report", "user_notified": False,
                  **{key: value for key, value in identifiers.items()
                     if key in {"task_id", "attempt_id", "request_id", "status", "exception_type", "issue_fingerprint"}}}
        try:
            filename = hashlib.sha256(event_id.encode()).hexdigest() + ".json"
            persisted = self._write_diagnostic(filename, record, alerts=True)
            self._exported_alerts.add(event_id)
            return persisted
        except Exception as error:
            self._diagnostic_fallback(reason, error)
            return {**record, "delivery_state": "not_persisted"}

    def alerts(self):
        """Read local pending reports without SQLite, mutations, or delivery claims."""
        records, errors = [], []
        try:
            with self._diagnostic_directory(alerts=True) as directory:
                for name in sorted(os.listdir(directory)):
                    if not name.endswith(".json"):
                        continue
                    try:
                        record = self._read_diagnostic(directory, name)
                        if (record.get("root") != str(self.root) or record.get("schema_version") != 1
                                or not isinstance(record.get("event_id"), str)
                                or name != hashlib.sha256(record["event_id"].encode()).hexdigest() + ".json"):
                            raise RunnerError("Alert root, schema or identity mismatch")
                        if (not all(isinstance(record.get(key), str) for key in ("kind", "reason", "next_action", "observed_at"))
                                or not isinstance(record.get("evidence"), list)
                                or record.get("delivery_state") != "local_pending_report" or record.get("user_notified") is not False):
                            raise RunnerError("Invalid local alert fields")
                        datetime.fromisoformat(record["observed_at"])
                        records.append(record)
                    except (OSError, ValueError) as error:
                        errors.append({"file": name, "reason": _summary(error)})
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as error:
            errors.append({"reason": _summary(error)})
        return {"root": str(self.root), "delivery_state": "local_pending_report", "user_notified": False,
                "alerts": sorted(records, key=lambda item: (item.get("observed_at", ""), item["event_id"])), "errors": errors}

    def health(self, max_age_seconds=30):
        """Observe a retained supervisor identity; never restart it or update state."""
        _number(max_age_seconds, "max_age_seconds")
        result = {"root": str(self.root), "status": "unknown", "record": None, "errors": [],
                  "max_age_seconds": max_age_seconds,
                  "scope": "Local process observation only; no external watcher or user delivery is activated"}
        try:
            with self._diagnostic_directory() as directory:
                record = self._read_diagnostic(directory, "health.json")
            if record.get("root") != str(self.root) or record.get("schema_version") != 1:
                raise RunnerError("Health root or schema mismatch")
            epoch = record.get("last_activity_epoch")
            if type(epoch) not in {int, float} or not math.isfinite(epoch) or epoch <= 0:
                raise RunnerError("Health activity timestamp must be positive and finite")
            identity = record.get("identity")
            if identity is not None and (not isinstance(identity, dict) or set(identity) != {"pid", "start_ticks", "boot_id"}
                    or type(identity["pid"]) is not int or identity["pid"] <= 0
                    or type(identity["start_ticks"]) is not int or identity["start_ticks"] < 0
                    or not isinstance(identity["boot_id"], str) or not identity["boot_id"]):
                raise RunnerError("Invalid retained supervisor identity")
            for key in ("started_at", "last_activity_at", "exited_at"):
                if key == "exited_at" and record.get(key) is None:
                    continue
                if not isinstance(record.get(key), str):
                    raise RunnerError("Invalid health timestamp")
                datetime.fromisoformat(record[key])
            result["record"] = record
            result["identity_observed_alive"] = process.identity_alive(record.get("identity"))
            result["activity_age_seconds"] = max(0, time.time() - record["last_activity_epoch"])
            result["status"] = ("exited" if record.get("exited_at") else
                                ("stale" if result["activity_age_seconds"] > max_age_seconds else "active")
                                if result["identity_observed_alive"] else "lost" if identity else "unknown")
            if result["status"] == "lost":
                result["reason"] = ("Retained process identity is unverified: it may have exited, changed identity, "
                                    "or become unavailable to local observation; no restart or reconciliation is implied")
            elif result["status"] == "stale":
                result["reason"] = "Process identity is live but activity is older than the requested threshold; progress is not established"
        except FileNotFoundError:
            pass
        except (OSError, ValueError, KeyError, TypeError) as error:
            result["errors"].append(_summary(error))
        return result

    def report_issue(self, issue_id, kind, reason, evidence, next_action):
        """A host supplies observed resource failures; this API does not infer them."""
        _name(issue_id, "issue_id")
        if kind not in ISSUE_KINDS:
            raise RunnerError("Unsupported host issue kind")
        _text(reason, "issue reason")
        _text(next_action, "issue next_action")
        self.loop._evidence(evidence, required=True)
        fingerprint = hashlib.sha256(_json({"kind": kind, "reason": reason, "evidence": evidence, "next_action": next_action}).encode()).hexdigest()
        result = self._emit_alert("host-issue:" + issue_id, kind, reason, next_action, evidence=evidence, issue_fingerprint=fingerprint)
        if result.get("issue_fingerprint") != fingerprint:
            raise RunnerError("Issue ID already binds a different report; use a new issue_id")
        return result

    def _write_health(self, stage, **extra):
        if self._health_record is None:
            return
        self._health_record.update(stage=stage, last_activity_epoch=time.time(), last_activity_at=process._now(), **extra)
        try:
            self._write_diagnostic("health.json", self._health_record)
        except Exception as error:
            self._diagnostic_fallback("Supervisor health record could not be persisted", error)

    @contextmanager
    def _diagnostic_session(self, mode):
        # Enter only after the supervisor lock: a contender cannot replace the
        # live owner's health record, even when its own invocation fails.
        record = {"schema_version": 1, "root": str(self.root), "session_id": uuid.uuid4().hex,
                  "identity": None, "mode": mode, "started_at": process._now(),
                  "exit_status": None, "exited_at": None}
        self._health_record = record
        try:
            record["identity"] = process.process_identity()
            self._write_health("starting")
            yield record
        except (Exception, KeyboardInterrupt) as error:
            interrupted = isinstance(error, KeyboardInterrupt)
            self._reported_error = error
            record["exit_status"] = "interrupted" if interrupted else "exception"
            kind = "supervisor_interrupted" if interrupted else "supervisor_exception"
            self._emit_alert("supervisor:" + record["session_id"] + ":" + kind, kind,
                             f"{type(error).__name__}: {_summary(error) or 'Supervisor interrupted'}",
                             "Inspect the retained attempts and restart the same runner after resolving this condition",
                             exception_type=type(error).__name__)
            raise
        finally:
            self._write_health("exited", exited_at=process._now(), exit_status=record["exit_status"] or "returned")
            self._health_record = None

    @contextmanager
    def _supervised_session(self, mode):
        try:
            with self._supervisor_lock():
                with self._diagnostic_session(mode) as record:
                    yield record
        except (Exception, KeyboardInterrupt) as error:
            if self._reported_error is not error:
                self._reported_error = error
                reason = f"{type(error).__name__}: {_summary(error)}"
                event_id = "supervisor-start:" + hashlib.sha256(reason.encode()).hexdigest()
                self._emit_alert(event_id, "supervisor_start_failed", reason,
                                 "Inspect the existing supervisor and project path before retrying; do not start a competing owner",
                                 exception_type=type(error).__name__)
            raise

    def _export_alerts(self):
        """Derive reports only from committed state; never export inside _notify."""
        try:
            with self.loop._connection(readonly=True) as connection:
                state = self._load(connection)
                journal = self.loop._output(connection, self.loop._load(connection))
            for observation in state["observations"]:
                if observation["event_id"] in self._exported_alerts:
                    continue
                kind, payload = observation["kind"], observation["payload"]
                if kind not in ALERT_ACTIONS or (kind == "task_result" and payload.get("status") in {"succeeded", "cancelled"}):
                    continue
                evidence = [payload["receipt_ref"]] if payload.get("receipt_ref") else []
                self._emit_alert(observation["event_id"], kind, payload.get("reason", kind), ALERT_ACTIONS[kind],
                                 evidence=evidence, **{key: payload[key] for key in ("task_id", "attempt_id", "request_id", "status") if key in payload})
            for attempt in state["attempts"].values():
                if attempt["kind"] == "agent" and attempt["state"] == "terminal" and attempt.get("result") not in {"succeeded", "cancelled"}:
                    self._emit_alert("agent-result:" + attempt["attempt_id"], "agent_result", attempt.get("reason", "Agent execution failed"),
                                     "Inspect the agent receipt and any accepted checkpoint; continue or repair within retained limits",
                                     evidence=[attempt["receipt_ref"]] if attempt.get("receipt_ref") else [],
                                     attempt_id=attempt["attempt_id"], request_id=attempt["request_id"], status=attempt["result"])
            for identity, watch in state["external_waits"].items():
                if watch.get("error"):
                    digest = hashlib.sha256(watch["error"].encode()).hexdigest()[:16]
                    self._emit_alert(f"watch:{identity}:{digest}", "external_watch_error", watch["error"],
                                     "Inspect the declared external event file and repair its identity or JSON before continuing")
            for request_id, request in state["requests"].items():
                if (request.get("error") or "").startswith("Budget fit:"):
                    self._emit_alert("agent-budget:" + request_id, "budget_fit", request["error"], ALERT_ACTIONS["budget_fit"], request_id=request_id)
            status = self._state_name(state, journal)
            if status in {"paused_budget", "paused_deadline", "paused_journal_budget"}:
                self._emit_alert("pause:" + status + ":" + str(state["deadline_epoch"]), status,
                                 "Runner cannot continue within its retained " + status.removeprefix("paused_") + " boundary",
                                 "Review remaining work and the retained limits; resume only within an authorized revision", status=status)
        except Exception as error:
            self._diagnostic_fallback("Committed alerts could not be exported; retained state can be replayed", error)

    def _monitored_tick(self):
        self._write_health("tick")
        state = self._tick()
        self._export_alerts()
        self._write_health(state["status"])
        return state

    def _path(self, relative, allow_dot=False):
        _text(relative, "project-relative path")
        if allow_dot and relative == ".":
            return self.root
        if PurePosixPath(relative).is_absolute() or "\\" in relative or any(p in {"", ".", ".."} for p in relative.split("/")):
            raise RunnerError(f"Unsafe project-relative path: {relative}")
        path = self.root
        for part in relative.split("/"):
            path = path / part
            if path.is_symlink():
                raise RunnerError(f"Symlink path is not supported: {relative}")
        return path

    def _ref(self, path):
        path = Path(path)
        relative = path.relative_to(self.root).as_posix()
        self._path(relative)
        ref = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.loop._evidence([ref], required=True)
        return ref

    def initialize(self, config):
        config = json.loads(_json(config))
        if not isinstance(config, dict) or set(config) - {"idea", "goal", "limits", "agent_command", "goal_contract"}:
            raise RunnerError("Config requires idea, goal, limits and optional agent_command/goal_contract")
        _name(config.get("idea"), "idea")
        _text(config.get("goal"), "goal")
        contract = config.get("goal_contract")
        self._validate_goal_contract(contract, allow_none=True)
        limits = config.get("limits")
        keys = {"max_attempts", "max_command_seconds", "deadline_seconds", "max_concurrency"}
        if not isinstance(limits, dict) or set(limits) != keys:
            raise RunnerError("All four explicit finite execution limits are required")
        for key, value in limits.items():
            _number(value, key, integer=key in {"max_attempts", "max_concurrency"})
        agent = config.get("agent_command")
        self._validate_agent(agent)
        if not self.loop.state_path.exists():
            self.loop.initialize(config["idea"], config["goal"])
        self.directory.mkdir(parents=True, exist_ok=True)
        initial_source = source.capture_source(self.root, self.source_root)
        if initial_source["digest"] != _IMPORTED_SOURCE_IDENTITY["digest"]:
            raise RunnerError("A fresh CLI process must load the source before initializing its execution identity")
        with self.loop._connection() as connection:
            journal = self.loop._load(connection)
            connection.execute("CREATE TABLE IF NOT EXISTS runner_state (id INTEGER PRIMARY KEY CHECK(id=1), initial_config TEXT NOT NULL, payload TEXT NOT NULL)")
            row = connection.execute("SELECT * FROM runner_state WHERE id=1").fetchone()
            if row:
                if row["initial_config"] != _json(config):
                    raise RunnerError("Existing runner config and cumulative limits cannot be reset")
            else:
                if journal["goal"] != config["goal"] or journal["active_idea"] != config["idea"]:
                    raise RunnerError("Runner must bind the existing journal's goal and idea")
                state = {"schema_version": 1, "root": str(self.root), "config": config,
                         "deadline_epoch": time.time() + limits["deadline_seconds"],
                         "tasks": {}, "attempts": {}, "submissions": {}, "responses": {}, "requests": {},
                         "observations": [], "external_waits": {}, "outbox": {}, "sequence": 0,
                         "attempts_used": 0, "elapsed_seconds": 0.0, "stop_requested": None, "complete_goal": False,
                         "source": initial_source, "source_history": [{"source": initial_source, "reason": "Initial source snapshot"}],
                         "source_adoptions": {}, "source_error": None, "continuations": [], "checkpoint_hashes": [],
                         "goal_contract": contract, "goal_contract_version": 1 if contract else 0,
                         "goal_contract_history": [{"version": 1 if contract else 0, "goal": config["goal"], "contract": contract, "reason": "Initial objective scope"}],
                         "goal_changes": {}, "goal_completions": [],
                         "agent": self._initial_agent(agent)}
                connection.execute("INSERT INTO runner_state VALUES (1,?,?)", (_json(config), _json(state)))
        return self.status()

    def _load(self, connection):
        self.loop._load(connection)
        try:
            row = connection.execute("SELECT payload FROM runner_state WHERE id=1").fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower():
                raise RunnerError("Runner is not initialized") from exc
            raise
        if row is None:
            raise RunnerError("Runner is not initialized")
        state = json.loads(row[0])
        if state["root"] != str(self.root) or state.get("schema_version") != 1:
            raise RunnerError("Runner root or schema mismatch")
        # Old attempts remain honestly unpinned until explicit quiet adoption;
        # reading old state must never invent executable ancestry.
        state.setdefault("source", None)
        state.setdefault("source_history", [])
        state.setdefault("source_adoptions", {})
        state.setdefault("source_error", None)
        state.setdefault("continuations", [])
        state.setdefault("checkpoint_hashes", [])
        state.setdefault("agent", self._initial_agent(state["config"].get("agent_command")))
        state.setdefault("goal_contract", None)
        state.setdefault("goal_contract_version", 0)
        state.setdefault("goal_contract_history", [])
        state.setdefault("goal_changes", {})
        state.setdefault("goal_completions", [])
        for task in state["tasks"].values():
            task.setdefault("supersedes", None)
            task.setdefault("replaced_by", None)
        for attempt in state["attempts"].values():
            attempt.setdefault("source", None)
        return state

    def _validate_goal_contract(self, contract, allow_none=False):
        if contract is None and allow_none:
            return
        if not isinstance(contract, dict) or set(contract) != {"mode", "completion_criteria"}:
            raise RunnerError("Goal contract requires mode and completion_criteria")
        if contract["mode"] not in {"bounded_task", "research", "continuous_research"}:
            raise RunnerError("Goal mode must be bounded_task, research or continuous_research")
        criteria = contract["completion_criteria"]
        if not isinstance(criteria, list) or (not criteria and contract["mode"] != "continuous_research"):
            raise RunnerError("Declared bounded/research goals need explicit completion criteria")
        seen = set()
        for criterion in criteria:
            if not isinstance(criterion, dict) or set(criterion) != {"id", "description"}:
                raise RunnerError("Each goal criterion requires id and description")
            _name(criterion["id"], "criterion id")
            _text(criterion["description"], "criterion description")
            if criterion["id"] in seen:
                raise RunnerError("Goal criterion IDs must be unique")
            seen.add(criterion["id"])

    def revise_goal(self, contract, reason, expected_version, change_id, reopen=False, goal=None):
        contract = json.loads(_json(contract))
        self._validate_goal_contract(contract)
        _text(reason, "goal revision reason")
        _name(change_id, "goal change_id")
        if type(reopen) is not bool or type(expected_version) is not int or expected_version < 0:
            raise RunnerError("Goal revision requires an integer expected_version and boolean reopen")
        if goal is not None:
            _text(goal, "revised goal")
        payload = _json({"contract": contract, "reason": reason, "expected_version": expected_version, "reopen": reopen, "goal": goal})
        with self._supervisor_lock():
            artifact = self.directory / "goal-revisions" / f"{change_id}.json"
            with self.loop._connection() as connection:
                state = self._load(connection)
                previous = state["goal_changes"].get(change_id)
                if previous is not None:
                    if previous != payload:
                        raise RunnerError("Conflicting goal revision identity")
                    return self._reconciled_snapshot(connection, state)
                if state["stop_requested"]:
                    raise RunnerError("Goal revision must not clear an explicit user stop")
                if state["goal_contract_version"] != expected_version:
                    raise RunnerError("Goal contract version is stale")
                if any(a["state"] in ACTIVE for a in state["attempts"].values()):
                    raise RunnerError("Goal revision requires a quiet boundary with all attempts settled")
                if state["complete_goal"] and not reopen:
                    raise RunnerError("Completed goal needs an explicit reopen correction")
                journal = self.loop._load(connection)
                new_goal = journal["goal"] if goal is None else goal
                artifact_data = {"change_id": change_id, "previous_version": expected_version,
                                 "goal": new_goal, "contract": contract, "reason": reason, "reopen": reopen}
                if artifact.exists() and json.loads(artifact.read_text()) != artifact_data:
                    raise RunnerError("Retained goal revision artifact conflicts with this change")
                process.atomic_json(artifact, artifact_data)
                evidence = [self._ref(artifact)]
                if state["complete_goal"] and not state["goal_completions"]:
                    state["goal_completions"].append({"legacy": True, "goal": journal["goal"],
                        "goal_contract_version": expected_version, "assessment": None, "journal_version": journal["version"]})
                self.loop.record_in_transaction(connection, {"event_id": f"goal-revision:{change_id}", "kind": "goal_revision",
                    "goal": new_goal, "reason": reason, "evidence": evidence}, journal["version"])
                journal = self.loop._load(connection)
                if reopen and journal["status"] in {"completed", "retired"}:
                    self.loop.record_in_transaction(connection, {"event_id": f"goal-reopen:{change_id}", "kind": "reopen_idea",
                        "next_phase": "inspect", "reason": reason, "evidence": evidence}, journal["version"])
                state.update(goal_contract=contract, goal_contract_version=expected_version + 1)
                if reopen:
                    state["complete_goal"] = False
                state["goal_contract_history"].append({"version": state["goal_contract_version"], "goal": new_goal,
                    "contract": contract, "reason": reason, "change_id": change_id, "evidence": evidence, "reopen": reopen})
                state["goal_changes"][change_id] = payload
                self._refresh_requests(state, "Parent objective was explicitly revised; reassess the current scope")
                self._notify(state, f"goal-revision:{change_id}", "goal_revised", artifact_data)
                self._save(connection, state)
        return self.status()

    @staticmethod
    def _initial_agent(command):
        version = 1 if command is not None else 0
        return {"version": version, "command": command, "enabled": command is not None, "error": None,
                "repairs": {}, "history": [{"version": version, "command": command, "reason": "Initial configuration"}]}

    def _validate_agent(self, command):
        if command is None:
            return
        if not isinstance(command, dict) or set(command) != {"argv", "timeout_seconds"}:
            raise RunnerError("agent_command requires argv and timeout_seconds")
        self._argv(command["argv"])
        _number(command["timeout_seconds"], "agent timeout")
        joined = "\n".join(command["argv"])
        if joined.count("{request}") != 1 or joined.count("{response}") != 1:
            raise RunnerError("agent argv must contain {request} and {response} exactly once")

    def _refresh_requests(self, state, reason):
        for request_id, request in state["requests"].items():
            if request["state"] not in {"open", "needs_repair"}:
                continue
            request.update(state="stale", error=reason)
            for observation in state["observations"]:
                if observation["request_id"] == request_id:
                    observation["request_id"] = None

    def repair_agent(self, command, reason, expected_version, repair_id):
        command = json.loads(_json(command))
        self._validate_agent(command)
        _text(reason, "agent repair reason")
        _name(repair_id, "repair_id")
        payload = _json({"command": command, "reason": reason, "expected_version": expected_version})
        with self.loop._connection() as connection:
            state = self._load(connection)
            agent = state["agent"]
            previous = agent["repairs"].get(repair_id)
            if previous is not None:
                if previous != payload:
                    raise RunnerError("Conflicting agent repair identity")
            else:
                if type(expected_version) is not int or expected_version != agent["version"]:
                    raise RunnerError("Agent configuration version is stale")
                if state["stop_requested"] or state["complete_goal"]:
                    raise RunnerError("Stopped or completed goal cannot repair its adapter")
                if any(a["kind"] == "agent" and a["state"] in ACTIVE for a in state["attempts"].values()):
                    raise RunnerError("Settle the current agent attempt before repairing its configuration")
                agent.update(version=agent["version"] + 1, command=command, enabled=command is not None, error=None)
                agent["history"].append({"version": agent["version"], "command": command, "reason": reason, "repair_id": repair_id})
                agent["repairs"][repair_id] = payload
                self._refresh_requests(state, "Agent configuration explicitly repaired")
                self._notify(state, f"agent-repair:{repair_id}", "agent_repaired", {"version": agent["version"], "reason": reason})
                self._save(connection, state)
        return self.status()

    def adopt_source(self, reason, expected_digest, adoption_id):
        _text(reason, "source adoption reason")
        _name(adoption_id, "adoption_id")
        with self._supervisor_lock():
            snapshot = source.capture_source(self.root, self.source_root)
            if snapshot["digest"] != _IMPORTED_SOURCE_IDENTITY["digest"]:
                raise RunnerError("Source bytes differ from the loaded controller; restart in a fresh CLI before adoption")
            payload = _json({"source": snapshot, "reason": reason, "expected_digest": expected_digest})
            with self.loop._connection() as connection:
                state = self._load(connection)
                previous = state["source_adoptions"].get(adoption_id)
                if previous is not None:
                    if previous != payload:
                        raise RunnerError("Conflicting source adoption identity")
                else:
                    current = state["source"]["digest"] if state["source"] else "unpinned"
                    if expected_digest != current:
                        raise RunnerError("Source adoption digest is stale")
                    if any(a["state"] in ACTIVE for a in state["attempts"].values()):
                        raise RunnerError("Source adoption requires every active/uncertain attempt settled")
                    state.update(source=snapshot, source_error=None)
                    state["source_history"].append({"source": snapshot, "reason": reason, "adoption_id": adoption_id})
                    state["source_adoptions"][adoption_id] = payload
                    self._refresh_requests(state, "Source explicitly adopted at a quiet boundary")
                    self._notify(state, f"source-adoption:{adoption_id}", "source_adopted", {"source": snapshot, "reason": reason})
                    self._save(connection, state)
        return self.status()

    def _save(self, connection, state):
        connection.execute("UPDATE runner_state SET payload=? WHERE id=1", (_json(state),))

    def _notify(self, state, event_id, kind, payload):
        if any(o["event_id"] == event_id for o in state["observations"]):
            return
        state["sequence"] += 1
        state["observations"].append({"sequence": state["sequence"], "event_id": event_id,
                                      "kind": kind, "payload": payload, "request_id": None})

    def _budget(self, state):
        reserved = sum(a["reservation_seconds"] for a in state["attempts"].values() if a["state"] in ACTIVE)
        limits = state["config"]["limits"]
        return {"attempts_used": state["attempts_used"], "max_attempts": limits["max_attempts"],
                "elapsed_seconds": state["elapsed_seconds"], "reserved_seconds": reserved,
                "remaining_seconds": max(0.0, limits["max_command_seconds"] - state["elapsed_seconds"] - reserved),
                "max_command_seconds": limits["max_command_seconds"], "deadline_epoch": state["deadline_epoch"],
                "remaining_deadline_seconds": max(0.0, state["deadline_epoch"] - time.time())}

    def _state_name(self, state, journal):
        known_active = any(a["state"] in {"reserved", "dispatched", "running"} for a in state["attempts"].values())
        unknown = any(a["state"] == "reconcile_required" for a in state["attempts"].values())
        if state["complete_goal"]:
            return "completed"
        if state["stop_requested"]:
            return "stopping" if known_active else "stopped_with_reconciliation" if unknown else "stopped"
        if time.time() >= state["deadline_epoch"]:
            return "stopping_deadline" if known_active else "paused_deadline"
        budget = self._budget(state)
        if journal["budget_exhausted"]:
            return "draining_journal_budget" if known_active else "paused_journal_budget"
        if not known_active and (budget["attempts_used"] >= budget["max_attempts"] or budget["remaining_seconds"] <= 0):
            return "paused_budget"
        if known_active:
            return "running"
        if state.get("source_error") or state.get("source") is None:
            return "paused_source"
        if any(r["state"] == "open" and (r.get("error") or "").startswith("Budget fit:") for r in state["requests"].values()):
            return "paused_budget"
        if any(r["state"] in {"open", "needs_repair"} for r in state["requests"].values()):
            return "awaiting_decision"
        if unknown:
            return "reconcile_required"
        if any(w["state"] == "waiting" for w in state["external_waits"].values()):
            return "waiting_external"
        return "ready"

    def status(self):
        with self.loop._connection(readonly=True) as connection:
            state = self._load(connection)
            journal = self.loop._output(connection, self.loop._load(connection))
            return {"root": str(self.root), "status": self._state_name(state, journal), "sequence": state["sequence"],
                    "budget": self._budget(state), "tasks": list(state["tasks"].values()),
                    "attempts": list(state["attempts"].values()), "requests": list(state["requests"].values()),
                    "external_waits": list(state["external_waits"].values()), "outbox": list(state["outbox"].values()),
                    "stop_requested": state["stop_requested"], "journal": journal,
                    "agent": state["agent"], "continuations": state["continuations"], "source": state["source"],
                    "source_history": state["source_history"], "source_error": state["source_error"],
                    **self._goal_view(state, journal)}

    @staticmethod
    def _goal_view(state, journal):
        return {"goal": journal["goal"], "complete_goal": state["complete_goal"], "goal_contract": state["goal_contract"],
                "goal_contract_version": state["goal_contract_version"], "goal_contract_history": state["goal_contract_history"],
                "goal_completions": state["goal_completions"], "idea_status": journal["status"],
                "current_question": journal.get("current_question", journal["next_action"]), "next_action": journal["next_action"],
                "research_cycle_count": len(journal["research_cycles"])}

    @staticmethod
    def _argv(argv):
        if not isinstance(argv, list) or not argv:
            raise RunnerError("Command argv must be a nonempty array, never a shell string")
        for argument in argv:
            _text(argument, "argv item")

    def _tasks(self, state, tasks, journal):
        if not isinstance(tasks, list):
            raise RunnerError("tasks must be an array")
        if tasks and journal["status"] in {"completed", "retired"}:
            raise DecisionRefresh("The idea is closed; explicitly replace or reopen it before adding new tasks")
        prepared = {}
        fields = {"task_id", "argv", "phase", "purpose", "timeout_seconds", "cwd", "depends_on", "input_refs", "outputs", "supersedes"}
        for supplied in tasks:
            if not isinstance(supplied, dict) or set(supplied) - fields:
                raise RunnerError("Unexpected task fields")
            task = {"cwd": ".", "depends_on": [], "input_refs": [], "outputs": [], "supersedes": None, **supplied}
            task_id = _name(task.get("task_id"), "task_id")
            self._argv(task.get("argv"))
            _number(task.get("timeout_seconds"), "task timeout")
            _text(task.get("purpose"), "task purpose")
            if task.get("phase") not in PHASES:
                raise RunnerError("Unknown task phase")
            if not self._path(task["cwd"], allow_dot=True).is_dir():
                raise RunnerError("Task working directory must exist")
            if not isinstance(task["depends_on"], list) or len(set(task["depends_on"])) != len(task["depends_on"]):
                raise RunnerError("Dependencies must be unique task IDs")
            for dependency in task["depends_on"]:
                _name(dependency, "dependency")
            if not isinstance(task["outputs"], list) or len(set(task["outputs"])) != len(task["outputs"]):
                raise RunnerError("Outputs must be unique project-relative paths")
            for output in task["outputs"]:
                self._path(output)
                if output.startswith(".research-autopilot/runner/"):
                    raise RunnerError("User tasks cannot declare runner state as output")
            self.loop._evidence(task["input_refs"])
            task.update(idea=journal["active_idea"], revision=journal["revision"])
            if task_id in prepared:
                raise RunnerError("Duplicate task ID in the plan")
            if task_id in state["tasks"]:
                old = state["tasks"][task_id]
                if {key: old[key] for key in task} != task:
                    raise RunnerError("Task ID conflicts with an immutable contract")
            else:
                prepared[task_id] = task
        replacements = {}
        for task_id, task in prepared.items():
            old_id = task["supersedes"]
            if old_id is None:
                continue
            _name(old_id, "supersedes")
            old = state["tasks"].get(old_id)
            if old is None or old_id == task_id:
                raise RunnerError("Replacement must name an existing distinct task")
            if old["state"] in ACTIVE or old["state"] == "succeeded":
                raise RunnerError("Cannot replace a live, uncertain or successful task")
            if old.get("replaced_by") or old_id in replacements:
                raise RunnerError("A task already has an immutable replacement")
            replacements[old_id] = task_id
        def latest_replacement(task_id):
            current, seen = task_id, set()
            while current not in seen:
                seen.add(current)
                successor = replacements.get(current) or state["tasks"].get(current, {}).get("replaced_by")
                if not successor:
                    return current if current != task_id else None
                current = successor
            raise RunnerError("Task replacement lineage contains a cycle")
        for task in prepared.values():
            if task["supersedes"] is None:
                continue
            for dependency in state["tasks"][task["supersedes"]]["depends_on"]:
                replacement = latest_replacement(dependency)
                if replacement and replacement not in task["depends_on"]:
                    raise RunnerError(f"Rebuilt downstream task must explicitly depend on replacement {replacement}")
        graph = {key: task["depends_on"] for key, task in {**state["tasks"], **prepared}.items()}
        visited, active = set(), set()
        def visit(node):
            if node in active:
                raise RunnerError("Task dependencies contain a cycle")
            if node in visited:
                return
            if node not in graph:
                raise RunnerError(f"Unknown dependency: {node}")
            active.add(node)
            for dependency in graph[node]:
                visit(dependency)
            active.remove(node)
            visited.add(node)
        for task_id in graph:
            visit(task_id)
        for task_id, task in prepared.items():
            state["tasks"][task_id] = {**task, "state": "queued", "attempt_id": None, "reason": "Awaiting its dependencies and finite execution budget", "cancel_requested": False, "replaced_by": None}
        for old_id, replacement in replacements.items():
            old = state["tasks"][old_id]
            old["replaced_by"] = replacement
            if old["state"] == "queued":
                old.update(state="cancelled", reason=f"Explicitly superseded by {replacement} before execution")
        for task in state["tasks"].values():
            required = {name: latest_replacement(name) for name in task["depends_on"] if latest_replacement(name)}
            if required and not task.get("replaced_by") and task["state"] != "succeeded":
                digest = hashlib.sha256(_json(required).encode()).hexdigest()[:16]
                self._notify(state, f"rebuild:{task['task_id']}:{digest}", "downstream_rebuild", {
                    "task_id": task["task_id"], "required_replacements": required,
                    "next_action": "Submit a new task with an explicit contract, supersedes and replacement dependencies",
                    "original_contract": {key: task[key] for key in fields}})

    def submit(self, plan):
        try:
            payload = _json(plan)
            plan = json.loads(payload)
            if not isinstance(plan, dict) or set(plan) != {"submission_id", "idea", "revision", "tasks"}:
                raise RunnerError("Plan requires submission_id, idea, revision and tasks")
            submission = _name(plan["submission_id"], "submission_id")
            with self.loop._connection() as connection:
                state = self._load(connection)
                previous = state["submissions"].get(submission)
                if previous is not None:
                    if previous != payload:
                        raise RunnerError("Conflicting submission identity")
                else:
                    journal = self.loop._load(connection)
                    if (plan["idea"], plan["revision"]) != (journal["active_idea"], journal["revision"]):
                        raise RunnerError("Plan idea/revision is stale")
                    if state["complete_goal"] or state["stop_requested"]:
                        raise RunnerError("Stopped or completed goal cannot accept new tasks")
                    self._tasks(state, plan["tasks"], journal)
                    state["submissions"][submission] = payload
                    self._save(connection, state)
        except LoopError as exc:
            raise RunnerError(str(exc)) from exc
        return self.status()

    def inbox(self):
        with self.loop._connection(readonly=True) as connection:
            state = self._load(connection)
            return [{**r["snapshot"], "state": r["state"], "error": r.get("error"), "request_ref": r["request_ref"]}
                    for r in state["requests"].values() if r["state"] in {"open", "needs_repair"}]

    def _unhandled(self, state):
        return [o for o in state["observations"] if o["request_id"] is None]

    def respond(self, response):
        try:
            payload = _json(response)
            response = json.loads(payload)
            fields = {"response_id", "request_id", "idea", "revision", "reason", "events", "tasks", "wait", "complete_goal", "await_tasks", "cancel_tasks", "continuation",
                      "goal_contract_version", "goal_assessment"}
            if not isinstance(response, dict) or set(response) - fields:
                raise RunnerError("Unexpected response fields")
            response_id = _name(response.get("response_id"), "response_id")
            _text(response.get("reason"), "response reason")
            with self.loop._connection() as connection:
                state = self._load(connection)
                old = state["responses"].get(response_id)
                if old is not None:
                    if old != payload:
                        raise RunnerError("Conflicting response identity")
                    return self._public_after_transaction(connection, state)
                if state["stop_requested"] or state["complete_goal"]:
                    raise RunnerError("Stopped or completed goal cannot accept a new response")
                request = state["requests"].get(response.get("request_id"))
                if request and request["state"] == "stale":
                    raise DecisionRefresh("Decision request is stale; inspect its current goal/idea/source successor")
                if request is None or request["state"] not in {"open", "needs_repair"}:
                    raise RunnerError("Decision request is missing or already closed")
                journal = self.loop._load(connection)
                goal_version = response.get("goal_contract_version", 0 if state["goal_contract_version"] == 0 else None)
                if (type(goal_version) is not int or goal_version != state["goal_contract_version"]
                        or goal_version != request["snapshot"].get("goal_contract_version", 0)):
                    raise DecisionRefresh("Response goal contract version is stale or missing; inspect the current objective")
                binding = (response.get("idea"), response.get("revision"))
                if binding != (request["snapshot"]["idea"], request["snapshot"]["revision"]) or binding != (journal["active_idea"], journal["revision"]):
                    raise DecisionRefresh("Response is stale for this request or active idea/revision")
                for flag in ("complete_goal", "await_tasks"):
                    if flag in response and type(response[flag]) is not bool:
                        raise RunnerError(f"{flag} must be a boolean")
                events, tasks = response.get("events", []), response.get("tasks", [])
                cancellations = response.get("cancel_tasks", [])
                if not isinstance(events, list) or not isinstance(cancellations, list):
                    raise RunnerError("events and cancel_tasks must be arrays")
                if not any((events, tasks, cancellations, response.get("wait"), response.get("complete_goal"), response.get("await_tasks"), response.get("continuation"))):
                    raise RunnerError("Response must provide concrete work, feedback, an observable wait or completion")
                for task_id in cancellations:
                    if task_id not in state["tasks"]:
                        raise RunnerError(f"Unknown cancellation task: {task_id}")
                    task = state["tasks"][task_id]
                    task["cancel_requested"] = True
                    if task["state"] == "queued":
                        task.update(state="cancelled", reason=response["reason"])
                closing = any(e.get("kind") in {"completion", "retire_idea", "replace_idea", "reopen_idea"} for e in events if isinstance(e, dict))
                if response.get("continuation") is not None and (closing or tasks or cancellations or response.get("wait")
                                                               or response.get("complete_goal") or response.get("await_tasks")):
                    raise RunnerError("Partial continuation must not mix with closing, tasks, cancellation or waits")
                unfinished = (any(t["state"] == "queued" or t["state"] in ACTIVE for t in state["tasks"].values())
                              or any(a["state"] in ACTIVE for a in state["attempts"].values()))
                if closing and self._unhandled(state):
                    raise DecisionRefresh("Recheck newer observations before closing an idea")
                if closing and unfinished:
                    raise RunnerError("Settle or cancel pending tasks and agent attempts before closing an idea")
                for event in events:
                    if not isinstance(event, dict) or event.get("kind") in {"budget_change", "goal_revision", "execution_receipt"}:
                        raise RunnerError("A decision cannot silently change budgets or the parent objective; use its explicit revision operation")
                    if event.get("kind") == "research_cycle":
                        version = event.get("goal_contract_version", state["goal_contract_version"])
                        if type(version) is not int or version != state["goal_contract_version"]:
                            raise DecisionRefresh("Research cycle goal contract version is stale; explicitly review its applicability to the current goal version")
                        event = {**event, "goal_contract_version": version}
                    self.loop.record_in_transaction(connection, event, self.loop._load(connection)["version"])
                journal = self.loop._load(connection)
                if response.get("continuation") is not None:
                    self._continuation(state, response, request, journal)
                self._tasks(state, tasks, journal)
                if response.get("wait") is not None:
                    watch = response["wait"]
                    if not isinstance(watch, dict) or set(watch) != {"identity", "event_path"}:
                        raise RunnerError("External wait requires identity and observable event_path")
                    identity = _name(watch["identity"], "external identity")
                    self._path(watch["event_path"])
                    if identity in state["external_waits"]:
                        raise RunnerError("External wait identity was already registered")
                    state["external_waits"][identity] = {**watch, "state": "waiting", "error": None}
                if response.get("await_tasks") and not unfinished and not self._unhandled(state):
                    raise RunnerError("await_tasks needs retained tasks or newer unhandled observations")
                if response.get("complete_goal"):
                    if tasks or response.get("wait") or cancellations or journal["status"] != "completed" or not any(e.get("kind") == "completion" for e in events):
                        raise RunnerError("Goal completion requires an evidence-backed completion event and no new work")
                    if any(w["state"] == "waiting" for w in state["external_waits"].values()):
                        raise RunnerError("Resolve external waits before goal completion")
                    assessment = self._assess_goal(state, journal, response.get("goal_assessment"))
                    state["complete_goal"] = True
                    state["goal_completions"].append({"goal": journal["goal"], "goal_contract_version": state["goal_contract_version"],
                        "response_id": response_id, "idea": journal["active_idea"], "revision": journal["revision"], "assessment": assessment})
                elif "goal_assessment" in response:
                    raise RunnerError("goal_assessment accompanies explicit goal completion")
                request["state"] = "answered"
                request["response_id"] = response_id
                state["responses"][response_id] = payload
                if events and not (tasks or response.get("wait") or response.get("complete_goal") or response.get("await_tasks") or response.get("continuation")):
                    self._notify(state, f"followup:{response_id}", "decision_followup", {"reason": response["reason"], "journal_phase": journal["phase"]})
                self._save(connection, state)
        except (LoopError, TypeError, KeyError) as exc:
            raise RunnerError(str(exc)) from exc
        return self.status()

    def _assess_goal(self, state, journal, assessment):
        contract = state["goal_contract"]
        if contract is None:
            raise DecisionRefresh("Parent goal contract is undeclared; use revise-goal before claiming overall completion")
        if contract["mode"] == "continuous_research":
            raise DecisionRefresh("Continuous research has no automatic completion; continue useful scoped work or preserve an explicit stop/budget pause")
        if not isinstance(assessment, dict) or set(assessment) != {"reason", "criteria", "remaining_work"}:
            raise DecisionRefresh("Goal completion needs a separate assessment of every declared criterion and remaining_work")
        _text(assessment["reason"], "goal assessment reason")
        if not isinstance(assessment["remaining_work"], list):
            raise RunnerError("Goal remaining_work must be an array")
        if assessment["remaining_work"]:
            raise DecisionRefresh("Parent goal still has scoped work; convert it to concrete next tasks or questions")
        answers = assessment["criteria"]
        if not isinstance(answers, list):
            raise RunnerError("Goal criterion assessments must be an array")
        ids = []
        for answer in answers:
            if not isinstance(answer, dict) or set(answer) != {"id", "conclusion", "evidence"}:
                raise DecisionRefresh("Each goal criterion needs its id, scoped conclusion and current evidence")
            _name(answer["id"], "criterion assessment id")
            _text(answer["conclusion"], "criterion conclusion")
            try:
                self.loop._evidence(answer["evidence"], required=True)
            except LoopError as exc:
                raise DecisionRefresh(f"Goal criterion {answer['id']} needs current evidence; plan the missing work: {exc}") from exc
            ids.append(answer["id"])
        if len(ids) != len(set(ids)) or set(ids) != {c["id"] for c in contract["completion_criteria"]}:
            raise DecisionRefresh("Goal criteria remain unassessed or mismatched; inspect the declared criteria and plan the missing work")
        if contract["mode"] == "research" and not any(
                cycle.get("goal_contract_version") == state["goal_contract_version"] for cycle in journal["research_cycles"]):
            raise DecisionRefresh("A research goal needs an explicit evidence-linked research_cycle interpretation for the current goal version; review retained evidence for this scope or perform the missing work")
        return assessment

    def _continuation(self, state, response, request, journal):
        partial = response["continuation"]
        required = {"reason", "checkpoint_refs", "next_action"}
        if not isinstance(partial, dict) or not required <= set(partial) or set(partial) - required - {"session_id"}:
            raise RunnerError("Continuation requires reason, checkpoint_refs, next_action and optional session_id")
        if partial["reason"] not in CONTINUATION_REASONS:
            raise RunnerError("Unknown structured continuation reason")
        _text(partial["next_action"], "continuation next_action")
        if "session_id" in partial:
            _text(partial["session_id"], "continuation session_id")
        self.loop._evidence(partial["checkpoint_refs"], required=True)
        hashes = {ref["sha256"] for ref in partial["checkpoint_refs"]}
        if not hashes - set(state["checkpoint_hashes"]):
            raise RunnerError("Continuation needs new checkpoint content; relabelled or recombined old bytes cannot retry")
        captured = []
        for index, ref in enumerate(partial["checkpoint_refs"]):
            raw = self._path(ref["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
                raise RunnerError("Checkpoint changed during capture")
            path = self.directory / "checkpoints" / response["response_id"] / f"{index}-{ref['sha256']}.checkpoint"
            self._path(path.relative_to(self.root).as_posix())
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with path.open("xb") as output:
                    output.write(raw)
                    output.flush()
                    os.fsync(output.fileno())
            except FileExistsError:
                pass
            captured_ref = self._ref(path)
            if captured_ref["sha256"] != ref["sha256"]:
                raise RunnerError("Retained checkpoint capture conflicts with current evidence")
            captured.append(captured_ref)
        continuation = {**partial, "checkpoint_refs": captured, "original_checkpoint_refs": partial["checkpoint_refs"],
                        "response_id": response["response_id"], "request_id": response["request_id"],
                        "attempt_id": request.get("agent_attempt_id"), "idea": journal["active_idea"], "revision": journal["revision"],
                        "agent_version": state["agent"]["version"]}
        state["continuations"].append(continuation)
        state["checkpoint_hashes"] = sorted(set(state["checkpoint_hashes"]) | hashes)
        self._notify(state, f"continuation:{response['response_id']}", "continuation", continuation)

    def _public_after_transaction(self, connection, state):
        journal = self.loop._load(connection)
        return {"status": self._state_name(state, journal), "sequence": state["sequence"], "budget": self._budget(state)}

    @contextmanager
    def _supervisor_lock(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "supervisor.lock").open("a+") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RunnerError("Another supervisor owns this project lock") from exc
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _outbox(self, connection, state):
        for item in state["outbox"].values():
            if item["state"] == "recorded":
                continue
            connection.execute("SAVEPOINT journal_outbox")
            try:
                self.loop.record_in_transaction(connection, item["event"], self.loop._load(connection)["version"])
                connection.execute("RELEASE journal_outbox")
                item.update(state="recorded", error=None)
            except LoopError as exc:
                connection.execute("ROLLBACK TO journal_outbox")
                connection.execute("RELEASE journal_outbox")
                item["error"] = str(exc)
                self._notify(state, f"journal-error:{item['event']['event_id']}", "journal_rejected", {"event_id": item["event"]["event_id"], "reason": str(exc)})

    def _observe_attempts(self):
        for snapshot in self.status()["attempts"]:
            if snapshot["state"] not in ACTIVE:
                continue
            directory = Path(snapshot["attempt_dir"])
            if (snapshot["state"] == "reserved" and not snapshot["contract_sha256"]
                    and not (directory / "attempt.json").exists()
                    and not any((directory / name).exists() for name in ("launch.json", "worker.json", "command.json", "receipt.json"))):
                # The DB reservation is known, but no wrapper was launchable yet.
                # Materialize its original contract in _launch_reserved below.
                continue
            try:
                observed = process.inspect_attempt(self.root, snapshot["attempt_dir"])
            except (OSError, ValueError) as exc:
                observed = {"state": "reconcile_required", "reason": str(exc)}
            if observed["state"] == "absent":
                continue
            with self.loop._connection() as connection:
                state = self._load(connection)
                attempt = state["attempts"][snapshot["attempt_id"]]
                if attempt["state"] not in ACTIVE:
                    continue
                if observed["state"] == "completed":
                    try:
                        self._settle(connection, state, attempt, observed["receipt"])
                    except (OSError, LoopError, ValueError) as exc:
                        attempt.update(state="reconcile_required", reason=f"Receipt ingestion requires reconciliation: {exc}")
                        if attempt["kind"] == "task":
                            state["tasks"][attempt["task_id"]].update(state="reconcile_required", reason=attempt["reason"])
                        self._notify(state, f"receipt-error:{attempt['attempt_id']}", "receipt_unreadable",
                                     {"task_id": attempt["task_id"], "attempt_id": attempt["attempt_id"], "reason": str(exc)})
                elif observed["state"] == "running":
                    attempt.update(state="running", reason=observed.get("reason", "Observed retained worker"))
                    if attempt["kind"] == "task":
                        state["tasks"][attempt["task_id"]]["state"] = "running"
                elif observed["state"] == "reconcile_required":
                    attempt.update(state="reconcile_required", reason=observed["reason"])
                    if attempt["kind"] == "task":
                        state["tasks"][attempt["task_id"]].update(state="reconcile_required", reason=observed["reason"])
                    self._notify(state, f"unknown:{attempt['attempt_id']}", "reconcile_required", {"task_id": attempt["task_id"], "attempt_id": attempt["attempt_id"], "reason": observed["reason"]})
                self._save(connection, state)

    def _settle(self, connection, state, attempt, receipt):
        reason = receipt.get("error") or f"Command execution reported {receipt.get('status')}"
        result = receipt.get("status")
        elapsed = receipt.get("elapsed_seconds")
        if type(elapsed) not in {int, float} or not math.isfinite(elapsed) or elapsed < 0:
            elapsed = attempt["reservation_seconds"]
        receipt_ref = self._ref(Path(attempt["attempt_dir"]) / "receipt.json")
        try:
            if (receipt.get("root"), receipt.get("attempt_id"), receipt.get("task_id"), receipt.get("contract_sha256")) != (str(self.root), attempt["attempt_id"], attempt["task_id"], attempt["contract_sha256"]):
                raise LoopError("Receipt identity does not match the retained command contract")
            if result not in TERMINAL - {"blocked", "invalid_evidence"}:
                raise LoopError("Unknown terminal receipt status")
            self.loop._evidence([receipt["stdout_ref"], receipt["stderr_ref"], *receipt.get("output_refs", [])])
        except (LoopError, KeyError) as exc:
            result, reason = "invalid_evidence", str(exc)
        attempt.update(state="terminal", result=result, reason=reason, receipt=receipt, receipt_ref=receipt_ref,
                       elapsed_seconds=elapsed, response_handled=attempt["kind"] == "task")
        state["elapsed_seconds"] += elapsed
        if attempt["kind"] == "task":
            state["tasks"][attempt["task_id"]].update(state=result, reason=reason)
            self._notify(state, f"result:{attempt['attempt_id']}", "task_result", {"task_id": attempt["task_id"], "attempt_id": attempt["attempt_id"], "status": result, "reason": reason, "receipt_ref": receipt_ref, "receipt": receipt})
        event = {"event_id": f"runner-result:{attempt['attempt_id']}", "kind": "progress",
                 "reason": f"Execution observation for {attempt['task_id']}: {result}; {reason}",
                 "next_phase": "verify" if result == "succeeded" else "diagnostic", "evidence": [receipt_ref],
                 "usage": {"wall_seconds": elapsed}}
        if attempt["kind"] == "agent":
            event["kind"] = "execution_receipt"
            event.pop("next_phase")
        state["outbox"][event["event_id"]] = {"event": event, "state": "pending", "error": None}
        self._outbox(connection, state)

    def _agent_responses(self):
        for attempt in self.status()["attempts"]:
            if attempt["kind"] != "agent" or attempt["state"] != "terminal" or attempt.get("response_handled"):
                continue
            error = None
            refresh = False
            try:
                if attempt["result"] not in {"succeeded", "failed", "timed_out"}:
                    raise RunnerError(f"Agent command failed: {attempt['reason']}")
                self.loop._evidence(attempt["receipt"]["output_refs"], required=True)
                self.loop._evidence(attempt["contract"]["input_refs"])
                response_ref = next((ref for ref in attempt["receipt"]["output_refs"] if ref["path"] == attempt["response_path"]), None)
                if response_ref is None:
                    raise RunnerError("Agent response is not a pinned output of this attempt")
                raw = self._path(attempt["response_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != response_ref["sha256"]:
                    raise RunnerError("Agent response changed after receipt validation")
                response = json.loads(raw)
                if response.get("request_id") != attempt["request_id"]:
                    raise RunnerError("Agent response targets a different request")
                if attempt["result"] != "succeeded" and response.get("continuation") is None:
                    raise RunnerError("Nonzero agent output may only provide an explicit evidence-backed continuation")
                self.respond(response)
            except DecisionRefresh as exc:
                error, refresh = str(exc), True
            except (RunnerError, LoopError, OSError, ValueError, AttributeError) as exc:
                error = str(exc)
            with self.loop._connection() as connection:
                state = self._load(connection)
                state["attempts"][attempt["attempt_id"]]["response_handled"] = True
                request = state["requests"][attempt["request_id"]]
                if error and not refresh and attempt.get("agent_version", 1) == state["agent"]["version"]:
                    state["agent"].update(enabled=False, error=error)
                    state["agent"]["history"][-1].setdefault("failures", []).append({"attempt_id": attempt["attempt_id"], "reason": error})
                if error and request["state"] in {"open", "needs_repair"}:
                    request.update(state="stale" if refresh else "needs_repair", error=error)
                    if refresh:
                        for observation in state["observations"]:
                            if observation["request_id"] == attempt["request_id"]:
                                observation["request_id"] = None
                    self._notify(state, f"agent-error:{attempt['attempt_id']}", "decision_refresh" if refresh else "decision_error", {"request_id": attempt["request_id"], "attempt_id": attempt["attempt_id"], "reason": error, "receipt_ref": attempt["receipt_ref"]})
                self._save(connection, state)

    def _watch(self, state):
        for watch in state["external_waits"].values():
            if watch["state"] != "waiting":
                continue
            try:
                path = self._path(watch["event_path"])
                if not path.is_file():
                    continue
                ref = self._ref(path)
                payload = json.loads(path.read_text())
                if not isinstance(payload, dict) or payload.get("identity") != watch["identity"]:
                    watch["error"] = "External event identity does not match"
                    continue
                capture = self.directory / "wake-events" / f"{uuid.uuid4().hex}.json"
                process.atomic_json(capture, payload)
                captured_ref = self._ref(capture)
                watch.update(state="consumed", error=None, observed_ref=ref, captured_ref=captured_ref)
                self._notify(state, f"wake:{watch['identity']}", "external_wake", {"identity": watch["identity"], "evidence": [captured_ref], "source_ref": ref})
            except (OSError, ValueError, LoopError) as exc:
                watch["error"] = str(exc)

    def _request(self, connection, state):
        journal = self.loop._load(connection)
        for request in state["requests"].values():
            if request["state"] in {"open", "needs_repair"}:
                if (request["snapshot"]["idea"], request["snapshot"]["revision"]) == (journal["active_idea"], journal["revision"]):
                    # A disabled adapter is not a scientific inbox gate. Refresh
                    # once new observations arrive, keeping the old error/history.
                    if (not state["agent"]["enabled"] and state["agent"]["error"]
                            and any(o["kind"] != "decision_error" for o in self._unhandled(state))):
                        request.update(state="stale", error=request.get("error") or state["agent"]["error"])
                        for observation in state["observations"]:
                            if observation["request_id"] == request["snapshot"]["request_id"]:
                                observation["request_id"] = None
                        continue
                    return
                request.update(state="stale", error="Active idea/revision changed before a response")
                for observation in state["observations"]:
                    if observation["request_id"] == request["snapshot"]["request_id"]:
                        observation["request_id"] = None
        if state["complete_goal"] or state["stop_requested"] or time.time() >= state["deadline_epoch"]:
            return
        observations = self._unhandled(state)
        pending = any(t["state"] == "queued" or t["state"] in ACTIVE for t in state["tasks"].values())
        waiting = any(w["state"] == "waiting" for w in state["external_waits"].values())
        if not observations and (pending or waiting):
            return
        request_id = "decision-" + uuid.uuid4().hex
        snapshot = json.loads(_json({"request_id": request_id, "root": str(self.root), "goal": journal["goal"],
                                    "idea": journal["active_idea"], "revision": journal["revision"], "journal_version": journal["version"],
                                    "observations": observations, "tasks": list(state["tasks"].values()),
                                    "attempts": list(state["attempts"].values()), "budget": self._budget(state),
                                    "agent_version": state["agent"]["version"], "agent_error": state["agent"]["error"],
                                    "source": state["source"],
                                    "continuation": state["continuations"][-1] if state["continuations"] else None,
                                    "goal_contract": state["goal_contract"], "goal_contract_version": state["goal_contract_version"],
                                    "idea_status": journal["status"], "current_question": journal.get("current_question", journal["next_action"]),
                                    "next_action": journal["next_action"], "research_cycles": journal["research_cycles"], "milestones": journal["milestones"]}))
        path = self.directory / "requests" / f"{request_id}.json"
        process.atomic_json(path, snapshot)
        state["requests"][request_id] = {"snapshot": snapshot, "request_ref": self._ref(path), "state": "open", "error": state["agent"]["error"], "agent_attempt_id": None}
        for observation in observations:
            observation["request_id"] = request_id

    def _reserve(self, state, task, kind="task", **extra):
        budget = self._budget(state)
        limits = state["config"]["limits"]
        reservation = task["timeout_seconds"] + RESERVATION_GRACE
        if (state["attempts_used"] >= limits["max_attempts"] or reservation > budget["remaining_seconds"]
                or reservation > budget["remaining_deadline_seconds"]
                or sum(a["state"] in ACTIVE for a in state["attempts"].values()) >= limits["max_concurrency"]):
            return None
        attempt_id = "attempt-" + uuid.uuid4().hex
        directory = self.directory / "attempts" / attempt_id
        contract = {"schema_version": 1, "root": str(self.root), "attempt_id": attempt_id, "task_id": task["task_id"],
                    "kind": kind, "argv": task["argv"], "cwd": task["cwd"], "timeout_seconds": task["timeout_seconds"],
                    "deadline_epoch": state["deadline_epoch"], "input_refs": task["input_refs"], "outputs": task["outputs"],
                    "source": state["source"]}
        state["attempts"][attempt_id] = {"attempt_id": attempt_id, "task_id": task["task_id"], "kind": kind,
                                        "state": "reserved", "attempt_dir": str(directory), "contract": contract, "contract_sha256": None,
                                        "reservation_seconds": reservation, "reason": "Durably reserved before dispatch", "source": state["source"], **extra}
        state["attempts_used"] += 1
        return attempt_id

    def _fit_error(self, state, timeout_seconds):
        budget = self._budget(state)
        reservation = timeout_seconds + RESERVATION_GRACE
        if budget["attempts_used"] >= budget["max_attempts"]:
            return "Attempt budget exhausted"
        if reservation > budget["remaining_seconds"]:
            return f"Command budget needs {reservation:g}s including cleanup, but only {budget['remaining_seconds']:g}s is unreserved"
        if reservation > budget["remaining_deadline_seconds"]:
            return f"Deadline budget cannot fit {reservation:g}s including cleanup"
        return None

    def _schedule(self, connection, state):
        journal = self.loop._load(connection)
        if (state["stop_requested"] or state["complete_goal"] or journal["budget_exhausted"] or time.time() >= state["deadline_epoch"]
                or state["source_error"] or state["source"] is None):
            return
        for task in state["tasks"].values():
            if task["state"] != "queued":
                continue
            dependencies = [state["tasks"][name] for name in task["depends_on"]]
            if any(d["state"] in TERMINAL - {"succeeded"} for d in dependencies):
                task.update(state="blocked", reason="A dependency failed; repair requires a new versioned task")
                self._notify(state, f"blocked:{task['task_id']}", "dependency_blocked", {"task_id": task["task_id"], "reason": task["reason"]})
                continue
            if any(d["state"] != "succeeded" for d in dependencies):
                task["reason"] = "Awaiting successful dependencies; uncertain dependencies retain their identity"
                continue
            if (task["idea"], task["revision"]) != (journal["active_idea"], journal["revision"]) or journal["status"] in {"completed", "retired"}:
                task.update(state="blocked", reason="Task belongs to an earlier or closed idea/revision")
                self._notify(state, f"stale:{task['task_id']}", "task_contract_stale", {"task_id": task["task_id"], "reason": task["reason"]})
                continue
            attempt_id = self._reserve(state, task)
            if attempt_id:
                task.update(state="reserved", attempt_id=attempt_id, reason="Attempt durably reserved")
            else:
                error = self._fit_error(state, task["timeout_seconds"])
                if error:
                    task["reason"] = error
                    self._notify(state, f"budget-fit:{task['task_id']}", "budget_fit", {"task_id": task["task_id"], "reason": error})
        agent = state["agent"]["command"]
        if agent and state["agent"]["enabled"]:
            for request_id, request in state["requests"].items():
                if request["state"] != "open" or request["agent_attempt_id"]:
                    continue
                response_path = (self.directory / "responses" / f"{request_id}.json").relative_to(self.root).as_posix()
                self._path(response_path).parent.mkdir(parents=True, exist_ok=True)
                request_path = str(self._path(request["request_ref"]["path"]))
                argv = [part.replace("{request}", request_path).replace("{response}", str(self._path(response_path))) for part in agent["argv"]]
                task = {"task_id": "agent:" + request_id, "argv": argv, "cwd": ".", "timeout_seconds": agent["timeout_seconds"],
                        "input_refs": [request["request_ref"], *(request["snapshot"].get("continuation") or {}).get("checkpoint_refs", [])], "outputs": [response_path]}
                attempt_id = self._reserve(state, task, kind="agent", request_id=request_id, response_path=response_path,
                                           agent_version=state["agent"]["version"])
                if attempt_id:
                    request["agent_attempt_id"] = attempt_id
                    request["error"] = None
                else:
                    error = self._fit_error(state, agent["timeout_seconds"])
                    if error:
                        request["error"] = "Budget fit: " + error + "; a Work agent may respond without starting this command"

    def _launch_reserved(self):
        for attempt in self.status()["attempts"]:
            if attempt["state"] not in {"reserved", "dispatched"}:
                continue
            try:
                with self.loop._connection(readonly=True) as connection:
                    state = self._load(connection)
                if not attempt["source"]:
                    continue
                # A reservation already binds approved bytes and budget. Disk
                # drift blocks new reservations, not this same pinned attempt.
                source.verify_snapshot(self.root, attempt["source"])
                pinned_process = source.load_process_module(self.root, attempt["source"])
                self._process_modules[attempt["source"]["digest"]] = pinned_process
                directory = Path(attempt["attempt_dir"])
                contract_path = directory / "attempt.json"
                if not contract_path.exists():
                    process.atomic_json(contract_path, attempt["contract"])
                elif json.loads(contract_path.read_text()) != attempt["contract"]:
                    raise RunnerError("Persisted attempt contract changed")
                contract_ref = self._ref(contract_path)
                with self.loop._connection() as connection:
                    state = self._load(connection)
                    current = state["attempts"][attempt["attempt_id"]]
                    if current["contract_sha256"] and current["contract_sha256"] != contract_ref["sha256"]:
                        raise RunnerError("Attempt contract bytes changed after pinning")
                    current["contract_sha256"] = contract_ref["sha256"]
                    if state["stop_requested"] or time.time() >= state["deadline_epoch"]:
                        process.cancel_attempt(self.root, directory, state["stop_requested"] or "Runner deadline reached")
                    self._save(connection, state)
                observed = process.inspect_attempt(self.root, directory)
                if observed["state"] == "absent":
                    pinned_process.launch_worker(self.root, directory, contract_ref["sha256"])
                with self.loop._connection() as connection:
                    state = self._load(connection)
                    current = state["attempts"][attempt["attempt_id"]]
                    if current["state"] == "reserved":
                        current["state"] = "dispatched"
                    self._save(connection, state)
            except (OSError, ValueError, LoopError) as exc:
                with self.loop._connection() as connection:
                    state = self._load(connection)
                    current = state["attempts"][attempt["attempt_id"]]
                    current.update(state="reconcile_required", reason=f"Dispatch requires reconciliation: {exc}")
                    if current["kind"] == "task":
                        state["tasks"][current["task_id"]].update(state="reconcile_required", reason=current["reason"])
                    self._notify(state, f"dispatch:{attempt['attempt_id']}", "reconcile_required", {"task_id": attempt["task_id"], "attempt_id": attempt["attempt_id"], "reason": str(exc)})
                    self._save(connection, state)

    def _cancel_owned(self):
        with self.loop._connection(readonly=True) as connection:
            state = self._load(connection)
        stopping = state["stop_requested"] or ("Runner deadline reached" if time.time() >= state["deadline_epoch"] else None)
        for attempt in state["attempts"].values():
            task = state["tasks"].get(attempt["task_id"])
            if attempt["state"] not in ACTIVE or not (stopping or (task and task["cancel_requested"])):
                continue
            try:
                process.cancel_attempt(self.root, attempt["attempt_dir"], stopping or "Task explicitly cancelled")
            except (OSError, ValueError) as exc:
                with self.loop._connection() as connection:
                    current = self._load(connection)
                    current["attempts"][attempt["attempt_id"]]["reason"] = f"Cancellation needs reconciliation: {exc}"
                    self._notify(current, f"cancel-error:{attempt['attempt_id']}", "cancellation_unresolved", {"attempt_id": attempt["attempt_id"], "reason": str(exc)})
                    self._save(connection, current)

    def _tick(self):
        for module in self._process_modules.values():
            module._reap_workers()
        self._check_source()
        self._cancel_owned()
        self._observe_attempts()
        self._agent_responses()
        with self.loop._connection() as connection:
            state = self._load(connection)
            self._outbox(connection, state)
            self._watch(state)
            self._request(connection, state)
            self._schedule(connection, state)
            self._save(connection, state)
        self._launch_reserved()
        return self.status()

    def _verify_active_source(self, state):
        if state["source"] is None:
            raise RunnerError("Legacy runner source is unpinned; explicitly adopt source at a quiet boundary")
        source.verify_snapshot(self.root, state["source"])
        if state["source"]["digest"] != _IMPORTED_SOURCE_IDENTITY["digest"]:
            raise RunnerError("Adopted source differs from the loaded controller; restart with its pinned or current CLI")
        if source.current_source_identity(self.source_root)["digest"] != state["source"]["digest"]:
            raise RunnerError("Current executable/guidance differs from adopted source; explicit quiet adoption is required")

    def _check_source(self):
        with self.loop._connection(readonly=True) as connection:
            snapshot = self._load(connection)
        error = None
        try:
            self._verify_active_source(snapshot)
        except (OSError, ValueError) as exc:
            error = str(exc)
        with self.loop._connection() as connection:
            state = self._load(connection)
            state["source_error"] = error
            if error:
                digest = hashlib.sha256(error.encode()).hexdigest()[:16]
                self._notify(state, f"source-error:{digest}", "source_adoption_required", {"reason": error})
            self._save(connection, state)

    def tick(self):
        with self._supervised_session("tick") as record:
            state = self._monitored_tick()
            record["exit_status"] = "tick_complete"
            return state

    def run(self, poll_seconds=.2):
        _number(poll_seconds, "poll_seconds")
        if poll_seconds > 10:
            raise RunnerError("poll_seconds must be at most 10")
        with self._supervised_session("run") as record:
            state = self._run_loop(poll_seconds)
            record["exit_status"] = state["status"]
            return state

    def _run_loop(self, poll_seconds):
        # This loop is entered only while both the supervisor lock and health
        # session are owned. Keep execution/deadline recovery semantics intact.
        last = None
        last_observed = None
        busy_started = None
        while True:
            try:
                state = self._monitored_tick()
                last_observed, busy_started = state, None
            except sqlite3.OperationalError as exc:
                code = getattr(exc, "sqlite_errorcode", None)
                busy = ((code is not None and (code & 255) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED})
                        or (code is None and str(exc).lower() in {"database is locked", "database table is locked", "database schema is locked"}))
                if not busy:
                    raise
                self._emit_alert("database-busy:" + self._health_record["session_id"], "database_unavailable",
                                 str(exc), "Allow the current database owner to finish; retain attempts and the original deadline")
                self._write_health("waiting_database")
                busy_started = busy_started or time.monotonic()
                if last_observed is None:
                    try:
                        last_observed = self.status()
                    except sqlite3.OperationalError:
                        if time.monotonic() - busy_started >= 10:
                            raise exc
                if last_observed is not None and time.time() >= last_observed["budget"]["deadline_epoch"]:
                    errors = []
                    for attempt in last_observed["attempts"]:
                        if attempt["state"] in ACTIVE:
                            try:
                                process.cancel_attempt(self.root, attempt["attempt_dir"], "Persisted runner deadline reached during database contention")
                            except (OSError, ValueError) as cancel_error:
                                errors.append(str(cancel_error))
                    return {**last_observed, "status": "paused_deadline", "snapshot_stale": True,
                            "reason_code": "DATABASE_BUSY_AT_DEADLINE", "cancellation_errors": errors,
                            "reason": f"Database unavailable at persisted deadline: {exc}; receipts remain for restart/inspection"}
                if last != ("waiting_database", str(exc)):
                    print(json.dumps({"status": "waiting_database", "reason": str(exc)}), flush=True)
                    last = ("waiting_database", str(exc))
                time.sleep(poll_seconds)
                continue
            signature = (state["status"], state["sequence"], state["budget"]["attempts_used"])
            if signature != last:
                print(json.dumps({"status": state["status"], "sequence": state["sequence"], "budget": state["budget"]}), flush=True)
                last = signature
            if state["status"] in {"completed", "stopped", "stopped_with_reconciliation", "paused_budget", "paused_deadline", "paused_journal_budget", "paused_source"}:
                return state
            time.sleep(poll_seconds)

    def wait(self, after=0, timeout_seconds=30):
        _number(timeout_seconds, "timeout_seconds")
        if type(after) is not int or after < 0:
            raise RunnerError("after must be a nonnegative sequence")
        end = time.monotonic() + min(timeout_seconds, 60)
        while True:
            state = self.status()
            if state["sequence"] > after or time.monotonic() >= end or state["status"] in {"completed", "stopped", "paused_budget", "paused_deadline"}:
                return state
            time.sleep(min(.1, max(0, end - time.monotonic())))

    def stop(self, reason):
        _text(reason, "stop reason")
        with self.loop._connection() as connection:
            state = self._load(connection)
            state["stop_requested"] = state["stop_requested"] or reason
            for task in state["tasks"].values():
                if task["state"] == "queued":
                    task.update(state="cancelled", reason=reason)
            self._save(connection, state)
        end = time.monotonic() + 4
        while True:
            self._cancel_owned()
            self._observe_attempts()
            state = self.status()
            if not any(a["state"] in {"dispatched", "running"} for a in state["attempts"]) or time.monotonic() >= end:
                return state
            time.sleep(.05)

    def reconcile(self, task_id, attempt_id, resolution, evidence, reason):
        if resolution not in {"failed", "cancelled"}:
            raise RunnerError("Manual reconciliation can close failed/cancelled work, never invent execution success")
        _text(reason, "reconciliation reason")
        self.loop._evidence(evidence, required=True)
        with self.loop._connection() as connection:
            state = self._load(connection)
            attempt = state["attempts"].get(attempt_id)
            if attempt is None or attempt["task_id"] != task_id or attempt["state"] != "reconcile_required":
                raise RunnerError("Reconciliation must match the retained uncertain task and attempt")
            observed = process.inspect_attempt(self.root, attempt["attempt_dir"])
            if observed["state"] == "completed":
                # The worker's authentic late receipt wins over the caller's
                # earlier unknown observation and conservative manual estimate.
                self._settle(connection, state, attempt, observed["receipt"])
                self._save(connection, state)
                return self._reconciled_snapshot(connection, state)
            if observed["state"] == "running":
                raise RunnerError("A live worker cannot be manually declared terminal")
            command_path = Path(attempt["attempt_dir"]) / "command.json"
            if command_path.exists():
                command = json.loads(command_path.read_text())
                _require_quiet_command_group(command.get("identity"))
            elif (Path(attempt["attempt_dir"]) / "launch.json").exists():
                raise RunnerError("Launch marker exists without command-group identity; retain unknown reservation")
            attempt.update(state="terminal", result=resolution, reason=reason, reconciliation_evidence=evidence,
                           elapsed_seconds=attempt["reservation_seconds"], response_handled=True)
            state["elapsed_seconds"] += attempt["reservation_seconds"]
            if task_id in state["tasks"]:
                state["tasks"][task_id].update(state=resolution, reason=reason)
            self._notify(state, f"manual-reconcile:{attempt_id}", "manual_reconciliation", {"task_id": task_id, "attempt_id": attempt_id, "reason": reason, "evidence": evidence})
            self._save(connection, state)
        return self.status()

    def _reconciled_snapshot(self, connection, state):
        journal = self.loop._output(connection, self.loop._load(connection))
        return {"root": str(self.root), "status": self._state_name(state, journal), "sequence": state["sequence"],
                "budget": self._budget(state), "tasks": list(state["tasks"].values()), "attempts": list(state["attempts"].values()),
                "requests": list(state["requests"].values()), "external_waits": list(state["external_waits"].values()),
                "outbox": list(state["outbox"].values()), "stop_requested": state["stop_requested"], "journal": journal,
                "agent": state["agent"], "continuations": state["continuations"], "source": state["source"],
                "source_history": state["source_history"], "source_error": state["source_error"],
                **self._goal_view(state, journal)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init").add_argument("--config", required=True)
    sub.add_parser("submit").add_argument("--plan", required=True)
    sub.add_parser("run").add_argument("--poll-seconds", type=float, default=.2)
    sub.add_parser("status")
    sub.add_parser("inbox")
    sub.add_parser("alerts", help="Read local pending reports without SQLite; this does not notify the user")
    health = sub.add_parser("health", help="Read supervisor identity and activity without SQLite or restarting work")
    health.add_argument("--max-age-seconds", type=float, default=30,
                        help="Mark a live supervisor stale after this activity age (default: 30 seconds)")
    issue = sub.add_parser("report-issue", help="Record a host-observed issue with actual evidence")
    issue.add_argument("--issue-id", required=True)
    issue.add_argument("--kind", choices=sorted(ISSUE_KINDS), required=True)
    issue.add_argument("--reason", required=True)
    issue.add_argument("--evidence", required=True, help="JSON file containing project-relative sha256 evidence refs")
    issue.add_argument("--next-action", required=True)
    sub.add_parser("respond").add_argument("--response", required=True)
    wait = sub.add_parser("wait")
    wait.add_argument("--after", type=int, default=0)
    wait.add_argument("--timeout-seconds", type=float, default=30)
    sub.add_parser("stop").add_argument("--reason", required=True)
    repair = sub.add_parser("repair-agent")
    repair.add_argument("--config", required=True)
    repair.add_argument("--reason", required=True)
    repair.add_argument("--expected-version", type=int, required=True)
    repair.add_argument("--repair-id", required=True)
    adopt = sub.add_parser("adopt-source")
    adopt.add_argument("--reason", required=True)
    adopt.add_argument("--expected-digest", required=True)
    adopt.add_argument("--adoption-id", required=True)
    revise = sub.add_parser("revise-goal")
    revise.add_argument("--contract", required=True)
    revise.add_argument("--reason", required=True)
    revise.add_argument("--expected-version", type=int, required=True)
    revise.add_argument("--change-id", required=True)
    revise.add_argument("--goal")
    revise.add_argument("--reopen", action="store_true")
    reconcile = sub.add_parser("reconcile")
    for option in ("task", "attempt", "resolution", "evidence", "reason"):
        reconcile.add_argument("--" + option, required=True)
    args = parser.parse_args(argv)
    runner = None
    try:
        runner = SimpleRunner(args.root)
        if args.command == "init":
            result = runner.initialize(json.loads(Path(args.config).read_text()))
        elif args.command == "submit":
            result = runner.submit(json.loads(Path(args.plan).read_text()))
        elif args.command == "respond":
            result = runner.respond(json.loads(Path(args.response).read_text()))
        elif args.command == "run":
            result = runner.run(args.poll_seconds)
        elif args.command == "report-issue":
            result = runner.report_issue(args.issue_id, args.kind, args.reason,
                                         json.loads(Path(args.evidence).read_text()), args.next_action)
        elif args.command == "health":
            result = runner.health(args.max_age_seconds)
        elif args.command == "wait":
            result = runner.wait(args.after, args.timeout_seconds)
        elif args.command == "stop":
            result = runner.stop(args.reason)
        elif args.command == "repair-agent":
            result = runner.repair_agent(json.loads(Path(args.config).read_text()), args.reason, args.expected_version, args.repair_id)
        elif args.command == "adopt-source":
            result = runner.adopt_source(args.reason, args.expected_digest, args.adoption_id)
        elif args.command == "revise-goal":
            result = runner.revise_goal(json.loads(Path(args.contract).read_text()), args.reason, args.expected_version,
                                        args.change_id, args.reopen, args.goal)
        elif args.command == "reconcile":
            result = runner.reconcile(args.task, args.attempt, args.resolution, json.loads(Path(args.evidence).read_text()), args.reason)
        else:
            result = getattr(runner, args.command)()
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except Exception as exc:
        if runner is not None and args.command not in {"alerts", "health", "status", "inbox", "wait"} and runner._reported_error is not exc:
            runner._emit_alert("cli:" + uuid.uuid4().hex, "cli_exception", f"{type(exc).__name__}: {_summary(exc)}",
                               "Inspect the requested operation and retained project state before retrying", exception_type=type(exc).__name__)
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    except KeyboardInterrupt as exc:
        if runner is not None and args.command not in {"alerts", "health", "status", "inbox", "wait"} and runner._reported_error is not exc:
            runner._emit_alert("cli:" + uuid.uuid4().hex, "supervisor_interrupted", "Command interrupted",
                               "Inspect retained work before resuming the interrupted operation")
        print(json.dumps({"status": "supervisor_interrupted", "reason": "Detached attempts retain identity; restart the same runner to resume"}), file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
