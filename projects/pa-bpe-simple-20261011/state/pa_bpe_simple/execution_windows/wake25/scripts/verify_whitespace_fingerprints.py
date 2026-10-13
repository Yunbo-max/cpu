#!/usr/bin/env python3
"""Independently recompute every frozen exact hash and whitespace shingle row."""

from __future__ import annotations

import collections
import gzip
import hashlib
import json
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
LANGUAGES = ("en", "fr", "es")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(element: ET.Element) -> str:
    return " ".join(part.strip() for part in element.itertext() if part and part.strip())


def locate(document: str, members: list[str]) -> str:
    targets = {document, document[:-3] if document.endswith(".gz") else document}
    found = [name for name in members if any(name == target or name.endswith("/" + target) for target in targets)]
    if len(found) != 1:
        raise RuntimeError(f"non-unique document mapping: {document}")
    return found[0]


def load_documents(archive_path: Path, wanted: dict[str, set[str]]) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    with zipfile.ZipFile(archive_path) as archive:
        members = [item.filename for item in archive.infolist() if not item.is_dir()]
        for document, wanted_ids in wanted.items():
            member = locate(document, members)
            payload = archive.read(member)
            if member.endswith(".gz"):
                payload = gzip.decompress(payload)
            root = ET.fromstring(payload)
            sentences: dict[str, str] = {}
            order: list[str] = []
            for element in root.iter():
                if local_name(element.tag) != "s":
                    continue
                sentence_id = element.attrib.get("id")
                if sentence_id in wanted_ids:
                    sentences[sentence_id] = text_of(element)
                    order.append(sentence_id)
            if set(sentences) != wanted_ids:
                raise RuntimeError(f"sentence identity mismatch: {document}")
            output[document] = {"sentences": sentences, "order": order}
    return output


def main() -> None:
    units_bytes = (BASE / "inputs/frozen_units.json").read_bytes()
    units = json.loads(units_bytes)["reserved_unit_identities"]
    source = json.loads((BASE / "inputs/frozen_source_manifest.json").read_bytes())
    database_path = BASE / "output/globalvoices_whitespace_fingerprints.sqlite3"
    summary = json.loads((BASE / "output/whitespace_fingerprint_summary.json").read_bytes())

    if len(units) != 512 or digest(units_bytes) != source["units"]["expected_sha256"]:
        raise RuntimeError("frozen units binding failed")
    wanted = {language: collections.defaultdict(set) for language in LANGUAGES}
    for unit in units:
        for language in LANGUAGES:
            wanted[language][unit["documents"][language]].update(unit["sentence_ids"][language])
    documents = {
        language: load_documents(BASE / f"inputs/raw/{language}.zip", wanted[language])
        for language in LANGUAGES
    }

    db = sqlite3.connect(f"file:{database_path.resolve()}?mode=ro", uri=True)
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise RuntimeError("SQLite integrity failure")
    meta = dict(db.execute("SELECT key,value FROM meta"))
    expected_normalization = (
        "Unicode NFKC + casefold + Unicode whitespace collapse; whitespace-separated normalized "
        "tokens; full SHA256 of NUL-separated contiguous 5-token shingle multiset"
    )
    if meta.get("normalization") != expected_normalization or meta.get("tokenization") != "whitespace-separated normalized tokens":
        raise RuntimeError("tokenization metadata mismatch")

    checked = collections.Counter()
    for unit in units:
        for language in LANGUAGES:
            record = documents[language][unit["documents"][language]]
            selected = set(unit["sentence_ids"][language])
            raw = " ".join(record["sentences"][sid] for sid in record["order"] if sid in selected)
            normalized = normalize(raw)
            tokens = normalized.split()
            grams = collections.Counter(
                hashlib.sha256("\0".join(tokens[index:index + 5]).encode()).digest()
                for index in range(max(0, len(tokens) - 4))
            )
            blinded = digest((source["release"] + "\0" + language + "\0" + unit["unit_sha256"]).encode())
            row = db.execute(
                "SELECT normalized_exact_sha256,word_count,shingle_mass FROM confirmation WHERE blinded_unit_sha256=? AND language=?",
                (blinded, language),
            ).fetchone()
            expected_row = (digest(normalized.encode()), len(tokens), sum(grams.values()))
            if row != expected_row:
                raise RuntimeError(f"confirmation mismatch: {blinded} {language}")
            stored_grams = dict(db.execute(
                "SELECT shingle_sha256,multiplicity FROM shingles WHERE blinded_unit_sha256=? AND language=?",
                (blinded, language),
            ))
            if stored_grams != dict(grams):
                raise RuntimeError(f"shingle mismatch: {blinded} {language}")
            checked[language] += 1
    total_confirmation = db.execute("SELECT COUNT(*) FROM confirmation").fetchone()[0]
    db.close()
    if total_confirmation != 1536 or dict(checked) != {language: 512 for language in LANGUAGES}:
        raise RuntimeError("coverage mismatch")

    result = {
        "schema": "pa-bpe-whitespace-fingerprint-verification-v1",
        "status": "passed",
        "units_sha256": digest(units_bytes),
        "database_sha256": digest(database_path.read_bytes()),
        "summary_database_sha256": summary["database_sha256"],
        "per_language_units_recomputed": dict(checked),
        "confirmation_rows": total_confirmation,
        "exact_hashes_recomputed": 1536,
        "shingle_multisets_recomputed": 1536,
        "raw_text_stored": False,
        "operator_output_contains_raw_text": False,
        "tokenizer_or_fairness_output_computed": False,
        "qualification": "independently_recomputed_whitespace_fingerprint_index",
        "limitation": "This verifies source reconstruction and fingerprint semantics only; contamination selection and tokenizer/fairness scoring remain unperformed."
    }
    if result["database_sha256"] != result["summary_database_sha256"]:
        raise RuntimeError("database summary hash mismatch")
    (BASE / "output/whitespace_fingerprint_verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "passed", "confirmation_rows": total_confirmation, "per_language": dict(checked)}))


if __name__ == "__main__":
    main()
