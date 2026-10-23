#!/usr/bin/env python3
"""R005 fixed-budget CPU witness for EventTune effective controller geometry.
No model, no network, no evaluation dataset, no GPU. NumPy only.
Run: python3 R005_controller_witness.py
"""
import numpy as np, time, json
start=time.perf_counter()
alpha=3.0
rng=np.random.default_rng(20261023)
errors=[]; norms=[]
for _ in range(100):
    raw=rng.normal(size=(16,16))
    effective=alpha*raw/(1+np.linalg.norm(raw,"fro"))
    recovered=effective/(alpha-np.linalg.norm(effective,"fro"))
    errors.append(float(np.max(np.abs(recovered-raw))))
    norms.append(float(np.linalg.norm(effective,"fro")))
assert max(errors)<2e-12 and max(norms)<alpha
B=np.array([[1.],[0.]])
Z=np.array([[0.,1.]])
G=np.array([[1.,0.]])
assert (G@B).item()==1
for a in (-2.9,-1,0,2.9):
    assert np.allclose(Z+(Z@B)@np.array([[a]])@B.T,Z)
live=np.array([[1.,0.]])
assert np.allclose(live+(live@B)@np.array([[1.]])@B.T,[[2.,0.]])
g=np.array([1.,1.,-1.])
m0=-.5*np.ones(3)
grid=np.linspace(-2.99,2.99,599)
correct=(m0[:,None]+g[:,None]*grid[None,:]>0).sum(axis=0)
assert correct.max()==2
assert np.max(np.min(m0[:,None]+g[:,None]*grid[None,:],axis=0))<=-.5+1e-12
dual_lam=np.array([.5,0.,.5])
upper=float(dual_lam@m0+alpha*abs(dual_lam@g))
assert upper==-.5
print(json.dumps({
  "100_effective_map_trials":True,
  "max_inverse_roundtrip_error":max(errors),
  "max_tested_effective_frobenius_norm":max(norms),
  "exact_null_edit":True,
  "shared_controller_max_correct_count":int(correct.max()),
  "shared_controller_accuracy_cap":2/3,
  "dual_upper_margin":upper,
  "elapsed_wall_seconds":time.perf_counter()-start
},indent=2))
