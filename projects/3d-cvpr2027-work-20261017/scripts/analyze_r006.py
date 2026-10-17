#!/usr/bin/env python3
"""Independently recount R006 raw rows and GT reprojection strata; diagnostic only."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(4<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def median(a):
    return float(np.median(a)) if len(a) else None


def summarize(ids, pair, rows, fractions):
    ok=[i for i in ids if i in pair and i in rows and len(rows[i])==2]
    out={'selected':len(ids),'qualified_and_scored':len(ok)}
    if not ok:return out
    a,b='up2pf_ori_oracle','p4pf_unknown_focal'
    for metric in ('rotation_error_deg','center_error_m','focal_relative_error','inliers','cpu_seconds'):
        av=np.array([float(rows[i][a][metric]) for i in ok]);bv=np.array([float(rows[i][b][metric]) for i in ok])
        out[metric]={'oracle_median':median(av),'p4pf_median':median(bv),'paired_median_difference_oracle_minus_p4pf':median(av-bv),
                     'oracle_strict_wins':int(np.sum(av<bv)) if metric not in ('inliers',) else int(np.sum(av>bv)),
                     'p4pf_strict_wins':int(np.sum(bv<av)) if metric not in ('inliers',) else int(np.sum(bv>av)),
                     'ties':int(np.sum(av==bv))}
    out['gt_inlier_fraction_median']=median([fractions[i] for i in ok])
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    run=args.run
    original=json.loads((run/'result.json').read_text())
    pair={}
    for x in csv.DictReader((run/'pairs.csv').open()):
        i=int(x['pair']);pair[i]=(np.array([float(x[f'R{k}']) for k in range(9)]).reshape(3,3),np.array([float(x[k]) for k in ('tx','ty','tz')]))
    rows=defaultdict(dict)
    for x in csv.DictReader((run/'raw.csv').open()):
        i=int(x['pair']);assert x['arm'] not in rows[i]
        rows[i][x['arm']]=x
    selection={int(x['pair']):x for x in original['selection']}
    counts=defaultdict(lambda:[0,0])
    with (run/'matches.csv').open() as f:
        for x in csv.DictReader(f):
            i=int(x['pair']);R,t=pair[i]
            q=R@np.array([float(x[k]) for k in ('X','Y','Z')])+t
            pred=525*q[:2]/q[2] if q[2]>0 else np.array([float('inf')]*2)
            e=np.linalg.norm(pred-np.array([float(x[k]) for k in ('u','v')]))
            counts[i][0]+=1;counts[i][1]+=int(e<=3)
    fractions={i:n[1]/n[0] for i,n in counts.items() if n[0]}
    accepted=[i for i,x in selection.items() if x['accepted']]
    qualified=[i for i,x in selection.items() if x.get('valid_depth_normal_matches',0)>=24]
    assert len(selection)==original['refs']*len(original['offsets_s'])
    assert len(qualified)==original['qualified_pairs']==len(rows)
    assert all(set(rows[i])=={'up2pf_ori_oracle','p4pf_unknown_focal'} for i in rows)
    assert len(rows)*2==original['native']['rows']
    assert all(x['valid']=='1' for arm in rows.values() for x in arm.values())
    assert original['input_sha256'][str(run/'matches.csv')]==sha(run/'matches.csv')
    assert original['input_sha256'][str(run/'pairs.csv')]==sha(run/'pairs.csv')
    offset={str(d):summarize([i for i,x in selection.items() if x['offset_s']==d],pair,rows,fractions) for d in original['offsets_s']}
    strata={'lt_0p5':[],'0p5_to_lt_0p75':[],'ge_0p75':[]}
    for i,w in fractions.items():
        strata['lt_0p5' if w<.5 else '0p5_to_lt_0p75' if w<.75 else 'ge_0p75'].append(i)
    t0=min(x['ref_t'] for x in selection.values())
    blocks=defaultdict(list)
    for i,x in selection.items():
        blocks[int((x['ref_t']-t0)//10)].append(i)
    result={'scope':'Independent R006 raw-row and fixed GT reprojection diagnostics on exposed fr2; oracle prior leaks GT',
            'input_sha256':{str(run/k):sha(run/k) for k in ('result.json','selection.json','pairs.csv','matches.csv','raw.csv')},
            'planned_pairs':len(selection),'accepted_pairs':len(accepted),'qualified_pairs':len(qualified),
            'all':summarize(list(selection),pair,rows,fractions),'offsets':offset,
            'gt_inlier_fraction_strata':{k:summarize(v,pair,rows,fractions) for k,v in strata.items()},
            'ten_second_reference_blocks':{str(k):summarize(v,pair,rows,fractions) for k,v in sorted(blocks.items())},
            'gt_inlier_fraction_definition':'3-px reprojection using true relative pose and 525-px focal; outcome stratification only',
            'caveats':['Oracle uses query GT Rxz and is not an IMU input','One exposed, highly dependent RGB-D sequence','Both minimal arms use 512 hypotheses without a full localization pipeline or LO refinement']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'all':result['all'],'offsets':{k: {'n':v['qualified_and_scored'],'oracle_rot':v.get('rotation_error_deg',{}).get('oracle_median'),'p4pf_rot':v.get('rotation_error_deg',{}).get('p4pf_median')} for k,v in offset.items()},
                      'strata':{k:len(v) for k,v in strata.items()}}))


if __name__=='__main__':main()
