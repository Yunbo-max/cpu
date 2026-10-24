#!/usr/bin/env python3
"""R026 static idealized Shannon-entropy two-arm mixture; NOT author's online source."""
import math,numpy as np
D_over_lam=10.0
q=1/(1+math.exp(D_over_lam))
T=10000
p0=math.exp(T*math.log1p(-q))
needed=math.ceil(math.log(.05)/math.log1p(-q))
rng=np.random.default_rng(20261024)
mc=float(np.mean(rng.binomial(T,q,size=20000)==0))
assert .63<p0<.64 and needed==65987 and abs(mc-p0)<.025
print({'q_rare':q,'P_no_rare_T10000':p0,'T95':needed,'mc_zero_fraction':mc})
