import hashlib
import json
from pathlib import Path

STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
manifest_path = STATE / "manifest.json"
current_path = PROJECT / "CURRENT.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


old = json.loads(manifest_path.read_text())
files = dict(old["files"])
files.pop("execution_windows/wake20/evidence/finalize_manifest.json", None)
for stale in [name for name in files if name.startswith("execution_windows/wake20/deps/")]:
    files.pop(stale)
for path in sorted(STATE.rglob("*")):
    relative = path.relative_to(STATE).as_posix()
    if (
        path.is_file()
        and path != manifest_path
        and path.name != "finalize_manifest.json"
        and not relative.startswith("execution_windows/wake20/deps/")
    ):
        files[relative] = sha(path)

manifest = {
    "generation": 21,
    "created_utc": "2026-10-12T15:56:00+00:00",
    "library_file_id": old["library_file_id"],
    "previous_generation": 20,
    "previous_library_version": old["previous_library_version"],
    "previous_archive_sha256": old["previous_archive_sha256"],
    "goal_mode": "continuous_research",
    "science_identity": "one active idea; hybrid-window passed all frozen TICO development promotion rules; fresh Tatoeba confirmation protocol frozen before text download or scoring",
    "files": dict(sorted(files.items())),
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
current = json.loads(current_path.read_text())
assert current["generation"] == 21 and current["manifest_sha256"] == "PENDING_FINALIZE"
current["manifest_sha256"] = sha(manifest_path)
current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"generation": 21, "files": len(files), "manifest_sha256": current["manifest_sha256"]}, indent=2))
