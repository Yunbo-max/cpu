"""Small consequential relation fixtures, not new native benchmark cases."""
import collections,json,pathlib
from r008_cartesian_reference_v1 import relation,refine_reference
op={'pre':(3,),'effects':(1,),'redundant':False,'cost':1};none={'pre':(3,),'effects':(-1,),'redundant':False,'cost':1}
checks={}
checks['fixed-effect-requires-target']=relation((1,),(2,),0,0,op) and not relation((1,),(1,),0,0,op)
checks['identity-effect-intersection']=relation((1,),(1,),0,0,none) and not relation((1,),(2,),0,0,none)
checks['spurious-source-and-target-rejected']=not relation((3,),(3,),1,0,op) and not relation((3,),(3,),0,1,op)
checks['redundant-op-rejected']=not relation((3,),(3,),0,0,{**op,'redundant':True})
checks['precondition-disjoint-rejected']=not relation((1,),(2,),0,0,{**op,'pre':(2,)})
checks['target-dependent-no-cache']=relation((1,),(2,),0,0,op)!=relation((1,),(1,),0,0,op)
old=collections.Counter({(0,0,0):2});d={0:(1,),1:(2,)};e={0:0,1:0};actual,calls=refine_reference(old,d,e,0,[0,1],{0:op});expected=collections.Counter({(0,0,1):2,(1,0,1):2})
checks['split-cross-and-loop-multiplicity']=actual==expected and calls==4
checks['missing-edge-detected']=actual!=collections.Counter({(1,0,1):2})
checks['extra-inapplicable-edge-detected']=actual!=(expected+collections.Counter({(0,0,0):1}))
assert all(checks.values());r=pathlib.Path(__file__).resolve().parents[1];(r/'evidence/R008-cartesian-reference-fixtures-v1.json').write_text(json.dumps({'valid':True,'checks':checks,'scope':'Finite implementation/evaluator fixtures only; native operator export and full native trace comparison not executed'},indent=2)+'\n');print(json.dumps(checks))
