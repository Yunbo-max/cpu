#!/usr/bin/env python3
import json
import struct
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


RAW_ZIPS = {
    "en": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/en.zip",
    "fr": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/fr.zip",
    "es": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/es.zip",
}


def get_range(url: str, start: int, end: int) -> tuple[bytes, dict]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "pa-bpe-research/1.0", "Range": f"bytes={start}-{end}"},
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read()
        headers = {k.lower(): v for k, v in response.headers.items()}
        if response.status != 206:
            raise RuntimeError(f"range request returned {response.status} for {url}")
        return data, headers


def remote_zip_index(url: str) -> dict:
    first, headers = get_range(url, 0, 0)
    content_range = headers.get("content-range", "")
    if "/" not in content_range:
        raise RuntimeError(f"missing total size in Content-Range: {content_range}")
    size = int(content_range.rsplit("/", 1)[1])
    tail_start = max(0, size - 131072)
    tail, _ = get_range(url, tail_start, size - 1)
    pos = tail.rfind(b"PK\x05\x06")
    if pos < 0:
        raise RuntimeError("ZIP EOCD not found")
    eocd = struct.unpack_from("<4s4H2IH", tail, pos)
    entry_count = eocd[4]
    cd_size = eocd[5]
    cd_offset = eocd[6]
    cd, _ = get_range(url, cd_offset, cd_offset + cd_size - 1)
    records = []
    cursor = 0
    header_fmt = "<4s6H3I5H2I"
    fixed = struct.calcsize(header_fmt)
    while cursor < len(cd):
        fields = struct.unpack_from(header_fmt, cd, cursor)
        if fields[0] != b"PK\x01\x02":
            raise RuntimeError(f"invalid central-directory signature at {cursor}")
        comp_method = fields[4]
        crc32 = fields[7]
        compressed = fields[8]
        uncompressed = fields[9]
        name_len, extra_len, comment_len = fields[10:13]
        local_offset = fields[-1]
        name_start = cursor + fixed
        name = cd[name_start:name_start + name_len].decode("utf-8", errors="replace")
        records.append({
            "name": name,
            "compression_method": comp_method,
            "crc32": f"{crc32:08x}",
            "compressed_bytes": compressed,
            "uncompressed_bytes": uncompressed,
            "local_header_offset": local_offset,
        })
        cursor += fixed + name_len + extra_len + comment_len
    if len(records) != entry_count:
        raise RuntimeError(f"central directory count mismatch {len(records)} != {entry_count}")
    return {
        "url": url,
        "archive_bytes": size,
        "entry_count": entry_count,
        "central_directory_bytes": cd_size,
        "entries": records,
    }


def canonical(doc_path: str) -> str:
    name = Path(doc_path).name
    return name.removesuffix(".gz").removesuffix(".xml")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: script ALIGNMENT_INVENTORY_JSON OUTPUT_JSON")
    source = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    pair_sets = {}
    for pair, record in source["alignments"].items():
        pair_sets[pair] = {
            canonical(row["fromDoc"])
            for row in record["inventory"]["document_pairs"]
        }
    triple = sorted(pair_sets["en-fr"] & pair_sets["en-es"] & pair_sets["es-fr"])
    archives = {lang: remote_zip_index(url) for lang, url in RAW_ZIPS.items()}
    by_lang = {
        lang: {
            canonical(e["name"]): e
            for e in archive["entries"]
            if e["name"].endswith((".xml", ".xml.gz"))
        }
        for lang, archive in archives.items()
    }
    works = []
    for work in triple:
        members = {lang: by_lang[lang].get(work) for lang in ("en", "fr", "es")}
        available = all(members.values())
        works.append({
            "work": work,
            "available_all_three": available,
            "members": members,
            "total_compressed_bytes": sum(m["compressed_bytes"] for m in members.values() if m),
            "total_uncompressed_bytes": sum(m["uncompressed_bytes"] for m in members.values() if m),
        })
    result = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "opus_books_version": "v1",
        "triple_aligned_work_count": len(triple),
        "archives": {
            k: {
                **{x: v[x] for x in ("url", "archive_bytes", "entry_count", "central_directory_bytes")},
                "entry_names": [row["name"] for row in v["entries"]],
            }
            for k, v in archives.items()
        },
        "works": works,
    }
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
