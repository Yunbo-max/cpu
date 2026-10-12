"""Verify Wake 6 state and build generation 7 of the canonical checkpoint."""
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
if old_manifest["generation"] != 6:
    raise RuntimeError("Expected generation 6 parent")
owner = load(".writer.lock/owner.json")
if owner["owner"] != "automation-wake6-20261011T2326Z":
    raise RuntimeError("Wake 6 does not own project writer lock")

changed = [
    name for name, sha256 in old_manifest["files"].items()
    if not (root / name).is_file() or digest(root / name) != sha256
]
allowed = {"PA_BPE_Simple_Checkpoint.md", "phase_budget.json"}
unexpected = sorted(set(changed) - allowed)
if unexpected:
    raise RuntimeError(f"Unexpected historical changes: {unexpected}")

state = load("evidence/wake6_final_state.json")
if state["attempts_used"] != 3 or state["reserved_seconds"] != 0:
    raise RuntimeError("Wake 6 attempt/reservation ledger mismatch")
if any(task["state"] != "succeeded" or task["exit_code"] != 0 for task in state["tasks"]):
    raise RuntimeError("Expected three successful Wake 6 tasks")

budget = load("phase_budget.json")
if budget["goal_mode"] != "continuous_research":
    raise RuntimeError("Continuous research authorization lost")
if abs(budget["cumulative_charged_seconds"] - 780.2824448219634) > 1e-12:
    raise RuntimeError("Cumulative wall ledger mismatch")

verification = load("execution_windows/wake6/output/conditional_shift_verification.json")
if not verification["all_passed"] or verification["checks"] != 2342:
    raise RuntimeError("Conditional-shift verification failed")

support = load("execution_windows/wake6/output/joint_support_diagnostic.json")
if support["full_3x4"]["estimable"]:
    raise RuntimeError("Joint support stop conclusion changed")
if support["full_3x4"]["books_positive_tico_empty"] != [["zero", "q4"]]:
    raise RuntimeError("Joint support empty-cell record changed")

review = load("review/wake6_conditional_shift_acceptance.json")
if review["status"] != "accepted":
    raise RuntimeError("Independent review not accepted")

for relative, sha256 in state["outputs"].items():
    if digest(root / relative) != sha256:
        raise RuntimeError(f"Wake 6 output hash mismatch: {relative}")

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
    "generation": 7,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "library_file_id": "libfile_8bb70b367b948191bfed83a45933917f",
    "previous_generation": 6,
    "previous_library_version": 6,
    "previous_archive_sha256": "4867648e58ebd652d7feed97422a1b686765ef8946dee7a8f056081c1800e8f4",
    "goal_mode": "continuous_research",
    "science_identity": "pa-bpe-domain-robustness revision1; conditional-shift partition-dependence audit",
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
    "generation": 7,
    "manifest_files": len(members),
    "historical_members_checked": len(old_manifest["files"]),
    "changed_historical_members": changed,
}))
