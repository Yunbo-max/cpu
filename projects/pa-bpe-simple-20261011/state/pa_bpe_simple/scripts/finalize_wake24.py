import hashlib
import json
from pathlib import Path


STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
MANIFEST = STATE / "manifest.json"
CURRENT = PROJECT / "CURRENT.json"
BUDGET = STATE / "phase_budget.json"
WAKE_INPUT_PREFIX = "execution_windows/wake24/inputs/"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


budget = json.loads(BUDGET.read_text())
assert budget["updated_utc"] in {"2026-10-13T06:56:00+00:00", "2026-10-13T07:39:38+00:00"}
budget["updated_utc"] = "2026-10-13T07:39:38+00:00"
window = {
    "id": "wake24-20261013",
    "root": "/workspace/scratch/42f1128b703b/pa_bpe_wake24_0mRbHc/repo/projects/pa-bpe-simple-20261011/state/pa_bpe_simple/execution_windows/wake24",
    "attempts": 2,
    "wall_seconds": 0.7278988190009841,
    "reserved_seconds": 0,
    "status": "source_gap_globalvoices_raw_required",
    "scientific_processes_active": 0,
    "receipt_inventory": "execution_windows/wake24/.research-autopilot/runner/attempts",
    "notes": "Result-blind contamination-source audit. First exit0 attempt invalidated because SQLite updated pinned WAL SHM; explicit replacement queried an isolated copy and succeeded with 24 immutable inputs. Stored GlobalVoices regex-word shingles are incompatible with the frozen whitespace-token rule, and raw archives are absent from the GitHub archive index. No selection, tokenizer or fairness score. Per-process CPU/RSS were not recorded and remain unknown."
}
matches = [index for index, row in enumerate(budget["windows"]) if row["id"] == "wake24-20261013"]
if matches:
    assert matches == [len(budget["windows"]) - 1]
    budget["windows"][matches[0]] = window
else:
    budget["windows"].append(window)
budget["cumulative_charged_seconds"] = 1946.8987242219716
BUDGET.write_text(json.dumps(budget, indent=2, ensure_ascii=False) + "\n")

current = json.loads(CURRENT.read_text())
assert current["generation"] in {24, 25}
current.update({
    "generation": 25,
    "manifest_sha256": "PENDING_FINALIZE",
    "external_raw_source_required_for_next_step": True,
    "next_action": "Recover and hash-verify the three frozen OPUS GlobalVoices raw archives, reconstruct the exact 512x3 units, rebuild whitespace-token fingerprints, then apply the complete contamination inventory to the 38091 eligible triangles and independently verify deterministic selection",
    "active_science_processes": 0,
    "reserved_seconds": 0,
    "confirmation_outcome_status": "Stored GlobalVoices shingles are incompatible with the frozen Tatoeba whitespace-token rule and raw text is absent from the GitHub archive index; contamination decision, development selection and tokenizer fairness scoring remain HOLD."
})
CURRENT.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")

old = json.loads(MANIFEST.read_text())
assert old["generation"] in {24, 25}
files = dict(old["files"])
for path in sorted(STATE.rglob("*")):
    if not path.is_file() or path == MANIFEST:
        continue
    relative = path.relative_to(STATE).as_posix()
    if relative.startswith(WAKE_INPUT_PREFIX):
        continue
    files[relative] = sha(path)

manifest = {
    "generation": 25,
    "created_utc": "2026-10-13T07:39:38+00:00",
    "library_file_id": old["library_file_id"],
    "previous_generation": 24,
    "previous_library_version": old["previous_library_version"],
    "previous_archive_sha256": old["previous_archive_sha256"],
    "goal_mode": "continuous_research",
    "science_identity": "Frozen contamination-source audit rejects persisted GlobalVoices fingerprints as incompatible with the Tatoeba whitespace-token rule; raw archives must be recovered before contamination filtering, deterministic development selection or tokenizer fairness scoring",
    "files": dict(sorted(files.items())),
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
current["manifest_sha256"] = sha(MANIFEST)
CURRENT.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")

print(json.dumps({
    "generation": 25,
    "files": len(files),
    "manifest_sha256": current["manifest_sha256"],
    "cumulative_charged_seconds": budget["cumulative_charged_seconds"],
    "wake24_inputs_excluded_from_manifest": True,
}, indent=2))
