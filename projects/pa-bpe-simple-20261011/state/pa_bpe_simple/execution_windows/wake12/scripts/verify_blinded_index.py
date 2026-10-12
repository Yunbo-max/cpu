import argparse
import gzip
import hashlib
import json
import re
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


LANGUAGES = ("en", "fr", "es")
HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def normalize_text(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def element_text(element):
    return " ".join(piece.strip() for piece in element.itertext() if piece and piece.strip())


def member_for(document, members):
    targets = {document, document[:-3] if document.endswith(".gz") else document}
    matches = [name for name in members if any(name == target or name.endswith("/" + target) for target in targets)]
    if len(matches) != 1:
        raise RuntimeError("raw document match is not unique")
    return matches[0]


def assert_true(condition, label, checks):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--units", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--raw-schema", required=True)
    parser.add_argument("--selector-protocol", required=True)
    parser.add_argument("--fetch-receipts", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    database_path = Path(args.database)
    database_bytes = database_path.read_bytes()
    summary = json.loads(Path(args.summary).read_bytes())
    units_bytes = Path(args.units).read_bytes()
    units = json.loads(units_bytes)["reserved_unit_identities"]
    source_manifest_bytes = Path(args.source_manifest).read_bytes()
    source_manifest = json.loads(source_manifest_bytes)
    raw_schema_bytes = Path(args.raw_schema).read_bytes()
    selector_protocol_bytes = Path(args.selector_protocol).read_bytes()
    checks = []

    database = sqlite3.connect(f"file:{database_path.resolve()}?mode=ro", uri=True)
    integrity = database.execute("PRAGMA integrity_check").fetchone()[0]
    assert_true(integrity == "ok", "sqlite_integrity", checks)
    objects = database.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name").fetchall()
    tables = [name for kind, name in objects if kind == "table"]
    assert_true(tables == ["confirmation", "meta", "shingles"], "only_expected_tables", checks)
    assert_true(not [row for row in objects if row[0] in {"view", "trigger"}], "no_views_or_triggers", checks)
    confirmation_columns = [row[1] for row in database.execute("PRAGMA table_info(confirmation)")]
    shingle_columns = [row[1] for row in database.execute("PRAGMA table_info(shingles)")]
    assert_true(confirmation_columns == ["blinded_unit_sha256", "language", "canonical_url_sha256", "normalized_exact_sha256", "word_count", "shingle_mass"], "confirmation_schema_hashes_and_counts_only", checks)
    assert_true(shingle_columns == ["blinded_unit_sha256", "language", "shingle_sha256", "multiplicity"], "shingle_schema_hashes_and_counts_only", checks)

    metadata = dict(database.execute("SELECT key,value FROM meta"))
    assert_true(metadata.get("complete") == "true", "complete_marker", checks)
    assert_true(metadata.get("raw_text_stored") == "false", "raw_text_storage_disabled", checks)
    assert_true(metadata.get("tokenizer_or_fairness_output_computed") == "false", "no_tokenizer_or_fairness_output", checks)
    assert_true(metadata.get("units_sha256") == summary["units_sha256"], "unit_manifest_binding", checks)
    assert_true(metadata.get("source_manifest_sha256") == summary["source_manifest_sha256"], "source_manifest_binding", checks)
    assert_true(summary["units_sha256"] == sha256_bytes(units_bytes) == source_manifest["units"]["expected_sha256"], "unit_manifest_fail_closed", checks)
    assert_true(summary["source_manifest_sha256"] == sha256_bytes(source_manifest_bytes), "source_manifest_hash_recomputed", checks)
    assert_true(metadata.get("raw_schema_sha256") == summary["raw_schema_sha256"] == sha256_bytes(raw_schema_bytes), "raw_schema_binding", checks)
    assert_true(metadata.get("selector_protocol_sha256") == summary["selector_protocol_sha256"] == sha256_bytes(selector_protocol_bytes), "selector_protocol_binding", checks)
    for key in ("project", "active_idea", "adopted_source_digest"):
        assert_true(metadata.get(key) == str(source_manifest[key]) == str(summary["project_binding"][key]), f"{key}_binding", checks)
    for key in ("idea_revision", "checkpoint_generation"):
        assert_true(metadata.get(key) == str(source_manifest[key]) == str(summary["project_binding"][key]), f"{key}_binding", checks)
    assert_true(sha256_bytes(database_bytes) == summary["database_sha256"], "database_hash_binding", checks)

    archive_hashes = {}
    for language in LANGUAGES:
        spec = source_manifest["archives"][language]
        archive_path = Path(args.raw_dir) / f"{language}.zip"
        actual_sha = file_sha256(archive_path)
        actual_bytes = archive_path.stat().st_size
        receipt_bytes = (Path(args.fetch_receipts) / f"fetch_{language}.json").read_bytes()
        receipt = json.loads(receipt_bytes)
        assert_true(actual_sha == spec["expected_sha256"] == metadata[f"archive_{language}_sha256"] == summary["archive_receipts"][language]["sha256"], f"{language}_archive_hash_recomputed", checks)
        assert_true(actual_bytes == spec["expected_bytes"] == int(metadata[f"archive_{language}_bytes"]) == summary["archive_receipts"][language]["bytes"], f"{language}_archive_bytes_recomputed", checks)
        assert_true(sha256_bytes(receipt_bytes) == spec["fetch_receipt_sha256"] == metadata[f"fetch_{language}_receipt_sha256"] == summary["archive_receipts"][language]["receipt_sha256"], f"{language}_fetch_receipt_binding", checks)
        assert_true(receipt["sha256"] == actual_sha and receipt["bytes"] == actual_bytes, f"{language}_fetch_receipt_content", checks)
        archive_hashes[language] = {"sha256": actual_sha, "bytes": actual_bytes}

    per_language = {}
    for language in LANGUAGES:
        row = database.execute(
            "SELECT COUNT(*),SUM(word_count),SUM(shingle_mass),SUM(canonical_url_sha256 IS NOT NULL) FROM confirmation WHERE language=?",
            (language,)
        ).fetchone()
        expected = summary["counts"][language]
        observed = {"units": row[0], "words": row[1], "shingle_mass": row[2], "source_url_present": row[3]}
        assert_true(observed == expected, f"{language}_summary_recomputed", checks)
        per_language[language] = observed
    assert_true(database.execute("SELECT COUNT(*) FROM confirmation").fetchone()[0] == 1536, "three_by_512_confirmation_rows", checks)
    assert_true(database.execute("SELECT COUNT(*) FROM confirmation WHERE blinded_unit_sha256 NOT GLOB '[0-9a-f]*' OR length(blinded_unit_sha256)!=64").fetchone()[0] == 0, "blinded_id_format", checks)
    assert_true(database.execute("SELECT COUNT(*) FROM confirmation WHERE normalized_exact_sha256 NOT GLOB '[0-9a-f]*' OR length(normalized_exact_sha256)!=64").fetchone()[0] == 0, "exact_hash_format", checks)
    assert_true(database.execute("SELECT COUNT(*) FROM confirmation WHERE canonical_url_sha256 IS NOT NULL AND length(canonical_url_sha256)!=64").fetchone()[0] == 0, "url_hash_format", checks)
    assert_true(database.execute("SELECT COUNT(*) FROM shingles WHERE length(shingle_sha256)!=32 OR multiplicity<1").fetchone()[0] == 0, "full_sha256_shingles_positive_multiplicity", checks)
    for blinded in summary["blinded_unit_sha256_samples"]:
        assert_true(HEX64.fullmatch(blinded) is not None and database.execute("SELECT COUNT(*) FROM confirmation WHERE blinded_unit_sha256=?", (blinded,)).fetchone()[0] == 1, "blinded_sample_present", checks)
    database.close()

    raw_markers_checked = {"document_references": 0, "unit_identities": 0, "urls": 0, "normalized_sentence_samples": 0}
    for unit in units:
        unit_marker = unit["unit_sha256"].encode()
        assert_true(unit_marker not in database_bytes, "unblinded_unit_identity_absent", checks)
        raw_markers_checked["unit_identities"] += 1
        for language in LANGUAGES:
            document_marker = unit["documents"][language].encode()
            assert_true(document_marker not in database_bytes, "raw_document_reference_absent", checks)
            raw_markers_checked["document_references"] += 1

    sampled_documents = {}
    for language in LANGUAGES:
        unique_documents = sorted({unit["documents"][language] for unit in units}, key=lambda value: sha256_bytes((language + "\0" + value).encode()))[:32]
        sampled_documents[language] = unique_documents
        archive_path = Path(args.raw_dir) / f"{language}.zip"
        with zipfile.ZipFile(archive_path) as archive:
            members = [info.filename for info in archive.infolist() if not info.is_dir()]
            for document in unique_documents:
                member = member_for(document, members)
                payload = archive.read(member)
                if member.endswith(".gz"):
                    payload = gzip.decompress(payload)
                root = ET.fromstring(payload)
                sampled_sentence = None
                for element in root.iter():
                    tag = local_name(element.tag)
                    value = element_text(element)
                    if tag == "URL" and value:
                        assert_true(value.encode() not in database_bytes, "plaintext_url_absent", checks)
                        raw_markers_checked["urls"] += 1
                    if tag == "s" and sampled_sentence is None:
                        normalized = normalize_text(value)
                        if len(normalized.encode()) >= 32:
                            sampled_sentence = normalized
                if sampled_sentence is not None:
                    assert_true(sampled_sentence.encode() not in database_bytes, "normalized_sentence_sample_absent", checks)
                    raw_markers_checked["normalized_sentence_samples"] += 1

    result = {
        "schema_version": 1,
        "checks_passed": len(checks),
        "unique_check_labels": len(set(checks)),
        "sqlite_integrity": integrity,
        "database_sha256": sha256_bytes(database_bytes),
        "recomputed_counts": per_language,
        "recomputed_archives": archive_hashes,
        "raw_markers_checked": raw_markers_checked,
        "raw_text_or_plaintext_metadata_detected": False,
        "operator_output_contains_raw_text": False,
        "tokenizer_or_fairness_output_computed": False,
        "qualification": "verified_result_blind_fingerprint_index",
        "limitations": [
            "This verifies index structure, bindings, aggregate counts and sampled plaintext absence, not semantic independence or tokenizer fairness.",
            "Production selector compatibility still requires a reviewed URL-hash and schema adapter plus actual training-row provenance."
        ]
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
