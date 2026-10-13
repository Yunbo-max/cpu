"""Read native TSV without touching planner state; independently reconstruct exact graph/distances."""
import argparse,collections,json,pathlib,heapq,hashlib,sys
p=argparse.ArgumentParser();p.add_argument('--expected-states',type=int,required=True);p.add_argument('--input',required=True);p.add_argument('--peer');p.add_argument('--output',required=True);a=p.parse_args()
def audit(path):
 rows=collections.defaultdict(list)
 for line in pathlib.Path(path).read_text().splitlines():
  q=line.split();assert q and q[0] in {'META','C','G','D','V','O','I','L'},'Unknown/malformed row';rows[q[0]].append(tuple(map(int,q[1:])))
 assert len(rows['META'])==1 and len(rows['META'][0])==5
 n,init,storededges,storedloops,inf=rows['META'][0];assert n==a.expected_states and n>0 and 0<=init<n
 costs=dict(rows['C']);assert len(costs)==len(rows['C']) and set(costs)==set(range(len(costs))) and all(c>=0 for c in costs.values())
 goals=sorted(x[0] for x in rows['G']);assert len(set(goals))==len(goals) and all(0<=x<n for x in goals)
 distances={x[0]:x[1:] for x in rows['D']};assert len(distances)==n==len(rows['D']) and set(distances)==set(range(n)) and all(len(x)==3 for x in distances.values())
 domains={(x[0],x[1]):x[2:] for x in rows['V']};assert len(domains)==len(rows['V']);var_counts=collections.Counter(s for s,v in domains);nv={s:var_counts[s] for s in range(n)};assert len(set(nv.values()))==1 and next(iter(nv.values()))>0
 for (s,v),values in domains.items():
  size,*members=values;assert 0<=s<n and v in range(nv[s]) and members==sorted(set(members)) and all(0<=x<size for x in members)
 for key in ['O','I']:
  assert all(len(x)==4 and 0<=x[0]<n and x[1] in costs and 0<=x[2]<n and x[3]>=0 for x in rows[key])
  positions=collections.defaultdict(list)
  for source,op,target,pos in rows[key]:positions[source].append(pos)
  for source in range(n):assert sorted(positions[source])==list(range(len(positions[source])))
 assert all(len(x)==3 and 0<=x[0]<n and x[1] in costs for x in rows['L'])
 positions=collections.defaultdict(list)
 for source,op,pos in rows['L']:positions[source].append(pos)
 for source in range(n):assert sorted(positions[source])==list(range(len(positions[source])))
 out=collections.Counter((s,op,t) for s,op,t,pos in rows['O']);incoming=collections.Counter((src,op,dst) for dst,op,src,pos in rows['I']);loops=collections.Counter((s,op) for s,op,pos in rows['L'])
 check={'mirror_multiset_exact':out==incoming,'stored_non_loop_count':storededges==sum(out.values())==len(rows['I']),'stored_loop_count':storedloops==sum(loops.values())}
 zero=any(c==0 for c in costs.values());weight={op:inf if c==2147483647 else ((1 if c==0 else c<<32) if zero else c) for op,c in costs.items()}
 forward=[[] for _ in range(n)];reverse=[[] for _ in range(n)]
 for src,op,dst in out:forward[src].append((dst,weight[op]));reverse[dst].append((src,weight[op]))
 def dijkstra(adj,start):
  dist=[inf]*n;heap=[]
  for x in start:dist[x]=0;heapq.heappush(heap,(0,x))
  while heap:
   value,s=heapq.heappop(heap)
   if value!=dist[s]:continue
   for target,w in adj[s]:
    candidate=inf if w==inf else value+w
    assert candidate<=inf,'64bit overflow'
    if candidate<dist[target]:dist[target]=candidate;heapq.heappush(heap,(candidate,target))
  return dist
 frominit=dijkstra(forward,[init]);togoal=dijkstra(reverse,goals)
 check['init_shortest_paths_exact']=all(distances[s][0]==frominit[s] for s in range(n));check['goal_shortest_paths_exact']=all(distances[s][1]==togoal[s] for s in range(n))
 canonical={'states':n,'initial':init,'goals':goals,'operator_costs':sorted(costs.items()),'domains':sorted((s,v,*values) for (s,v),values in domains.items()),'state_empty_markers':[(s,distances[s][2]) for s in range(n)],'outgoing_multiset':sorted((*t,m) for t,m in out.items()),'incoming_multiset':sorted((*t,m) for t,m in incoming.items()),'loop_multiset':sorted((*t,m) for t,m in loops.items()),'ordered_outgoing':sorted(rows['O'],key=lambda x:(x[0],x[3])),'ordered_incoming':sorted(rows['I'],key=lambda x:(x[0],x[3])),'ordered_loops':sorted(rows['L'],key=lambda x:(x[0],x[2])),'native_distances':sorted(rows['D']),'reference_init_distances':frominit,'reference_goal_distances':togoal,'inf_marker':inf}
 return {'input':str(path),'input_sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),'checks':check,'valid':all(check.values()),'canonical':canonical,'summary':{'states':n,'edges_with_multiplicity':sum(out.values()),'distinct_edges':len(out),'loops_with_multiplicity':sum(loops.values()),'variables_per_state':nv[0],'zero_cost_encoding':zero,'unreachable_from_init':frominit.count(inf),'unreachable_to_goal':togoal.count(inf)}}
try:
 first=audit(a.input);result={'scope':'Exact caller-declared final-state native snapshot only; no every-step equivalence or timing claim','first':first,'valid':first['valid']}
 if a.peer:
  peer=audit(a.peer);result['peer']=peer;result['exact_peer_checks']={k:first['canonical'][k]==peer['canonical'][k] for k in first['canonical']};result['valid']=first['valid'] and peer['valid'] and all(result['exact_peer_checks'].values())
except Exception as e:result={'valid':False,'error_type':type(e).__name__,'error':str(e),'scope':'Invalid/incomplete graph audit; no correctness conclusion'}
pathlib.Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['first','peer']}));print(json.dumps(result.get('first',{}).get('summary',{})));sys.exit(0 if result['valid'] else 24)
