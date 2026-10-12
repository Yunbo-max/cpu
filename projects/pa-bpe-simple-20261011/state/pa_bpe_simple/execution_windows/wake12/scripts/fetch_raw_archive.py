import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--language", choices=("en", "fr", "es"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    spec = manifest["archives"][args.language]
    output = Path(args.output)
    receipt = Path(args.receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    digest = hashlib.sha256()
    size = 0
    try:
        request = urllib.request.Request(spec["url"], headers={"User-Agent": "PA-BPE-research-source-fetch/1"})
        with urllib.request.urlopen(request, timeout=45) as response, temporary.open("wb") as stream:
            response_etag = (response.headers.get("ETag") or "").strip('"')
            response_last_modified = response.headers.get("Last-Modified")
            response_length = response.headers.get("Content-Length")
            if response_etag and response_etag != spec["expected_etag"]:
                raise RuntimeError("ETag mismatch")
            if response_last_modified and response_last_modified != spec["expected_last_modified"]:
                raise RuntimeError("Last-Modified mismatch")
            if response_length is not None and int(response_length) != spec["expected_bytes"]:
                raise RuntimeError("Content-Length mismatch")
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                stream.write(chunk)
                digest.update(chunk)
                size += len(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        if size != spec["expected_bytes"]:
            raise RuntimeError(f"byte count mismatch: {size}")
        os.replace(temporary, output)
        directory_fd = os.open(output.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        record = {
            "schema_version": 1,
            "release": manifest["release"],
            "language": args.language,
            "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "url": spec["url"],
            "bytes": size,
            "sha256": digest.hexdigest(),
            "expected_etag": spec["expected_etag"],
            "expected_last_modified": spec["expected_last_modified"],
            "raw_text_inspected": False,
            "tokenizer_or_fairness_output_computed": False
        }
        temp_receipt = receipt.with_name(receipt.name + ".tmp")
        with temp_receipt.open("w", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_receipt, receipt)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
