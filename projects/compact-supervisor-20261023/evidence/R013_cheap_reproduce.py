#!/usr/bin/env python3
"""R013 two independent CPU micro-witnesses, source-path-equivalent but not an import of TabKG.
Requires numpy, pandas, networkx. No API, GPU, downloading, or model.
"""
import itertools
import json
import math
import time
import numpy as np
import pandas as pd
import networkx as nx

start=time.process_time()
def encoding(Y):
    df=pd.DataFrame({"region":["a","a","b","b"],"code":Y})
    # Exact group FD validation expression from pinned TabKG source:
    score=float((df.groupby("region")["code"].nunique()==1).mean())
    assert score==1.0
    # Exact action on the single-edge acyclic case in pinned compression path:
    compressed=df[["region"]].to_csv(index=False)
    descriptor={"code":{"sources":["region"],"type":"hierarchical","rule":""}}
    return compressed,json.dumps(descriptor,sort_keys=True),score

y0=[0,0,1,1]; y1=[1,1,0,0]
assert all(a!=b for a,b in zip(y0,y1))
assert encoding(y0)==encoding(y1)

# Exhaust 2^K deterministic function assignments from K source groups:
K=5
result_map={}
for vals in itertools.product((0,1),repeat=K):
    X=list(itertools.chain.from_iterable([[str(j)]*3 for j in range(K)]))
    Y=list(itertools.chain.from_iterable([[vals[j]]*3 for j in range(K)]))
    df=pd.DataFrame({"X":X,"Y":Y})
    score=float((df.groupby("X")["Y"].nunique()==1).mean())
    assert score==1.0
    key=(df[["X"]].to_csv(index=False),json.dumps({"Y":{"sources":["X"],"type":"hierarchical","rule":""}},sort_keys=True),score)
    result_map.setdefault(key,0)
    result_map[key]+=1
assert len(result_map)==1 and next(iter(result_map.values()))==32

# Unit thermal constraints and susceptance; compare transport maxflow to DC:
grid=nx.DiGraph()
for u,v in ((0,1),(1,2),(0,2)):
    grid.add_edge(u,v,capacity=1)
    grid.add_edge(v,u,capacity=1)
transport=nx.maximum_flow_value(grid,0,2)
theta=np.linalg.solve(np.array([[2.,-1.],[-1.,2.]]),np.array([1.,0.]))
pot=np.array([theta[0],theta[1],0.])
unit_flows={f"{u}-{v}":float(pot[u]-pot[v]) for u,v in ((0,1),(1,2),(0,2))}
dc_limit=min(1/abs(x) for x in unit_flows.values() if abs(x)>1e-12)
grid.remove_edge(0,2)
grid.remove_edge(2,0)
assert transport==2 and abs(dc_limit-1.5)<1e-12
assert nx.maximum_flow_value(grid,0,2)==1
output={
  "G1":{"transport_before":transport,"dc_before":dc_limit,"transport_after":1,"dc_after":1,
   "transport_loss":1,"dc_loss":.5,"unit_dc_line_flows":unit_flows},
  "T1":{"FD_score_both":1.0,"two_swapped_tables_same_CRKG_save_pair":True,"K":K,
   "q":2,"valid_mappings":32,"distinct_save_artifacts":len(result_map),"missing_mapping_bits":5},
  "executed_original_TabKG_package":False,
  "cpu_process_seconds":time.process_time()-start
}
print(json.dumps(output,indent=2,sort_keys=True))
