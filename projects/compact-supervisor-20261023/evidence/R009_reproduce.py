#!/usr/bin/env python3
"""R009 compact deterministic validation of fault-response information checks."""
from itertools import product, combinations
import random, json
import networkx as nx

def risk(p):
    strings=list(product((0,1),repeat=3))
    best=2
    for assignment in product((0,1),repeat=8):
        D=0
        for y in (0,1):
            xs=[x for x,z in zip(strings,assignment) if z==y]
            for j,w in enumerate(p):
                ones=sum(x[j] for x in xs)
                D+=w*min(ones,len(xs)-ones)/8
        best=min(best,D)
    return best
assert abs(risk((1/3,)*3)-.25)<1e-12
assert abs(risk((.8,.15,.05))-.1)<1e-12

def flow(G):
    return int(nx.maximum_flow_value(G,'s','t',capacity='capacity'))
def cuts(G):
    inner=[x for x in G if x not in ('s','t')]
    for mask in range(1<<len(inner)):
        S={'s'}|{inner[j] for j in range(len(inner)) if mask&(1<<j)}
        rows=[(u,v,d['capacity']) for u,v,d in G.edges(data=True) if u in S and v not in S]
        yield sum(c for _,_,c in rows),rows
r=random.Random(20261023);tested=0
for seed in range(16):
    G=nx.DiGraph();G.add_nodes_from(['s','t','a','b','c','d'])
    for u,v in zip(['s','a','b','c','d'],['a','b','c','d','t']):
        G.add_edge(u,v,capacity=r.randint(1,5))
    for u in G.nodes:
        for v in G.nodes:
            if u!=v and v!='s' and u!='t' and not G.has_edge(u,v) and r.random()<.27:
                G.add_edge(u,v,capacity=r.randint(1,5))
    original=flow(G); allcuts=list(cuts(G)); assert min(x for x,_ in allcuts)==original
    edges=list(G.edges)[:4]
    for k in range(5):
        for subset in combinations(edges,k):
            H=G.copy(); H.remove_edges_from(subset)
            drop=max(sum(c for u,v,c in rows if (u,v) in subset)-(value-original) for value,rows in allcuts)
            assert flow(H)==original-drop
            tested+=1
assert tested==256
print(json.dumps({'G1_uniform_one_bit_opt':risk((1/3,)*3),
   'G1_skew_one_bit_opt':risk((.8,.15,.05)),
   'G2_cut_slack_random_queries':tested,
   'G3_named_mapping_bit_needed_on_the_saved_two_branch_toy':1},
  indent=2))
