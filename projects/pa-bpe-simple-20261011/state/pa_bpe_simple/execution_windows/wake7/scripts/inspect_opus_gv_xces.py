import gzip
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / "opus_gv_xces_protocol.json").read_text())
inputs = ROOT / "inputs" / "opus_gv_v2018q4"
inputs.mkdir(parents=True, exist_ok=True)
outputs = {}
for pair, meta in protocol["source"]["alignment_files"].items():
    request = urllib.request.Request(meta["url"], headers={"User-Agent": "PA-BPE-source-audit/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        path = inputs / f"{pair}.xml.gz"
        h = hashlib.sha256()
        size = 0
        with path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > meta["content_length_bytes"]:
                    raise RuntimeError(f"{pair}: response exceeded advertised size")
                h.update(chunk)
                out.write(chunk)
        headers = {k.lower(): v for k, v in response.headers.items()}
    if size != meta["content_length_bytes"]:
        raise RuntimeError(f"{pair}: expected {meta['content_length_bytes']} bytes, got {size}")
    tag_counts = Counter()
    attr_counts = Counter()
    linkgrp_samples = []
    link_samples = []
    with gzip.open(path, "rb") as stream:
        for event, elem in ET.iterparse(stream, events=("start",)):
            tag = elem.tag.rsplit("}", 1)[-1]
            tag_counts[tag] += 1
            for key in elem.attrib:
                attr_counts[key.rsplit("}", 1)[-1]] += 1
            if tag == "linkGrp" and len(linkgrp_samples) < 3:
                linkgrp_samples.append(dict(elem.attrib))
            if tag == "link" and len(link_samples) < 3:
                structural = {k: v for k, v in elem.attrib.items() if k.rsplit("}", 1)[-1] in {"id", "xtargets", "certainty"}}
                link_samples.append(structural)
            elem.clear()
    has_doc_ids = bool(linkgrp_samples) and all("fromDoc" in x and "toDoc" in x for x in linkgrp_samples)
    has_sentence_ids = tag_counts.get("link", 0) > 0 and attr_counts.get("xtargets", 0) == tag_counts.get("link", 0)
    outputs[pair] = {
        "download": {"bytes": size, "sha256": h.hexdigest(), "headers": {k: headers.get(k) for k in ["last-modified", "etag", "content-length", "content-type"]}},
        "xml": {"tag_counts": dict(tag_counts), "attribute_counts": dict(attr_counts), "linkGrp_samples": linkgrp_samples, "link_samples": link_samples},
        "schema": {"document_references_present": has_doc_ids, "sentence_target_identities_present": has_sentence_ids}
    }

qualified = all(x["schema"]["document_references_present"] and x["schema"]["sentence_target_identities_present"] for x in outputs.values())
result = {
    "schema_version": 1,
    "source_release": "OPUS-GlobalVoices/v2018q4",
    "pairs": outputs,
    "qualification": {
        "xces_schema": "qualified" if qualified else "not_qualified",
        "closed_trilingual_units": "not_yet_computed",
        "raw_text_access": "not_started",
        "tokenizer_confirmation": "not_started"
    },
    "next_action": "Freeze and execute a closed tripartite component reconstruction over XCES identities; require at least 512 valid units before opening raw text."
}
(ROOT / "output" / "opus_gv_xces_schema.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
