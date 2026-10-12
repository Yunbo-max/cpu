from __future__ import annotations
import os,sys,json,time,hashlib,platform,resource
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import scipy,sklearn
from sklearn.datasets import load_digits
from certificate import prepare,exact_extremes,propose_certificate

ROOT=Path(__file__).resolve().parents[1]
def enc(x):
    if isinstance(x,F):return {'numerator':str(x.numerator),'denominator':str(x.denominator),'float':float(x)}
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    if isinstance(x,np.generic):return x.item()
    return x

def arrayhash(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def save(p,x):
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(enc(x),indent=2));temp.replace(p)
def snap():
    out={}
    for name in ['cpu.max','memory.max','memory.current','memory.events']:
        p=Path('/sys/fs/cgroup')/name;out[name]=p.read_text() if p.exists() else None
    return out

def author_generator(seed,n=4096,d=16):
    # Source-faithful numerical generator port: default scale deliberately reduced.
    rng=np.random.RandomState(seed)
    centers=rng.randn(5,d)*10
    assignments=rng.randint(0,5,size=n)
    noise=rng.randn(n,d)*2
    return centers[assignments]+noise

if __name__=='__main__':
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    begin=time.perf_counter(); cpu=time.process_time()
    env={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,
         'pid':os.getpid(),'thread_env':{k:os.getenv(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},'before':snap()}
    data={'author_gaussian_seed0':author_generator(0),'author_gaussian_seed1':author_generator(1),'digits':load_digits().data}
    inputs=[]
    for name,X in data.items():
        file=ROOT/'sources'/f'{name}.npy';np.save(file,X,allow_pickle=False)
        inputs.append({'name':name,'shape':X.shape,'dtype':str(X.dtype),'sha256_array_C':arrayhash(X),'sha256_npy':hashlib.sha256(file.read_bytes()).hexdigest()})
    cases=[]
    for name,X in data.items():
        for m in [16,64,256]:
            for seed in [40,41,42,43]:
                idx=np.random.RandomState(seed).choice(len(X),m,replace=True)
                cases.append({'id':f'{name}-m{m}-s{seed}','dataset':name,'m':m,'seed':seed,'indices':idx.tolist(),'indices_sha256_int64_C':arrayhash(idx.astype(np.int64))})
    save(ROOT/'sources'/'input_manifest.json',{'inputs':inputs,'cases':cases,'versions':env,'protocol_commit':'5918b04ea31fc3082d869bd330a3f3b9c48a7811','admission_commit':'28119bb102f693349225492da13c4c2bc6a95a87'})
    # All draws and data identities are now persisted, before any scoring.
    alpha=F(1,100);betas=[F(1,10),F(1,5),F(2,5)];rows=[]
    for i,case in enumerate(cases):
        print('START',i,case['id'],flush=True)
        X=data[case['dataset']];Q=X[np.array(case['indices'])];t0=time.perf_counter()
        t=time.perf_counter();s=prepare(X,Q);tprep=time.perf_counter()-t
        t=time.perf_counter();e=exact_extremes(s);text=time.perf_counter()-t
        distortion=(1+alpha)*e['upper']/e['lower']-1 if e['lower']>0 else None
        rcda_e=max(e['rcda'],alpha*max(F(1),e['median_ratio']))
        outcomes=[]
        for beta in betas:
            t=time.perf_counter();answer=propose_certificate(s,alpha,beta,e);elapsed=time.perf_counter()-t
            strong=distortion is not None and distortion<=beta
            rcda=rcda_e<F(1,5) and 4*rcda_e<=beta
            if answer['certified'] and answer['primal_violation']:raise AssertionError('Contradictory certificate')
            outcomes.append({'alpha':alpha,'beta':beta,'strong_certified':strong,'rcda_certified':rcda,'dual':answer,'dual_seconds':elapsed})
        row={'case_id':case['id'],'dataset':case['dataset'],'m':case['m'],'sample_seed':case['seed'],'n':s.n,'d':len(s.cols),
             'encoding_exponent':s.exponent,'knot_count':sum(len(c.knots) for c in s.cols),'extremes':e,'strong_beta_bound':distortion,
             'rcda_e_used':rcda_e,'outcomes':outcomes,'prepare_seconds':tprep,'exact_baselines_seconds':text,'case_seconds':time.perf_counter()-t0}
        rows.append(row);save(ROOT/'results'/f'case_{i:02d}.json',row)
        print('DONE',i,'dual',[o['dual']['certified'] for o in outcomes], 'strong',[o['strong_certified'] for o in outcomes],
              'rcda',[o['rcda_certified'] for o in outcomes], 'seconds',round(row['case_seconds'],3),flush=True)
    summary={'cases':len(rows),'settings':sum(len(r['outcomes']) for r in rows),'dual_certified':0,'strong_certified':0,'rcda_certified':0,
             'dual_only_vs_both':0,'strong_not_dual':0,'rcda_not_dual':0,'primal_violations':0,'by_dataset':{}}
    for r in rows:
        dd=summary['by_dataset'].setdefault(r['dataset'],{'settings':0,'dual':0,'strong':0,'rcda':0,'dual_only':0})
        for o in r['outcomes']:
            a=o['dual']['certified'];b=o['strong_certified'];c=o['rcda_certified']
            summary['dual_certified']+=a;summary['strong_certified']+=b;summary['rcda_certified']+=c
            summary['dual_only_vs_both']+=a and not(b or c);summary['strong_not_dual']+=b and not a;summary['rcda_not_dual']+=c and not a
            summary['primal_violations']+=o['dual']['primal_violation']
            dd['settings']+=1;dd['dual']+=a;dd['strong']+=b;dd['rcda']+=c;dd['dual_only']+=a and not(b or c)
    summary.update(wall_seconds=time.perf_counter()-begin,cpu_seconds=time.process_time()-cpu,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   after=snap(),interpretation='Descriptive finite-input certificate counts; not independent dataset counts or coreset sampler gains',independent_review='pending')
    save(ROOT/'results'/'summary.json',summary);save(ROOT/'receipts'/'environment.json',env)
    print(json.dumps(summary,indent=2),flush=True)
