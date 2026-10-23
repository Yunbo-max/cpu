"""Finite-permutation estimator audit; no model training/native-framework execution."""
import itertools,json
import numpy as np
G,K,d=4,3,2
perms=list(itertools.permutations(range(G)))
rows=[]
for seed in range(64):
    rng=np.random.default_rng(seed)
    x=rng.normal(size=(G,d)); W=rng.normal(size=(K,d))
    z=x@W.T;z-=z.max(1,keepdims=True)
    p=np.exp(z);p/=p.sum(1,keepdims=True)
    f=np.eye(K)[p.argmax(1)]
    def grad(coef):
        dz=p*(coef-(coef*p).sum(1,keepdims=True))
        return K/G*dz.T@x
    glob=grad(np.tile(f.mean(0),(G,1)));micro=grad(f)
    lam=(sum(1/j for j in range(1,G+1))-1)/(G-1)
    results={name:[] for name in ['prefix','positive','subtract','pair_ht']}
    for perm in perms:
        pre=np.zeros_like(f);positive=np.zeros_like(f);ht=np.zeros_like(f)
        past=np.zeros(K)
        for j,i in enumerate(perm):
            pre[i]=(past+f[i])/(j+1)
            positive[i]=f[i]/G+(past/j if j else 0)
            ht[i]=(f[i]+2*past)/G
            past+=f[i]
        gp=grad(pre)
        results['prefix'].append(gp)
        results['positive'].append(grad(positive))
        results['subtract'].append((gp-lam*micro)/(1-lam))
        results['pair_ht'].append(grad(ht))
    stats={}
    for name, vals in results.items():
        vals=np.stack(vals);mean=vals.mean(0)
        bias=float(np.sum((mean-glob)**2));var=float(np.mean(np.sum((vals-mean)**2,axis=(1,2))))
        mse=float(np.mean(np.sum((vals-glob)**2,axis=(1,2))))
        assert abs(mse-bias-var)<1e-12
        if name!='prefix': assert bias<1e-25
        else: assert np.max(abs(mean-((1-lam)*glob+lam*micro)))<1e-12
        stats[name]={'bias_squared':bias,'variance':var,'mse':mse}
    rows.append({'seed':seed,'expert_counts':f.sum(0).tolist(),'stats':stats})
summary={}
for name in ['prefix','positive','subtract','pair_ht']:
    summary[name]={m:float(np.mean([r['stats'][name][m] for r in rows])) for m in ['bias_squared','variance','mse']}
    summary[name]['mse_better_than_prefix']=sum(r['stats'][name]['mse']<r['stats']['prefix']['mse']-1e-14 for r in rows)
    summary[name]['mse_worse_than_prefix']=sum(r['stats'][name]['mse']>r['stats']['prefix']['mse']+1e-14 for r in rows)
out={'scope':'64 seeded random analytic softmax fixtures, G4 K3 d2, all24 permutations; descriptive no benchmark inference', 'summary':summary,'rows':rows}
print(json.dumps(out,indent=2))
