#!/usr/bin/env python3
"""R020 source-derived GDN2 contrast guard probe; not NVIDIA Triton or trained model."""
import numpy as np, torch, math, json
K=np.array([1.,1.])/math.sqrt(2)
ALPHA=.98
MARGIN=1/32

def guard(b,k=K,alpha=ALPHA):
    a=float(np.sum(b*k*k)); n=float(k@k);nu=float(np.sum(b*b*k*k))
    r2=max(n*nu-a*a,0.);c2=alpha**(-2)
    critical=max((c2-1)*(1-(1-a)**2/c2),0.)
    if r2<=critical:return np.array(b,dtype=float)
    eta=min(1.,math.sqrt((1-MARGIN)*critical/max(r2,1e-30)))
    return a/n+eta*(b-a/n)

def A(b,k=K,alpha=ALPHA):return alpha*(np.eye(len(k))-np.outer(k,b*k))

b=np.array([.99,.01]);raw=A(b);safe=A(guard(b));
assert np.allclose(np.linalg.eigvals(raw),[.49,.98],atol=1e-12)
assert np.linalg.norm(raw,2)>1.1 and np.linalg.norm(safe,2)<1

bflat=[guard(np.array([.5+t,.5-t])) for t in (.20,.30,.40,.49)]
assert all(np.allclose(bflat[0],v) for v in bflat)

# The actual projection derivative is zero on this contrast ray, but the
# published chunkwise kernel explicitly uses straight-through db to raw b.
t=torch.tensor(.49,requires_grad=True,dtype=torch.float64)
kt=torch.tensor(K);bp=torch.stack((.5+t,.5-t))
aa=(bp*kt*kt).sum();rr=((bp*bp)*(kt*kt)).sum()-aa*aa
c2=ALPHA**(-2);cr=(c2-1)*(1-(1-aa)**2/c2)
eff=aa+torch.sqrt((1-MARGIN)*cr/rr)*(bp-aa)
ste=bp+(eff-bp).detach()

def loss(v):
    y=(ALPHA*(torch.eye(2,dtype=torch.float64)-torch.outer(kt,kt*v))@torch.tensor([1.,0.],dtype=torch.float64))[1]
    return .5*(y+.8)**2
true_grad=torch.autograd.grad(loss(eff),t,retain_graph=True)[0].item()
ste_grad=torch.autograd.grad(loss(ste),t)[0].item()
assert abs(true_grad)<1e-12 and abs(ste_grad+.23011904714695403)<1e-9

rng=np.random.default_rng(20261024);N=2000;count_raw=0;count_guarded=0
for _ in range(N):
    k=rng.normal(size=2);k/=np.linalg.norm(k)
    bb=rng.uniform(.001,.999,size=2);alpha=rng.uniform(.9,.995)
    count_raw+=np.linalg.norm(A(bb,k,alpha),2)>1+1e-10
    count_guarded+=np.linalg.norm(A(guard(bb,k,alpha),k,alpha),2)>1+1e-10
assert count_guarded==0
print(json.dumps({"raw_norm":float(np.linalg.norm(raw,2)),
 "protected_norm":float(np.linalg.norm(safe,2)),
 "raw_eigenvalues":np.linalg.eigvals(raw).tolist(),
 "true_gradient":true_grad,"straight_through_gradient":ste_grad,
 "raw_expansion_count":int(count_raw),"protected_expansion_count":int(count_guarded),
 "synthetic_samples":N,"not_a_model_benchmark":True},indent=2))
