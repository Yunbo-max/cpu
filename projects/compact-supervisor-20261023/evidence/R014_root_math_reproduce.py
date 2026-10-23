#!/usr/bin/env python3
"""R014 root-screen mathematics using Python stdlib only.
No LLM call, GPU, external dataset, API or training.
Original in-chat numeric integration used scipy.integrate.quad; this is a separately checked equivalent Simpson implementation.
"""
import json, math, time
start=time.process_time()
def expected_max_normal(n,steps=3000):
    def f(t):
        p=.5*(1+math.erf(t/math.sqrt(2)))
        return 1-p**n-(1-p)**n
    h=9.0/steps
    total=f(0)+f(9)
    for i in range(1,steps): total+=(4 if i%2 else 2)*f(i*h)
    return total*h/3
values={n:expected_max_normal(n) for n in (1,2,8,32,128)}
assert abs(values[2]-1/math.sqrt(math.pi))<1e-10
assert abs(values[128]-2.594597368599473)<1e-9
# An option policy class is a superset when adding an optional skill.
base_value=.8
skill_success=.9
mandatory_cost=.3
optional=max(base_value,skill_success-mandatory_cost)
assert optional==base_value and skill_success-mandatory_cost<base_value
# Two worlds agree on passive a0=0.5 but opposite on a1.
regrets=[max(.5*(1-p/1000),.5*(p/1000)) for p in range(1001)]
assert abs(min(regrets)-.25)<1e-12
# Two anti-correlated bits form valid joint outcomes (0,1),(1,0).
valid={(0,1),(1,0)}
valid_factorized=sum(.25 for a in (0,1) for b in (0,1) if (a,b) in valid)
assert valid_factorized==.5
print(json.dumps({"expected_best_normal_noise":[{"n":n,"value":x} for n,x in values.items()],
 "true_score":0,"best_optional_net":optional,"mandatory_skill_net":skill_success-mandatory_cost,
 "two_world_minimax_regret":min(regrets),"parallel_factorized_validity":valid_factorized,
 "cpu_process_seconds":time.process_time()-start},indent=2))
