import collections
import gzip
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / "opus_gv_closed_components_protocol.json").read_text())
pair_specs = {
    "en-fr": ("en", "fr", ROOT / "inputs/opus_gv_v2018q4/en-fr.xml.gz"),
    "en-es": ("en", "es", ROOT / "inputs/opus_gv_v2018q4/en-es.xml.gz"),
    "es-fr": ("es", "fr", ROOT / "inputs/opus_gv_v2018q4/es-fr.xml.gz")
}
for path_str, expected in protocol["input_hashes"].items():
    observed = hashlib.sha256((ROOT / path_str).read_bytes()).hexdigest()
    if observed != expected:
        raise RuntimeError(f"hash mismatch for {path_str}: {observed}")

def strip_tag(tag):
    return tag.rsplit("}", 1)[-1]

def group_pairs(path):
    out = set()
    with gzip.open(path, "rb") as stream:
        for event, elem in ET.iterparse(stream, events=("start", "end")):
            if event == "start" and strip_tag(elem.tag) == "linkGrp":
                out.add((elem.attrib["fromDoc"], elem.attrib["toDoc"]))
            if event == "end":
                elem.clear()
    return out

doc_edges = {name: group_pairs(path) for name, (_, _, path) in pair_specs.items()}
en_to_fr = collections.defaultdict(set)
en_to_es = collections.defaultdict(set)
for en, fr in doc_edges["en-fr"]:
    en_to_fr[en].add(fr)
for en, es in doc_edges["en-es"]:
    en_to_es[en].add(es)

all_triangles = []
for en in sorted(set(en_to_fr) & set(en_to_es)):
    choices = sorted((fr, es) for fr in en_to_fr[en] for es in en_to_es[en] if (es, fr) in doc_edges["es-fr"])
    if choices:
        fr, es = choices[0]
        canonical = f"{en}|{fr}|{es}"
        all_triangles.append((hashlib.sha256(canonical.encode()).hexdigest(), en, fr, es))
all_triangles.sort()
selected = all_triangles[:512]
selected_by_pair = {
    "en-fr": {(en, fr): (en, fr, es) for _, en, fr, es in selected},
    "en-es": {(en, es): (en, fr, es) for _, en, fr, es in selected},
    "es-fr": {(es, fr): (en, fr, es) for _, en, fr, es in selected}
}

edges_by_triple = collections.defaultdict(list)
link_counts = collections.Counter()
empty_sided = collections.Counter()
for pair_name, (left_lang, right_lang, path) in pair_specs.items():
    current = None
    keep_triple = None
    with gzip.open(path, "rb") as stream:
        for event, elem in ET.iterparse(stream, events=("start", "end")):
            tag = strip_tag(elem.tag)
            if event == "start" and tag == "linkGrp":
                current = (elem.attrib["fromDoc"], elem.attrib["toDoc"])
                keep_triple = selected_by_pair[pair_name].get(current)
            elif event == "start" and tag == "link" and keep_triple is not None:
                sides = elem.attrib.get("xtargets", "").split(";", 1)
                if len(sides) != 2 or not sides[0].strip() or not sides[1].strip():
                    empty_sided[pair_name] += 1
                else:
                    left = [(left_lang, current[0], sid) for sid in sides[0].split()]
                    right = [(right_lang, current[1], sid) for sid in sides[1].split()]
                    edges_by_triple[keep_triple].append((pair_name, left, right))
                    link_counts[pair_name] += 1
            elif event == "end" and tag == "linkGrp":
                current = None
                keep_triple = None
            if event == "end":
                elem.clear()

def components_for(triple, edges):
    parent = {}
    rank = {}
    def find(x):
        parent.setdefault(x, x)
        rank.setdefault(x, 0)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
    for _, left, right in edges:
        nodes = left + right
        for node in nodes:
            find(node)
        for node in nodes[1:]:
            union(nodes[0], node)
    nodes_by_root = collections.defaultdict(list)
    for node in parent:
        nodes_by_root[find(node)].append(node)
    pair_types = collections.defaultdict(set)
    for pair_name, left, right in edges:
        if left and right:
            pair_types[find(left[0])].add(pair_name)
    closed = []
    rejected = collections.Counter()
    required_pairs = {"en-fr", "en-es", "es-fr"}
    for root, nodes in nodes_by_root.items():
        langs = {n[0] for n in nodes}
        if langs != {"en", "fr", "es"}:
            rejected["missing_language"] += 1
            continue
        if pair_types[root] != required_pairs:
            rejected["missing_pair_type"] += 1
            continue
        per_lang = {lang: sorted(n[2] for n in nodes if n[0] == lang) for lang in ["en", "fr", "es"]}
        identity_payload = json.dumps({"release": protocol["release"], "documents": {"en": triple[0], "fr": triple[1], "es": triple[2]}, "sentence_ids": per_lang}, sort_keys=True, separators=(",", ":"))
        closed.append({"unit_sha256": hashlib.sha256(identity_payload.encode()).hexdigest(), "documents": {"en": triple[0], "fr": triple[1], "es": triple[2]}, "sentence_ids": per_lang})
    return closed, rejected

all_units = []
reject_counts = collections.Counter()
for triple in [(en, fr, es) for _, en, fr, es in selected]:
    units, rejected = components_for(triple, edges_by_triple.get(triple, []))
    all_units.extend(units)
    reject_counts.update(rejected)
all_units.sort(key=lambda x: x["unit_sha256"])
duplicate_identities = len(all_units) - len({u["unit_sha256"] for u in all_units})
qualified = len(all_units) >= 512 and duplicate_identities == 0
result = {
    "schema_version": 1,
    "release": protocol["release"],
    "document_support": {
        "pairwise_link_groups": {k: len(v) for k, v in doc_edges.items()},
        "all_edge_document_triangles_one_per_english": len(all_triangles),
        "hash_ranked_document_triangles_inspected": len(selected)
    },
    "selected_scope_links": {"retained_nonempty": dict(link_counts), "empty_sided_rejected": dict(empty_sided)},
    "component_support": {
        "closed_three_language_all_pair_units": len(all_units),
        "duplicate_unit_identities": duplicate_identities,
        "rejected_components": dict(reject_counts),
        "reserved_units": 512 if qualified else 0
    },
    "reserved_unit_identities": all_units[:512] if qualified else [],
    "qualification": {
        "structure": "qualified" if qualified else "not_qualified",
        "raw_text_access": "not_started",
        "tokenizer_confirmation": "not_started",
        "freshness": "preserved_no_story_text_or_tokenizer_outcome_read"
    },
    "next_action": "Before opening raw text, audit attribution and source-manifest leakage, then freeze tokenizer candidate, preprocessing, metric, total-token constraint and confirmation analysis."
}
(ROOT / "output" / "opus_gv_closed_components.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
