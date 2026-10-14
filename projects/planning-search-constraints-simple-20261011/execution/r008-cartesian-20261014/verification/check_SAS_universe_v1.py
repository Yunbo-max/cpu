"""Independent raw SAS identity/domain/count/cost crosswalk, not converted-precondition equality."""
import pathlib,json,sys,hashlib
B=pathlib.Path(__file__).resolve().parent;R=B/'project/windows/W0005';sys.path.insert(0,str(R/'scripts'));from r008_cartesian_reference_v1 import load_operators
cfg=json.loads((R/'plans/configs/R006-fixed1000-blocksworld-p05-states_ops-v1.json').read_text());sas=R/cfg['sas'];lines=sas.read_text().splitlines();sizes=[];costs=[];names=[];i=0
while i<len(lines):
 if lines[i]=='begin_variable':
  size=int(lines[i+3]);assert lines[i+4+size]=='end_variable';sizes.append(size);i+=size+5
 elif lines[i]=='begin_operator':
  end=lines.index('end_operator',i+1);names.append(lines[i+1]);costs.append(int(lines[end-1]));i=end+1
 else:i+=1
universe,ops=load_operators(R/'results/R008-native-operator-object-export-W5-v2/operators.tsv');assert tuple(sizes)==universe and len(costs)==len(ops);assert {i:c for i,c in enumerate(costs)}=={i:o['cost'] for i,o in ops.items()}
rng=R/'vendor/scorpion_r008_observer_v1/src/search/utils/rng_options.cc';txt=rng.read_text();assert 'make_shared<utils::RandomNumberGenerator>(2011)' in txt
result={'valid':True,'SAS_sha256':hashlib.sha256(sas.read_bytes()).hexdigest(),'variable_domain_sizes':sizes,'num_operators':len(costs),'all_operator_ID_costs_match_native_converted_export':True,'operator_names_order_sha256':hashlib.sha256(json.dumps(names).encode()).hexdigest(),'default_rng_source_sha256':hashlib.sha256(rng.read_bytes()).hexdigest(),'default_rng_seed':2011,'scope':'Independent raw SAS variable capacities/operator count/ordered cost crosswalk and exact primary default RNG source. Not independent verification of AC3 conversion, converted preconditions/effects, or concrete action applicability.'}
p=B/'r008-relation-publication/SAS-universe-crosswalk-v1.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
