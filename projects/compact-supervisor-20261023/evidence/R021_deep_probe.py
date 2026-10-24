#!/usr/bin/env python3
"""R021 independent source-derived CPU reproducer (not original Triton or trained EEFP)."""
import math, json, time
import numpy as np
import torch
start=time.process_time()
torch.set_default_dtype(torch.float64)
alpha=.98; margin=1/32
k=torch.ones(2)/math.sqrt(2); I=torch.eye(2); init=torch.tensor([1.,0.])
rcrit=(alpha**-2-1)*(1-.25/(alpha**-2))
T=math.sqrt(rcrit); tau=math.sqrt((1-margin)*rcrit)
def calc(tval,target,mode):
    t=torch.tensor(tval,requires_grad=True); b=torch.stack([.5+t,.5-t])
    a=(b*k*k).sum(); n=(k*k).sum(); r2=((b*b*k*k).sum()*n-a*a).clamp(min=0)
    rc=((alpha**-2-1)*(1-(1-a)**2/(alpha**-2))).clamp(min=0)
    factor=torch.sqrt((1-margin)*rc/r2.clamp(min=1e-30)).clamp(max=1)
    projected=a/n+factor*(b-a/n)
    eff=torch.where(r2>rc,projected,b)
    if mode=="STE":eff=b+(eff-b).detach()
    output=(alpha*(I-torch.outer(k,k*eff))@init)[1]
    loss=.5*(output-target)**2
    grad=torch.autograd.grad(loss,t)[0]
    return float(output.detach()),float(loss.detach()),float(grad.detach())
assert abs(T-.17701078966683267)<1e-10
assert abs(tau-.17422304395271113)<1e-10
outward=[calc(.49,-.8,x) for x in ("true","STE")]
inward=[calc(.49,0.,x) for x in ("true","STE")]
assert abs(outward[0][2])<1e-10 and outward[1][2]<0
assert abs(inward[0][2])<1e-10 and inward[1][2]>0
jump=calc(T+1e-8,0.,"true")[0]-calc(T-1e-8,0.,"true")[0]
assert abs(jump-alpha*(T-tau)/2)<1e-6
t=.49; first=None; start_output=calc(t,0.,"true")[0]
for step in range(1,251):
    t-=.01*calc(t,0.,"STE")[2]
    if first is None and abs(calc(t,0.,"true")[0]-start_output)>1e-8:first=step
assert first==194
n=10000;g=np.repeat([0,1],n//2);idx=np.tile(np.arange(n//2),2)
early=(idx%5==0).astype(float)
plus=np.where(g==0,0.,(idx%5<2).astype(float))
minus=np.where(g==1,0.,(idx%5<2).astype(float))
risk=lambda mask,d:float(np.where(mask,d+.05,early).mean())
policies={"stop":np.zeros(n,bool),"A":g==0,"B":g==1,"both":np.ones(n,bool)}
losses={name:{"plus":risk(mask,plus),"minus":risk(mask,minus)} for name,mask in policies.items()}
assert abs(losses["stop"]["plus"]-.2)<1e-10
assert abs(losses["A"]["plus"]-.125)<1e-10
rng=np.random.default_rng(20261024); audit=rng.random(n)<.05
print(json.dumps({"E1":{"tcrit":T,"tau":tau,"jump":jump,"outward_grad_true_STE":[outward[0][2],outward[1][2]],"inward_grad_true_STE":[inward[0][2],inward[1][2]],"inward_first_change_step":first},"C1":{"risks":losses,"audits":int(audit.sum()),"audit_cost_per_item":float(audit.mean()*.05)},"CPU_s":time.process_time()-start,"model_gpu_training":False},indent=2))
