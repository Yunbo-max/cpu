import json,sqlite3,hashlib,collections,re
from pathlib import Path as P
import fingerprints as f
data=json.loads(P('inputs/dev.json').read_text());db=P('inputs/confirmation.sqlite3')
assert f.file_sha256(db)=='26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7'
con=sqlite3.connect('file:'+str(db.resolve())+'?mode=ro',uri=True)
records={};index=collections.defaultdict(list)
for unit,lang,url,exact,words,mass in con.execute('SELECT * FROM confirmation'):records[(unit,lang)]={'url':url,'exact':exact,'words':words,'mass':mass}
for unit,lang,sh,n in con.execute('SELECT * FROM shingles'):index[(lang,sh)].append((unit,n))
hits=[]
for row in data:
 for l in ['en','fr','es']:
  norm=f.normalize_text(row[l]);words=f.WORD_RE.findall(norm);grams=f.shingle_counter(words);exact=f.sha256_bytes(norm.encode());url=f.canonical_url(row['url']);uh=f.sha256_bytes(url.encode()) if url else None
  matches=[]
  for (u,lang),a in records.items():
   if lang==l and a['exact']==exact:matches.append('exact')
   if uh and a['url']==uh:matches.append('url')
  if len(words)>=20:
   intersections=collections.Counter()
   for sh,n in grams.items():
    for u,m in index[(l,sh)]:intersections[u]+=min(n,m)
   for u,n in intersections.items():
    a=records[(u,l)]
    if a['words']>=20 and n/min(sum(grams.values()),a['mass'])>=.8:matches.append('near')
  if matches:hits.append({'id':row['id'],'language':l,'reasons':sorted(set(matches))})
e=json.loads(P('output/evaluation.json').read_text());checks=0
for name,a in e['arms'].items():
 costs=a['paired_costs'];totals=[sum(r[j] for r in costs) for j in range(3)];means=[t/970 for t in totals]
 g=sum((2*(i+1)-4)*x for i,x in enumerate(sorted(totals)))/(3*sum(totals))
 assert abs(g-a['gini'])<1e-12
 for l,x in zip(['en','fr','es'],means):assert abs(x-a['mean_tokens'][l])<1e-12
 assert a['vocab']==1256 and a['merges']==1000 and len(costs)==970;checks+=6
P('output/independent_arithmetic_and_dev_overlap.json').write_text(json.dumps({'arithmetic_checks':checks,'rows_checked':len(data),'blind_confirmation_matches':hits,'scope':'Independent integer-sum Gini and means recomputation; exact/URL/80percent5gram>=20worddev overlap screening, not semantic proof','status':'PASS' if not hits else 'HOLD'},indent=2))
assert not hits,'dev_confirmation_overlap_requires_revision_before_unblinding'
print('PASS arithmetic and blinded dev-overlap')
