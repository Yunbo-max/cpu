#!/usr/bin/env python3
"""R016 self-contained NumPy micro-probe. Not original QED code or trained-model evaluation."""
import json, math, time
import numpy as np
t=time.process_time();rho=.6;beta=.8;k=np.array([1.,0.]);q=np.array([rho,math.sqrt(1-rho**2)])
S=np.array([[0.],[1.]]);r=k.copy();b=np.array([beta,beta])
D=b*q-k*float(k @ (b*q))
base=(np.eye(2)-np.outer(k,b*k))@S
rows=[]
for lam in (.101,.120,.25):
    qed=(np.eye(2)-np.outer(k,b*k+lam*D))@S
    for p in (.05,.1):
        risk=lambda X:p*float((q@X).item()**2)+(1-p)*float((r@X).item()**2)
        d0=risk(qed)-risk(base)
        delta=(1-rho**2)*lam*beta*(-2*p*rho+lam*beta*(1-p+p*rho**2))
        assert math.isclose(d0,delta,abs_tol=1e-12)
        pstar=lam*beta/(2*rho+lam*beta*(1-rho**2))
        rows.append({"lambda":lam,"p":p,"baseline":risk(base),"qed":risk(qed),
                     "delta":d0,"p_star":pstar,
                     "beta_star":2*p*rho/(lam*(1-p+p*rho**2))})
qed=(np.eye(2)-np.outer(k,b*k+.12*D))@S
A=np.eye(2)-np.outer(k,k)
assert np.allclose(A@(qed-base),0)
assert np.allclose((.8**5)*(qed-base),(.8**5)*qed-(.8**5)*base)
print(json.dumps({"rows":rows,"overwrite_k_annihilates":True,"decay_factor_five":.8**5,
                  "CPU_process_seconds":time.process_time()-t,
                  "scope":"fixed-state linear operator, NOT trained QED model"},indent=2))
