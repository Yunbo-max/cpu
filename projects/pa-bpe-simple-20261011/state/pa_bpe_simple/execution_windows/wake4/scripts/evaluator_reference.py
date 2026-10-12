import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace,ByteLevel,Sequence
P=Path(__file__).resolve().parents[1]
pre=Sequence([Whitespace(),ByteLevel(use_regex=False)])
def gini(x):
 assert x and all(math.isfinite(v) and v>=0 for v in x) and sum(x)>0
 return sum(abs(a-b) for a in x for b in x)/(2*len(x)*sum(x))
def gini_sorted(x):
 s=sorted(x);n=len(s);return 2*sum((i+1)*v for i,v in enumerate(s))/(n*sum(s))-(n+1)/n
def tokenizer(path):
 merges=[tuple(l.split()) for l in path.read_text().splitlines() if l and not l.startswith('#')]
 assert all(len(m)==2 for m in merges)
 vocab={c:i for i,c in enumerate(sorted(ByteLevel.alphabet()))}
 for a,b in merges:
  if a+b not in vocab:vocab[a+b]=len(vocab)
 t=Tokenizer(BPE(vocab=vocab,merges=merges));t.pre_tokenizer=pre
 return t,merges,vocab
def replay(text,merges):
 out=[]
 for word,_ in pre.pre_tokenize_str(text):
  pieces=list(word)
  for a,b in merges:
   new=[];i=0
   while i<len(pieces):
    if i+1<len(pieces) and pieces[i]==a and pieces[i+1]==b:new.append(a+b);i+=2
    else:new.append(pieces[i]);i+=1
   pieces=new
  out.extend(pieces)
 return out
def checks():
 cases=[([1,1],0),([0,2],.5),([1,2,3],2/9),([0,0,4],2/3)]
 for vals,expected in cases:assert abs(gini(vals)-expected)<1e-12 and abs(gini(vals)-gini_sorted(vals))<1e-12
 try:gini([0,0]);raise RuntimeError('zero accepted')
 except AssertionError:pass
 return {'analytic_cases':4,'zero_denominator_rejected':True,'pairwise_sorted_agree':True}
if __name__=='__main__':
 validation=checks();out={}
 for path in sorted((P/'runs').glob('*.merges')):
  arm=path.stem;t,merges,vocab=tokenizer(path);details={'merges':len(merges),'vocab':len(vocab),'datasets':{}}
  # Exact token-string agreement, including Unicode and repetition, not counts alone.
  fixtures=['Bonjour, le monde!','The quick brown fox.','é café 😀 中文 العربية','aaaaaa aa   a','', '\n']
  rows=json.loads((P/'data/tico.dev.json').read_text())
  fixtures += [r[l] for r in rows[:8] for l in ['en','fr']]
  for text in fixtures:assert t.encode(text).tokens==replay(text,merges),(arm,text)
  details['replay_cases_passed']=len(fixtures)
  for split in ['tico.dev','tico.test','books.pilot']:
   rows=json.loads((P/f'data/{split}.json').read_text());costs=[[len(t.encode(r[l]).ids) for l in ['en','fr']] for r in rows]
   means=[sum(c[i] for c in costs)/len(costs) for i in range(2)];g=gini(means);assert abs(g-gini_sorted(means))<1e-12
   details['datasets'][split]={'n':len(rows),'mean_tokens':means,'gini':g,'worst_language':['en','fr'][means.index(max(means))],'worst_cost':max(means),'sum_language_means':sum(means),'paired_costs':costs,'mean_sentence_gini':sum(gini(c) for c in costs)/len(costs)}
  out[arm]=details
 assert len({v['merges'] for v in out.values()})==1,'unequal realized merges'
 assert len({v['vocab'] for v in out.values()})==1,'unequal realized vocabulary'
 result={'validation':validation,'arms':out,'notes':'Pilot results; contiguous Books sample, no independent-book uncertainty claim. tico.test is now exposed pilot; remaining official test rows reserved.'}
 (P/'runs/evaluation_v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({a:{'vocab':v['vocab'],'scores':{s:{k:d[k] for k in ['n','mean_tokens','gini']} for s,d in v['datasets'].items()}} for a,v in out.items()},indent=2))
