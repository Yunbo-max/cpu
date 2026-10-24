#!/usr/bin/env python3
"""R024 two non-KV mathematical probes. Not trained model or original oracle import."""
import json, math, numpy as np
from scipy.linalg import logm, expm
rng = np.random.default_rng(20261024)
n=2000
z=rng.uniform(0.,1.,n);y=rng.uniform(-.5,.5,n)
bias=.8
results=[]
for eps in (.1,.03,.01,.003):
    A=np.array([[eps,1.],[-eps,0.]])
    H=np.eye(3);H[:2,:2]=A;H[:2,2]=[bias,0.]
    assert np.allclose(expm(logm(H)).real,H,atol=1e-8)
    out=A@np.vstack([z,y])+np.array([[bias],[0.]])
    decoded=np.linalg.solve(A,np.vstack([out[0],np.zeros(n)])-np.array([[bias],[0.]]))
    zdev=np.mean(out[1]**2)
    sc=np.mean((decoded[1]-y)**2)
    true=np.mean((out[0]-y)**2)
    assert abs(zdev-sc)<1e-10 and np.linalg.det(A)>0
    results.append(dict(eps=eps,zero=float(zdev),self_consistency=float(sc),
                        deployed_truth=float(true),ratio=float(true/sc)))
c0=np.array([0.,.2]);chosen=np.eye(2)
wref=chosen[0]
cw=c0+wref   # observed-cost optimal action used to build static adversarial label
angles=np.linspace(0,2*math.pi,100001)
uncert=c0+np.column_stack([np.cos(angles),np.sin(angles)])
res=[]
for i,w in enumerate(chosen):
    proxy=float(cw@w-np.min(cw))
    worst=float(np.max(np.maximum(0.,uncert@w-uncert.min(axis=1))))
    exact=math.sqrt(2)+(-.2 if i==0 else .2)
    assert abs(worst-exact)<1e-5
    res.append(dict(action=i,static_proxy_regret=proxy,actual_worst_regret=worst))
print(json.dumps(dict(DiagCFM_affine=results,RobustDFL_proxy=res,
    scope="synthetic closed-form tests, not original pretrained models"),indent=2))
