"""Streaming independent structural/domain/distance audit; not an operator semantic oracle."""
import collections,hashlib,heapq,json,pathlib,argparse

def graphs(path):
 header=None;rows=None
 with pathlib.Path(path).open() as f:
  for line in f:
   x=line.split();assert x,'blank row'
   if x[0]=='BEGIN':
    assert header is None and len(x)==7,'nested/malformed BEGIN';header=(x[1],*map(int,x[2:]));rows=collections.defaultdict(list)
   elif x[0]=='END':
    assert header and x[1:]==[header[0],str(header[1])],'incomplete END';yield header,rows;header=rows=None
   else:
    assert header and x[0] in {'META','C','M','G','E','D','V','O','I','L'},'row outside snapshot/unknown'
    rows[x[0]].append(tuple(map(int,x[1:])))
 assert header is None,'truncated snapshot'

def check_graph(header,rows):
 kind,n,parent,c1,c2,var=header
 assert len(rows['META'])==1 and len(rows['META'][0])==5
 count,init,stored,storedloops,inf=rows['META'][0];assert count==n and n>0 and 0<=init<n
 costs=dict(rows['C']);assert len(costs)==len(rows['C']) and set(costs)==set(range(len(costs))) and all(x>=0 for x in costs.values())
 goals=[x[0] for x in rows['G']];assert goals==sorted(set(goals)) and all(0<=s<n for s in goals)
 empty=dict(rows['E']);assert len(empty)==len(rows['E'])==n and set(empty)==set(range(n)) and set(empty.values())<= {0,1}
 domains={(x[0],x[1]):x[2:] for x in rows['V']};assert len(domains)==len(rows['V'])
 variable_counts=collections.Counter(s for s,v in domains);nv=variable_counts[0];assert nv>0 and all(variable_counts[s]==nv for s in range(n))
 for (s,v),d in domains.items():
  size,*values=d;assert 0<=s<n and 0<=v<nv and size>0 and values==sorted(set(values)) and all(0<=x<size for x in values)
  assert size==domains[0,v][0]
  if not empty[s]:assert values,'nonspurious state has empty coordinate'
 for key in ['O','I','L']:
  pos=collections.defaultdict(list)
  for x in rows[key]:
   assert len(x)==(3 if key=='L' else 4) and 0<=x[0]<n and x[1] in costs and x[-1]>=0
   if key!='L':assert 0<=x[2]<n and x[0]!=x[2]
   pos[x[0]].append(x[-1])
  for s in range(n):assert pos[s]==list(range(len(pos[s]))),'adjacency order/position'
 out=collections.Counter((s,op,t) for s,op,t,pos in rows['O']);incoming=collections.Counter((s,op,t) for t,op,s,pos in rows['I']);loops=collections.Counter((s,op) for s,op,pos in rows['L'])
 assert out==incoming,'mirror multiplicity';assert sum(out.values())==stored and sum(loops.values())==storedloops
 zero=any(c==0 for c in costs.values());weights={op:inf if c==2147483647 else ((1 if c==0 else c<<32) if zero else c) for op,c in costs.items()}
 adj=[[] for _ in range(n)];rev=[[] for _ in range(n)]
 for (s,op,t),multiplicity in out.items():adj[s].append((t,weights[op]));rev[t].append((s,weights[op]))
 def dijkstra(graph,starts):
  d=[inf]*n;q=[]
  for s in starts:d[s]=0;heapq.heappush(q,(0,s))
  while q:
   cost,s=heapq.heappop(q)
   if cost!=d[s]:continue
   for t,w in graph[s]:
    nd=inf if w==inf else cost+w;assert nd<=inf,'cost overflow'
    if nd<d[t]:d[t]=nd;heapq.heappush(q,(nd,t))
  return d
 forward=dijkstra(adj,[init]);backward=dijkstra(rev,goals)
 assert kind in {'initial','post_refine','sp_updated','final'}
 if kind in {'sp_updated','final'}:
  distances={x[0]:x[1:] for x in rows['D']};assert len(distances)==len(rows['D'])==n
  assert all(distances[s]==(forward[s],backward[s]) for s in range(n)),'native distance mismatch'
 else:assert not rows['D'],'stale phase native distance supplied'
 canonical={k:rows[k] for k in ['META','C','G','E','V','O','I','L']}
 return {'kind':kind,'states':n,'nonloops':stored,'loops':storedloops,'variables':nv,'unreachable_init':forward.count(inf),'unreachable_goal':backward.count(inf),'topology_sha256':hashlib.sha256(json.dumps({k:v for k,v in canonical.items() if k!='G'},separators=(',',':')).encode()).hexdigest(),'graph_sha256':hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest(),'reference_distances_sha256':hashlib.sha256(json.dumps([forward,backward],separators=(',',':')).encode()).hexdigest(),'native_distances_checked':kind in {'sp_updated','final'}},domains,empty

def audit(path,expected,expected_sp_updates):
 previous=None;last_post=1;last_kind=None;summaries=[];nsp=0;excess=[];fixed=None;sp_started=False
 for h,rows in graphs(path):
  summary,domains,empty=check_graph(h,rows);kind,n,parent,c1,c2,var=h
  universe=(rows["C"],rows["META"][0][-1],tuple(domains[0,v][0] for v in range(summary["variables"])))
  if fixed is None:fixed=universe
  else:assert universe==fixed,"operator costs/INF/domain universe drift"
  if previous is None:assert kind=='initial' and n==1
  elif kind=='initial':raise AssertionError('second abstraction not in frozen scope')
  elif kind=='post_refine':
   assert not sp_started or last_kind=='sp_updated','missing main-loop distance milestone'
   assert n==last_post+1 and {c1,c2}=={parent,n-1} and 0<=parent<n-1 and 0<=var<summary['variables'],'missing/invalid split'
   old=previous[0];oldempty=previous[1];changed=set()
   for v in range(summary['variables']):
    pv=set(old[parent,v][1:]);a=set(domains[c1,v][1:]);b=set(domains[c2,v][1:]);assert a<=pv and b<=pv,'child domain outside parent'
    if v==var:assert not(a&b),'children overlap in split coordinate'
    if a!=pv or b!=pv:changed.add(v)
   assert len(rows['M'])==1;reported=rows['M'][0];assert list(reported)==sorted(set(reported)) and set(reported)<=set(range(summary['variables']))
   assert changed<=set(reported),'changed coordinate omitted'
   for s in range(n-1):
    if s==parent:continue
    assert empty[s]==oldempty[s] and all(domains[s,v]==old[s,v] for v in range(summary['variables'])),'untouched domain changed'
   excess.append({'states':n,'actual_changed':len(changed),'reported':len(reported),'excess':len(set(reported)-changed),'actual_changed_vars':sorted(changed),'reported_vars':list(reported)})
   last_post=n
  else:
   assert n==last_post,'distance milestone before split coverage'
   if kind=='sp_updated':
    assert last_kind=='post_refine','unbound/duplicate SP milestone';nsp+=1;sp_started=True
   elif sp_started:assert last_kind=='sp_updated','missing final main-loop SP milestone'
   assert domains==previous[0] and empty==previous[1],'domain mutation outside real refine'
   assert summary['topology_sha256']==summaries[-1]['topology_sha256'],'topology/order mutation outside refine under NONE'
  summaries.append(summary);previous=(domains,empty);last_kind=kind
 assert nsp==expected_sp_updates,'SP milestone count mismatch'
 assert last_post==expected and last_kind=='final' and len(excess)==expected-1,'incomplete trajectory'
 return {'valid':True,'expected_states':expected,'post_refine_count':len(excess),'initial_count':1,'sp_updated_count':nsp,'snapshot_count':len(summaries),'scope':'Every actual committed refinement in this exposed native trace; independent graph structure/domains/Dijkstra, native SP only at labelled stable milestones. No independent operator applicability or parent-vs-new-algorithm trajectory proof; no performance claim.','snapshots':summaries,'modified_variable_coverage':excess,'excess_reporting_splits':sum(x['excess']>0 for x in excess),'excess_reported_coordinates':sum(x['excess'] for x in excess),'reported_coordinates':sum(x['reported'] for x in excess),'actually_changed_coordinates':sum(x['actual_changed'] for x in excess)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--expected-states',required=True,type=int);p.add_argument('--output',required=True);p.add_argument('--expected-sp-updates',type=int,required=True);a=p.parse_args()
 try:result=audit(a.input,a.expected_states,a.expected_sp_updates)
 except Exception as e:result={'valid':False,'error_type':type(e).__name__,'error':str(e)}
 pathlib.Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['snapshots','modified_variable_coverage']}));raise SystemExit(0 if result['valid'] else 1)
