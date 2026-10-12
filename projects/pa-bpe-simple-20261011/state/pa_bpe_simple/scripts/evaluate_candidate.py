import sys,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
from evaluate_pilot import tokenizer,replay,gini,gini_sorted,checks
old=json.loads((P/'experiment_plan_v1.json').read_text())['arms'];expected=old+['pooled','robust_domain']
actual={p.stem for p in (P/'runs').glob('*.merges')};assert actual==set(expected),(actual,expected)
m=json.loads((P/'data/manifest_v2.json').read_text())
for name,digest in m['hashes'].items():assert hashlib.sha256((P/'data'/name).read_bytes()).hexdigest()==digest,name
result={'checks':checks(),'arms':{}}
for arm in expected:
 t,merges,v=tokenizer(P/f'runs/{arm}.merges');assert len(merges)==1000 and len(v)==1256
 out={'vocab':len(v),'datasets':{}}
 for split in ['tico.dev100','books.dev100','tico.confirm','books.confirm']:
  rows=json.loads((P/f'data/{split}.json').read_text());costs=[]
  for i,r in enumerate(rows):
   cost=[]
   for lang in ['en','fr']:
    encoded=t.encode(r[lang]);cost.append(len(encoded.ids))
    if i<3:assert encoded.tokens==replay(r[lang],merges)
   costs.append(cost)
  means=[sum(c[i] for c in costs)/len(rows) for i in [0,1]];assert abs(gini(means)-gini_sorted(means))<1e-12
  out['datasets'][split]={'n':len(rows),'mean_tokens':means,'gini':gini(means),'worst_cost':max(means),'sum_language_means':sum(means),'paired_costs':costs}
 result['arms'][arm]=out
(P/'runs/evaluation_v2.json').write_text(json.dumps(result,indent=2))
print(json.dumps({a:{s:{k:d[k] for k in ['n','gini','mean_tokens']} for s,d in r['datasets'].items()} for a,r in result['arms'].items()},indent=2))
