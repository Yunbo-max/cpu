"""Finite predicate diagnostic, not a planner run, benchmark, speed test or proof of native trajectories."""
import itertools,json,pathlib,time,hashlib,resource
resource.setrlimit(resource.RLIMIT_AS,(128*1024**2,128*1024**2))
R=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple/windows/W0004');S=R/'vendor/scorpion_cpu_clock_coarse_r006_v1/src/search';start=time.monotonic();cpu=time.process_time();before=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());assert before+30000000<7800000000,'LowRAM diagnostic admission unavailable'
full=(0,1);states=list(itertools.product((1,2,3),repeat=2));pres=states;effects=list(itertools.product((-1,0,1),repeat=2));counts={'incoming_comparisons':0,'outgoing_comparisons':0,'loop_comparisons':0,'proper_split_cases':0};mismatches=[]
def empty(c):return any(x==0 for x in c)
def app(c,p,coords):return not empty(c) and all(c[i]&p[i] for i in coords)
def reach(c,w,p,e,coords):return not empty(w) and all((w[i]&(1<<e[i])) if e[i]!=-1 else (w[i]&c[i]&p[i]) for i in coords)
def valid(c,w,p,e,coords):return bool(app(c,p,coords) and reach(c,w,p,e,coords))
def subsets(x):return [m for m in range(4) if m&~x==0]
for parent in states:
 for split in full:
  if parent[split]!=3:continue
  other=1-split
  for direction in (1,2):
   for a,b in itertools.product(subsets(parent[other]),repeat=2):
    c1=list(parent);c2=list(parent);c1[split]=direction;c2[split]=3^direction;c1[other]=a;c2[other]=b;c1=tuple(c1);c2=tuple(c2)
    changed=tuple(i for i in full if parent[i]!=c1[i] or parent[i]!=c2[i]);assert split in changed;counts['proper_split_cases']+=1
    for pre,eff in itertools.product(pres,effects):
     for neighbor in states:
      if valid(neighbor,parent,pre,eff,full):
       for child in (c1,c2):
        counts['incoming_comparisons']+=1
        if bool(reach(neighbor,child,pre,eff,full))!=bool(reach(neighbor,child,pre,eff,changed)):mismatches.append(['incoming',parent,child,neighbor,pre,eff,changed])
      if valid(parent,neighbor,pre,eff,full):
       for child in (c1,c2):
        counts['outgoing_comparisons']+=1
        if valid(child,neighbor,pre,eff,full)!=valid(child,neighbor,pre,eff,changed):mismatches.append(['outgoing',parent,child,neighbor,pre,eff,changed])
     if valid(parent,parent,pre,eff,full):
      for src,dst in itertools.product((c1,c2),repeat=2):
       counts['loop_comparisons']+=1
       if valid(src,dst,pre,eff,full)!=valid(src,dst,pre,eff,changed):mismatches.append(['loop',parent,src,dst,pre,eff,changed])
    assert time.monotonic()-start<45,'Bounded predicate diagnostic timeout'
# A bad omitted-coordinate certificate yields a real logical counterexample.
examples=[]
for label,parent,child,neighbor,pre,eff,changed in [('missing_parent_certificate',(3,1),(1,1),(3,2),(3,2),(-1,-1),(0,)),('omitted_changed_coordinate',(3,3),(1,1),(3,3),(3,2),(-1,-1),(0,))]:
 f=valid(child,neighbor,pre,eff,full);d=valid(child,neighbor,pre,eff,changed);assert f!=d;examples.append({'condition_removed':label,'parent':parent,'child':child,'target':neighbor,'pre':pre,'effect':eff,'claimed_changed':changed,'old_edge_full_valid':valid(parent,neighbor,pre,eff,full),'full_predicate':f,'restricted_predicate':d})
source={p:hashlib.sha256((S/p).read_bytes()).hexdigest() for p in ['cartesian_abstractions/abstraction.cc','cartesian_abstractions/transition_system.cc','cartesian_abstractions/cegar.cc','task_utils/cartesian_state.cc','task_utils/cartesian_set.cc','task_utils/disambiguated_operator.h']};result={'scope':'Finite2variable/2value Cartesian predicate enumeration under certified old-edge and all-changed-coordinate assumptions. Not native graph/audit/VAL/timing, not public benchmark, not new algorithm or novelty proof. Existing frozen native source unchanged.','source_sha256':source,'counts':counts,'mismatches':mismatches,'conditional_enumeration_consistent':not mismatches,'necessity_counterexamples':examples,'wall_seconds':time.monotonic()-start,'process_cpu_seconds':time.process_time()-cpu,'shared_before':before,'shared_after':int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text()),'peak_process_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024};out=R/'results/R006-changed-coordinate-lemma-diagnostic-v1.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','necessity_counterexamples']}));assert not mismatches
