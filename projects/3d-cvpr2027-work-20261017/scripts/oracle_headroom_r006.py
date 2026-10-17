#!/usr/bin/env python3
"""Source/baseline qualification: ideal Rxz UP2PfORI versus unknown-focal P4Pf."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import resource
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()


def cpu():
    r, c = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
    return float(r.ru_utime+r.ru_stime+c.ru_utime+c.ru_stime)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--legacy-helper', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=['pilot', 'full'], required=True)
    parser.add_argument('--reference-count', type=int, default=0)
    parser.add_argument('--offsets', type=float, nargs='+', default=[.15, .30, .60, 1.20])
    args = parser.parse_args()
    t_start, c_start = time.monotonic(), cpu()
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:1])
    args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('legacy_pose_helpers', args.legacy_helper)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    rgb = old.rows((args.data/'rgb.txt').read_text(), -1)
    depth = old.rows((args.data/'depth.txt').read_text(), -1)
    gt = old.rows((args.data/'groundtruth.txt').read_text(), 7)
    if args.mode == 'pilot':
        assert args.reference_count == 0 and args.offsets == [.15, .30, .60, 1.20]
        refs = [15.25, 60.25, 105.25]
    else:
        assert 1 <= args.reference_count <= 1500
        refs = np.linspace(10.25, 110.25, args.reference_count).tolist()
    pairrows, matchrows, selection = [], [], []
    for ri, ref_elapsed in enumerate(refs):
        rt = rgb[0][0] + ref_elapsed
        r = old.near(rgb, rt)
        d = old.near(depth, r[0])
        g1 = old.near(gt, r[0])
        common_miss = max(abs(r[0]-rt), abs(d[0]-r[0]), abs(g1[0]-r[0]))
        ref_feat = old.feat(args.data/r[1][0]) if common_miss <= .02 else None
        dep_img = np.asarray(Image.open(args.data/d[1][0]), dtype=np.uint16) if ref_feat is not None else None
        for oi, offset in enumerate(args.offsets):
            pid = ri*len(args.offsets)+oi
            q = old.near(rgb, r[0]+offset)
            g2 = old.near(gt, q[0])
            miss = max(common_miss, abs(q[0]-(r[0]+offset)), abs(g2[0]-q[0]))
            rec = {'pair': pid, 'reference_index': ri, 'offset_s': offset, 'ref_t': r[0], 'query_t': q[0],
                   'ref_path': r[1][0], 'query_path': q[1][0], 'depth_path': d[1][0],
                   'timestamp_miss_max_s': miss, 'accepted': miss <= .02}
            if rec['accepted']:
                p1, p2 = ref_feat, old.feat(args.data/q[1][0])
                matches = old.matches(p1, p2)
                valid = []
                for score, i, j, _, _ in matches:
                    x, y = np.rint(p1[0][i]).astype(int)
                    X = old.xyz(dep_img, x, y)
                    n = old.normal(dep_img, x, y)
                    if X is not None and n is not None:
                        valid.append((score, X, p2[0][j]-[319.5, 239.5], p1[2][i], p2[2][j], n))
                valid = valid[:128]
                R1, R2 = old.qR(g1[1][3:]), old.qR(g2[1][3:])
                t1, t2 = np.array(g1[1][:3]), np.array(g2[1][:3])
                R = R2.T@R1
                t = R2.T@(t1-t2)
                G = old.rxz(R)  # Intentional impossible oracle input; never measured gravity.
                pairrows.append([pid, *R.ravel(), *t, *G.ravel()])
                for _, X, y, ar, aq, n in valid:
                    matchrows.append([pid, *X, *y, ar, aq, *n])
                rec.update(image_matches=len(matches), valid_depth_normal_matches=len(valid))
            selection.append(rec)
        if (ri+1) % (1 if args.mode == 'pilot' else 10) == 0:
            print(json.dumps({'ref_done':ri+1,'ref_total':len(refs),'cpu_seconds':cpu()-c_start,
                              'qualified':sum(x.get('valid_depth_normal_matches',0)>=24 for x in selection)}), flush=True)
    pairfile, matchfile = args.out/'pairs.csv', args.out/'matches.csv'
    with pairfile.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['pair',*[f'R{i}' for i in range(9)],'tx','ty','tz',*[f'G{i}' for i in range(9)]]);w.writerows(pairrows)
    with matchfile.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['pair','X','Y','Z','u','v','angle_ref','angle_query','nx','ny','nz']);w.writerows(matchrows)
    (args.out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')

    poselib = args.source/'sources/PoseLib'
    grav = args.source/'sources/GravityPose'
    eigen = Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/casadi/include/eigen3')
    sources = [args.native,grav/'src/solvers/solver_up2pf_ori.cpp',poselib/'PoseLib/solvers/p3p.cc',
               poselib/'PoseLib/solvers/p4pf.cc',poselib/'PoseLib/misc/re3q3.cc',poselib/'PoseLib/misc/univariate.cc']
    binary = args.out/'native_run'
    command = ['g++','-std=c++17','-O3','-DNDEBUG','-I',str(eigen),'-I',str(grav/'src/include'),'-I',str(poselib),
               *map(str,sources),'-o',str(binary)]
    compile_run = subprocess.run(command,text=True,capture_output=True,timeout=300)
    (args.out/'compile.stdout.log').write_text(compile_run.stdout)
    (args.out/'compile.stderr.log').write_text(compile_run.stderr)
    native_run = None
    if compile_run.returncode == 0:
        native_run = subprocess.run([str(binary),str(pairfile),str(matchfile)],text=True,capture_output=True,timeout=3600)
        (args.out/'raw.csv').write_text(native_run.stdout)
        (args.out/'native.stderr.log').write_text(native_run.stderr)
    raw = list(csv.DictReader(io.StringIO(native_run.stdout))) if native_run and native_run.returncode == 0 else []
    arms = {}
    for row in raw:
        arms.setdefault(row['arm'],[]).append(row)
    summary = {}
    for arm, rows in arms.items():
        good = [x for x in rows if x['valid'] == '1']
        summary[arm] = {'rows':len(rows),'valid_rows':len(good),
                        'rotation_median_deg':float(np.median([float(x['rotation_error_deg']) for x in good])) if good else None,
                        'center_median_m':float(np.median([float(x['center_error_m']) for x in good])) if good else None,
                        'focal_relative_median':float(np.median([float(x['focal_relative_error']) for x in good])) if good else None,
                        'inlier_median':float(np.median([int(x['inliers']) for x in rows])) if rows else None,
                        'native_cpu_sum_s':sum(float(x['cpu_seconds']) for x in rows)}
    result = {'scope':'Development source qualification; GT-derived Rxz oracle, no measured-prior or CVPR claim',
              'mode':args.mode,'refs':len(refs),'offsets_s':args.offsets,'selection':selection,
              'qualified_pairs':sum(x.get('valid_depth_normal_matches',0)>=24 for x in selection),
              'source_sha256':{str(s):sha(s) for s in sources},'legacy_helper_sha256':sha(args.legacy_helper),
              'input_sha256':{str(p):sha(p) for p in [args.data/'rgb.txt',args.data/'depth.txt',args.data/'groundtruth.txt',pairfile,matchfile]},
              'compile':{'cmd':command,'exit_code':compile_run.returncode},
              'native':None if native_run is None else {'exit_code':native_run.returncode,'rows':len(raw)},
              'summary':summary,
              'runtime':{'cpu_seconds':cpu()-c_start,'wall_seconds':time.monotonic()-t_start,
                         'self_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         'children_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}}
    (args.out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'summary':summary,'qualified_pairs':result['qualified_pairs'],
                      'runtime':result['runtime'],'compile':compile_run.returncode,
                      'native':result['native']}),flush=True)
    return 0 if native_run and native_run.returncode == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
