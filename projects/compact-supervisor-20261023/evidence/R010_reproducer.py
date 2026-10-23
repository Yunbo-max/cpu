#!/usr/bin/env python3
"""R010 source-backed toy arithmetic; no model inference or GPU."""
import math
import json
vacuous=(1-.001)**200
near=sum(math.comb(50,k)*.02**k*.98**(50-k) for k in range(6))
assert abs(vacuous-.8186488294786356)<1e-12
assert abs(near-.9995217827857852)<1e-12
assert .05**(1/28)<.9<.05**(1/29)
def copies(n,t,d=4096):
    return {'prefix':n,'added':t,'new_bytes':t*d,
      'cumulative_cat_write_bytes':d*(n*t+t*(t+1)//2),
      'write_over_added_ratio':n+(t+1)/2}
result={'rare_antecedent_no_support_probability':vacuous,
  'near_rule_empirical_accept_probability':near,
  'CP_L_28':.05**(1/28),'CP_L_29':.05**(1/29),
  'copy_4096_1024':copies(4096,1024),
  'copy_8192_8192':copies(8192,8192),
  'scope':'mathematical toy, not measured inference'}
print(json.dumps(result,indent=2))
