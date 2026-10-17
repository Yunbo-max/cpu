#!/usr/bin/env python3
"""Counterexample test: two gravity vectors need not determine inherited Rxz(R)."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import resource
import time
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def angle(A, B):
    x = (np.trace(A@B.T)-1)/2
    return math.degrees(math.acos(np.clip(x, -1., 1.)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--pair-csv", type=Path, required=True)
    p.add_argument("--selection", type=Path, required=True)
    p.add_argument("--frame-result", type=Path, required=True)
    p.add_argument("--legacy-helper", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    spec = importlib.util.spec_from_file_location("legacy_pose_helpers", args.legacy_helper)
    assert spec and spec.loader
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    selection = json.loads(args.selection.read_text())["selection"]
    rec = next(x for x in selection if x["pair"] == 0)
    pair = next(x for x in csv.DictReader(args.pair_csv.open()) if int(x["pair"]) == 0)
    R0 = np.array([float(pair[f"R{i}"]) for i in range(9)]).reshape(3, 3)
    gt = old.rows((args.data / "groundtruth.txt").read_text(), 7)
    g1, g2 = old.near(gt, rec["ref_t"]), old.near(gt, rec["query_t"])
    b = np.array(json.loads(args.frame_result.read_text())["fitted_world_vector_unit"])
    u_ref = old.qR(g1[1][3:]).T @ b
    u_query = old.qR(g2[1][3:]).T @ b
    assert np.linalg.norm(R0 @ u_ref-u_query) < 1e-10
    alternatives = []
    for psi in (-20, 0, 20):
        R = Rotation.from_rotvec(np.deg2rad(psi)*u_query).as_matrix() @ R0
        G = old.rxz(R)
        alternatives.append({"yaw_about_query_gravity_deg": psi,
                             "gravity_constraint_residual": float(np.linalg.norm(R @ u_ref-u_query)),
                             "rxz_geodesic_from_original_deg": angle(G, old.rxz(R0)),
                             "rxz_row_y": G[1].tolist(),
                             "pose_rotation_from_original_deg": angle(R, R0)})
    out = {"scope": "exact mathematical information-condition fixture on one exposed pair; no new pose estimator or performance claim",
           "input_sha256": {"pairs.csv": sha(args.pair_csv), "selection": sha(args.selection),
                            "frame-result": sha(args.frame_result), "groundtruth.txt": sha(args.data / "groundtruth.txt"),
                            "helper": sha(args.legacy_helper)},
           "pair": 0, "world_gravity_vector": b.tolist(), "ideal_ref_gravity": u_ref.tolist(), "ideal_query_gravity": u_query.tolist(),
           "query_gravity_angle_from_camera_y_deg": float(math.degrees(math.acos(np.clip(u_query[1], -1, 1)))),
           "construction": "For any psi, Rpsi=Rot(u_query,psi) R0 maps u_ref to u_query, yet rxz(Rpsi) can vary.",
           "alternatives": alternatives,
           "runtime": {"wall_seconds": time.monotonic()-start,
                       "cpu_seconds": sum(resource.getrusage(resource.RUSAGE_SELF)[i] for i in (0, 1)),
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"pair": 0, "alternatives": alternatives}), flush=True)
    return 0 if all(x["gravity_constraint_residual"] < 1e-10 for x in alternatives) else 1


if __name__ == "__main__":
    raise SystemExit(main())
