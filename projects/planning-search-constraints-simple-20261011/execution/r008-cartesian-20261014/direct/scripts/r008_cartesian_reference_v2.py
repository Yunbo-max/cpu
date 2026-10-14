"""Fail-closed domain schema plus independent full-coordinate relation.
Structural/phase/native-distance evidence is composed via exact trace/receipt hashes,
not silently inferred from this predicate audit. No concrete-state planning claim.
"""
import collections,hashlib,json
from audit_r008_split_witness_v2 import graphs
from r008_cartesian_reference_v1 import load_operators,relation,refine_reference

def canonical_domains(rows,n,universe):
 nv=len(universe);assert n>0
 assert all(len(x)==2 for x in rows['E'])
 empty=dict(rows['E']);assert len(empty)==len(rows['E'])==n and set(empty)==set(range(n)) and set(empty.values())<={0,1}
 dd={}
 for row in rows['V']:
  assert len(row)>=3
  s,v,size,*values=row
  assert 0<=s<n and 0<=v<nv and size==universe[v]
  assert values==sorted(set(values)) and all(0<=x<size for x in values),'noncanonical domain members'
  assert (s,v) not in dd,'duplicate domain key'
  if not empty[s]:assert values,'nonspurious state has empty coordinate'
  dd[s,v]=sum(1<<x for x in values)
 assert set(dd)=={(s,v) for s in range(n) for v in range(nv)},'incomplete domain keys'
 return {s:tuple(dd[s,v] for v in range(nv)) for s in range(n)},empty

def audit(trace,operators,expected_states,snapshot_bindings=None):
 universe,ops=load_operators(operators);assert universe and all(v>0 for v in universe)
 last=None;nlast=0;steps=[];snapshot_count=0
 for h,rows in graphs(trace):
  kind,n,p,c1,c2,var=h
  assert kind in {'initial','post_refine','sp_updated','final'}
  # Every observed snapshot is bound to the previous independent structural audit.
  if snapshot_bindings is not None:
   assert snapshot_count<len(snapshot_bindings),'extra snapshot'
   b=snapshot_bindings[snapshot_count];canonical={k:rows[k] for k in ['META','C','G','E','V','O','I','L']}
   assert b['kind']==kind and b['states']==n
   assert hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()==b['graph_sha256'],'unbound graph snapshot'
  snapshot_count+=1
  if kind not in {'initial','post_refine'}:continue
  assert all(len(x)==2 for x in rows['C']) and len(rows['C'])==len(ops)
  assert dict(rows['C'])=={i:o['cost'] for i,o in ops.items()}
  domains,empty=canonical_domains(rows,n,universe)
  actual=collections.Counter()
  for row in rows['O']:
   assert len(row)==4;s,o,t,pos=row;assert 0<=s<n and 0<=t<n and s!=t and o in ops and pos>=0;actual[s,o,t]+=1
  for row in rows['L']:
   assert len(row)==3;s,o,pos=row;assert 0<=s<n and o in ops and pos>=0;actual[s,o,s]+=1
  if last is None:
   assert kind=='initial' and n==1
   expected=collections.Counter({(0,o,0):1 for o in ops if relation(domains[0],domains[0],empty[0],empty[0],ops[o])});calls=len(ops)
  else:
   assert kind=='post_refine' and n==nlast+1 and {c1,c2}=={p,n-1} and 0<=p<n-1 and 0<=var<len(universe)
   old_domains,old_empty,old_graph=last
   assert all((domains[c][v]&~old_domains[p][v])==0 for c in (c1,c2) for v in range(len(universe))),'child outside parent'
   if old_empty[p]:assert empty[c1] and empty[c2],'spurious parent revived'
   for s in range(n-1):
    if s!=p:assert domains[s]==old_domains[s] and empty[s]==old_empty[s],'untouched domain changed'
   changed={v for v in range(len(universe)) if any(domains[c][v]!=old_domains[p][v] for c in (c1,c2))}
   assert len(rows['M'])==1;reported=rows['M'][0];assert list(reported)==sorted(set(reported)) and set(reported)<=set(range(len(universe)))
   assert changed<=set(reported),'changed coordinate omitted'
   expected,calls=refine_reference(old_graph,domains,empty,p,[c1,c2],ops)
  assert expected==actual,{'states':n,'missing':list((expected-actual).items())[:10],'extra':list((actual-expected).items())[:10]}
  steps.append({'states':n,'predicate_candidates':calls,'triples':sum(actual.values())});last=(domains,empty,actual);nlast=n
 assert nlast==expected_states and len(steps)==expected_states
 if snapshot_bindings is not None:assert snapshot_count==len(snapshot_bindings),'missing snapshot'
 return {'valid':True,'steps':steps,'relation_snapshots':len(steps),'all_snapshot_bindings_checked':snapshot_count if snapshot_bindings is not None else None,'scope':'Declared full-coordinate Cartesian relation of exported converted operators, complete base and shrinking-domain inherited multiset induction. Composition supplies exact prior structural/phase/distance checks. Not concrete feasibility, goal classification, new-method equivalence, speed or novelty.'}
