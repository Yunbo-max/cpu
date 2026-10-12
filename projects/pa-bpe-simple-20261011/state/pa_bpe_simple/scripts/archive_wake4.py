"""Verify the Wake 4 handoff and build generation 5 of the canonical archive.

Administrative packaging only; this script does not launch scientific work.
"""
import datetime
import hashlib
import json
from pathlib import Path
import sys
import zipfile


root = Path(__file__).resolve().parents[1]
destination = Path(sys.argv[1]).resolve()


def load(relative):
    return json.loads((root / relative).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


old_manifest = load("manifest.json")
if old_manifest["generation"] != 4:
    raise RuntimeError("Expected generation 4 as the packaging parent")

owner = load(".writer.lock/owner.json")
if owner["owner"] != "automation-wake4-20261011T2126Z":
    raise RuntimeError("Current process does not own the project writer lock")

changed_existing = [
    name
    for name, sha256 in old_manifest["files"].items()
    if not (root / name).is_file() or digest(root / name) != sha256
]
allowed_changes = {"PA_BPE_Simple_Checkpoint.md", "phase_budget.json"}
unexpected = sorted(set(changed_existing) - allowed_changes)
if unexpected:
    raise RuntimeError(f"Unexpected historical member changes: {unexpected}")

status = load("evidence/wake4_final_status.json")
if len(status["attempts"]) != 8:
    raise RuntimeError("Wake 4 attempt count is not eight")
if not all(attempt["receipt"]["status"] == "succeeded" for attempt in status["attempts"]):
    raise RuntimeError("A Wake 4 scientific attempt is not successful")
if status["budget"]["reserved_seconds"] != 0:
    raise RuntimeError("Wake 4 has a nonzero command reservation")

budget = load("phase_budget.json")
if budget["goal_mode"] != "continuous_research":
    raise RuntimeError("Continuous-research authorization was lost")
if budget["cumulative_charged_seconds"] != 770.0206822679628:
    raise RuntimeError("Cumulative scientific wall does not match the final receipt ledger")

replay = load("execution_windows/wake4/output/training_trace_replay.json")
for arm, result in replay["arms"].items():
    required = (
        result["steps_replayed"] == 1000
        and result["all_selected_train_and_dev_gains_match"]
        and result["all_trace_lengths_match"]
        and result["merge_file_matches_trace"]
        and result["independent_final_totals_match"]
    )
    if not required:
        raise RuntimeError(f"Replay verification failed for {arm}")

tables = load("execution_windows/wake4/output/efficiency_table_verification.json")
if tables["integer_cost_tables_checked"] != 36 or not tables["arithmetic_passed"]:
    raise RuntimeError("Integer-table verification is incomplete")
if tables["prediction_checks"] != {
    "cost_lower_than_full_minmax": False,
    "gini_lower_than_full_pooled": True,
}:
    raise RuntimeError("Prediction-check record changed")

process_check = (root / "evidence/wake4_science_process_check.txt").read_text()
if process_check.strip():
    raise RuntimeError("Scientific-process check is not empty")

members = []
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if any(part in (".writer.lock", "__pycache__") for part in relative.parts):
        continue
    if path.is_symlink():
        raise RuntimeError(f"Unreviewed symlink in checkpoint: {relative}")
    if not path.is_file():
        continue
    if path.suffix in (".pyc", ".lock") or path.name.endswith(("-wal", "-shm")):
        continue
    if relative.as_posix() == "manifest.json":
        continue
    members.append(path)

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest = {
    "generation": 5,
    "created_utc": now,
    "library_file_id": "libfile_8bb70b367b948191bfed83a45933917f",
    "previous_generation": 4,
    "previous_library_version": 4,
    "previous_archive_sha256": "47b9c8e6688dec17da28c7205b29f3fdcf64297576fa0f373f646e71ec83a49e",
    "goal_mode": "continuous_research",
    "science_identity": "pa-bpe-domain-robustness revision1; method4",
    "files": {str(path.relative_to(root)): digest(path) for path in members},
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

destination.parent.mkdir(parents=True, exist_ok=True)
if destination.exists():
    raise RuntimeError("Refuse to replace a local archive")
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in members + [root / "manifest.json"]:
        archive.write(path, "pa_bpe_simple/" + str(path.relative_to(root)))

with zipfile.ZipFile(destination) as archive:
    if archive.testzip() is not None:
        raise RuntimeError("Archive CRC verification failed")
    for name, sha256 in manifest["files"].items():
        observed = hashlib.sha256(archive.read("pa_bpe_simple/" + name)).hexdigest()
        if observed != sha256:
            raise RuntimeError(f"Archive member hash mismatch: {name}")

print(
    json.dumps(
        {
            "archive": str(destination),
            "sha256": digest(destination),
            "size_bytes": destination.stat().st_size,
            "generation": 5,
            "manifest_files": len(members),
            "historical_members_checked": len(old_manifest["files"]),
            "changed_historical_members": changed_existing,
        },
        ensure_ascii=False,
    )
)
