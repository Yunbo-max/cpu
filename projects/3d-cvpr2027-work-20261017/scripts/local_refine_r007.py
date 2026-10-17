#!/usr/bin/env python3
"""Qualified child output plus fixed 48-pair focal/pose reprojection refinement."""
import argparse
import csv
import hashlib
import json
import math
import os
import resource
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


ARMS=('up2pf_ori_oracle','p4pf_unknown_focal')
SCIENTIFIC=('pair','arm','valid','valid_hypotheses','inliers','median_reproj_px','rotation_error_deg','center_error_m','focal_relative_error','focal_px')


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for z in iter(lambda:f.read(4<<20),b''):h.update(z)
    return h.hexdigest()


def cpu():
    a,b=resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime


def rot_y(theta):
    c,s=np.cos(theta),np.sin(theta)
    return np.array([[c,0,-s],[0,1,0],[s,0,c]])


def angles(R,S):
    return float(np.degrees(np.arccos(np.clip((np.trace(R@S.T)-1)/2,-1,1))))


def stats(R,t,f,X,y,Rgt,tgt):
    q=X@R.T+t
    z=f*q[:,:2]/q[:,2,None]
    errors=np.linalg.norm(z-y,axis=1)
    return {'rotation_error_deg':angles(R,Rgt),'center_error_m':float(np.linalg.norm(-R.T@t+Rgt.T@tgt)),
            'focal_relative_error':abs(f-525)/525,'focal_px':float(f),'inliers':int(np.sum((q[:,2]>0)&(errors<=3))),
            'positive_depth':int(np.sum(q[:,2]>0))}


def main():
    p=argparse.ArgumentParser()
    for key in ('source','native','run006','out'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    t0,c0=time.monotonic(),cpu()
    resource.setrlimit(resource.RLIMIT_AS,(4_000_000_000,4_000_000_000))
    os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:1])
    a.out.mkdir(parents=True,exist_ok=True)
    pose=a.source/'sources/PoseLib';grav=a.source/'sources/GravityPose'
    eigen=Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/casadi/include/eigen3')
    src=[a.native,grav/'src/solvers/solver_up2pf_ori.cpp',pose/'PoseLib/solvers/p3p.cc',
         pose/'PoseLib/solvers/p4pf.cc',pose/'PoseLib/misc/re3q3.cc',pose/'PoseLib/misc/univariate.cc']
    binary=a.out/'models_binary'
    cmd=['g++','-std=c++17','-O3','-DNDEBUG','-I',str(eigen),'-I',str(grav/'src/include'),'-I',str(pose),*map(str,src),'-o',str(binary)]
    comp=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
    (a.out/'compile.stdout.log').write_text(comp.stdout)
    (a.out/'compile.stderr.log').write_text(comp.stderr)
    if comp.returncode:raise RuntimeError('compile '+str(comp.returncode))
    native=subprocess.run([str(binary),str(a.run006/'pairs.csv'),str(a.run006/'matches.csv')],capture_output=True,text=True,timeout=120)
    (a.out/'model_rows.csv').write_text(native.stdout)
    (a.out/'native.stderr.log').write_text(native.stderr)
    if native.returncode:raise RuntimeError('native '+str(native.returncode))
    current=list(csv.DictReader((a.out/'model_rows.csv').open()))
    frozen=list(csv.DictReader((a.run006/'raw.csv').open()))
    assert len(current)==len(frozen)==2836
    for i,(u,v) in enumerate(zip(current,frozen)):
        for key in SCIENTIFIC:
            if key in ('pair','arm','valid','valid_hypotheses','inliers'):
                assert u[key]==v[key],(i,key,u[key],v[key])
            else:
                assert math.isclose(float(u[key]),float(v[key]),abs_tol=1e-12,rel_tol=1e-12),(i,key,u[key],v[key])
    print(json.dumps({'source_check':'all 2836 rows matched first ten scientific fields','cpu_seconds':cpu()-c0}),flush=True)

    wanted={ri*6+oi for ri in [20,48,76,104,132,160,188,216] for oi in range(6)}
    scored={int(r['pair']) for r in current if int(r['pair']) in wanted}
    pairs={}
    for r in csv.DictReader((a.run006/'pairs.csv').open()):
        i=int(r['pair'])
        if i in scored:
            pairs[i]={'Rgt':np.array([float(r[f'R{k}']) for k in range(9)]).reshape(3,3),
                      'tgt':np.array([float(r[k]) for k in ('tx','ty','tz')]),
                      'G':np.array([float(r[f'G{k}']) for k in range(9)]).reshape(3,3)}
    matches=defaultdict(lambda:[[],[]])
    with (a.run006/'matches.csv').open() as f:
        for r in csv.DictReader(f):
            i=int(r['pair'])
            if i in scored:
                matches[i][0].append([float(r[k]) for k in ('X','Y','Z')])
                matches[i][1].append([float(r[k]) for k in ('u','v')])
    out=[]
    for r in current:
        i=int(r['pair'])
        if i not in scored:continue
        X,y=map(np.array,matches[i]);base=pairs[i]
        R=np.array([float(r[f'R{k}']) for k in range(9)]).reshape(3,3)
        t=np.array([float(r[k]) for k in ('tx','ty','tz')]);f=float(r['focal_px'])
        before=stats(R,t,f,X,y,base['Rgt'],base['tgt'])
        assert before['inliers']==int(r['inliers'])
        assert math.isclose(before['rotation_error_deg'],float(r['rotation_error_deg']),abs_tol=1e-6)
        arm=r['arm']
        if arm==ARMS[0]:
            Q=R@base['G'].T
            angle=np.arctan2(Q[2,0],Q[0,0])
            assert np.linalg.norm(rot_y(angle)@base['G']-R)<1e-7
            initial=np.r_[angle,t,np.log(f)]
            def pose_of(z):return rot_y(z[0])@base['G'],z[1:4],np.exp(z[4])
            low=np.r_[[-np.inf]*4,np.log(50.)];high=np.r_[[np.inf]*4,np.log(2000.)]
        else:
            initial=np.r_[Rotation.from_matrix(R).as_rotvec(),t,np.log(f)]
            def pose_of(z):return Rotation.from_rotvec(z[:3]).as_matrix(),z[3:6],np.exp(z[6])
            low=np.r_[[-np.inf]*6,np.log(50.)];high=np.r_[[np.inf]*6,np.log(2000.)]
        q=X@R.T+t
        mask=(q[:,2]>0)&(np.linalg.norm(f*q[:,:2]/q[:,2,None]-y,axis=1)<=3)
        assert mask.sum()>=6
        X0,y0=X[mask],y[mask]
        def residual(z):
            rot,trans,focal=pose_of(z)
            query=X0@rot.T+trans
            denom=np.maximum(query[:,2],.01)
            diff=focal*query[:,:2]/denom[:,None]-y0
            diff[query[:,2]<=.01]=1e3
            return diff.ravel()
        fit=least_squares(residual,initial,bounds=(low,high),loss='soft_l1',f_scale=3.,max_nfev=100)
        R1,t1,f1=pose_of(fit.x)
        after=stats(R1,t1,f1,X,y,base['Rgt'],base['tgt'])
        out.append({'pair':i,'arm':arm,'initial':before,'refined':after,'initial_consensus_n':int(mask.sum()),
                    'optimizer_success':bool(fit.success),'nfev':int(fit.nfev),'cost':float(fit.cost)})
    assert len(out)==2*len(pairs)==2*len(scored)
    summary={}
    for arm in ARMS:
        rows=[r for r in out if r['arm']==arm]
        summary[arm]={'n':len(rows),'optimizer_success_n':sum(r['optimizer_success'] for r in rows),
                      'median_nfev':float(np.median([r['nfev'] for r in rows]))}
        for key in ('rotation_error_deg','center_error_m','focal_relative_error','inliers'):
            summary[arm][key]={'initial_median':float(np.median([r['initial'][key] for r in rows])),
                               'refined_median':float(np.median([r['refined'][key] for r in rows]))}
    result={'scope':'R007 exposed 48-pair source-equivalence and local-refinement pilot, not a source-native full LO baseline',
            'planned_pairs':48,'qualified_pairs':len(pairs),'unqualified_pair_ids':sorted(wanted-scored),'native_row_equivalence':len(current),
            'input_sha256':{str(z):sha(z) for z in [a.run006/'raw.csv',a.run006/'pairs.csv',a.run006/'matches.csv',a.native]},
            'source_sha256':{str(z):sha(z) for z in src},'rows':out,'summary':summary,
            'runtime':{'cpu_seconds':cpu()-c0,'wall_seconds':time.monotonic()-t0,
                       'peak_self_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       'peak_child_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}}
    (a.out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'planned':48,'qualified':len(pairs),'summary':summary,'runtime':result['runtime']}),flush=True)


if __name__=='__main__':main()
