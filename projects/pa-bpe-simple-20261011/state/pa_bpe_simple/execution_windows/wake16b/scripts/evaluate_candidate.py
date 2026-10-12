import sys,json,math,collections,hashlib,datetime
from pathlib import Path as P
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/candidate_eval_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':536870912}))
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

for path,expected in json.loads(P('evidence/candidate_parent_inputs.json').read_text()).items():assert f.file_sha256(path)==expected
result=json.loads(P('output/damped_result.json').read_text());assert f.file_sha256('output/damped.codes')==result['codes_sha256'] and f.file_sha256('candidate_plan.json')==result['plan_sha256']
merges=[tuple(x.split()) for x in P('output/damped.codes').read_text().splitlines() if x and not x.startswith('#')];vocab={c:i for i,c in enumerate(sorted(pre_tokenizers.ByteLevel.alphabet()))}
for a,b in merges:
 assert a in vocab and b in vocab
 if a+b not in vocab:vocab[a+b]=len(vocab)
assert len(merges)==1000 and len(vocab)==1256
tok=Tokenizer(BPE(vocab=vocab,merges=merges));tok.pre_tokenizer=pre
out={}
for domain,data,reference in [('TICO_dev',json.loads(P('inputs/dev.json').read_text()),'output/evaluation.json'),('GlobalVoices_exposed',rows,'output/confirmation.json')]:
 for r in data[:3]:
  for l in langs:assert tok.encode(r[l]).tokens==replay(r[l],merges)
 costs=[[len(tok.encode(r[l]).ids) for l in langs] for r in data];means=[sum(c[j] for c in costs)/len(costs) for j in range(3)];g=gini(means)
 old=json.loads(P(reference).read_text())['arms'];comparisons={}
 for name,a in old.items():comparisons[name]={'gini_difference_candidate_minus_arm':g-a['gini'],'total_cost_relative_change':sum(means)/a['total_cost']-1,'worst_cost_relative_change':max(means)/a['worst_cost']-1}
 out[domain]={'n':len(data),'gini':g,'mean_tokens':dict(zip(langs,means)),'total_cost':sum(means),'worst_cost':max(means),'worst_language':langs[means.index(max(means))],'mean_sentence_gini':sum(map(gini,costs))/len(costs),'paired_costs':costs,'comparisons':comparisons}
P('output/candidate_evaluation.json').write_text(json.dumps({'candidate':'damped-target-half','vocab':len(vocab),'merges':len(merges),'plan_sha256':f.file_sha256('candidate_plan.json'),'codes_sha256':f.file_sha256('output/damped.codes'),'domains':out,'scope':'Exploratory candidate proposed afterGV exposure; not new independent confirmation. Compare to strong fixedhybrid; preserve negative outcome.'},indent=2)+'\n')
print(json.dumps({d:{k:v for k,v in a.items() if k!='paired_costs'} for d,a in out.items()},indent=2))
