#!/usr/bin/env python3
"""R007 reproducible fault-flow counterexample; no ML training."""
from itertools import product, combinations
import json, time
import networkx as nx
m=8; t0=time.process_time()
def graph(bits):
    q=len(bits); G=nx.DiGraph()
    for i,x in enumerate(bits):
        G.add_edge("s",f"p{i}",capacity=1+x)
        G.add_edge(f"p{i}","t",capacity=q+2)
    G.add_edge("s","spare",capacity=1+q-sum(bits))
    G.add_edge("spare","t",capacity=q+2)
    return G
def flow(G):return int(nx.maximum_flow_value(G,"s","t",capacity="capacity"))
responses=set()
for bits in product((0,1),repeat=m):
    G=graph(bits)
    assert flow(G)==2*m+1
    row=[]
    for i in range(m):
        cap=G["s"][f"p{i}"]["capacity"]
        G.remove_edge("s",f"p{i}")
        out=flow(G)
        assert out==2*m-bits[i]
        row.append(out)
        G.add_edge("s",f"p{i}",capacity=cap)
    responses.add(tuple(row))
assert len(responses)==2**m
def branches(extra=0):
    G=nx.DiGraph();G.add_edge("s","hub",capacity=1)
    for i in range(3+extra):
        G.add_edge("hub",f"p{i}",capacity=1)
        G.add_edge(f"p{i}","t",capacity=1)
    return G
A,B=branches(0),branches(1); higher={}
for k in range(4):
    scores=[]
    for subset in combinations(range(3),k):
        pair=[]
        for original in [A,B]:
            G=original.copy()
            for i in subset:G.remove_edge("hub",f"p{i}")
            pair.append(flow(G))
        assert pair==([1,1] if k<3 else [0,1])
        scores.append(pair)
    higher[k]=scores
summary={"networkx":nx.__version__,"m":m,"graphs":2**m,
         "single_failure_queries":(2**m)*m,
         "baseline_flow":2*m+1,"distinct_failure_responses":len(responses),
         "triple_vs_lower_order":higher,
         "measured_cpu_seconds":time.process_time()-t0}
print(json.dumps(summary,indent=2))
