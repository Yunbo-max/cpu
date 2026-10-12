import collections
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / "confirmation_source_protocol.json").read_text())
url = protocol["source"]["metadata_url"]
expected = protocol["source"]["metadata_http"]["content_length_bytes"]
request = urllib.request.Request(url, headers={"User-Agent": "PA-BPE-source-audit/1.0"})
with urllib.request.urlopen(request, timeout=60) as response:
    payload = response.read(expected + 1)
    headers = {k.lower(): v for k, v in response.headers.items()}
if len(payload) != expected:
    raise RuntimeError(f"content length mismatch: expected {expected}, got {len(payload)}")
archive_path = ROOT / "inputs" / "pgv_docpairs.txt.zip"
archive_path.parent.mkdir(parents=True, exist_ok=True)
archive_path.write_bytes(payload)

with zipfile.ZipFile(io.BytesIO(payload)) as zf:
    bad = zf.testzip()
    members = [{"name": i.filename, "compressed_bytes": i.compress_size, "uncompressed_bytes": i.file_size} for i in zf.infolist()]
    text_members = [i for i in zf.infolist() if not i.is_dir()]
    if len(text_members) != 1:
        raise RuntimeError(f"expected one metadata member, found {len(text_members)}")
    with zf.open(text_members[0]) as stream:
        wrapper = io.TextIOWrapper(stream, encoding="utf-8", errors="strict", newline="")
        total_lines = 0
        malformed = 0
        delimiter_counts = collections.Counter()
        language_mentions = collections.Counter()
        preview = []
        for raw in wrapper:
            total_lines += 1
            line = raw.rstrip("\r\n")
            if len(preview) < 5:
                preview.append(line[:500])
            delimiter_counts["tab"] += line.count("\t")
            delimiter_counts["space"] += line.count(" ")
            hits = set(re.findall(r"(?<![A-Za-z])(eng|fra|spa|en|fr|es)(?![A-Za-z])", line.lower()))
            for hit in hits:
                language_mentions[hit] += 1
            if not line.strip():
                malformed += 1

result = {
    "schema_version": 1,
    "source": url,
    "download": {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "response_headers": {k: headers.get(k) for k in ["last-modified", "etag", "content-length", "content-type"]}
    },
    "zip": {"crc_error_member": bad, "members": members},
    "text_structure": {
        "line_count": total_lines,
        "blank_line_count": malformed,
        "delimiter_counts": dict(delimiter_counts),
        "language_mentions_by_code": dict(language_mentions),
        "escaped_preview_first_five": preview
    },
    "qualification": {
        "official_object_and_integrity": bad is None,
        "document_identity_schema_visible": total_lines > 0,
        "trilingual_document_support": "pending_semantic_parse",
        "trilingual_sentence_rows": "not_qualified_by_docpairs_metadata",
        "confirmation_freshness": "preserved; no story text or tokenizer outcome read"
    },
    "next_action": "Parse the observed docpairs record grammar, then inspect pair-archive schemas without reading tokenizer outcomes; do not score until method and deterministic selection are frozen."
}
(ROOT / "output").mkdir(exist_ok=True)
(ROOT / "output" / "pgv_docpairs_qualification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
