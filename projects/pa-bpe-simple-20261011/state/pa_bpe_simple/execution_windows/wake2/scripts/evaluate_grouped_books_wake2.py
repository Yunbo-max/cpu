#!/usr/bin/env python3
import csv
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve()
PROJECT = HERE.parents[3]
EVALUATOR = PROJECT / "scripts" / "evaluate_pilot.py"
spec = importlib.util.spec_from_file_location("pa_bpe_eval", EVALUATOR)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    if any(set(row) != {"en_id", "fr_id", "es_id", "en", "fr", "es"} or any(value is None for value in row.values()) for row in rows):
        raise RuntimeError(f"malformed aligned TSV: {path}")
    return rows


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: script ALIGNED_DIR INPUT_MANIFEST OUTPUT_JSON")
    aligned = Path(sys.argv[1])
    manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    for rel, expected in manifest["sha256"].items():
        path = PROJECT / rel
        actual = file_sha256(path)
        if actual != expected:
            raise RuntimeError(f"input hash mismatch for {rel}: {actual} != {expected}")
    result = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "whole-work-isolated English/French evaluation; Spanish excluded because tokenizers were trained only on English/French",
        "checks": module.checks(),
        "arms": {},
    }
    for merge_path in sorted((PROJECT / "runs").glob("*.merges")):
        tok, merges, vocab = module.tokenizer(merge_path)
        if len(merges) != 1000 or len(vocab) != 1256:
            raise RuntimeError(f"unexpected realized vocabulary for {merge_path.name}")
        arm = {"merges": len(merges), "vocab": len(vocab), "datasets": {}}
        for split in ("dev", "confirm"):
            rows = read_rows(aligned / f"{split}.tsv")
            costs = []
            for i, row in enumerate(rows):
                pair = [len(tok.encode(row[lang]).ids) for lang in ("en", "fr")]
                if i < 3:
                    for lang in ("en", "fr"):
                        if tok.encode(row[lang]).tokens != module.replay(row[lang], merges):
                            raise RuntimeError(f"replay mismatch {merge_path.stem} {split} {lang} {i}")
                costs.append(pair)
            means = [sum(row[i] for row in costs) / len(costs) for i in (0, 1)]
            g = module.gini(means)
            if abs(g - module.gini_sorted(means)) >= 1e-12:
                raise RuntimeError("Gini implementations disagree")
            arm["datasets"][split] = {
                "n": len(rows),
                "mean_tokens": means,
                "gini": g,
                "worst_language": ("en", "fr")[means.index(max(means))],
                "worst_cost": max(means),
                "sum_language_means": sum(means),
                "paired_costs": costs,
            }
        result["arms"][merge_path.stem] = arm
    Path(sys.argv[3]).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compact = {
        arm: {
            split: {key: values[key] for key in ("n", "mean_tokens", "gini", "worst_cost", "sum_language_means")}
            for split, values in record["datasets"].items()
        }
        for arm, record in result["arms"].items()
    }
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
