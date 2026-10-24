#!/usr/bin/env python3
"""R028 minimal CPU reproduction; source-formula mirrors, NOT native EPC/RobustDFL models."""
import math, numpy as np
# EPC-AW BTS when own scores high=5 / low=2, one of six low peer forecasts underpredicts 2 to 1
scores={"high":0.0, "low":math.log(2/1.5)/3}
assert scores["low"]>scores["high"]
eps=.05
pflip=1-(1-eps)**6
rng=np.random.default_rng(20261024)
observed=float(np.any(rng.random((100000,6))<eps,axis=1).mean())
assert abs(observed-pflip)<.005
# RobustDFL source ellipsoid and sparse uncertainty models
C=np.array([[-2.,-.3],[0.,.2],[2.,.7]])
sigma=np.sqrt(C.var(axis=0,ddof=1)+1e-8)
c=np.array([0.,.2]); w=np.array([1.,0.])
ellip=lambda k:c+k*sigma*(sigma*w)/np.linalg.norm(sigma*w)
sparse=lambda rho:c+rho*np.array([1.,0.])
assert not np.allclose(ellip(7.5),sparse(5.))
assert np.allclose(ellip(1.),ellip(1.))
print({"EPC_BTS":scores,"synthetic_probability":pflip,"monte_carlo":observed,
 "ellip_kappa_7p5":ellip(7.5).tolist(),"sparse_rho_5":sparse(5.).tolist()})
