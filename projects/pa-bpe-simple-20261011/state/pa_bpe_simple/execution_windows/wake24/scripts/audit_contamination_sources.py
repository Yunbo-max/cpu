import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
OUTPUT = ROOT / "output" / "contamination_source_recovery_audit_v2.json"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def selected_training_counts():
    selected = json.loads((INPUT / "selected_rows.json").read_text())
    wanted = {(lang, row["row_id"]): row for lang, rows in selected["selected"].items() for row in rows}
    # SQLite may update a WAL-mode -shm file even for a mode=ro query. Query
    # an isolated copy so the runner's immutable input contract remains true.
    with tempfile.TemporaryDirectory(prefix="pa_bpe_selection_audit_") as td:
        copied = Path(td) / "selection.sqlite3"
        for suffix in ("", "-wal", "-shm"):
            shutil.copy2(INPUT / f"selection.sqlite3{suffix}", Path(f"{copied}{suffix}"))
        con = sqlite3.connect(f"file:{copied.resolve()}?mode=ro", uri=True)
        observed = {}
        raw_hash_failures = []
        for lang, sid, text, raw_hash in con.execute("SELECT lang,id,text,raw_hash FROM rows"):
            key = (lang, sid)
            if key not in wanted:
                continue
            observed[key] = True
            actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if actual != raw_hash or actual != wanted[key]["raw_text_sha256"]:
                raw_hash_failures.append([lang, sid, raw_hash, actual])
        con.close()
    if set(observed) != set(wanted):
        raise RuntimeError("selected training rows are not fully recoverable from selection.sqlite3")
    if raw_hash_failures:
        raise RuntimeError("selected training raw-text hash mismatch")
    return {lang: sum(1 for l, _ in wanted if l == lang) for lang in ("en", "fr", "es")}, len(wanted)


def globalvoices_inventory():
    con = sqlite3.connect(f"file:{(INPUT / 'globalvoices_fingerprints.sqlite3').resolve()}?mode=ro", uri=True)
    items = con.execute("SELECT language,COUNT(*) FROM confirmation GROUP BY language ORDER BY language").fetchall()
    shingles = con.execute("SELECT COUNT(*) FROM shingles").fetchone()[0]
    meta = dict(con.execute("SELECT key,value FROM meta"))
    con.close()
    return dict(items), shingles, meta


def main():
    manifest = json.loads((INPUT / "project_manifest.json").read_text())
    archive_index = json.loads((INPUT / "archives_index.json").read_text())["archives"]
    training_counts, training_total = selected_training_counts()
    gv_counts, gv_shingles, gv_meta = globalvoices_inventory()
    tico = json.loads((INPUT / "tico_dev.json").read_text())
    books = json.loads((INPUT / "multibook_raw_evaluation.json").read_text())
    expected_gv_archives = {
        "en": "974c2b104717a99662e6756272e2463989e7e78002e1a78e8e0e83c046fa9b3f",
        "fr": "84cfd37dec57098be81c7309ca878cad104c71e37087bbc9f70f4f16b5c36587",
        "es": "2af6fb985de8965c5ae722a6ce0fdaf61477d3faa083a32cf2490a86e983be55",
    }
    files = {}
    for p in sorted(INPUT.iterdir()):
        if p.is_file():
            files[p.name] = {"bytes": p.stat().st_size, "sha256": sha256(p)}
    source_hash_expectations = {
        "selected_rows.json": manifest["files"]["execution_windows/wake15b/output/selected_rows.json"],
        "selection.sqlite3": manifest["files"]["execution_windows/wake15b/output/selection.sqlite3"],
        "globalvoices_fingerprints.sqlite3": manifest["files"]["execution_windows/wake12/output/globalvoices_blinded_fingerprints_v2.sqlite3"],
        "tico_dev.json": manifest["files"]["execution_windows/wake16/output/v3_tico.trilingual.dev.json"],
        "flores200_dataset.tar.gz": manifest["files"]["execution_windows/wake17c/inputs/flores200_dataset.tar.gz"],
        "multibook_raw_evaluation.json": manifest["files"]["execution_windows/wake3/output/multibook_raw_evaluation.json"],
        "decontam_selector.py": manifest["files"]["execution_windows/wake11/scripts/decontam_selector.py"],
    }
    hash_checks = {name: files[name]["sha256"] == expected for name, expected in source_hash_expectations.items()}
    if not all(hash_checks.values()):
        raise RuntimeError("canonical source hash mismatch")
    tatoeba_expected = {
        "eng_sentences.tsv.bz2": "0eabb52f54350bbb39807190920bfddaf9fee2ba50ca75af67e11a22ec475c29",
        "fra_sentences.tsv.bz2": "fac31d82b216c95affee7dffcee6c0ae59c45f254ebbfbbf8abb9e66da86ee8f",
        "spa_sentences.tsv.bz2": "d1f7aa997368571e8bbba341ab60f9145fefe14970f21065bd97be8e03c8e6fb",
    }
    tatoeba_checks = {name: files[name]["sha256"] == expected for name, expected in tatoeba_expected.items()}
    if not all(tatoeba_checks.values()):
        raise RuntimeError("restored Tatoeba source hash mismatch")
    old_selector = (INPUT / "decontam_selector.py").read_text()
    addendum = (INPUT / "protocol_implementation_addendum.md").read_text()
    tokenizer_mismatch = {
        "stored_globalvoices_builder": "Unicode regex \\w+ tokens; five-token hashes join tokens with NUL",
        "tatoeba_frozen_addendum": "whitespace-separated normalized tokens; contiguous five-token multiset",
        "code_evidence": "WORD_RE.findall(normalize_text(text))" in old_selector and '"\\0".join' in old_selector,
        "protocol_evidence": "Tokens are whitespace-separated normalized tokens" in addendum,
        "compatible": False,
    }
    missing_gv = {lang: digest not in archive_index for lang, digest in expected_gv_archives.items()}
    outcome = {
        "schema_version": 1,
        "status": "SOURCE_GAP_GLOBALVOICES_RAW_REQUIRED",
        "scope": "Result-blind source recovery audit only; no contamination decision, development selection, tokenizer scoring, or fairness result.",
        "canonical_hash_checks": hash_checks,
        "restored_tatoeba_sentence_hash_checks": tatoeba_checks,
        "recoverable_inventories": {
            "training_selected_documents": {"by_language": training_counts, "total": training_total, "raw_text_hashes_verified": True, "final_partial_items_screen_whole_document_conservatively": True},
            "tico_development": {"aligned_rows": len(tico), "items": len(tico) * 3, "languages": ["en", "fr", "es"]},
            "globalvoices_stored_fingerprints": {"by_language": gv_counts, "items": sum(gv_counts.values()), "stored_shingle_rows": gv_shingles, "raw_text_persisted": False},
            "flores_devtest": {"archive_sha256": files["flores200_dataset.tar.gz"]["sha256"], "archive_bytes": files["flores200_dataset.tar.gz"]["bytes"], "expected_rows_per_language": 1012},
            "books_diagnostics": {"multibook_works": len(books["sampling"]), "sampled_alignment_units": sum(v["sampled"] for v in books["sampling"].values()), "paired_alice_poe_sources_present": all(name in files for name in ["books_dev.tsv", "books_confirm.tsv", "alice_en.xml", "alice_fr.xml", "alice_es.xml", "poe_en.xml", "poe_fr.xml", "poe_es.xml"])},
        },
        "globalvoices_blocker": {
            "expected_raw_archive_sha256": expected_gv_archives,
            "raw_archives_absent_from_github_archive_index": missing_gv,
            "stored_fingerprint_tokenizer_mismatch": tokenizer_mismatch,
            "why_hashes_are_insufficient": "Normalized exact hashes and old shingle hashes cannot reconstruct raw normalized text or whitespace-token shingles.",
            "recovery_condition": "Fetch the three frozen OPUS GlobalVoices archives, verify every expected SHA256, reconstruct the exact 512x3 unit texts from the frozen source manifest, and rebuild whitespace-token fingerprints before applying the Tatoeba contamination filter.",
        },
        "globalvoices_meta": {k: gv_meta[k] for k in sorted(gv_meta) if k in {"source_manifest_sha256", "protocol_sha256", "units_sha256", "unit_count", "complete"}},
        "input_files": files,
        "decision": "Do not apply the incompatible stored GlobalVoices shingles and do not select Tatoeba development rows.",
        "next_action": "Recover the three frozen GlobalVoices raw archives by their recorded hashes, rebuild addendum-compatible whitespace-token fingerprints, then apply the complete contamination inventory to the 38,091 eligible triangles and independently verify deterministic selection.",
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": outcome["status"], "training_items": training_total, "tico_items": len(tico) * 3, "globalvoices_items": sum(gv_counts.values()), "books_units": sum(v["sampled"] for v in books["sampling"].values()), "missing_globalvoices_archives": missing_gv}, sort_keys=True))


if __name__ == "__main__":
    main()
