#!/usr/bin/env python3
"""Incrementally finalize generation 26 without dropping sparse history."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
MANIFEST = STATE / "manifest.json"
CURRENT = PROJECT / "CURRENT.json"


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


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["generation"] = 26
    manifest["created_utc"] = "2026-10-13T08:48:00+00:00"
    manifest["previous_generation"] = 25
    manifest["science_identity"] = (
        "Exact frozen GlobalVoices archives recovered from the persisted bundle; a whitespace-token "
        "fingerprint index was rebuilt and independently recomputed for all 1536 unit-language rows. "
        "Complete-inventory Tatoeba contamination filtering, development selection and tokenizer "
        "fairness scoring remain on hold."
    )
    files = manifest["files"]
    for path in sorted(STATE.rglob("*")):
        if not path.is_file() or path == MANIFEST or path.is_symlink():
            continue
        relative = path.relative_to(STATE).as_posix()
        if relative.startswith("execution_windows/wake25/inputs/"):
            raise RuntimeError("private wake25 inputs must not enter the manifest")
        files[relative] = file_sha256(path)
    manifest["files"] = dict(sorted(files.items()))
    atomic_json(MANIFEST, manifest)

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current["generation"] != 26:
        raise RuntimeError("CURRENT generation was not advanced to 26")
    current["manifest_sha256"] = file_sha256(MANIFEST)
    atomic_json(CURRENT, current)
    print(json.dumps({
        "generation": 26,
        "manifest_sha256": current["manifest_sha256"],
        "manifest_entries": len(manifest["files"]),
    }))


if __name__ == "__main__":
    main()
