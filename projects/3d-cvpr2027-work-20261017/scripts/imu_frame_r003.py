#!/usr/bin/env python3
"""Calibrate a constant IMU-camera rotation on an early interval; test on later time."""
import argparse
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def angles(u, v):
    return np.degrees(np.arccos(np.clip(np.sum(u*v, axis=-1), -1, 1)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--legacy-helper", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    spec = importlib.util.spec_from_file_location("legacy_pose_helpers", args.legacy_helper)
    assert spec and spec.loader
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    a = np.loadtxt(args.data / "accelerometer.txt")
    gt = old.rows((args.data / "groundtruth.txt").read_text(), 7)
    rgb = old.rows((args.data / "rgb.txt").read_text(), -1)
    t0 = rgb[0][0]
    # Predetermined 10 Hz time grid. All matching/exclusion depends only on timestamps.
    records = []
    for i in range(1, 1220):
        t = t0 + .1*i
        g = old.near(gt, t)
        if abs(g[0]-t) > .012:
            continue
        w = a[np.abs(a[:, 0]-t) <= .02, 1:]
        if len(w) < 5:
            continue
        mean = np.mean(w, axis=0)
        records.append((t, old.qR(g[1][3:]), mean/np.linalg.norm(mean), np.linalg.norm(mean), len(w)))
    t = np.array([r[0] for r in records])
    R = np.stack([r[1] for r in records])
    u = np.stack([r[2] for r in records])
    norm = np.array([r[3] for r in records])
    train = t < t0 + 30.0
    test = t >= t0 + 30.0
    assert train.sum() >= 100 and test.sum() >= 500

    def prediction(x, rotations):
        C = Rotation.from_rotvec(x[:3]).as_matrix()  # sensor coordinates -> camera coordinates
        b = x[3:]/np.linalg.norm(x[3:])  # constant world specific-force direction
        # GT camera-to-world R; map world vector back to camera, then sensor.
        return np.einsum("ij,njk,k->ni", C.T, rotations.transpose(0, 2, 1), b)

    def residual(x):
        return (prediction(x, R[train])-u[train]).ravel()

    starts = [np.zeros(3), np.array([np.pi, 0, 0])]
    solutions = []
    for c in starts:
        b = R[train][0] @ (Rotation.from_rotvec(c).as_matrix() @ u[train][0])
        x = np.r_[c, b]
        fit = least_squares(residual, x, loss="soft_l1", f_scale=.08, max_nfev=250)
        solutions.append((float(np.linalg.norm(residual(fit.x))), fit))
    solutions.sort(key=lambda s: s[0])
    fit = solutions[0][1]
    pred = prediction(fit.x, R)
    errors = angles(pred, u)
    per_interval = []
    for j in range(3, 13):
        sel = (t >= t0+10*j) & (t < t0+10*(j+1))
        if sel.any():
            per_interval.append({"elapsed_s": [10*j, 10*(j+1)], "n": int(sel.sum()), "median_angle_deg": float(np.median(errors[sel])), "p90_angle_deg": float(np.percentile(errors[sel], 90))})
    singular_values = np.linalg.svd(fit.jac, compute_uv=False)
    out = {"scope": "development frame/accelerometer model diagnostic; ground truth used only in first 30 s fitting, later poses only score angular consistency; not a pose-method result",
           "data_sha256": {n: sha(args.data/n) for n in ("accelerometer.txt", "rgb.txt", "groundtruth.txt")},
           "legacy_helper_sha256": sha(args.legacy_helper), "fit_interval_s": [0, 30], "test_interval_s": [30, 122],
           "time_grid_hz": 10, "gt_max_miss_s": .012, "acc_window_half_s": .02,
           "train_count": int(train.sum()), "test_count": int(test.sum()),
           "train_median_angle_deg": float(np.median(errors[train])), "test_median_angle_deg": float(np.median(errors[test])),
           "test_p90_angle_deg": float(np.percentile(errors[test], 90)), "test_max_angle_deg": float(np.max(errors[test])),
           "test_norm_median_m_s2": float(np.median(norm[test])), "test_norm_p5_p95_m_s2": np.percentile(norm[test], [5, 95]).tolist(),
           "fitted_sensor_to_camera_rotvec": fit.x[:3].tolist(), "fitted_world_vector_unit": (fit.x[3:]/np.linalg.norm(fit.x[3:])).tolist(),
           "jacobian_singular_values": singular_values.tolist(), "intervals": per_interval,
           "runtime": {"wall_seconds": time.monotonic()-start, "cpu_seconds": sum(resource.getrusage(resource.RUSAGE_SELF)[i] for i in (0, 1)),
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k: out[k] for k in ("train_count", "test_count", "train_median_angle_deg", "test_median_angle_deg", "test_p90_angle_deg", "jacobian_singular_values")}), flush=True)


if __name__ == "__main__":
    main()
