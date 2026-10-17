#!/usr/bin/env python3
"""Frozen-source, GT-prior transfer diagnostic; never cite as measured-IMU evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="extracted official fr2/xyz directory")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True, help="verified archived source root")
    parser.add_argument("--legacy-helper", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    t0 = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:1])
    assert digest(a.archive) == "a4903027a7fe6bc6573a1ce96a8afa5689f15d74f4a3f0627e91b5799f62e40b"
    a.output.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("legacy_pose_helpers", a.legacy_helper)
    assert spec and spec.loader
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    rgb = old.rows((a.data / "rgb.txt").read_text(), -1)
    dep = old.rows((a.data / "depth.txt").read_text(), -1)
    gt = old.rows((a.data / "groundtruth.txt").read_text(), 7)
    selected = []
    pairrows, matchrows = [], []
    for k in range(24):
        target = rgb[0][0] + 15.25 + 4.0*k
        r = old.near(rgb, target)
        q = old.near(rgb, r[0] + .30)
        d = old.near(dep, r[0])
        g1, g2 = old.near(gt, r[0]), old.near(gt, q[0])
        miss = max(abs(r[0]-target), abs(q[0]-(r[0]+.30)), abs(d[0]-r[0]), abs(g1[0]-r[0]), abs(g2[0]-q[0]))
        row = {"pair": k, "accepted": miss <= .02, "ref_t": r[0], "query_t": q[0], "depth_t": d[0],
               "ref_path": r[1][0], "query_path": q[1][0], "depth_path": d[1][0], "timestamp_miss_max_s": miss}
        if row["accepted"]:
            p1 = old.feat(a.data / r[1][0])
            p2 = old.feat(a.data / q[1][0])
            mm = old.matches(p1, p2)
            depth = np.asarray(Image.open(a.data / d[1][0]), dtype=np.uint16)
            valid = []
            rej = {"zero_depth": 0, "normal": 0}
            for score, i, j, _r1, _r2 in mm:
                x, y = np.rint(p1[0][i]).astype(int)
                X = old.xyz(depth, x, y)
                n = old.normal(depth, x, y)
                if X is None:
                    rej["zero_depth"] += 1
                    continue
                if n is None:
                    rej["normal"] += 1
                    continue
                valid.append((score, X, p2[0][j]-[319.5, 239.5], p1[2][i], p2[2][j], n))
            valid = valid[:128]
            R1, R2 = old.qR(g1[1][3:]), old.qR(g2[1][3:])
            t1, t2 = np.array(g1[1][:3]), np.array(g2[1][:3])
            R = R2.T@R1
            t = R2.T@(t1-t2)
            G = old.rxz(R)  # GT LEAKAGE: code-transfer diagnostic only.
            pairrows.append([k, *R.ravel(), *t, *G.ravel()])
            for _, X, y, ar, aq, n in valid:
                matchrows.append([k, *X, *y, ar, aq, *n])
            row.update(image_matches=len(mm), valid_depth_normal_matches=len(valid), rejections=rej)
        selected.append(row)
        print(json.dumps({"pair": k, "accepted": row["accepted"], "valid_matches": row.get("valid_depth_normal_matches", 0)}), flush=True)

    pairs, matches = a.output / "pairs.csv", a.output / "matches.csv"
    with pairs.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pair", *[f"R{i}" for i in range(9)], "tx", "ty", "tz", *[f"G{i}" for i in range(9)]])
        writer.writerows(pairrows)
    with matches.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pair", "X", "Y", "Z", "u", "v", "angle_ref", "angle_query", "nx", "ny", "nz"])
        writer.writerows(matchrows)

    cpp = a.source / "experiments/gravity_pose_tum_fr1xyz_v1.cpp"
    src = a.source / "sources/GravityPose"
    poselib = a.source / "sources/PoseLib"
    eigen = Path("/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/casadi/include/eigen3")
    sources = [cpp, src / "src/solvers/solver_up2pf_ori.cpp", poselib / "PoseLib/solvers/p3p.cc", poselib / "PoseLib/misc/univariate.cc"]
    cmd = ["g++", "-std=c++17", "-O3", "-DNDEBUG", "-I", str(eigen), "-I", str(src / "src/include"), "-I", str(poselib), *map(str, sources), "-o", str(a.output / "run")]
    compile_result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    (a.output / "compile.stdout.log").write_text(compile_result.stdout)
    (a.output / "compile.stderr.log").write_text(compile_result.stderr)
    run = None
    if compile_result.returncode == 0:
        run = subprocess.run([str(a.output / "run"), str(pairs), str(matches)], capture_output=True, text=True, timeout=240)
        (a.output / "raw.csv").write_text(run.stdout)
        (a.output / "run.stderr.log").write_text(run.stderr)
    arms = list(csv.DictReader(io.StringIO(run.stdout))) if run and run.returncode == 0 else []
    by = {}
    for item in arms:
        by.setdefault(item["arm"], []).append(item)
    summary = {arm: {"pairs": len(items), "valid_pairs": sum(x["valid"] == "1" for x in items),
                     "median_rotation_error_deg": float(np.median([float(x["rotation_error_deg"]) for x in items if x["valid"] == "1"])) if any(x["valid"] == "1" for x in items) else None,
                     "median_center_error_m": float(np.median([float(x["center_error_m"]) for x in items if x["valid"] == "1"])) if any(x["valid"] == "1" for x in items) else None,
                     "median_inliers": float(np.median([int(x["inliers"]) for x in items])) if items else None} for arm, items in by.items()}
    result = {"scope": "development diagnostic; GT-derived prior; not measured IMU or focal-fair scientific comparison",
              "archive_sha256": digest(a.archive), "legacy_helper_sha256": digest(a.legacy_helper),
              "source_sha256": {str(x.relative_to(a.source)): digest(x) for x in sources},
              "selection": selected, "raw_rows": len(arms), "summary": summary,
              "qualifying_pairs": sum(x.get("valid_depth_normal_matches", 0) >= 24 for x in selected),
              "compile": {"cmd": cmd, "returncode": compile_result.returncode},
              "run": None if run is None else {"returncode": run.returncode},
              "runtime": {"elapsed_wall_seconds": time.monotonic()-t0, "self_cpu_seconds": sum(resource.getrusage(resource.RUSAGE_SELF)[i] for i in (0, 1)),
                          "children_cpu_seconds": sum(resource.getrusage(resource.RUSAGE_CHILDREN)[i] for i in (0, 1)),
                          "peak_self_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                          "peak_child_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                          "platform": platform.platform(), "python": sys.version}}
    (a.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"summary": summary, "qualifying_pairs": result["qualifying_pairs"], "compile": compile_result.returncode, "run": None if run is None else run.returncode}), flush=True)
    return 0 if run and run.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
