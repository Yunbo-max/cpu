#!/usr/bin/env python3
"""Incrementally finalize generation 27 without dropping sparse history."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
MANIFEST = STATE / "manifest.json"
CURRENT = PROJECT / "CURRENT.json"
PHASE_BUDGET = STATE / "phase_budget.json"
CREATED = "2026-10-13T09:22:30+00:00"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def update_budget() -> None:
    budget = json.loads(PHASE_BUDGET.read_text(encoding="utf-8"))
    if any(item["id"] == "wake26-20261013" for item in budget["windows"]):
        raise RuntimeError("wake26 budget entry already exists")
    budget["updated_utc"] = CREATED
    budget["windows"].append({
        "id": "wake26-20261013",
        "root": "/workspace/scratch/42f1128b703b/pa_bpe_wake26_GPc4rMEd/runner",
        "attempts": 1,
        "wall_seconds": 12.868660200001614,
        "reserved_seconds": 0,
        "status": "selector_repaired_waiting_for_memory_selection_hold",
        "scientific_processes_active": 0,
        "receipt_inventory": "execution_windows/wake26/.research-autopilot/runner/attempts",
        "notes": "One retained exit1 attempt exposed an incorrect 947 row-count assertion before candidate decisions. Both primary and independent verifier were corrected to 946 and compiled. No replacement started because three bounded memory rechecks ended below the 746586112-byte restart threshold. No OOM, selection, tokenizer or fairness result; continuous goal remains active."
    })
    atomic_json(PHASE_BUDGET, budget)


def update_current() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current["generation"] != 26:
        raise RuntimeError(f"expected generation 26, found {current['generation']}")
    current["generation"] = 27
    current["next_action"] = (
        "Recheck shared cgroup memory and unknown/duplicate PA-BPE jobs; only with at least "
        "746586112 bytes headroom, submit corrected wake26-tatoeba-selection-v2 superseding v1, "
        "then independently verify the deterministic 1024-row development selection before tokenizer scoring"
    )
    current["active_science_processes"] = 0
    current["reserved_seconds"] = 0
    current["confirmation_outcome_status"] = (
        "The complete-inventory selector and independent verifier are implemented and corrected, but the only "
        "attempt failed before candidate decisions on a repaired 946-row assertion. The corrected experiment "
        "was not rerun because latest memory headroom was below the 746586112-byte threshold. Development "
        "selection, independent verification, tokenizer training and fairness scoring remain HOLD."
    )
    atomic_json(CURRENT, current)


def update_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["generation"] = 27
    manifest["created_utc"] = CREATED
    manifest["previous_generation"] = 26
    manifest["science_identity"] = (
        "A complete-inventory Tatoeba selector attempt failed before candidate decisions on an incorrect "
        "Alice/Poe row-count assertion. Both primary and independent implementations were corrected to 946 "
        "and compiled, but rerun remains waiting for the evidence-based memory threshold; no selection, "
        "tokenizer or fairness result exists."
    )
    files = manifest["files"]
    for path in sorted(STATE.rglob("*")):
        if not path.is_file() or path == MANIFEST or path.is_symlink():
            continue
        relative = path.relative_to(STATE).as_posix()
        if relative.startswith("execution_windows/wake26/inputs/") or relative.startswith("execution_windows/wake26/scratch/"):
            raise RuntimeError("private wake26 inputs or scratch must not enter the manifest")
        files[relative] = file_sha256(path)
    manifest["files"] = dict(sorted(files.items()))
    atomic_json(MANIFEST, manifest)

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current["generation"] != 27:
        raise RuntimeError("CURRENT generation was not advanced to 27")
    current["manifest_sha256"] = file_sha256(MANIFEST)
    atomic_json(CURRENT, current)


def main() -> None:
    update_budget()
    update_current()
    update_manifest()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    print(json.dumps({
        "generation": 27,
        "manifest_sha256": current["manifest_sha256"],
        "manifest_entries": len(manifest["files"]),
    }))


if __name__ == "__main__":
    main()
