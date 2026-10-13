#!/usr/bin/env python3
"""Run the frozen builder with the addendum's whitespace-token semantics."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ORIGINAL = BASE / "inputs" / "frozen_original_builder.py"


class WhitespaceTokens:
    @staticmethod
    def findall(text: str) -> list[str]:
        return text.split()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def option_path(flag: str) -> Path:
    return Path(sys.argv[sys.argv.index(flag) + 1])


def main() -> None:
    spec = importlib.util.spec_from_file_location("frozen_original_builder", ORIGINAL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.WORD_RE = WhitespaceTokens()
    module.__file__ = __file__
    module.main()

    database_path = option_path("--database")
    summary_path = option_path("--summary")
    normalization = (
        "Unicode NFKC + casefold + Unicode whitespace collapse; whitespace-separated normalized "
        "tokens; full SHA256 of NUL-separated contiguous 5-token shingle multiset"
    )
    with sqlite3.connect(database_path) as database:
        database.execute("UPDATE meta SET value=? WHERE key='normalization'", (normalization,))
        database.execute("INSERT INTO meta(key,value) VALUES('tokenization','whitespace-separated normalized tokens')")
        database.execute("INSERT INTO meta(key,value) VALUES('shingle_encoding','NUL-separated token bytes; full SHA256')")
        database.commit()
        database.execute("VACUUM")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["database_sha256"] = file_sha256(database_path)
    summary["database_bytes"] = database_path.stat().st_size
    summary["normalization"] = normalization
    summary["tokenization"] = "whitespace-separated normalized tokens"
    summary["shingle_encoding"] = "NUL-separated token bytes; full SHA256"
    summary["builder_sha256"] = file_sha256(Path(__file__))
    summary["qualification"] = "result_blind_whitespace_fingerprint_index_built"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
