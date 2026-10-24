#!/usr/bin/env python3
"""R026 source-formula test, NOT original native PyEPO/Gurobi model."""
import math, numpy as np, torch
W=np.eye(2)
delta=.2; rho=1.
observed=np.array([0.,delta]); fixed=np.array([rho,delta])
def choose(cost):return int(np.argmin(cost))
def surrogate(cp,c):
    w=W[choose(c)]
    q=2*cp-c; wq=W[choose(q)]
    return float(-q.min()+2*cp@w-c@w), 2*(w-wq)
def true_regret(i,r=.9999999999999999,d=delta):
    return max(0.,math.sqrt(2)*r+(-d if i==0 else d))
L,g=surrogate(observed,fixed)
after=observed-.1*g
L2,_=surrogate(after,fixed)
assert np.allclose(g,[-2,2]) and np.allclose(after,[.2,0])
assert abs(L-1.2)<1e-10 and abs(L2-.4)<1e-10
def train(method):
    c=observed if method=='emp' else fixed
    cp=torch.nn.Parameter(torch.tensor(observed,dtype=torch.float64))
    optim=torch.optim.Adam([cp],lr=.01,weight_decay=1e-4)
    history=[]
    for i in range(31):
        cost=cp.detach().numpy().copy()
        loss,grad=surrogate(cost,c)
        history.append((i,choose(cost),float(loss),true_regret(choose(cost))))
        if i<30:
            cp.grad=torch.tensor(grad,dtype=torch.float64)
            optim.step(); optim.zero_grad(set_to_none=True)
    return history
emp=train('emp'); reg=train('robust_regret'); opt=train('robust_opt')
assert reg==opt
assert emp[-1][1]==0 and reg[-1][1]==1
assert next(i for i,a,*_ in reg if a==1)==11
n_flip=n_rank=0
for d in np.linspace(.01,2,100):
  for r in np.linspace(.01,2,100):
    if d>=r:continue
    n_rank+=1
    before=np.array([0.,d]);cf=np.array([r,d])
    _,g=surrogate(before,cf)
    if choose(before-.1*g)!=choose(before):n_flip+=1
assert (n_rank,n_flip)==(4950,1790)
print({'SPO+':(L,L2),'action':(choose(observed),choose(after)),
       'robust_regret':(true_regret(0),true_regret(1)),
       'robust_regret_and_robust_opt_equal':reg==opt,
       'switch_step':11,'grid_rank_flips':n_rank,'grid_spoplus_action_switch':n_flip})
