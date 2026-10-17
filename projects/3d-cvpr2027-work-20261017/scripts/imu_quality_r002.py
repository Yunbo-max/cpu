#!/usr/bin/env python3
"""Inspect measured accelerometer stability without using ground truth for priors."""
import argparse
import hashlib
import json
import math
import resource
import time
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def window(a, t):
    w = a[np.abs(a[:, 0] - t) <= .05, 1:]
    if not len(w):
        return {"count": 0}
    mean = np.mean(w, axis=0)
    unit = mean / np.linalg.norm(mean)
    directions = w / np.linalg.norm(w, axis=1)[:, None]
    dispersion = np.degrees(np.arccos(np.clip(directions @ unit, -1., 1.)))
    return {"count": len(w), "mean_m_s2": mean.tolist(), "norm_mean_m_s2": float(np.linalg.norm(mean)),
            "norm_sample_std_m_s2": float(np.std(np.linalg.norm(w, axis=1))),
            "angle_p95_from_mean_deg": float(np.percentile(dispersion, 95)),
            "unit": unit.tolist()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accelerometer", type=Path, required=True)
    p.add_argument("--selection", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    a = np.loadtxt(args.accelerometer)
    selected = json.loads(args.selection.read_text())["selection"]
    rows = []
    for pair in selected:
        ref = window(a, pair["ref_t"])
        query = window(a, pair["query_t"])
        delta = None
        if ref["count"] and query["count"]:
            delta = math.degrees(math.acos(np.clip(np.dot(ref["unit"], query["unit"]), -1, 1)))
        rows.append({"pair": pair["pair"], "ref": ref, "query": query, "unit_angle_change_deg": delta})
    changes = [r["unit_angle_change_deg"] for r in rows if r["unit_angle_change_deg"] is not None]
    out = {"scope": "measured accelerometer descriptive diagnostic; frame mapping and motion acceleration unresolved",
           "accelerometer_sha256": sha(args.accelerometer), "selection_sha256": sha(args.selection),
           "samples": len(a), "window_half_width_s": .05, "pairs": rows,
           "summary": {"median_pair_angle_change_deg": float(np.median(changes)),
                       "max_pair_angle_change_deg": float(np.max(changes)),
                       "median_window_p95_dispersion_deg": float(np.median([w["angle_p95_from_mean_deg"] for r in rows for w in (r["ref"], r["query"]) if w["count"]])),
                       "median_window_norm_m_s2": float(np.median([w["norm_mean_m_s2"] for r in rows for w in (r["ref"], r["query"]) if w["count"]]))},
           "runtime": {"wall_seconds": time.monotonic()-start, "cpu_seconds": sum(resource.getrusage(resource.RUSAGE_SELF)[i] for i in (0, 1)),
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
