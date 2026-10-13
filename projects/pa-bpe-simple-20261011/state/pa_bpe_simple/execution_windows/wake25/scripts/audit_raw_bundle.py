#!/usr/bin/env python3
"""Audit and restore frozen GlobalVoices archives without reading raw text."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
BUNDLE = BASE / "inputs" / "PA_BPE_GlobalVoices_v2018q4_Raw_Source.zip"
OUTPUT = BASE / "output" / "raw_bundle_audit.json"
RAW_DIR = BASE / "inputs" / "raw"

EXPECTED = {
    "en": {
        "member": "PA_BPE_GlobalVoices_v2018q4_Raw_Source/raw/en.zip",
        "bytes": 115_069_300,
        "sha256": "974c2b104717a99662e6756272e2463989e7e78002e1a78e8e0e83c046fa9b3f",
    },
    "fr": {
        "member": "PA_BPE_GlobalVoices_v2018q4_Raw_Source/raw/fr.zip",
        "bytes": 37_776_586,
        "sha256": "84cfd37dec57098be81c7309ca878cad104c71e37087bbc9f70f4f16b5c36587",
    },
    "es": {
        "member": "PA_BPE_GlobalVoices_v2018q4_Raw_Source/raw/es.zip",
        "bytes": 80_028_192,
        "sha256": "2af6fb985de8965c5ae722a6ce0fdaf61477d3faa083a32cf2490a86e983be55",
    },
}
BUNDLE_SHA256 = "825a8c063b19d4b1dc21f8a540ea2acbe5e11fa1da1cd6bfdeac5200c6805b6c"


def hash_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def atomic_copy_member(zf: zipfile.ZipFile, member: str, target: Path) -> tuple[str, int]:
    target.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    n = 0
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as dst, zf.open(member, "r") as src:
            while block := src.read(1024 * 1024):
                dst.write(block)
                h.update(block)
                n += len(block)
            dst.flush()
            os.fsync(dst.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return h.hexdigest(), n


def main() -> int:
    bundle_hash, bundle_bytes = hash_file(BUNDLE)
    if bundle_hash != BUNDLE_SHA256:
        raise ValueError(f"bundle SHA mismatch: {bundle_hash}")

    observed: dict[str, dict[str, object]] = {}
    embedded_json: dict[str, object] = {}
    with zipfile.ZipFile(BUNDLE) as zf:
        bad_member = zf.testzip()
        if bad_member is not None:
            raise ValueError(f"ZIP CRC failure: {bad_member}")
        names = set(zf.namelist())
        for lang, spec in EXPECTED.items():
            member = str(spec["member"])
            if member not in names:
                raise KeyError(f"missing member: {member}")
            target = RAW_DIR / f"{lang}.zip"
            sha, size = atomic_copy_member(zf, member, target)
            ok = sha == spec["sha256"] and size == spec["bytes"]
            observed[lang] = {
                "member": member,
                "output": str(target.relative_to(BASE)),
                "sha256": sha,
                "bytes": size,
                "matches_frozen_identity": ok,
            }
            if not ok:
                raise ValueError(f"frozen identity mismatch for {lang}: {observed[lang]}")

        prefix = "PA_BPE_GlobalVoices_v2018q4_Raw_Source/"
        for suffix in (
            "manifests/confirmation_index_build_manifest_v2.json",
            "manifests/confirmation_raw_source_manifest.json",
            "receipts/fetch_en.json",
            "receipts/fetch_fr.json",
            "receipts/fetch_es.json",
        ):
            name = prefix + suffix
            if name not in names:
                raise KeyError(f"missing embedded metadata: {name}")
            embedded_json[suffix] = json.loads(zf.read(name))

    receipt_checks: dict[str, object] = {}
    for lang, spec in EXPECTED.items():
        receipt = embedded_json[f"receipts/fetch_{lang}.json"]
        if not isinstance(receipt, dict):
            raise TypeError(f"bad receipt for {lang}")
        receipt_sha = receipt.get("sha256")
        receipt_bytes = receipt.get("bytes")
        receipt_checks[lang] = {
            "sha256": receipt_sha,
            "bytes": receipt_bytes,
            "matches_frozen_identity": receipt_sha == spec["sha256"] and receipt_bytes == spec["bytes"],
        }
        if not receipt_checks[lang]["matches_frozen_identity"]:
            raise ValueError(f"embedded receipt mismatch for {lang}: {receipt_checks[lang]}")

    result = {
        "schema": "pa-bpe-raw-bundle-audit-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "bundle": {"path": str(BUNDLE.relative_to(BASE)), "sha256": bundle_hash, "bytes": bundle_bytes},
        "archives": observed,
        "embedded_receipt_checks": receipt_checks,
        "embedded_raw_source_manifest": embedded_json["manifests/confirmation_raw_source_manifest.json"],
        "embedded_index_build_manifest": embedded_json["manifests/confirmation_index_build_manifest_v2.json"],
        "raw_text_inspected": False,
        "tokenizer_or_fairness_result": False,
        "interpretation": (
            "The persisted bundle contains the three exact frozen OPUS GlobalVoices raw archives. "
            "This repairs the prior source-gap inference but does not yet validate the whitespace-token "
            "fingerprint index or any tokenizer/fairness outcome."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, OUTPUT)
    print(json.dumps({"status": "passed", "output": str(OUTPUT), "archives": observed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
