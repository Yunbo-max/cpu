#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "evidence" / "official_exporter_excerpt.txt"
text = source.read_text(encoding="utf-8")
required = {
    "sentences_are_eligibility_filtered": "WHERE correctness > -1 AND license != ''",
    "global_links_are_unfiltered": "SELECT sentence_id, translation_id FROM `sentences_translations`",
    "per_language_sentences_derive_from_filtered_export": "split_file sentences.csv",
    "per_language_links_query_relation_directly": "FROM sentences_translations\" | awk",
}
checks = {name: needle in text for name, needle in required.items()}
if not all(checks.values()):
    raise SystemExit("official exporter excerpt does not satisfy all frozen checks")

previous = json.loads((root / "evidence" / "wake21_source_endpoint_diagnostic.json").read_text())
excluded_edges = {pair: info["missing_or_wrong_language_endpoints"] for pair, info in previous["links"].items()}
result = {
    "status": "export_semantics_identified",
    "official_repository": "https://github.com/Tatoeba/tatoeba2",
    "official_commit": "0fbb4506ce071827f85375bd4c8c8f9c7cf23d41",
    "excerpt_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "checks": checks,
    "mechanism": "Sentence exports exclude correctness <= -1 or empty-license rows, while link exports are drawn directly from sentences_translations without the same eligibility predicate. Therefore a per-language link file can legitimately reference an ID absent from the corresponding per-language sentence export.",
    "wake21_excluded_edge_counts": excluded_edges,
    "wake21_excluded_edge_total": sum(excluded_edges.values()),
    "strict_protocol_v1": "retained_as_failed",
    "revised_protocol_rule": "For a separately versioned protocol, define the eligible graph as the inner join of each frozen pair-link table with both frozen, language-matched sentence tables; record every excluded edge and never score or select an item using an absent endpoint.",
    "tokenizer_scored": False,
    "confirmation_items_selected": False,
}
out = root / "output" / "official_export_semantics.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
