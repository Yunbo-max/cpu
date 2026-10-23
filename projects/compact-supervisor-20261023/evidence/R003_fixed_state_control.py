#!/usr/bin/env python3
"""R003: deterministic fixed-optimizer-state control on R002 cached gradients.
Python 3 standard library only; no network, model, GPU, or data generation.
Run from the evidence/ directory: python R003_fixed_state_control.py
"""
from pathlib import Path
import json, math

root = Path(__file__).resolve().parent
src = json.loads((root / "supervisor_adam_probe.json").read_text())
b1, b2, lr, eps = 0.9, 0.999, 0.001, 1e-8

def flat(xs):
    if isinstance(xs, list):
        result = []
        for x in xs:
            result.extend(flat(x))
        return result
    return [float(xs)]

def step(g, m, v, t):
    mh = (b1*m+(1-b1)*g)/(1-b1**t)
    vh = (b2*v+(1-b2)*g*g)/(1-b2**t)
    return -lr*mh/(math.sqrt(vh)+eps)

out = []
for row in src["rows"]:
    grads = [flat(v) for v in row["prefix_gradients"]]
    n, d = len(grads), len(grads[0])
    mu = [sum(g[j] for g in grads)/n for j in range(d)]
    var = [sum((g[j]-mu[j])**2 for g in grads)/n for j in range(d)]
    sd = [math.sqrt(v) for v in var]
    mixture = flat(row["explicit_mixture_gradient"])
    original = flat(row["adam_mean_minus_mixture"])
    reproduced = [sum(step(g[j],0,0,1) for g in grads)/n - step(mixture[j],0,0,1) for j in range(d)]
    assert max(abs(a-b) for a,b in zip(original,reproduced)) < 3e-10
    for c in [0, 0.5, 2]:
        for t in [1, 100]:
            q = [x+c*sd[j]*(-1 if x<0 else 1) for j,x in enumerate(mu)]
            mp = [0 if t==1 else (1-b1**(t-1))*x for x in q]
            vp = [0 if t==1 else (1-b2**(t-1))*(x*x+var[j]) for j,x in enumerate(q)]
            det = [step(x,mp[j],vp[j],t) for j,x in enumerate(q)]
            stoch = [sum(step(x+g[j]-mu[j],mp[j],vp[j],t) for g in grads)/n for j,x in enumerate(q)]
            delta = [a-b for a,b in zip(stoch,det)]
            flips = sum((x+g[j]-mu[j])*x<0 for j,x in enumerate(q) for g in grads)/(n*d)
            out.append({"seed":row["seed"],"synthetic_task_shift_sigma":c,"adam_step":t,
                        "max_abs_update_difference":max(abs(z) for z in delta),
                        "l2_update_difference":math.sqrt(sum(z*z for z in delta)),
                        "fraction_sign_crossings":flips})
print(json.dumps(out,indent=2))
