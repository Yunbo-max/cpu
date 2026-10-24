#!/usr/bin/env python3
"""R022 simple exact product Bernoulli sequence TV calculation.
Not ARC-Decode's code; does NOT evaluate a trained LLM or call APIs.
"""
import math, json, time
t0=time.process_time()
def kl(p,q):
    return p*math.log(p/q)+(1-p)*math.log((1-p)/(1-q))
def js(p,q):
    m=(p+q)/2
    return .5*(kl(p,m)+kl(q,m))
def total_variation(n,p,q):
    s=0.
    for k in range(n+1):
        coeff=math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)
        lp=coeff+k*math.log(p)+(n-k)*math.log1p(-p)
        lq=coeff+k*math.log(q)+(n-k)*math.log1p(-q)
        s+=abs(math.exp(lp)-math.exp(lq))
    return s/2
p,q=.5,.51
values=[{"T":n,"TV":total_variation(n,p,q)} for n in (1,10,30,60,100,300,1000,5000)]
assert abs(values[0]["TV"]-.01)<1e-12
assert .06<values[3]["TV"]<.063
all_valid=.99**60
assert abs(all_valid-.5471566423907612)<1e-12
print(json.dumps({"local_JS":js(p,q),"values":values,"T60_all_valid_prob":all_valid,
                  "cpu_process_seconds":time.process_time()-t0},indent=2))
