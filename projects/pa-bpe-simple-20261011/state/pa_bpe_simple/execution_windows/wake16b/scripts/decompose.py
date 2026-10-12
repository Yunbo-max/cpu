import json,math,collections
from pathlib import Path as P
d=json.loads(P('output/evaluation.json').read_text());c=json.loads(P('output/confirmation.json').read_text());langs=['en','fr','es'];out={};checks=0
for domain,data in [('TICO_development',d),('GlobalVoices_first_confirmation',c)]:
 arms=data['arms'];base=arms['classical'];res={}
 for name,a in arms.items():
  costs=a['paired_costs'];n=len(costs);totals=[sum(row[j] for row in costs) for j in range(3)];s=sorted(totals)
  g=sum((2*(j+1)-4)*x for j,x in enumerate(s))/(3*sum(s));assert math.isclose(g,a['gini'],abs_tol=1e-12)
  means={l:totals[j]/n for j,l in enumerate(langs)};assert all(math.isclose(means[l],a['mean_tokens'][l],abs_tol=1e-12) for l in langs)
  delta={l:means[l]-base['mean_tokens'][l] for l in langs}
  pairs={}
  for i,l in enumerate(langs):
   for m in langs[i+1:]:
    before=base['mean_tokens'][l]-base['mean_tokens'][m];after=means[l]-means[m]
    pairs[l+'-'+m]={'classical_signed_gap':before,'method_signed_gap':after,'signed_correction':after-before,'absolute_gap_reduction':abs(before)-abs(after),'overshoot':before*after<0}
  res[name]={'mean_tokens':means,'change_from_classical':delta,'pair_gaps':pairs,'numerator_sum_abs_unordered':sum(abs(v['method_signed_gap']) for v in pairs.values()),'denominator_3times_sum_means':3*sum(means.values()),'mean_sentence_gini':a['mean_sentence_gini']}
  assert math.isclose(res[name]['numerator_sum_abs_unordered']/res[name]['denominator_3times_sum_means'],g,abs_tol=1e-12);checks+=5
 out[domain]=res
r={'independent_arithmetic_checks':checks,'decomposition':out,'interpretation':'Observed cost-shift/overshoot decomposition, not causal proof of morphology/domain mechanism. Confirmation now exposed; all future adaptive use explicitly exploratory.','next_candidate':'Constrain added total development token cost while balancing; pre-existing500-global hybrid strong comparator. Choose/freeze constraint using development only; obtain fresh confirmation before claiming improvement.','not_new_result':'Historical two-language cost-constrained candidate exists; adapt and compare rather than claim new mechanism'}
P('output/transfer_decomposition.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
