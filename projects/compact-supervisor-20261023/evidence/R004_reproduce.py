#!/usr/bin/env python3
"""R004 deterministic reproduction of sign/Adam and reachability witnesses.
Standard-library Python. Run from the evidence directory. No model inference.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json
getcontext().prec = 55
r = json.loads((Path(__file__).parent / "supervisor_adam_probe.json").read_text())
alpha, eps = 0.001, 1e-8
for row in r["rows"]:
    grads=[sum(g,[]) for g in row["prefix_gradients"]]
    actual=sum(row["mean_adam_prefix_update"],[])
    mixture=sum(row["explicit_mixture_gradient"],[])
    differences=sum(row["adam_mean_minus_mixture"],[])
    pred=[sum(-alpha*(1 if g[j]>0 else -1 if g[j]<0 else 0) for g in grads)/len(grads) for j in range(len(grads[0]))]
    errs=max(abs(a-b) for a,b in zip(actual,pred))
    gaperrs=max(abs(a-b) for a,b in zip(differences,[pred[j]+alpha*(1 if mixture[j]>0 else -1 if mixture[j]<0 else 0) for j in range(len(pred))]))
    assert errs < 1e-8 and gaperrs < 1e-8
    print(row["seed"],errs,gaperrs)
b1,b2=D(".9"),D(".999")
alpha,eps=D(".001"),D(".00000001")
m=(1-b1**99)*3
v=(1-b2**99)*10
def f(g):
    mh=(b1*m+(1-b1)*g)/(1-b1**100)
    vh=(b2*v+(1-b2)*g*g)/(1-b2**100)
    return -alpha*mh/(vh.sqrt()+eps)
a=(f(D(2))+f(D(4)))/2
b=f(D(1))/5+4*f(D("3.5"))/5
assert b-a < D("-1.8e-8") and b-a > D("-1.9e-8")
print("higher_moment_gap",b-a)
assert -2+1 < 0 and -D(".5")+1 > 0
print("reachability toy: negative margin impossible, moderate margin reachable")
