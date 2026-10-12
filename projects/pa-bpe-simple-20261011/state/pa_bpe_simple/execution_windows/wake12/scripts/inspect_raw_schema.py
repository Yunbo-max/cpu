import argparse
import collections
import gzip
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def load_xml(payload, name):
    return gzip.decompress(payload) if name.endswith(".gz") else payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    units_path = Path(args.units)
    units_bytes = units_path.read_bytes()
    units = json.loads(units_bytes)["reserved_unit_identities"]
    if len(units) != 512:
        raise RuntimeError("expected exactly 512 frozen units")

    requested = {language: collections.defaultdict(set) for language in ("en", "fr", "es")}
    for unit in units:
        for language in requested:
            requested[language][unit["documents"][language]].update(unit["sentence_ids"][language])

    per_language = {}
    for language in ("en", "fr", "es"):
        archive_path = Path(args.raw_dir) / f"{language}.zip"
        archive_sha = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        with zipfile.ZipFile(archive_path) as archive:
            members = [info.filename for info in archive.infolist() if not info.is_dir()]
            inventory_sha = hashlib.sha256("\n".join(sorted(members)).encode()).hexdigest()
            matched = {}
            for document in requested[language]:
                # XCES document references end in .xml.gz, while the language raw ZIP
                # stores the same XML member without the inner gzip wrapper.
                targets = {document}
                if document.endswith(".gz"):
                    targets.add(document[:-3])
                candidates = [
                    name
                    for name in members
                    if any(name == target or name.endswith("/" + target) for target in targets)
                ]
                if len(candidates) != 1:
                    raise RuntimeError(f"{language} document match count {len(candidates)}")
                matched[document] = candidates[0]

            tag_counts = collections.Counter()
            attribute_counts = collections.Counter()
            requested_sentence_count = 0
            located_sentence_count = 0
            uncompressed_xml_bytes = 0
            for document, member in matched.items():
                xml_bytes = load_xml(archive.read(member), member)
                uncompressed_xml_bytes += len(xml_bytes)
                root = ET.fromstring(xml_bytes)
                wanted = requested[language][document]
                requested_sentence_count += len(wanted)
                found = set()
                for element in root.iter():
                    tag = local_name(element.tag)
                    tag_counts[tag] += 1
                    attribute_counts.update(element.attrib.keys())
                    if tag == "s" and element.attrib.get("id") in wanted:
                        found.add(element.attrib["id"])
                if found != wanted:
                    raise RuntimeError(f"{language} sentence identity mismatch")
                located_sentence_count += len(found)

        per_language[language] = {
            "archive_sha256": archive_sha,
            "zip_member_count": len(members),
            "zip_member_inventory_sha256": inventory_sha,
            "requested_document_count": len(requested[language]),
            "matched_document_count": len(matched),
            "requested_sentence_identity_count": requested_sentence_count,
            "located_sentence_identity_count": located_sentence_count,
            "selected_xml_uncompressed_bytes": uncompressed_xml_bytes,
            "tag_counts": dict(sorted(tag_counts.items())),
            "attribute_name_counts": dict(sorted(attribute_counts.items()))
        }

    result = {
        "schema_version": 1,
        "units_sha256": hashlib.sha256(units_bytes).hexdigest(),
        "reserved_units": len(units),
        "languages": per_language,
        "qualification": "qualified" if all(
            item["requested_document_count"] == item["matched_document_count"]
            and item["requested_sentence_identity_count"] == item["located_sentence_identity_count"]
            for item in per_language.values()
        ) else "not_qualified",
        "operator_output_contains_raw_text": False,
        "tokenizer_or_fairness_output_computed": False
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
