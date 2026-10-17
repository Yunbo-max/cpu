#!/usr/bin/env python3
"""Preregistered observable acceleration quality versus held-out-time gravity error."""
import argparse
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation
from scipy.stats import rankdata, spearmanr


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ang(u, v):
    return np.degrees(np.arccos(np.clip(np.sum(u*v, axis=-1), -1., 1.)))


def auc(score, positive):
    n1 = int(positive.sum())
    n0 = len(positive) - n1
    if not n1 or not n0:
        return None
    ranks = rankdata(score)
    return float((ranks[positive].sum() - n1*(n1+1)/2)/(n1*n0))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--frame-result', type=Path, required=True)
    p.add_argument('--legacy-helper', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    spec = importlib.util.spec_from_file_location('legacy_pose_helpers', a.legacy_helper)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    frame = json.loads(a.frame_result.read_text())
    C = Rotation.from_rotvec(frame['fitted_sensor_to_camera_rotvec']).as_matrix()
    b = np.array(frame['fitted_world_vector_unit'])
    samples = np.loadtxt(a.data/'accelerometer.txt')
    gt = old.rows((a.data/'groundtruth.txt').read_text(), 7)
    rgb = old.rows((a.data/'rgb.txt').read_text(), -1)
    t0 = rgb[0][0]
    records = []
    for i in range(1, 1220):
        t = t0 + .1*i
        g = old.near(gt, t)
        if abs(g[0]-t) > .012:
            continue
        lo, hi = np.searchsorted(samples[:, 0], [t-.02, t+.02])
        w = samples[lo:hi, 1:]
        if len(w) < 5:
            continue
        mean = w.mean(axis=0)
        u = mean/np.linalg.norm(mean)
        norm = np.linalg.norm(w, axis=1)
        dirs = w/norm[:, None]
        pred = C.T @ old.qR(g[1][3:]).T @ b
        records.append({'grid_index': i, 'elapsed_s': float(t-t0), 'n': int(len(w)),
                        'error_deg': float(ang(u, pred)), 'mean_norm': float(np.linalg.norm(mean)),
                        'dispersion_p95_deg': float(np.percentile(ang(dirs, u), 95)),
                        'norm_std': float(np.std(norm))})
    train = [r for r in records if r['elapsed_s'] < 30]
    test = [r for r in records if r['elapsed_s'] >= 30]
    assert len(train) == frame['train_count'] and len(test) == frame['test_count']
    norm_base = float(np.median([r['mean_norm'] for r in train]))
    errs = np.array([r['error_deg'] for r in test])
    rng = np.random.default_rng(5005)
    blocks = np.array([int(r['elapsed_s']//10) for r in test])
    unique = np.unique(blocks)
    metrics = {}
    for name in ('norm_deviation', 'dispersion_p95_deg', 'norm_std'):
        x = np.array([abs(r['mean_norm']-norm_base) if name == 'norm_deviation' else r[name] for r in test])
        q1, q3 = np.percentile(x, [25, 75])
        boot = []
        for _ in range(1000):
            draw = rng.choice(unique, len(unique), replace=True)
            inds = np.concatenate([np.flatnonzero(blocks == block) for block in draw])
            corr = spearmanr(x[inds], errs[inds]).statistic
            if np.isfinite(corr):
                boot.append(corr)
        metrics[name] = {'spearman': float(spearmanr(x, errs).statistic),
                         'spearman_block_bootstrap_95pct': np.percentile(boot, [2.5, 97.5]).tolist(),
                         'bootstrap_valid_draws': len(boot), 'quartile_cutoffs': [float(q1), float(q3)],
                         'low_n': int((x <= q1).sum()), 'high_n': int((x >= q3).sum()),
                         'low_error_median_deg': float(np.median(errs[x <= q1])),
                         'high_error_median_deg': float(np.median(errs[x >= q3])),
                         'auc_error_gt_1p5_deg': auc(x, errs > 1.5),
                         'auc_error_gt_2_deg': auc(x, errs > 2)}
    result = {'scope': 'exposed-sequence temporal development diagnostic; no pose efficacy or external validation',
              'inputs_sha256': {n: sha(a.data/n) for n in ('accelerometer.txt', 'rgb.txt', 'groundtruth.txt')}
                              | {'frame-result': sha(a.frame_result), 'helper': sha(a.legacy_helper)},
              'train_count': len(train), 'test_count': len(test), 'test_10s_blocks': unique.tolist(),
              'train_norm_median_m_s2': norm_base, 'error_median_deg': float(np.median(errs)),
              'error_p90_deg': float(np.percentile(errs, 90)),
              'error_gt_1p5_n': int((errs > 1.5).sum()), 'error_gt_2_n': int((errs > 2).sum()),
              'metrics': metrics,
              'runtime': {'cpu_seconds': sum(resource.getrusage(resource.RUSAGE_SELF)[i] for i in (0, 1)),
                          'wall_seconds': time.monotonic()-start,
                          'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'train_count': len(train), 'test_count': len(test), 'metrics': metrics}), flush=True)


if __name__ == '__main__':
    main()
