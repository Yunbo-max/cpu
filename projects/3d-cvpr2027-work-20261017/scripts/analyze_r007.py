#!/usr/bin/env python3
"""Independent paired outcome and GT-overlap recount for R007 developmental cohort."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ARMS = ('up2pf_ori_oracle', 'p4pf_unknown_focal')
METRICS = ('rotation_error_deg', 'center_error_m', 'focal_relative_error', 'inliers')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(4 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def report(ids, rows, fractions):
    ids = sorted(set(ids))
    kept = [i for i in ids if i in rows]
    out = {'selected': len(ids), 'qualified_and_scored': len(kept),
           'optimization_skips': sum('skip_reason' in rows[i][arm] for i in kept for arm in ARMS)}
    if not kept:
        return out
    out['gt_inlier_fraction_median'] = float(np.median([fractions[i] for i in kept]))
    for metric in METRICS:
        result = {}
        for stage in ('initial', 'refined'):
            a = np.array([rows[i][ARMS[0]][stage][metric] for i in kept])
            b = np.array([rows[i][ARMS[1]][stage][metric] for i in kept])
            result[stage] = {'oracle_median': float(np.median(a)),
                             'p4pf_median': float(np.median(b)),
                             'paired_median_difference_oracle_minus_p4pf': float(np.median(a-b)),
                             'oracle_strict_wins': int(np.sum(a < b)) if metric != 'inliers' else int(np.sum(a > b)),
                             'p4pf_strict_wins': int(np.sum(b < a)) if metric != 'inliers' else int(np.sum(b > a)),
                             'ties': int(np.sum(a == b))}
        out[metric] = result
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--r006', type=Path, required=True)
    p.add_argument('--r007', type=Path, required=True)
    a = p.parse_args()
    original = json.loads((a.r006/'result.json').read_text())
    new = json.loads((a.r007/'result.json').read_text())
    selection = {int(r['pair']): r for r in original['selection']}
    rows = defaultdict(dict)
    for r in new['rows']:
        i = r['pair']
        assert r['arm'] not in rows[i]
        rows[i][r['arm']] = r
    assert len(selection) == 1440 and len(rows) == new['qualified_pairs'] == 1418
    assert set(rows) == {int(x['pair']) for x in selection.values() if x.get('valid_depth_normal_matches', 0) >= 24}
    assert all(set(v) == set(ARMS) for v in rows.values())
    assert len(new['rows']) == 2836 and new['native_row_equivalence'] == 2836
    assert {x['pair'] for x in new['optimization_skips']} == {83, 101}
    pair = {}
    for r in csv.DictReader((a.r006/'pairs.csv').open()):
        pair[int(r['pair'])] = (np.array([float(r[f'R{k}']) for k in range(9)]).reshape(3, 3),
                                np.array([float(r[k]) for k in ('tx', 'ty', 'tz')]))
    counts = defaultdict(lambda: [0, 0])
    for r in csv.DictReader((a.r006/'matches.csv').open()):
        i = int(r['pair'])
        R, t = pair[i]
        q = R @ np.array([float(r[k]) for k in ('X', 'Y', 'Z')]) + t
        e = np.linalg.norm(525*q[:2]/q[2] - np.array([float(r[k]) for k in ('u', 'v')])) if q[2] > 0 else np.inf
        counts[i][0] += 1
        counts[i][1] += int(e <= 3)
    fractions = {i: v[1]/v[0] for i, v in counts.items() if v[0]}
    assert set(rows) <= set(fractions) and len(fractions) == 1438
    offsets = {str(d): report([i for i, r in selection.items() if r['offset_s'] == d], rows, fractions)
               for d in original['offsets_s']}
    strata = {'lt_0p5': [], '0p5_to_lt_0p75': [], 'ge_0p75': []}
    for i, w in fractions.items():
        strata['lt_0p5' if w < .5 else '0p5_to_lt_0p75' if w < .75 else 'ge_0p75'].append(i)
    first_t = min(r['ref_t'] for r in selection.values())
    blocks = defaultdict(list)
    for i, r in selection.items():
        blocks[int((r['ref_t']-first_t)//10)].append(i)
    result = {'scope': 'R007 exposed-sequence paired diagnostic; oracle pose uses query GT tilt',
              'input_sha256': {str(z): sha(z) for z in (a.r006/'result.json', a.r006/'pairs.csv',
                                 a.r006/'matches.csv', a.r007/'result.json')},
              'planned_pairs': 1440, 'qualified_pairs': 1418,
              'all': report(selection, rows, fractions), 'offsets': offsets,
              'gt_inlier_fraction_strata': {k: report(v, rows, fractions) for k, v in strata.items()},
              'ten_second_reference_blocks': {str(k): report(v, rows, fractions) for k, v in sorted(blocks.items())},
              'gt_inlier_fraction_definition': '3-px true-pose and 525-px focal reprojection, used only for outcome strata',
              'limitations': ['Oracle uses query GT', 'Correlated pairs from one exposed RGB-D sequence',
                              'In-house nonminimal refinement is not source-native full LO-RANSAC',
                              'Two source-valid oracle rows with four initial inliers retain unchanged model']}
    (a.r007/'analysis.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'all': result['all'], 'offset_rotations': {k: v['rotation_error_deg']['refined'] for k, v in offsets.items()},
                      'strata_rotations': {k: v['rotation_error_deg']['refined'] for k, v in result['gt_inlier_fraction_strata'].items()}}))


if __name__ == '__main__':
    main()
