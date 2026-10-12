import sys,json,math,collections,hashlib,datetime
from pathlib import Path as P
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/confirm_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':536870912}))
assert free>=536870912
sys.path.insert(0,json.loads(P('evidence/parent.json').read_text())['deps'])
from tokenizers import Tokenizer,pre_tokenizers
from tokenizers.models import BPE
pre=pre_tokenizers.Sequence([pre_tokenizers.Whitespace(),pre_tokenizers.ByteLevel(use_regex=False)])
langs=['en','fr','es']
import fingerprints as f
assert json.loads(P('output/independent_arithmetic_and_dev_overlap.json').read_text())['status']=='PASS'
plan=json.loads(P('confirmation_plan.json').read_text());spec=json.loads(P('inputs/source_manifest.json').read_text())
assert f.file_sha256('inputs/units.json')==plan['unit_manifest_sha256']
units=json.loads(P('inputs/units.json').read_text())['reserved_unit_identities'];assert len(units)==512
wanted={l:collections.defaultdict(set) for l in langs}
for u in units:
 assert f.recompute_unit_identity('OPUS-GlobalVoices/v2018q4',u)==u['unit_sha256']
 for l in langs:wanted[l][u['documents'][l]].update(u['sentence_ids'][l])
docs={}
for l in langs:
 assert f.file_sha256('raw/'+l+'.zip')==spec['archives'][l]['expected_sha256']
 docs[l]=f.load_selected_documents(P('raw/'+l+'.zip'),wanted[l])
rows=[{l:f.unit_text(docs[l][u['documents'][l]],u['sentence_ids'][l]) for l in langs} for u in units]

def gini(x):
 assert sum(x)>0
 a=sum(abs(i-j) for i in x for j in x)/(2*len(x)*sum(x))
 s=sorted(x);b=2*sum((i+1)*v for i,v in enumerate(s))/(len(s)*sum(s))-(len(s)+1)/len(s)
 assert abs(a-b)<1e-12
 return a
assert abs(gini([1,2,3])-2/9)<1e-12 and gini([1,1,1])==0 and abs(gini([0,0,3])-2/3)<1e-12
def replay(text,merges):
 out=[]
 for word,_ in pre.pre_tokenize_str(text):
  pieces=list(word)
  for a,b in merges:
   nxt=[];i=0
   while i<len(pieces):
    if i+1<len(pieces) and pieces[i]==a and pieces[i+1]==b:nxt.append(a+b);i+=2
    else:nxt.append(pieces[i]);i+=1
   pieces=nxt
  out.extend(pieces)
 return out
out={}
for name in ['classical','base','window','hybrid','ratio']:
 path=P('inputs/'+name+'.codes');assert f.file_sha256(path)==plan['codes'][name];merges=[tuple(x.split()) for x in path.read_text().splitlines() if x and not x.startswith('#')];assert len(merges)==1000
 vocab={c:i for i,c in enumerate(sorted(pre_tokenizers.ByteLevel.alphabet()))}
 for a,b in merges:
  assert a in vocab and b in vocab
  if a+b not in vocab:vocab[a+b]=len(vocab)
 tok=Tokenizer(BPE(vocab=vocab,merges=merges));tok.pre_tokenizer=pre
 fixtures=['é café 😀 中文 العربية','aaaaaa aa   a','',*([rows[j][l] for j in [0,255,511] for l in langs])]
 for t in fixtures:assert tok.encode(t).tokens==replay(t,merges)
 costs=[[len(tok.encode(r[l]).ids) for l in langs] for r in rows]
 assert all(all(c>0 for c in a) for a in costs)
 means=[sum(a[j] for a in costs)/len(costs) for j in range(3)]
 out[name]={'codes_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n':len(rows),'vocab':len(vocab),'merges':len(merges),'mean_tokens':dict(zip(langs,means)),'gini':gini(means),'worst_language':langs[means.index(max(means))],'worst_cost':max(means),'total_cost':sum(means),'mean_sentence_gini':sum(map(gini,costs))/len(costs),'paired_costs':costs,'replay_checks':len(fixtures)}
assert len({a['vocab'] for a in out.values()})==1,'realized_vocab_mismatch'
base=out['classical']
for name,a in out.items():
 a['gini_improvement_vs_classical']=base['gini']-a['gini']
 a['total_cost_relative_change']=a['total_cost']/base['total_cost']-1
 a['worst_cost_relative_change']=a['worst_cost']/base['worst_cost']-1

import numpy as np
clusters=sorted(set(u['documents']['en'] for u in units));rng=np.random.default_rng(20261012);draws=rng.integers(0,len(clusters),size=(1000,len(clusters)))
cluster_counts=np.array([sum(u['documents']['en']==c for u in units) for c in clusters]);denom=cluster_counts[draws].sum(axis=1)
ginis={};total_costs={};worsts={}
for name,a in out.items():
 values=np.array(a['paired_costs']);agg=np.array([values[[u['documents']['en']==c for u in units]].sum(axis=0) for c in clusters]);tot=agg[draws].sum(axis=1)
 gs=np.abs(tot[:,:,None]-tot[:,None,:]).sum(axis=(1,2))/(6*tot.sum(axis=1));ginis[name]=gs;total_costs[name]=tot.sum(axis=1)/denom;worsts[name]=tot.max(axis=1)/denom
 a['gini_bootstrap95']=np.quantile(gs,[.025,.975]).tolist()
for name,a in out.items():
 a['paired_gain_bootstrap95']=np.quantile(ginis['classical']-ginis[name],[.025,.975]).tolist()
 a['total_cost_change_bootstrap95']=np.quantile(total_costs[name]/total_costs['classical']-1,[.025,.975]).tolist()
 a['gain_retention_vs_dev']=a['gini_improvement_vs_classical']/json.loads(P('output/evaluation.json').read_text())['arms'][name]['gini_improvement_vs_classical'] if name!='classical' else None
result={'arms':out,'scope':'First fixed-model confirmation on512 previously outcome-sealed GlobalVoices units. Freeze made after970TICO development comparison; no tuning after opening. Convenience training and conditionalfr/es source proof remain limitations.','unit_manifest_sha256':f.file_sha256('inputs/units.json'),'plan_sha256':f.file_sha256('confirmation_plan.json'),'unit_ids':[u['unit_sha256'] for u in units],'clusters':len(clusters),'cluster_ids':[u['documents']['en'] for u in units],'bootstrap':{'replicates':1000,'seed':20261012,'unit':'English document','method':'paired percentile, descriptive one-domain uncertainty'},'attribution':[{l:docs[l][u['documents'][l]]['url'] for l in langs} for u in units],'confirmation_accessed':True,'raw_text_persisted':False}
P('output/confirmation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:{k:v for k,v in a.items() if k!='paired_costs'} for n,a in out.items()},indent=2))
