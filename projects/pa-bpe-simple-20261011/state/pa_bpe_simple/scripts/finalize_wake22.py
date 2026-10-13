import hashlib
import json
from pathlib import Path

STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
manifest_path = STATE / "manifest.json"
current_path = PROJECT / "CURRENT.json"
budget_path = STATE / "phase_budget.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


budget = json.loads(budget_path.read_text())
assert not any(row["id"] == "wake22-20261013" for row in budget["windows"])
budget["updated_utc"] = "2026-10-13T05:46:10+00:00"
budget["windows"].append({
    "id": "wake22-20261013",
    "root": "/workspace/scratch/42f1128b703b/pa_bpe_wake22_20261013T0535/repo/projects/pa-bpe-simple-20261011/state/pa_bpe_simple/execution_windows/wake22",
    "attempts": 1,
    "wall_seconds": 0.08367272399937065,
    "reserved_seconds": 0,
    "status": "stopped_after_source_semantics_milestone_waiting_for_memory",
    "scientific_processes_active": 0,
    "receipt_inventory": "execution_windows/wake22/.research-autopilot/runner/attempts",
    "notes": "Official exporter source audit identified unequal sentence/link eligibility predicates. One low-memory task succeeded; fixed source restore and membership audit did not start because shared headroom stayed below the unchanged 512MiB guard. Four management CLI errors were repaired before creating any extra scientific attempt."
})
budget["cumulative_charged_seconds"] = 1923.041858638973
budget_path.write_text(json.dumps(budget, indent=2, ensure_ascii=False) + "\n")

current = json.loads(current_path.read_text())
assert current["generation"] == 22
current.update({
    "generation": 23,
    "manifest_sha256": "PENDING_FINALIZE",
    "next_action": "Remeasure shared memory; at >=536870912 bytes headroom restore six fixed Tatoeba archives and execute the separately versioned eligible-inner-join membership audit before any selection or scoring",
    "active_science_processes": 0,
    "reserved_seconds": 0,
    "confirmation_outcome_status": "Official export semantics explain the744 missing-endpoint edges; strict protocol v1 remains failed; revised eligible-join protocol is unexecuted and waiting for memory; no confirmation score."
})
current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")

old = json.loads(manifest_path.read_text())
files = dict(old["files"])
for path in sorted(STATE.rglob("*")):
    if path.is_file() and path != manifest_path:
        files[path.relative_to(STATE).as_posix()] = sha(path)

manifest = {
    "generation": 23,
    "created_utc": "2026-10-13T05:46:10+00:00",
    "library_file_id": old["library_file_id"],
    "previous_generation": 22,
    "previous_library_version": old["previous_library_version"],
    "previous_archive_sha256": old["previous_archive_sha256"],
    "goal_mode": "continuous_research",
    "science_identity": "Official Tatoeba export rules explain744 missing-endpoint edges; strict v1 retained failed; eligible-inner-join repair specified but fixed-source membership audit unstarted due shared-memory wait; no confirmation score",
    "files": dict(sorted(files.items())),
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
current["manifest_sha256"] = sha(manifest_path)
current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({
    "generation": 23,
    "files": len(files),
    "manifest_sha256": current["manifest_sha256"],
    "cumulative_charged_seconds": budget["cumulative_charged_seconds"],
}, indent=2))
