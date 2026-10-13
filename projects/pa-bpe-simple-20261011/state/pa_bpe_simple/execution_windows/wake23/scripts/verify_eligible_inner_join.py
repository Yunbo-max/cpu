import bz2
import datetime
import gzip
import hashlib
import json
import resource
from collections import defaultdict
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
OUTPUT = ROOT / "output"

def sentence_ids(name, lang):
    ids = set()
    with bz2.open(INPUT / name, "rt", encoding="utf-8", newline="") as stream:
        for line in stream:
            fields = line.rstrip("\r\n").split("\t", 2)
            if len(fields) != 3 or fields[1] != lang:
                raise ValueError(f"invalid {lang} sentence row")
            ids.add(int(fields[0]))
    return ids

def eligible_links(name, left, right):
    rows = 0
    all_edges = set()
    eligible = set()
    categories = {"left_only_missing": 0, "right_only_missing": 0, "both_missing": 0}
    with bz2.open(INPUT / name, "rt", encoding="utf-8", newline="") as stream:
        for line in stream:
            edge = tuple(map(int, line.rstrip("\r\n").split("\t")))
            rows += 1
            all_edges.add(edge)
    for a, b in all_edges:
        has_a, has_b = a in left, b in right
        if has_a and has_b:
            eligible.add((a, b))
        elif not has_a and has_b:
            categories["left_only_missing"] += 1
        elif has_a and not has_b:
            categories["right_only_missing"] += 1
        else:
            categories["both_missing"] += 1
    return rows, all_edges, eligible, categories

audit = json.loads((OUTPUT / "eligible_inner_join_audit.json").read_text())
eng = sentence_ids("eng_sentences.tsv.bz2", "eng")
fra = sentence_ids("fra_sentences.tsv.bz2", "fra")
spa = sentence_ids("spa_sentences.tsv.bz2", "spa")

computed = {}
eligible = {}
for table, name, left, right in (
    ("ef", "eng-fra_links.tsv.bz2", eng, fra),
    ("es", "eng-spa_links.tsv.bz2", eng, spa),
    ("fs", "fra-spa_links.tsv.bz2", fra, spa),
):
    rows, all_edges, kept, categories = eligible_links(name, left, right)
    eligible[table] = kept
    computed[table] = {
        "rows": rows,
        "unique_edges": len(all_edges),
        "duplicate_edges": rows - len(all_edges),
        "retained_edges": len(kept),
        "excluded_edges": len(all_edges) - len(kept),
        **categories,
    }
    if computed[table] != audit["links"][table]:
        raise AssertionError(f"independent edge audit mismatch for {table}")

es_by_eng = defaultdict(set)
for e, s in eligible["es"]:
    es_by_eng[e].add(s)
triangles = set()
for e, f in eligible["ef"]:
    for s in es_by_eng.get(e, ()):
        if (f, s) in eligible["fs"]:
            triangles.add((e, f, s))
if len(triangles) != audit["closed_triangles"]:
    raise AssertionError("independent triangle count mismatch")

on_disk = set()
with gzip.open(OUTPUT / "eligible_closed_triangles.tsv.gz", "rt", encoding="utf-8") as stream:
    for line in stream:
        on_disk.add(tuple(map(int, line.rstrip("\n").split("\t"))))
if on_disk != triangles:
    raise AssertionError("triangle membership mismatch")

verification = {
    "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "implementation": "independent_in_memory_set_membership",
    "audit_sha256": hashlib.sha256((OUTPUT / "eligible_inner_join_audit.json").read_bytes()).hexdigest(),
    "links": computed,
    "closed_triangles": len(triangles),
    "triangle_membership_exact": True,
    "status": "verified",
}
(OUTPUT / "eligible_inner_join_verification.json").write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
print(json.dumps(verification, sort_keys=True))
