import argparse
import collections
import gzip
import hashlib
import ipaddress
import json
import os
import re
import sqlite3
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


WORD_RE = re.compile(r"\w+", re.UNICODE)
LANGUAGES = ("en", "fr", "es")


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def normalize_text(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def canonical_url(value):
    if not value:
        return None
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return None
        rawhost = parsed.hostname.lower()
        try:
            host = ipaddress.ip_address(rawhost).compressed
            host_render = f"[{host}]" if ":" in host else host
        except ValueError:
            if rawhost.endswith("."):
                rawhost = rawhost[:-1]
            if not rawhost or rawhost.endswith("."):
                return None
            host = rawhost.encode("idna").decode("ascii").lower()
            host_render = host
        port = parsed.port
        netloc = host_render if port is None or (parsed.scheme.lower(), port) in {("http", 80), ("https", 443)} else f"{host_render}:{port}"
        return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))
    except (UnicodeError, ValueError):
        return None


def member_for(document, members):
    targets = {document}
    if document.endswith(".gz"):
        targets.add(document[:-3])
    matches = [name for name in members if any(name == target or name.endswith("/" + target) for target in targets)]
    if len(matches) != 1:
        raise RuntimeError(f"raw document match count {len(matches)}")
    return matches[0]


def xml_payload(archive, member):
    payload = archive.read(member)
    return gzip.decompress(payload) if member.endswith(".gz") else payload


def element_text(element):
    return " ".join(piece.strip() for piece in element.itertext() if piece and piece.strip())


def load_selected_documents(archive_path, wanted):
    result = {}
    with zipfile.ZipFile(archive_path) as archive:
        members = [info.filename for info in archive.infolist() if not info.is_dir()]
        for document, wanted_ids in wanted.items():
            member = member_for(document, members)
            root = ET.fromstring(xml_payload(archive, member))
            sentences = {}
            order = []
            source_url = None
            for element in root.iter():
                tag = local_name(element.tag)
                if tag == "URL" and source_url is None:
                    source_url = canonical_url(element_text(element))
                if tag == "s":
                    sentence_id = element.attrib.get("id")
                    if sentence_id in wanted_ids:
                        value = element_text(element)
                        if not value:
                            raise RuntimeError("selected sentence is empty")
                        sentences[sentence_id] = value
                        order.append(sentence_id)
            if set(sentences) != set(wanted_ids):
                raise RuntimeError("selected sentence identity mismatch")
            result[document] = {"sentences": sentences, "order": order, "url": source_url}
    return result


def unit_text(document_record, sentence_ids):
    wanted = set(sentence_ids)
    ordered = [document_record["sentences"][sentence_id] for sentence_id in document_record["order"] if sentence_id in wanted]
    if len(ordered) != len(wanted):
        raise RuntimeError("unit sentence ordering mismatch")
    return " ".join(ordered)


def shingle_counter(words, width=5):
    return collections.Counter(
        hashlib.sha256("\0".join(words[index:index + width]).encode()).digest()
        for index in range(max(0, len(words) - width + 1))
    )


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def recompute_unit_identity(release, unit):
    payload = json.dumps(
        {
            "release": release,
            "documents": unit["documents"],
            "sentence_ids": unit["sentence_ids"]
        },
        sort_keys=True,
        separators=(",", ":")
    )
    return sha256_bytes(payload.encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--fetch-receipts", required=True)
    parser.add_argument("--raw-schema", required=True)
    parser.add_argument("--selector-protocol", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    units_path = Path(args.units)
    units_bytes = units_path.read_bytes()
    units = json.loads(units_bytes)["reserved_unit_identities"]
    source_manifest_bytes = Path(args.source_manifest).read_bytes()
    source_manifest = json.loads(source_manifest_bytes)
    if len(units) != source_manifest["units"]["expected_count"]:
        raise RuntimeError("frozen unit count mismatch")
    if sha256_bytes(units_bytes) != source_manifest["units"]["expected_sha256"]:
        raise RuntimeError("frozen unit manifest hash mismatch")
    for unit in units:
        if recompute_unit_identity(source_manifest["release"], unit) != unit["unit_sha256"]:
            raise RuntimeError("frozen canonical unit identity mismatch")
    raw_schema_bytes = Path(args.raw_schema).read_bytes()
    raw_schema = json.loads(raw_schema_bytes)
    if sha256_bytes(raw_schema_bytes) != source_manifest["bindings"]["raw_schema_sha256"] or raw_schema.get("qualification") != "qualified":
        raise RuntimeError("raw schema binding mismatch")
    selector_protocol_bytes = Path(args.selector_protocol).read_bytes()
    if sha256_bytes(selector_protocol_bytes) != source_manifest["bindings"]["selector_protocol_sha256"]:
        raise RuntimeError("selector protocol binding mismatch")

    receipts = {}
    for language in LANGUAGES:
        receipt_path = Path(args.fetch_receipts) / f"fetch_{language}.json"
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes)
        if receipt["language"] != language or receipt["raw_text_inspected"] or receipt["tokenizer_or_fairness_output_computed"]:
            raise RuntimeError("invalid source receipt")
        spec = source_manifest["archives"][language]
        receipt_sha = sha256_bytes(receipt_bytes)
        archive_path = Path(args.raw_dir) / f"{language}.zip"
        actual_sha = file_sha256(archive_path)
        actual_bytes = archive_path.stat().st_size
        if receipt_sha != spec["fetch_receipt_sha256"]:
            raise RuntimeError("source receipt hash mismatch")
        if receipt["sha256"] != spec["expected_sha256"] or actual_sha != spec["expected_sha256"]:
            raise RuntimeError("source archive hash mismatch")
        if receipt["bytes"] != spec["expected_bytes"] or actual_bytes != spec["expected_bytes"]:
            raise RuntimeError("source archive byte mismatch")
        if receipt["expected_etag"] != spec["expected_etag"] or receipt["expected_last_modified"] != spec["expected_last_modified"]:
            raise RuntimeError("source HTTP provenance mismatch")
        if raw_schema["languages"][language]["archive_sha256"] != actual_sha:
            raise RuntimeError("raw schema archive binding mismatch")
        receipts[language] = {"sha256": actual_sha, "bytes": actual_bytes, "receipt_sha256": receipt_sha}

    wanted = {language: collections.defaultdict(set) for language in LANGUAGES}
    for unit in units:
        for language in LANGUAGES:
            wanted[language][unit["documents"][language]].update(unit["sentence_ids"][language])
    documents = {
        language: load_selected_documents(Path(args.raw_dir) / f"{language}.zip", wanted[language])
        for language in LANGUAGES
    }

    output_db = Path(args.database)
    output_db.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output_db.name}.", dir=output_db.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    temporary.unlink()
    counts = {language: {"units": 0, "words": 0, "shingle_mass": 0, "source_url_present": 0} for language in LANGUAGES}
    blinded_samples = []
    try:
        database = sqlite3.connect(temporary)
        database.executescript("""
          PRAGMA journal_mode=DELETE;
          PRAGMA synchronous=FULL;
          PRAGMA temp_store=FILE;
          CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
          CREATE TABLE confirmation(
            blinded_unit_sha256 TEXT NOT NULL,
            language TEXT NOT NULL,
            canonical_url_sha256 TEXT,
            normalized_exact_sha256 TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            shingle_mass INTEGER NOT NULL,
            PRIMARY KEY(blinded_unit_sha256, language)
          ) WITHOUT ROWID;
          CREATE INDEX confirmation_exact ON confirmation(language, normalized_exact_sha256);
          CREATE INDEX confirmation_url ON confirmation(canonical_url_sha256);
          CREATE TABLE shingles(
            blinded_unit_sha256 TEXT NOT NULL,
            language TEXT NOT NULL,
            shingle_sha256 BLOB NOT NULL,
            multiplicity INTEGER NOT NULL,
            PRIMARY KEY(blinded_unit_sha256, language, shingle_sha256)
          ) WITHOUT ROWID;
          CREATE INDEX shingles_inverted ON shingles(language, shingle_sha256);
        """)
        metadata = {
            "schema_version": "1",
            "release": source_manifest["release"],
            "units_sha256": sha256_bytes(units_bytes),
            "source_manifest_sha256": sha256_bytes(source_manifest_bytes),
            "raw_schema_sha256": sha256_bytes(raw_schema_bytes),
            "selector_protocol_sha256": sha256_bytes(selector_protocol_bytes),
            "builder_sha256": sha256_bytes(Path(__file__).read_bytes()),
            "project": source_manifest["project"],
            "active_idea": source_manifest["active_idea"],
            "idea_revision": str(source_manifest["idea_revision"]),
            "checkpoint_generation": str(source_manifest["checkpoint_generation"]),
            "adopted_source_digest": source_manifest["adopted_source_digest"],
            "normalization": "Unicode NFKC + casefold + Unicode whitespace collapse; Unicode \\w+ words; full SHA256 5-word shingle multiset",
            "raw_text_stored": "false",
            "tokenizer_or_fairness_output_computed": "false"
        }
        for language in LANGUAGES:
            metadata[f"archive_{language}_sha256"] = receipts[language]["sha256"]
            metadata[f"archive_{language}_bytes"] = str(receipts[language]["bytes"])
            metadata[f"fetch_{language}_receipt_sha256"] = receipts[language]["receipt_sha256"]
        database.executemany("INSERT INTO meta(key,value) VALUES(?,?)", sorted(metadata.items()))

        for unit in units:
            for language in LANGUAGES:
                document = unit["documents"][language]
                record = documents[language][document]
                raw_text = unit_text(record, unit["sentence_ids"][language])
                normalized = normalize_text(raw_text)
                words = WORD_RE.findall(normalized)
                shingles = shingle_counter(words)
                blinded = sha256_bytes((source_manifest["release"] + "\0" + language + "\0" + unit["unit_sha256"]).encode())
                url_hash = sha256_bytes(record["url"].encode()) if record["url"] else None
                database.execute(
                    "INSERT INTO confirmation VALUES(?,?,?,?,?,?)",
                    (blinded, language, url_hash, sha256_bytes(normalized.encode()), len(words), sum(shingles.values()))
                )
                database.executemany(
                    "INSERT INTO shingles VALUES(?,?,?,?)",
                    ((blinded, language, shingle, multiplicity) for shingle, multiplicity in shingles.items())
                )
                counts[language]["units"] += 1
                counts[language]["words"] += len(words)
                counts[language]["shingle_mass"] += sum(shingles.values())
                counts[language]["source_url_present"] += int(url_hash is not None)
                if len(blinded_samples) < 6:
                    blinded_samples.append(blinded)
                raw_text = normalized = ""
        database.execute("INSERT INTO meta(key,value) VALUES('complete','true')")
        database.commit()
        database.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        database.close()
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, output_db)
        directory_fd = os.open(output_db.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)

    database_sha = sha256_bytes(output_db.read_bytes())
    summary = {
        "schema_version": 1,
        "release": source_manifest["release"],
        "units_sha256": sha256_bytes(units_bytes),
        "source_manifest_sha256": sha256_bytes(source_manifest_bytes),
        "raw_schema_sha256": sha256_bytes(raw_schema_bytes),
        "selector_protocol_sha256": sha256_bytes(selector_protocol_bytes),
        "project_binding": {
            "project": source_manifest["project"],
            "active_idea": source_manifest["active_idea"],
            "idea_revision": source_manifest["idea_revision"],
            "checkpoint_generation": source_manifest["checkpoint_generation"],
            "adopted_source_digest": source_manifest["adopted_source_digest"]
        },
        "archive_receipts": receipts,
        "counts": counts,
        "blinded_unit_sha256_samples": blinded_samples,
        "database_sha256": database_sha,
        "database_bytes": output_db.stat().st_size,
        "raw_text_stored": False,
        "operator_output_contains_raw_text": False,
        "tokenizer_or_fairness_output_computed": False,
        "qualification": "result_blind_fingerprint_index_built"
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
