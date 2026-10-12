#!/usr/bin/env python3
"""Durable, one-idea observation journal. This module never executes research.

File hashes establish the identity of supplied bytes, not the truth of their
contents. The host is responsible for scientific review and supplying all
relevant dependencies. A reported outcome is never an automatic scientific PASS.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import sys


class LoopError(ValueError):
    """Invalid observation or stale/conflicting journal operation."""


PHASES = frozenset({"inspect", "sources", "math", "code", "design", "evaluator",
                    "diagnostic", "experiment", "verify", "analysis", "delivery",
                    "resources"})
ROUTES = {
    "missing_evidence": ("evaluator", "Produce the missing evidence or qualify the metric implementation"),
    "source_gap": ("sources", "Find the specific missing primary source or protocol definition"),
    "mathematical_error": ("math", "Repair the assumptions or derivation and review the changed argument"),
    "implementation_error": ("code", "Repair the implementation and rerun the relevant diagnostic"),
    "evaluation_error": ("evaluator", "Repair or qualify the evaluator using independent checks"),
    "valid_negative_result": ("analysis", "Interpret the retained negative result and revise or retire the idea"),
    "insufficient_precision": ("design", "Design a justified comparison that resolves the remaining uncertainty"),
    "resource_issue": ("resources", "Revise the execution plan within the actual resource constraints"),
    "transient_failure": ("diagnostic", "Diagnose the transient failure before considering a bounded retry"),
}
ISSUE_KINDS = frozenset(ROUTES) - {"valid_negative_result"}
FIELDS = {
    **{kind: {"issue", "change_evidence"} for kind in ISSUE_KINDS},
    "missing_evidence": {"issue", "target_phase", "change_evidence"},
    "valid_negative_result": set(),
    "progress": {"next_phase"},
    "milestone": {"label", "next_phase"},
    "research_cycle": {"hypothesis", "prediction", "result", "interpretation", "next_action", "goal_contract_version"},
    "execution_receipt": set(),
    "goal_revision": {"goal"},
    "reopen_idea": {"next_phase"},
    "completion": {"outcome"},
    "wait": {"identity", "condition"},
    "wake": {"identity"},
    "uncertain_launch": {"identity"},
    "reconcile": {"identity", "resolution"},
    "revision": {"next_phase"},
    "retire_idea": set(),
    "replace_idea": {"idea"},
    "budget_change": {"limits"},
}
BASE_FIELDS = {"event_id", "kind", "reason", "evidence", "usage"}
USAGE_FIELDS = {"cpu_seconds", "wall_seconds", "tokens", "cost_micro_usd"}
OUTCOMES = {"supported", "not_supported", "inconclusive", "repaired"}
WORK_KINDS = frozenset(ROUTES) | {"progress", "revision", "replace_idea", "milestone", "research_cycle"}
INDEPENDENT_PHASES = frozenset({"sources", "math", "code", "design", "evaluator", "analysis"})


def _json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LoopError(f"Observation must contain finite JSON values: {exc}") from exc


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise LoopError(f"{name} must be a nonempty string")
    return value


def _positive_integer(value, name):
    if type(value) is not int or value < 1:
        raise LoopError(f"{name} must be a positive integer")
    return value


def _now():
    return datetime.now(timezone.utc).isoformat()


class SimpleLoop:
    """One goal and serial idea lineage, stored transactionally in SQLite.

    Every fresh event uses compare-and-swap ``expected_version``. Replaying an
    identical event ID returns current status without a new mutation or freshness
    assertion. Reinitialization may only repeat the original initialization.
    """

    def __init__(self, root, state_path=None):
        try:
            self.root = Path(root).expanduser().resolve(strict=True)
        except OSError as exc:
            raise LoopError(f"Project root must exist: {exc}") from exc
        if not self.root.is_dir():
            raise LoopError("Project root must be a directory")
        path = Path(state_path).expanduser() if state_path is not None else self.root / ".research-autopilot" / "simple-loop.sqlite3"
        if not path.is_absolute():
            path = self.root / path
        self.state_path = path.resolve()

    @contextmanager
    def _connection(self, create=False, readonly=False):
        if create:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.state_path.is_file():
            raise LoopError("Journal is not initialized")
        uri = self.state_path.as_uri() + ("?mode=ro" if readonly else "?mode=rwc" if create else "?mode=rw")
        connection = sqlite3.connect(uri, uri=True, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("BEGIN" if readonly else "BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self, idea, goal, max_iterations=None, max_repairs=3):
        """Create a journal once; do not reset a resumed goal or its counters."""
        contract = {"idea": _text(idea, "idea"), "goal": _text(goal, "goal"),
                    "max_iterations": None if max_iterations is None else _positive_integer(max_iterations, "max_iterations"),
                    "max_repairs": _positive_integer(max_repairs, "max_repairs")}
        with self._connection(create=True) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY CHECK(id=1), root TEXT NOT NULL, initial_contract TEXT NOT NULL, state TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS events (version INTEGER NOT NULL UNIQUE, event_id TEXT PRIMARY KEY, idea TEXT NOT NULL, revision INTEGER NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)")
            for operation in ("UPDATE", "DELETE"):
                connection.execute(f"CREATE TRIGGER IF NOT EXISTS events_no_{operation.lower()} BEFORE {operation} ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END")
            existing = connection.execute("SELECT * FROM project WHERE id=1").fetchone()
            if existing:
                state = self._load(connection)
                if existing["initial_contract"] != _json(contract):
                    raise LoopError("Existing initialization cannot replace the idea, goal or limits")
                return self._output(connection, state)
            state = {"schema_version": 1, "root": str(self.root), "goal": goal,
                     "active_idea": idea, "revision": 1, "phase": "inspect", "status": "active",
                     "version": 0, "next_action": "Inspect the existing method and choose its next important uncertainty",
                     "blocker": None, "wait": None, "pending_launch": None,
                     "limits": {"max_iterations": max_iterations, "max_repairs": max_repairs},
                     "counters": {"iterations": 0, "repairs": 0, "usage": {}},
                     "budget_exhausted": False, "reported_outcome": None,
                     "scientific_certification": False, "idea_history": [],
                     "milestones": [], "research_cycles": [],
                     "_progress_seen": [], "_issues": {}}
            connection.execute("INSERT INTO project VALUES (1,?,?,?)", (str(self.root), _json(contract), _json(state)))
            connection.execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (0, "__initialize__", idea, 1, _now(), _json({"kind": "initialize", **contract})))
            return self._output(connection, state)

    def _load(self, connection):
        try:
            row = connection.execute("SELECT * FROM project WHERE id=1").fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower():
                raise LoopError("Not a simple-loop journal") from exc
            raise
        if row is None:
            raise LoopError("Journal is not initialized")
        if row["root"] != str(self.root):
            raise LoopError("Journal project root does not match the bound root")
        state = json.loads(row["state"])
        if state.get("schema_version") != 1:
            raise LoopError("Unsupported journal schema version")
        state.setdefault("milestones", [])
        state.setdefault("research_cycles", [])
        return state

    def _output(self, connection, state):
        result = {key: value for key, value in state.items() if not key.startswith("_")}
        result["history"] = [{"version": row["version"], "idea": row["idea"],
                              "revision": row["revision"], "created_at": row["created_at"],
                              "event": json.loads(row["payload"])}
                             for row in connection.execute("SELECT * FROM events ORDER BY version")]
        return result

    def status(self):
        """Read a consistent snapshot. Reading never consumes iterations."""
        with self._connection(readonly=True) as connection:
            return self._output(connection, self._load(connection))

    def _evidence(self, refs, required=False):
        if not isinstance(refs, list) or (required and not refs):
            raise LoopError("Current evidence references are required")
        seen = set()
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
                raise LoopError("Evidence must contain exactly path and sha256")
            name = _text(ref["path"], "evidence path")
            if (PurePosixPath(name).is_absolute() or "\\" in name
                    or any(part in {"", ".", ".."} for part in name.split("/"))
                    or "\x00" in name):
                raise LoopError("Evidence paths must be safe project-relative paths")
            if name in seen:
                raise LoopError("Duplicate evidence path")
            seen.add(name)
            digest = ref["sha256"]
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise LoopError("Evidence sha256 must be a lowercase SHA-256 hash")
            # Walk with directory descriptors so no path component can redirect
            # the read outside the root. Symlink evidence is deliberately refused.
            descriptors = []
            try:
                directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                descriptors.append(directory)
                parts = name.split("/")
                for part in parts[:-1]:
                    directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    descriptors.append(directory)
                handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                descriptors.append(handle)
                if not stat.S_ISREG(os.fstat(handle).st_mode):
                    raise LoopError("Evidence must be a regular file")
                hasher = hashlib.sha256()
                while block := os.read(handle, 1024 * 1024):
                    hasher.update(block)
                if hasher.hexdigest() != digest:
                    raise LoopError(f"Evidence hash changed: {name}")
            except OSError as exc:
                raise LoopError(f"Evidence path cannot be safely read: {name}: {exc}") from exc
            finally:
                for descriptor in reversed(descriptors):
                    os.close(descriptor)

    def _validate(self, event):
        if not isinstance(event, dict):
            raise LoopError("Event must be an object")
        event_id = _text(event.get("event_id"), "event_id")
        if event_id.startswith("__"):
            raise LoopError("Reserved event ID")
        kind = event.get("kind")
        if not isinstance(kind, str) or kind not in FIELDS:
            raise LoopError("Unknown event kind")
        if set(event) - BASE_FIELDS - FIELDS[kind]:
            raise LoopError("Unexpected event fields")
        _text(event.get("reason"), "reason")
        if kind in ISSUE_KINDS:
            _text(event.get("issue"), "issue")
        if kind == "research_cycle" and "goal_contract_version" in event:
            version = event["goal_contract_version"]
            if type(version) is not int or version < 0:
                raise LoopError("research_cycle goal_contract_version must be a nonnegative integer")
        usage = event.get("usage", {})
        if not isinstance(usage, dict) or set(usage) - USAGE_FIELDS:
            raise LoopError("Unknown usage fields")
        for key, value in usage.items():
            if type(value) not in {int, float} or not math.isfinite(value) or value < 0:
                raise LoopError("Usage must be finite and nonnegative")
            if key in {"tokens", "cost_micro_usd"} and type(value) is not int:
                raise LoopError(f"{key} must be an integer")
        return _json(event)

    def _check_transition(self, state, event):
        kind = event["kind"]
        if kind in {"execution_receipt", "goal_revision"}:
            return  # Control/accounting observations do not reopen an idea.
        if state["status"] in {"completed", "retired"} and kind not in {"replace_idea", "budget_change", "reopen_idea"}:
            raise LoopError("This idea is closed; explicitly replace or reopen it to continue")
        if state["budget_exhausted"] and kind in WORK_KINDS:
            raise LoopError("Iteration budget exhausted; an explicit budget_change is required")
        if state["pending_launch"]:
            if (kind in {"uncertain_launch", "wake", "wait", "completion", "retire_idea", "replace_idea"}
                    or (kind in {"progress", "revision", "milestone"} and event.get("next_phase") == "experiment")):
                raise LoopError("Reconcile the retained launch identity before another run or finalization")
        elif state["wait"] and kind not in {"wake", "budget_change"}:
            if kind in {"progress", "revision", "milestone"}:
                phase = event.get("next_phase", "math" if kind == "revision" else None)
            elif kind == "research_cycle":
                phase = "analysis"
            elif kind in ROUTES:
                phase = event.get("target_phase", ROUTES[kind][0])
            else:
                phase = None
            if not isinstance(phase, str) or phase not in INDEPENDENT_PHASES:
                raise LoopError("The retained wait permits independent work; dependent work needs its matching wake")

    def _feedback(self, state, event):
        kind = event["kind"]
        phase, action = ROUTES[kind]
        if kind == "missing_evidence":
            phase = event.get("target_phase", phase)
            if not isinstance(phase, str) or phase not in PHASES - {"experiment", "verify", "delivery"}:
                raise LoopError("Missing evidence must route to work that can produce it")
        blocker = {"kind": kind, "issue": event.get("issue"), "reason": event["reason"]}
        if kind in ISSUE_KINDS:
            self._evidence(event.get("change_evidence", []))
            key = _json([state["active_idea"], event["issue"]])
            issue = state["_issues"].setdefault(key, {"consecutive": 0, "seen_change_hashes": []})
            changes = {ref["sha256"] for ref in event.get("change_evidence", [])}
            seen = set(issue.get("seen_change_hashes", []))
            # Read earlier in-development journals that recorded combinations.
            # Novel combinations of already observed bytes are not a new repair.
            for previous in issue.pop("seen_changes", []):
                seen.update(json.loads(previous))
            if changes - seen:
                issue["consecutive"] = 0
            issue["seen_change_hashes"] = sorted(seen | changes)
            issue["consecutive"] += 1
            reached = issue["consecutive"] >= state["limits"]["max_repairs"]
            blocker.update(consecutive_failures=issue["consecutive"], repair_limit_reached=reached)
            if reached:
                phase = "analysis"
                action = "Repeated failure requires a changed repair hypothesis, redesign or retirement; do not repeat the unchanged action"
        state.update(phase=phase, next_action=f"{action}: {event['reason']}", blocker=blocker)

    def _wait_or_reconcile(self, state, event):
        kind = event["kind"]
        identity = _text(event.get("identity"), "identity")
        if kind == "wait":
            condition = _text(event.get("condition"), "condition")
            state["wait"] = {"identity": identity, "condition": condition, "resume_phase": state["phase"]}
            state["next_action"] = f"Wait without model polling for {identity}: {condition}"
        elif kind == "wake":
            if not state["wait"] or state["wait"]["identity"] != identity:
                raise LoopError("Wake does not match the current wait identity")
            independent_action = state["wait"].get("independent_action")
            if independent_action:
                state["next_action"] = f"{independent_action}. External wait {identity} resolved: {event['reason']}"
            else:
                state["phase"] = state["wait"]["resume_phase"]
                state["next_action"] = f"Resume {state['phase']} after the recorded external observation: {event['reason']}"
            state["wait"] = None
        elif kind == "uncertain_launch":
            state["pending_launch"] = {"identity": identity, "idea": state["active_idea"],
                                       "revision": state["revision"], "recorded_version": state["version"] + 1}
            state.update(phase="reconcile", next_action=f"Observe and reconcile the same launch {identity}; do not launch a replacement")
        else:
            pending = state["pending_launch"]
            if pending is None or pending["identity"] != identity:
                raise LoopError("Reconciliation must match the retained launch identity")
            resolution = event.get("resolution")
            if not isinstance(resolution, str) or resolution not in {"unknown", "running", "completed", "failed", "not_started"}:
                raise LoopError("Reconciliation requires an observed resolution")
            if resolution in {"unknown", "running"}:
                state["phase"] = "reconcile"
                state["wait"] = ({"identity": identity, "condition": "Terminal evidence for the same retained launch",
                                  "resume_phase": "reconcile"} if resolution == "running" else None)
                state["next_action"] = f"Retain {identity}; await or collect its terminal observation without relaunching"
            else:
                state["pending_launch"] = None
                state["wait"] = None
                phase = {"completed": "verify", "failed": "diagnostic", "not_started": "experiment"}[resolution]
                state.update(phase=phase, next_action=f"Continue {phase} using the retained {identity} observation: {event['reason']}")

    def _budget_change(self, state, event):
        limits = event.get("limits")
        if not isinstance(limits, dict) or not limits or set(limits) - {"max_iterations", "max_repairs"}:
            raise LoopError("Budget change requires explicit supported limits")
        increased = False
        for key, value in limits.items():
            _positive_integer(value, key)
            current = state["limits"][key]
            if current is None:
                raise LoopError("An uncapped observation journal has no finite limit to increase")
            if value < current:
                raise LoopError("Budget change cannot reduce or reset existing limits")
            increased = increased or value > state["limits"][key]
        if not increased:
            raise LoopError("Budget change must explicitly increase at least one limit")
        state["limits"].update(limits)
        if state["status"] == "paused_budget":
            state["next_action"] = f"Resume {state['phase']} within the explicitly changed limits"

    def _apply(self, state, event):
        kind = event["kind"]
        self._check_transition(state, event)
        self._evidence(event.get("evidence", []), required=kind in {
            "progress", "completion", "valid_negative_result", "revision", "wake", "reconcile", "milestone",
            "research_cycle", "execution_receipt", "goal_revision", "reopen_idea"})
        if kind in {"progress", "revision"}:
            phase = event.get("next_phase")
            if kind == "revision":
                phase = event.get("next_phase", "math")
            if not isinstance(phase, str) or phase not in PHASES:
                raise LoopError("Progress requires an explicit next_phase")
            hashes = {ref["sha256"] for ref in event["evidence"]}
            if kind == "progress" and not hashes - set(state["_progress_seen"]):
                raise LoopError("Repeated observation is not progress; provide new evidence")
            state["_progress_seen"] = sorted(set(state["_progress_seen"]) | hashes)
            if kind == "revision":
                state["revision"] += 1
            state.update(phase=phase, blocker=None, next_action=f"Continue {phase}: {event['reason']}")
        elif kind == "milestone":
            label = _text(event.get("label"), "milestone label")
            phase = event.get("next_phase")
            if phase not in PHASES:
                raise LoopError("Milestone requires an explicit next_phase")
            state["milestones"].append({"event_id": event["event_id"], "idea": state["active_idea"],
                                        "revision": state["revision"], "label": label, "reason": event["reason"], "evidence": event["evidence"]})
            state.update(phase=phase, blocker=None, next_action=f"Milestone observed: {label}; continue {phase}")
        elif kind == "research_cycle":
            for field in ("hypothesis", "prediction", "result", "interpretation", "next_action"):
                _text(event.get(field), f"research_cycle {field}")
            state["research_cycles"].append({**event, "idea": state["active_idea"], "revision": state["revision"]})
            state.update(phase="analysis", blocker=None, current_question=event["hypothesis"], next_action=event["next_action"])
        elif kind == "execution_receipt":
            pass  # Usage below is cumulative; no phase, closure or iteration change.
        elif kind == "goal_revision":
            state["goal"] = _text(event.get("goal"), "revised goal")
        elif kind == "reopen_idea":
            if state["status"] not in {"completed", "retired"}:
                raise LoopError("Only a closed idea can be explicitly reopened")
            phase = event.get("next_phase", "inspect")
            if phase not in PHASES:
                raise LoopError("Reopen requires a known next_phase")
            state["idea_history"].append({"idea": state["active_idea"], "revision": state["revision"] + 1,
                                         "status": "reopened", "reopen_event": event["event_id"], "reason": event["reason"]})
            state.update(status="active", revision=state["revision"] + 1, phase=phase, reported_outcome=None,
                         blocker=None, current_question=event["reason"], next_action=f"Reopened {state['active_idea']}: {event['reason']}")
        elif kind in {"completion", "retire_idea"}:
            if kind == "completion" and (not isinstance(event.get("outcome"), str) or event["outcome"] not in OUTCOMES):
                raise LoopError("Completion requires a scoped reported outcome")
            state.update(status="completed" if kind == "completion" else "retired", phase="delivery", reported_outcome=event.get("outcome"),
                         blocker=None, next_action="Deliver the reported outcome and its evidence; this is not scientific certification")
            state["idea_history"].append({"idea": state["active_idea"], "revision": state["revision"],
                                         "status": state["status"], "reported_outcome": state["reported_outcome"],
                                         "terminal_event": event["event_id"], "reason": event["reason"]})
        elif kind == "replace_idea":
            if state["status"] not in {"completed", "retired"}:
                raise LoopError("Retire or complete the current idea before replacement")
            idea = _text(event.get("idea"), "idea")
            if idea == state["active_idea"] or any(old["idea"] == idea for old in state["idea_history"]):
                raise LoopError("Replacement must use a new serial idea identity")
            state.update(active_idea=idea, revision=1, phase="inspect", status="active", reported_outcome=None,
                         blocker=None, current_question=f"Inspect replacement idea {idea}",
                         next_action="Inspect the replacement idea; preserve the previous negative evidence and cumulative budgets")
        elif kind in {"wait", "wake", "uncertain_launch", "reconcile"}:
            self._wait_or_reconcile(state, event)
        elif kind == "budget_change":
            self._budget_change(state, event)
        else:
            self._feedback(state, event)
        if kind in WORK_KINDS:
            state["counters"]["iterations"] += 1
        if kind in ISSUE_KINDS:
            state["counters"]["repairs"] += 1
        for key, value in event.get("usage", {}).items():
            state["counters"]["usage"][key] = state["counters"]["usage"].get(key, 0) + value
        if state["wait"] and not state["pending_launch"] and kind in WORK_KINDS:
            state["wait"]["independent_action"] = state["next_action"]
        cap = state["limits"]["max_iterations"]
        state["budget_exhausted"] = cap is not None and state["counters"]["iterations"] >= cap
        if state["status"] not in {"completed", "retired"}:
            if state["pending_launch"]:
                state["status"] = "waiting" if state["wait"] else "reconcile_required"
            elif state["wait"] and not state["wait"].get("independent_action"):
                state["status"] = "waiting"
            else:
                state["status"] = "paused_budget" if state["budget_exhausted"] else "active"
            if state["status"] == "paused_budget":
                state["next_action"] = f"Iteration budget exhausted; explicitly change the budget before continuing {state['phase']}"
            elif state["wait"] and not state["pending_launch"] and state["wait"].get("independent_action"):
                wait = state["wait"]
                state["next_action"] = (f"{wait['independent_action']}. Independent work only; retain wait "
                                        f"{wait['identity']}: {wait['condition']}. Matching wake is required "
                                        "before an experiment or finalization")

    def record(self, event, expected_version):
        """Append an observation atomically; never approve or launch an experiment."""
        with self._connection() as connection:
            return self.record_in_transaction(connection, event, expected_version)

    def record_in_transaction(self, connection, event, expected_version):
        """Runner integration: join the caller's transaction in this same database."""
        payload = self._validate(event)
        event = json.loads(payload)
        if type(expected_version) is not int or expected_version < 0:
            raise LoopError("Expected version must be a nonnegative integer")
        state = self._load(connection)
        existing = connection.execute("SELECT payload FROM events WHERE event_id=?", (event["event_id"],)).fetchone()
        if existing:
            if existing["payload"] != payload:
                raise LoopError("Existing event ID conflicts with different content")
            return self._output(connection, state)
        if state["version"] != expected_version:
            raise LoopError(f"Expected version {expected_version}, current version {state['version']}")
        self._apply(state, event)
        state["version"] += 1
        connection.execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (state["version"], event["event_id"], state["active_idea"], state["revision"], _now(), payload))
        connection.execute("UPDATE project SET state=? WHERE id=1", (_json(state),))
        return self._output(connection, state)


def main(argv=None):
    """JSON-in/JSON-out CLI; it has no command execution or provider backend."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Existing project root")
    parser.add_argument("--state-path", help="Optional journal path; relative paths are under the project")
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init", help="Initialize once, or resume an identical initialization")
    initialize.add_argument("--idea", required=True)
    initialize.add_argument("--goal", required=True)
    initialize.add_argument("--max-iterations", type=int, default=None, help="Optional explicit observation cap; omitted means no observation-count cap")
    initialize.add_argument("--max-repairs", type=int, default=3)
    commands.add_parser("status", help="Read persisted state and append-only history")
    record = commands.add_parser("record", help="Append a versioned observation from a JSON file")
    record.add_argument("--event", required=True)
    record.add_argument("--expected-version", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        loop = SimpleLoop(args.root, state_path=args.state_path)
        if args.command == "init":
            result = loop.initialize(args.idea, args.goal, args.max_iterations, args.max_repairs)
        elif args.command == "status":
            result = loop.status()
        else:
            event = json.loads(Path(args.event).read_text(encoding="utf-8"))
            result = loop.record(event, args.expected_version)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (LoopError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
