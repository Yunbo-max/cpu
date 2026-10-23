#!/usr/bin/env python3
"""Reproducer for R008 synthetic fault mechanisms; no ML inference."""
import itertools
import json
import networkx as nx

def F(g):
    return int(nx.maximum_flow_value(g, "s", "t", capacity="capacity"))

def indexed(bits):
    k=len(bits); g=nx.DiGraph()
    for i,x in enumerate(bits):
        g.add_edge("s",str(i),capacity=1+x)
        g.add_edge(str(i),"t",capacity=k+2)
    g.add_edge("s","spare",capacity=1+k-sum(bits))
    g.add_edge("spare","t",capacity=k+2)
    return g
vectors=set();restricted=set()
for bits in itertools.product((0,1),repeat=8):
    g=indexed(bits);assert F(g)==17
    row=[]
    for i in range(8):
        h=g.copy();h.remove_edge("s",str(i))
        v=F(h);assert v==16-bits[i];row.append(v)
    vectors.add(tuple(row));restricted.add(tuple(row[:2]))
assert len(vectors)==256 and len(restricted)==4

def higher(extra):
    g=nx.DiGraph();g.add_edge("s","hub",capacity=1)
    for i in range(4+extra):
        g.add_edge("hub",str(i),capacity=1)
        g.add_edge(str(i),"t",capacity=1)
    return g
a,b=higher(0),higher(1)
for k in range(4):
    for ids in itertools.combinations(range(4),k):
        for g in (a,b):
            h=g.copy()
            for i in ids:h.remove_edge("hub",str(i))
            assert F(h)==1
all_four=[]
for g in (a,b):
    h=g.copy()
    for i in range(4):h.remove_edge("hub",str(i))
    all_four.append(F(h))
assert all_four==[0,1]

def named(swap):
    g=nx.DiGraph()
    for n,c in (("p",1),("q",2)):
        g.add_edge("s",n,capacity=(3-c if swap else c))
        g.add_edge(n,"t",capacity=3)
    return g
a,b=named(False),named(True)
assert nx.is_isomorphic(a,b,edge_match=lambda x,y:x["capacity"]==y["capacity"])
q=[]
for g in (a,b):
    assert F(g)==3
    h=g.copy();h.remove_edge("s","p");q.append(F(h))
assert q==[2,1]
print(json.dumps({"family":256,"all_fault_queries":2048,
  "all_response_patterns":256,"restricted_patterns":4,
  "low_order_masks":15,"four_failure_flows":all_four,
  "named_edge_responses":q,"networkx":nx.__version__},indent=2))
