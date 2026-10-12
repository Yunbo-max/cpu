import collections
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / "pgv_triangle_protocol_v2.json").read_text())
archive_path = ROOT / "inputs" / "pgv_docpairs.txt.zip"
payload_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
if payload_hash != protocol["input_archive_sha256"]:
    raise RuntimeError(f"archive hash mismatch: {payload_hash}")

target = {"eng", "fra", "spa"}
pairs = {("eng", "fra"): set(), ("eng", "spa"): set(), ("fra", "spa"): set()}
all_pair_counts = collections.Counter()
malformed = 0
prefix_mismatches = 0
with zipfile.ZipFile(archive_path) as zf, zf.open("docpairs.txt") as raw:
    text = io.TextIOWrapper(raw, encoding="utf-8", errors="strict")
    for line in text:
        fields = line.strip().split()
        if len(fields) != 4:
            malformed += 1
            continue
        l1, l2, d1, d2 = fields
        all_pair_counts[f"{l1}-{l2}"] += 1
        if not d1.startswith(f"gv-{l1}-") or not d2.startswith(f"gv-{l2}-"):
            prefix_mismatches += 1
        if {l1, l2}.issubset(target):
            if (l1, l2) in pairs:
                pairs[(l1, l2)].add((d1, d2))
            elif (l2, l1) in pairs:
                pairs[(l2, l1)].add((d2, d1))

ef = pairs[("eng", "fra")]
es = pairs[("eng", "spa")]
fs = pairs[("fra", "spa")]
e_to_f = collections.defaultdict(set)
e_to_s = collections.defaultdict(set)
for e, f in ef:
    e_to_f[e].add(f)
for e, s in es:
    e_to_s[e].add(s)

english_with_both = sorted(set(e_to_f) & set(e_to_s))
consistent = []
potential_cartesian = 0
for e in english_with_both:
    potential_cartesian += len(e_to_f[e]) * len(e_to_s[e])
    triangles = sorted((f, s) for f in e_to_f[e] for s in e_to_s[e] if (f, s) in fs)
    if triangles:
        f, s = triangles[0]
        canonical = f"{e}|{f}|{s}"
        consistent.append({"eng": e, "fra": f, "spa": s, "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest()})

consistent.sort(key=lambda x: (x["canonical_sha256"], x["eng"], x["fra"], x["spa"]))
reserved = consistent[:512] if len(consistent) >= 512 else []
qualified = malformed == 0 and prefix_mismatches == 0 and len(consistent) >= 512
result = {
    "schema_version": 1,
    "input": {"path": "inputs/pgv_docpairs.txt.zip", "sha256": payload_hash},
    "integrity": {"malformed_records": malformed, "language_prefix_mismatches": prefix_mismatches},
    "target_pair_counts": {"eng-fra": len(ef), "eng-spa": len(es), "fra-spa": len(fs)},
    "triangle_support": {
        "english_documents_with_both_french_and_spanish_links": len(english_with_both),
        "candidate_french_spanish_combinations": potential_cartesian,
        "english_documents_with_at_least_one_all-three-edge_triangle": len(consistent),
        "reserved_deterministic_document_triples": len(reserved)
    },
    "reserved_document_triples": reserved,
    "qualification": {
        "document_level": "qualified" if qualified else "not_qualified",
        "sentence_level": "not_qualified_pending_segment_identity_check",
        "tokenizer_confirmation": "not_started",
        "freshness": "preserved_no_story_text_or_tokenizer_outcome_read"
    },
    "next_action": "Inspect only the schemas and identifiers of the three official segment archives for a deterministic common-row construction; freeze tokenizer and row protocol before any scoring."
}
(ROOT / "output" / "pgv_triangle_qualification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
