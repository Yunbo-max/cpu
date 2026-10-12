"""Verify Wake 10 state and build generation 11 of the canonical checkpoint."""
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
if old_manifest["generation"] != 10:
    raise RuntimeError("Expected generation 10 parent")
owner = load(".writer.lock/owner.json")
if owner["owner"] != "automation-wake10-20261012T0326Z":
    raise RuntimeError("Wake 10 does not own project writer lock")

changed = [
    name for name, sha256 in old_manifest["files"].items()
    if not (root / name).is_file() or digest(root / name) != sha256
]
allowed = {"PA_BPE_Simple_Checkpoint.md", "phase_budget.json"}
unexpected = sorted(set(changed) - allowed)
if unexpected:
    raise RuntimeError(f"Unexpected historical changes: {unexpected}")

state = load("evidence/wake10_final_status.json")
if state["budget"]["attempts_used"] != 4 or state["budget"]["reserved_seconds"] != 0:
    raise RuntimeError("Wake 10 attempt/reservation ledger mismatch")
if any(a["state"] != "terminal" or a.get("result") != "succeeded" for a in state["attempts"]):
    raise RuntimeError("Expected four successful Wake 10 tasks")

budget = load("phase_budget.json")
if budget["goal_mode"] != "continuous_research":
    raise RuntimeError("Continuous research authorization lost")
if abs(budget["cumulative_charged_seconds"] - 874.3221149459877) > 1e-12:
    raise RuntimeError("Cumulative wall ledger mismatch")

verification = load("execution_windows/wake10/output/row_selection_verification_v2.json")
if not verification["all_checks_passed"] or len(verification["checks"]) != 25:
    raise RuntimeError("Wake 10 revised verification failed")
review = load("review/wake10_row_selection_acceptance.json")
if review["coordinator_decision"]["extended_software_and_author_parser_invariants"] != "PASS":
    raise RuntimeError("Independent review not accepted")
if review["coordinator_decision"]["payload_sampling_acceptance"] != "HOLD":
    raise RuntimeError("Payload gate changed unexpectedly")

members = []
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if any(part in (".writer.lock", "__pycache__", ".venv") for part in relative.parts):
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
    "generation": 11,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "library_file_id": "libfile_8bb70b367b948191bfed83a45933917f",
    "previous_generation": 10,
    "previous_library_version": 10,
    "previous_archive_sha256": "4f144fd91536fdedecd262d968b333c00b0e004890fd19eeb15cfa8fdbcee784",
    "goal_mode": "continuous_research",
    "science_identity": "pa-bpe-domain-robustness revision1; deterministic row-selection and exact pretoken-budget parser contract verified, production payload/training HOLD",
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
    "generation": 11,
    "manifest_files": len(members),
    "manifest_sha256": digest(root / "manifest.json"),
    "historical_members_checked": len(old_manifest["files"]),
    "changed_historical_members": changed,
}))
