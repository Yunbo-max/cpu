#!/usr/bin/env python3
import gzip
import hashlib
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ALIGNMENTS = {
    "en-fr": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/en-fr.xml.gz",
    "en-es": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/en-es.xml.gz",
    "es-fr": "https://object.pouta.csc.fi/OPUS-Books/v1/xml/es-fr.xml.gz",
}

HF_FILES = {
    "spa_test": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/resolve/main/data/spa_Latn/test/000_00000.parquet",
    "spa_train_0": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/resolve/main/data/spa_Latn/train/000_00000.parquet",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, path: Path) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "pa-bpe-research/1.0"})
    with urllib.request.urlopen(req, timeout=35) as response, path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
        headers = {k.lower(): v for k, v in response.headers.items()}
        status = response.status
        final_url = response.geturl()
    return {
        "requested_url": url,
        "final_url": final_url,
        "status": status,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "content_type": headers.get("content-type"),
        "etag": headers.get("etag"),
    }


def alignment_inventory(path: Path) -> dict:
    documents = []
    total_links = 0
    with gzip.open(path, "rb") as stream:
        for _, elem in ET.iterparse(stream, events=("end",)):
            tag = elem.tag.rsplit("}", 1)[-1]
            if tag == "linkGrp":
                documents.append({
                    "fromDoc": elem.attrib.get("fromDoc"),
                    "toDoc": elem.attrib.get("toDoc"),
                    "targType": elem.attrib.get("targType"),
                })
            elif tag == "link":
                total_links += 1
            elem.clear()
    unique = []
    seen = set()
    for row in documents:
        key = (row["fromDoc"], row["toDoc"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return {
        "link_groups": len(documents),
        "unique_document_pairs": len(unique),
        "alignment_links": total_links,
        "document_pairs": unique,
    }


def range_probe(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "pa-bpe-research/1.0", "Range": "bytes=0-4095"},
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        prefix = response.read(4096)
        headers = {k.lower(): v for k, v in response.headers.items()}
        return {
            "requested_url": url,
            "final_url": response.geturl(),
            "status": response.status,
            "bytes_read": len(prefix),
            "prefix_sha256": hashlib.sha256(prefix).hexdigest(),
            "parquet_magic": prefix[:4].decode("ascii", errors="replace"),
            "content_range": headers.get("content-range"),
            "content_length": headers.get("content-length"),
            "accept_ranges": headers.get("accept-ranges"),
            "etag": headers.get("etag"),
            "commit": headers.get("x-repo-commit"),
        }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: script OUTPUT_DIR")
    out = Path(sys.argv[1])
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    records = {}
    for pair, url in ALIGNMENTS.items():
        path = raw / f"{pair}.xml.gz"
        record = download(url, path)
        record["inventory"] = alignment_inventory(path)
        records[pair] = record
    hf = {}
    for key, url in HF_FILES.items():
        try:
            hf[key] = range_probe(url)
        except Exception as exc:
            hf[key] = {
                "requested_url": url,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
    result = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "opus_books_version": "v1",
        "alignments": records,
        "fineweb2_spanish": {
            "dataset_commit_from_prior_metadata": "af9c13333eb981300149d5ca60a8e9d659b276b9",
            "probes": hf,
        },
    }
    (out / "opus_identity_and_hf_probe_wake2.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
