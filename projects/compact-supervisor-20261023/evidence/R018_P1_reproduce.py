#!/usr/bin/env python3
"""R018 equivalent two-expert expected STE test. Published path mirror, not model import."""
import torch, json, time
t = time.process_time()
torch.set_default_dtype(torch.float64)
v = torch.tensor([-1.387488, -2.649662]); target = -1.44243766
gap = 2.182

def marginal(logits, variant):
    lp = torch.nn.functional.logsigmoid(logits)
    lq = torch.log1p(-torch.exp(lp if variant == "olmoe" else lp.detach()))
    sel = torch.eye(2)
    if variant == "olmoe":
        probe = torch.zeros_like(lp, requires_grad=True)
        z = torch.logsumexp((sel*(lp+probe)+(1-sel)*lq).sum(-1),0)
        return torch.autograd.grad(z,probe,create_graph=True)[0]
    z = torch.logsumexp((sel*lp+(1-sel)*lq).sum(-1),0)
    return torch.autograd.grad(z,lp,create_graph=True)[0]

def objective(logits):
    pi = torch.softmax(logits,0)
    return 0.5*(pi*(pi*v-target)**2).sum()

def expected_proxy_gradient(logits, variant):
    r = logits.detach().clone().requires_grad_(True)
    pi = torch.softmax(r,0)
    m = marginal(r,variant)
    gs = []
    for i in range(2):
        z = torch.eye(2)[i]
        gate = (z-m).detach()+m
        prediction = (gate*pi*v)[i]
        loss = 0.5*(prediction-target)**2
        gs.append(torch.autograd.grad(loss,r,retain_graph=(i==0))[0].detach())
    return (pi.detach()[:,None]*torch.stack(gs)).sum(0)

rows=[]
for c in [-6.,0.,3.,6.]:
    r = torch.tensor([gap/2+c,-gap/2+c],requires_grad=True)
    before = objective(r)
    true = torch.autograd.grad(before,r)[0].detach()
    for variant in ["olmoe","qwen"]:
        g=expected_proxy_gradient(r,variant)
        after=objective(r.detach()-0.1*g)
        rows.append(dict(shift=c,method=variant,before=float(before),after=float(after),
          proxy_gradient=g.tolist(),true_gradient=true.tolist(),
          cosine=float(torch.nn.functional.cosine_similarity(g,true,dim=0))))
assert rows[-1]["method"]=="qwen" and rows[-1]["after"]>rows[-1]["before"]
assert rows[-2]["method"]=="olmoe" and rows[-2]["after"]<rows[-2]["before"]
print(json.dumps({"rows":rows,"measured_cpu_s":time.process_time()-t,
 "note":"synthetic exact expectation, not full trained ProbMoE run"},indent=2))
