#!/usr/bin/env python3
"""R019 CPU standalone source-equivalent ProbMoE Exact-k marginal Jacobian check.
Reference: HengHugoZhao/ProbMoE@3f0e538e8cab9b4b91f12479a0c0040c843723d2
Two model backbones are NOT instantiated. No GPU/training/API.
"""
import torch
import torch.nn.functional as F
def log1mexp(x):
    x=-x.abs()
    return torch.where(x > -0.6931471805599453,torch.log(-torch.expm1(x)),torch.log1p(-torch.exp(x)))
def stable_logaddexp(x,y):
    delta=torch.where(x==y,0.,x-y)
    return torch.maximum(x,y)+F.softplus(-delta.abs())
def partition(lp,lq,k):
    b,n=lp.shape
    state=torch.full((b,k+2),-300.,dtype=lp.dtype)
    state[:,1]=0.
    for i in range(1,n+1):
        state=torch.cat([torch.full((b,1),-300.),stable_logaddexp(
           state[:,:-1]+lp[:,i-1:i],state[:,1:]+lq[:,i-1:i])],dim=1)
    return state[:,-1:].sum()
def marginals(r,k,path):
    lp=torch.clamp(F.logsigmoid(r.float()),max=-1e-7)
    if path=="qwen":
        lq=log1mexp(lp.detach())
        return torch.autograd.grad(partition(lp,lq,k),lp,create_graph=True)[0]
    lq=log1mexp(lp)
    probe=torch.zeros_like(lp,requires_grad=True)
    return torch.autograd.grad(partition(lp+probe,lq,k),probe,create_graph=True)[0]
def j00(logits,k,path):
    r=torch.tensor([logits],dtype=torch.float32,requires_grad=True)
    m=marginals(r,k,path)
    return float(torch.autograd.grad(m[0,0],r)[0][0,0].detach())
if __name__=="__main__":
    for r,k in [([5.,5.],1),([5.001,5.],1),([.4,-.2,1.2,-1.],2)]:
        print(r,k,"Qwen",j00(r,k,"qwen"),"OLMoE",j00(r,k,"olmoe"))
    assert j00([5.,5.],1,"qwen")==0 and j00([5.,5.],1,"olmoe")==0
    assert abs(j00([5.001,5.],1,"olmoe")-.25)<1e-5
    assert abs(j00([5.001,5.],1,"qwen")-.00167155)<1e-5
