#!/usr/bin/env python3
"""R027 self-contained CPU equations reproduction; full source-body isolation is in local ZIP.
No original Gurobi/PyEPO, EPC-AW agent framework, LLM or GPU imported.
"""
import math,numpy as np
C=np.array([[-1.,-.8],[0.,.2],[1.,1.2]],dtype=np.float64)
sigma=np.sqrt(C.var(0,ddof=1)+1e-8)
def src_wc(c,w,kappa=1.,sense=1):
    v=sigma*w
    return c+(1 if sense==1 else -1)*kappa*sigma*v/np.linalg.norm(v)
sols=np.eye(2)[np.argmin(C,axis=1)]
c_w=np.stack([src_wc(c,w) for c,w in zip(C,sols)])
assert np.allclose(sigma,[1.000000005,1.000000005])
assert np.allclose(c_w[1],[1.000000005,.2])
proxy=[max(0,c_w[1][0]-c_w[1][1]),max(0,c_w[1][1]-c_w[1][0])]
true=[math.sqrt(2)-.2,math.sqrt(2)+.2]
assert proxy[1]==0 and true[0]<true[1]
A={'High':5.,'Low':2.};P={'High':5.,'Low':1.}
def bts(A,P):return {k: math.log(A[k]+1e-12)-math.log(P[k]+1e-12) for k in A}
select=lambda B:max(A,key=lambda k:(B[k],A[k]))
assert select(bts(A,P))=='Low'
assert select(bts(A,A))=='High'
print({'S13':{'sigma':sigma.tolist(),'static_center':c_w[1].tolist(),'proxy':proxy,'true':true},
'S15':{'BTS':bts(A,P),'selected':select(bts(A,P)),'calibrated_selected':select(bts(A,A))}})
