#!/usr/bin/env python3
import gzip
import hashlib
import json
import struct
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timezone
from pathlib import Path


SELECTED = {
    "dev": "Carroll_Lewis-Alice_in_wonderland",
    "confirm": "Poe_Edgar_Allan-Fall_of_the_House_of_Usher",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_member(url: str, member: dict) -> bytes:
    start = member["local_header_offset"]
    # A single bounded range contains the local header, name/extra fields and payload.
    end = start + 65536 + member["compressed_bytes"] - 1
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "pa-bpe-research/1.0", "Range": f"bytes={start}-{end}"},
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        blob = response.read()
        if response.status != 206:
            raise RuntimeError(f"range status {response.status} for {member['name']}")
    fields = struct.unpack_from("<4s5H3I2H", blob, 0)
    if fields[0] != b"PK\x03\x04":
        raise RuntimeError(f"invalid local ZIP header for {member['name']}")
    method = fields[3]
    name_len, extra_len = fields[-2:]
    payload_start = 30 + name_len + extra_len
    payload = blob[payload_start:payload_start + member["compressed_bytes"]]
    if len(payload) != member["compressed_bytes"]:
        raise RuntimeError(f"truncated payload for {member['name']}")
    if method == 0:
        data = payload
    elif method == 8:
        data = zlib.decompress(payload, -15)
    else:
        raise RuntimeError(f"unsupported ZIP method {method}")
    if len(data) != member["uncompressed_bytes"]:
        raise RuntimeError(f"uncompressed-size mismatch for {member['name']}")
    return data


def sentence_texts(path: Path) -> dict[str, str]:
    texts = {}
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag.rsplit("}", 1)[-1] == "s":
            sid = elem.attrib.get("id")
            text = "".join(elem.itertext()).strip()
            if sid and text:
                texts[sid] = " ".join(text.split())
            elem.clear()
    return texts


def one_to_one_alignment(path: Path, work: str) -> dict[str, str]:
    mapping = {}
    active = False
    with gzip.open(path, "rb") as stream:
        for event, elem in ET.iterparse(stream, events=("start", "end")):
            tag = elem.tag.rsplit("}", 1)[-1]
            if event == "start" and tag == "linkGrp":
                active = work in elem.attrib.get("fromDoc", "") and work in elem.attrib.get("toDoc", "")
            elif event == "end" and tag == "link" and active:
                targets = elem.attrib.get("xtargets", "")
                if ";" in targets:
                    left, right = targets.split(";", 1)
                    if len(left.split()) == 1 and len(right.split()) == 1 and left and right:
                        mapping[left] = right
            elif event == "end" and tag == "linkGrp":
                if active:
                    return mapping
                active = False
            if event == "end":
                elem.clear()
    return mapping


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: script ZIP_INDEX ALIGNMENT_DIR OUTPUT_DIR MANIFEST")
    index = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    alignment_dir = Path(sys.argv[2])
    out = Path(sys.argv[3])
    raw = out / "raw_xml"
    aligned = out / "aligned"
    raw.mkdir(parents=True, exist_ok=True)
    aligned.mkdir(parents=True, exist_ok=True)
    by_work = {row["work"]: row for row in index["works"]}
    records = {}
    for split, work in SELECTED.items():
        work_record = by_work[work]
        texts = {}
        raw_records = {}
        for lang in ("en", "fr", "es"):
            member = work_record["members"][lang]
            data = fetch_member(index["archives"][lang]["url"], member)
            path = raw / f"{split}.{lang}.xml"
            path.write_bytes(data)
            texts[lang] = sentence_texts(path)
            raw_records[lang] = {
                "path": str(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "sentence_count": len(texts[lang]),
                "source_member": member["name"],
            }
        en_fr = one_to_one_alignment(alignment_dir / "en-fr.xml.gz", work)
        en_es = one_to_one_alignment(alignment_dir / "en-es.xml.gz", work)
        common = sorted(set(en_fr) & set(en_es), key=lambda x: [int(p) if p.isdigit() else p for p in x[1:].replace(".", " ").split()])
        rows = []
        for en_id in common:
            fr_id, es_id = en_fr[en_id], en_es[en_id]
            if en_id in texts["en"] and fr_id in texts["fr"] and es_id in texts["es"]:
                rows.append((en_id, fr_id, es_id, texts["en"][en_id], texts["fr"][fr_id], texts["es"][es_id]))
        tsv = aligned / f"{split}.tsv"
        with tsv.open("w", encoding="utf-8") as f:
            f.write("en_id\tfr_id\tes_id\ten\tfr\tes\n")
            for row in rows:
                f.write("\t".join(value.replace("\t", " ").replace("\n", " ") for value in row) + "\n")
        records[split] = {
            "work": work,
            "raw": raw_records,
            "en_fr_one_to_one": len(en_fr),
            "en_es_one_to_one": len(en_es),
            "three_way_rows": len(rows),
            "tsv": {"path": str(tsv), "sha256": sha256(tsv), "bytes": tsv.stat().st_size},
        }
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_scope": "resource-bounded data-pipeline smoke test; not a confirmatory experiment",
        "selection_rule": "two smallest compressed three-language works from the verified 12-work OPUS Books core",
        "splits": records,
    }
    Path(sys.argv[4]).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
