#!/usr/bin/env python3
"""Complete R001 from immutable matched-pair CSV after archive-header repair."""
import argparse
import csv
import hashlib
import io
import json
import os
import resource
import subprocess
import time
from pathlib import Path

import numpy as np


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--predecessor", type=Path, required=True)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:1])
    previous = json.loads(args.predecessor.read_text())
    assert previous["qualifying_pairs"] == 24 and previous["raw_rows"] == 0
    binary = args.run_dir / "run"
    pairs, matches = args.run_dir / "pairs.csv", args.run_dir / "matches.csv"
    assert binary.exists() and pairs.exists() and matches.exists()
    cmd = [str(binary), str(pairs), str(matches)]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    wall = time.monotonic()-start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    (args.run_dir / "raw.csv").write_text(run.stdout)
    (args.run_dir / "run.stderr.log").write_text(run.stderr)
    arms = list(csv.DictReader(io.StringIO(run.stdout))) if run.returncode == 0 else []
    by = {}
    for item in arms:
        by.setdefault(item["arm"], []).append(item)
    summary = {}
    for arm, items in by.items():
        valid = [x for x in items if x["valid"] == "1"]
        summary[arm] = {"pairs": len(items), "valid_pairs": len(valid),
                        "median_rotation_error_deg": float(np.median([float(x["rotation_error_deg"]) for x in valid])) if valid else None,
                        "median_center_error_m": float(np.median([float(x["center_error_m"]) for x in valid])) if valid else None,
                        "median_focal_relative_error": float(np.median([float(x["focal_relative_error"]) for x in valid])) if valid else None,
                        "median_inliers": float(np.median([int(x["inliers"]) for x in items])) if items else None}
    paired = {}
    if all(len(by.get(a, [])) == 24 for a in ("up2pf_ori_ransac", "p3p_ransac")):
        u = {int(x["pair"]): x for x in by["up2pf_ori_ransac"]}
        b = {int(x["pair"]): x for x in by["p3p_ransac"]}
        assert set(u) == set(b) == set(range(24))
        for key, lower in (("rotation_error_deg", True), ("center_error_m", True), ("inliers", False)):
            wins = sum((float(u[i][key]) < float(b[i][key])) if lower else (float(u[i][key]) > float(b[i][key])) for i in range(24))
            paired[key] = {"up2_strict_wins": wins, "denominator": 24}
    result = {**previous, "scope": "development source-transfer diagnostic with GT-derived prior and non-focal-fair fixed-f P3P; no measured IMU effectiveness claim",
              "raw_rows": len(arms), "summary": summary, "paired": paired,
              "compile": {"returncode": 0, "cmd": previous["compile"]["cmd"], "evidence": "compile.verify.stdout.log and compile.verify.stderr.log; successful standalone command after full original PoseLib restoration"},
              "predecessor_compile": previous["compile"],
              "repair": {"cause": "incomplete archived PoseLib header restoration in two full-run compile failures and one stand-alone compile failure", "archived_source_changed": False,
                         "predecessor_result_sha256": sha(args.predecessor), "binary_sha256": sha(binary),
                         "input_csv_sha256": {"pairs.csv": sha(pairs), "matches.csv": sha(matches)},
                         "compilation": "unchanged original C++ successfully compiled with complete archived PoseLib source; standalone compile CPU time not measured"},
              "run": {"cmd": cmd, "returncode": run.returncode, "wall_seconds": wall,
                      "children_cpu_seconds": (after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime),
                      "peak_child_rss_kib": after.ru_maxrss, "stdout_sha256": sha(args.run_dir / "raw.csv"), "stderr_sha256": sha(args.run_dir / "run.stderr.log")}}
    (args.run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"returncode": run.returncode, "rows": len(arms), "summary": summary, "paired": paired, "run_cpu_seconds": result["run"]["children_cpu_seconds"]}), flush=True)
    return 0 if run.returncode == 0 and len(arms) == 48 else 1


if __name__ == "__main__":
    raise SystemExit(main())
