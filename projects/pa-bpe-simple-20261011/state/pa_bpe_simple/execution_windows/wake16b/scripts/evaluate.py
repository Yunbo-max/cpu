import sys,json,math,collections,hashlib,datetime
from pathlib import Path as P
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':536870912}))
assert free>=536870912
sys.path.insert(0,json.loads(P('evidence/parent.json').read_text())['deps'])
from tokenizers import Tokenizer,pre_tokenizers
from tokenizers.models import BPE
pre=pre_tokenizers.Sequence([pre_tokenizers.Whitespace(),pre_tokenizers.ByteLevel(use_regex=False)])
langs=['en','fr','es'];rows=json.loads(P('inputs/dev.json').read_text());assert len(rows)==970
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
 path=P('inputs/'+name+'.codes');merges=[tuple(x.split()) for x in path.read_text().splitlines() if x and not x.startswith('#')];assert len(merges)==1000
 vocab={c:i for i,c in enumerate(sorted(pre_tokenizers.ByteLevel.alphabet()))}
 for a,b in merges:
  assert a in vocab and b in vocab
  if a+b not in vocab:vocab[a+b]=len(vocab)
 tok=Tokenizer(BPE(vocab=vocab,merges=merges));tok.pre_tokenizer=pre
 fixtures=['é café 😀 中文 العربية','aaaaaa aa   a','',*([rows[j][l] for j in [0,484,969] for l in langs])]
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
P('output/evaluation.json').write_text(json.dumps({'arms':out,'scope':'970 aligned TICO development rows; same rows used as PA dev objective, no unseen-domain conclusion; no semantic train/dev overlap guarantee','data_sha256':hashlib.sha256(P('inputs/dev.json').read_bytes()).hexdigest(),'confirmation_accessed':False},indent=2)+'\n')
print(json.dumps({n:{k:v for k,v in a.items() if k!='paired_costs'} for n,a in out.items()},indent=2))
