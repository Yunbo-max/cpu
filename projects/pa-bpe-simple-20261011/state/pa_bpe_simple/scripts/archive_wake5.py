"""Verify Wake 5 state and build generation 6 of the canonical checkpoint."""
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
if old_manifest["generation"] != 5:
    raise RuntimeError("Expected generation 5 parent")
owner = load(".writer.lock/owner.json")
if owner["owner"] != "automation-wake5-20261011T2226Z":
    raise RuntimeError("Wake 5 does not own project writer lock")

changed = [
    name for name, sha256 in old_manifest["files"].items()
    if not (root / name).is_file() or digest(root / name) != sha256
]
allowed = {"PA_BPE_Simple_Checkpoint.md", "phase_budget.json"}
unexpected = sorted(set(changed) - allowed)
if unexpected:
    raise RuntimeError(f"Unexpected historical changes: {unexpected}")

state = load("evidence/wake5_final_state.json")
if state["attempts_used"] != 3 or state["reserved_seconds"] != 0:
    raise RuntimeError("Wake 5 attempt/reservation ledger mismatch")
if [task["state"] for task in state["tasks"]].count("succeeded") != 2:
    raise RuntimeError("Expected two successful Wake 5 tasks")
if [task["state"] for task in state["tasks"]].count("failed") != 1:
    raise RuntimeError("Expected one retained Wake 5 failure")

budget = load("phase_budget.json")
if budget["goal_mode"] != "continuous_research":
    raise RuntimeError("Continuous research authorization lost")
if budget["cumulative_charged_seconds"] != 772.9383674239524:
    raise RuntimeError("Cumulative wall ledger mismatch")

audit = load("execution_windows/wake5/output/mass_cancellation_audit.json")
if not audit["verification"]["all_available_stored_fields_passed"]:
    raise RuntimeError("Mass audit verification failed")
if audit["arms_with_tico_cancellation_mismatch"]:
    raise RuntimeError("Recorded TICO mismatch conclusion changed")
if audit["arms_with_stable_books_cancellation_mismatch"]:
    raise RuntimeError("Recorded Books mismatch conclusion changed")
if audit["arms_with_stable_books_aligned_improvement"]:
    raise RuntimeError("Recorded Books aligned conclusion changed")

expected_outputs = state["outputs"]
for relative, sha256 in expected_outputs.items():
    if digest(root / relative) != sha256:
        raise RuntimeError(f"Wake 5 output hash mismatch: {relative}")

members = []
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if any(part in (".writer.lock", "__pycache__") for part in relative.parts):
        continue
    if path.is_symlink():
        raise RuntimeError(f"Unreviewed symlink: {relative}")
    if not path.is_file():
        continue
    if path.suffix in (".pyc", ".lock") or path.name.endswith(("-wal", "-shm")):
        continue
    if relative.as_posix() == "manifest.json":
        continue
    members.append(path)

manifest = {
    "generation": 6,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "library_file_id": "libfile_8bb70b367b948191bfed83a45933917f",
    "previous_generation": 5,
    "previous_library_version": 5,
    "previous_archive_sha256": "7eef55a8365196eb5a67483fc13d90bd5d2854d7a67b8e1f8753bedcb98438fa",
    "goal_mode": "continuous_research",
    "science_identity": "pa-bpe-domain-robustness revision1; objective/cancellation mechanism audit",
    "files": {str(path.relative_to(root)): digest(path) for path in members},
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

if destination.exists():
    raise RuntimeError("Refuse to replace local archive")
destination.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in members + [root / "manifest.json"]:
        archive.write(path, "pa_bpe_simple/" + str(path.relative_to(root)))
with zipfile.ZipFile(destination) as archive:
    if archive.testzip() is not None:
        raise RuntimeError("Archive CRC failure")
    for name, sha256 in manifest["files"].items():
        if hashlib.sha256(archive.read("pa_bpe_simple/" + name)).hexdigest() != sha256:
            raise RuntimeError(f"Archive member mismatch: {name}")

print(json.dumps({
    "archive": str(destination),
    "sha256": digest(destination),
    "size_bytes": destination.stat().st_size,
    "generation": 6,
    "manifest_files": len(members),
    "historical_members_checked": len(old_manifest["files"]),
    "changed_historical_members": changed,
}))
