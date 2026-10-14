"""Independent full-coordinate Cartesian relation; needs a future native operator export.
This is not a concrete-state transition oracle or an efficiency benchmark.
"""
import collections,json,pathlib,argparse
from audit_r008_split_witness_v2 import graphs

def load_operators(path):
 meta=None;ops={};pre={};effects={}
 for line in pathlib.Path(path).read_text().splitlines():
  tag,*q=line.split();q=list(map(int,q))
  if tag=='OPS':assert meta is None and len(q)==2;meta=tuple(q)
  elif tag=='OP':
   i,redundant,cost=q;assert i not in ops and redundant in (0,1) and cost>=0;ops[i]={'redundant':bool(redundant),'cost':cost}
  elif tag=='P':
   i,v,size,*members=q;assert (i,v) not in pre and size>0 and members==sorted(set(members)) and all(0<=x<size for x in members);pre[i,v]=(size,sum(1<<x for x in members))
  elif tag=='F':
   i,v,e=q;assert (i,v) not in effects;effects[i,v]=e
  else:raise AssertionError('Unknown operator row')
 assert meta and set(ops)==set(range(meta[0]))
 nops,nv=meta;universe=None
 for i in range(nops):
  assert {(a,v) for a,v in pre if a==i}=={(i,v) for v in range(nv)} and {(a,v) for a,v in effects if a==i}=={(i,v) for v in range(nv)}
  sizes=tuple(pre[i,v][0] for v in range(nv))
  if universe is None:universe=sizes
  else:assert universe==sizes
  assert all(-1<=effects[i,v]<sizes[v] for v in range(nv))
  ops[i].update(pre=tuple(pre[i,v][1] for v in range(nv)),effects=tuple(effects[i,v] for v in range(nv)))
 return universe,ops

def applicable(src,empty,op):
 return not empty and not op['redundant'] and all(a&b for a,b in zip(src,op['pre']))
def reachable(src,dst,empty_target,op):
 if empty_target:return False
 return all((dst[v]&(1<<eff)) if eff>=0 else (src[v]&op['pre'][v]&dst[v]) for v,eff in enumerate(op['effects']))
def relation(src,dst,empty_src,empty_dst,op):return applicable(src,empty_src,op) and reachable(src,dst,empty_dst,op)

def refine_reference(old,domains,empty,parent,children,ops):
 expected=collections.Counter();calls=0
 for (s,op,t),m in old.items():
  if s!=parent and t!=parent:expected[s,op,t]+=m;continue
  for source in children if s==parent else [s]:
   for target in children if t==parent else [t]:
    calls+=1
    if relation(domains[source],domains[target],empty[source],empty[target],ops[op]):expected[source,op,target]+=m
 return expected,calls

def audit(trace,operators,expected_states):
 universe,ops=load_operators(operators);last=None;nlast=0;steps=[]
 for h,rows in graphs(trace):
  kind,n,p,c1,c2,var=h
  if kind not in {'initial','post_refine'}:continue
  assert dict(rows['C'])=={i:o['cost'] for i,o in ops.items()}
  dd={(s,v):(size,tuple(vals)) for s,v,size,*vals in rows['V']};domains={s:tuple(sum(1<<x for x in dd[s,v][1]) for v in range(len(universe))) for s in range(n)};empty=dict(rows['E'])
  assert all(tuple(dd[s,v][0] for v in range(len(universe)))==universe for s in range(n))
  actual=collections.Counter((s,o,t) for s,o,t,pos in rows['O']);actual.update((s,o,s) for s,o,pos in rows['L'])
  if last is None:
   assert kind=='initial' and n==1
   expected=collections.Counter({(0,o,0):1 for o in ops if relation(domains[0],domains[0],empty[0],empty[0],ops[o])});calls=len(ops)
  else:
   assert n==nlast+1 and {c1,c2}=={p,n-1}
   old_domains,old_empty,old_graph=last
   assert all((domains[c][v]&~old_domains[p][v])==0 for c in (c1,c2) for v in range(len(universe)))
   if old_empty[p]:assert empty[c1] and empty[c2],'spurious parent revived'
   for s in range(n-1):
    if s!=p:assert domains[s]==old_domains[s] and empty[s]==old_empty[s]
   expected,calls=refine_reference(old_graph,domains,empty,p,[c1,c2],ops)
  assert expected==actual,{'states':n,'missing':list((expected-actual).items())[:10],'extra':list((actual-expected).items())[:10]}
  steps.append({'states':n,'predicate_candidates':calls,'triples':sum(actual.values())});last=(domains,empty,actual);nlast=n
 assert nlast==expected_states and len(steps)==expected_states
 return {'valid':True,'steps':steps,'scope':'Declared Cartesian predicate relation from exported converted operators, base and shrinking-domain induction. Not concrete transition feasibility, goal-classification proof, efficiency or novelty.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--operators',required=True);p.add_argument('--expected-states',type=int,required=True);p.add_argument('--output',required=True);a=p.parse_args()
 try:r=audit(a.trace,a.operators,a.expected_states)
 except Exception as e:r={'valid':False,'error_type':type(e).__name__,'error':str(e)}
 pathlib.Path(a.output).write_text(json.dumps(r,indent=2)+'\n');raise SystemExit(0 if r['valid'] else 1)
