"""Finish evaluation of retained native run. Never invokes the planner or repeats trajectory audit."""
import pathlib,json,hashlib,subprocess,sys,os,re,zstandard
r=pathlib.Path(__file__).resolve().parents[1];original=r/'results/R008-split-witness-native-W5-v2';out=r/'results/R008-retained-witness-completion-W5-v1';out.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
a=json.loads((original/'trajectory-audit.json').read_text());assert a['valid'] and a['post_refine_count']==999 and a['sp_updated_count']==999 and a['snapshot_count']==2000
raw=(original/'command/stdout.log').read_text();assert 'Total number of Cartesian states: 1000' in raw and 'Plan cost: 24' in raw
metrics=json.loads((original/'command/metrics.json').read_text());assert metrics['exit_code']==0
assert sha(original/'final-graph.tsv')=='6d8625157b472ac3c372bfda6afc6124f1468c70a8e6cf8a0e6df2926bb39d3a'
subprocess.run([sys.executable,str(r/'scripts/audit_r007_graph_linear_v1.py'),'--input',str(original/'final-graph.tsv'),'--peer',str(r/'results/R006-graph-export-coarse-v2/graph.tsv'),'--expected-states','1000','--output',str(out/'final-audit.json')],check=True,timeout=40)
v=r/'vendor/val/builds/release/bin/Validate';env=dict(os.environ);env['LD_LIBRARY_PATH']=str(v.parent);val=subprocess.run([str(v),str(r/'data/autoscale21.11/blocksworld/domain.pddl'),str(r/'data/autoscale21.11/blocksworld/p05.pddl'),str(original/'sas_plan')],env=env,capture_output=True,text=True,timeout=10);(out/'VAL.stdout.log').write_text(val.stdout);(out/'VAL.stderr.log').write_text(val.stderr);assert val.returncode==0 and 'Plan valid' in val.stdout
parent=r/'results/R006-overhead-r1-coarse-v1';old=(parent/'command/stdout.log').read_text()
def work(t):return {name:int(re.search(pattern,t).group(1)) for name,pattern in [('expanded',r'Expanded (\d+) state'),('evaluated',r'Evaluated (\d+) state'),('cost',r'Plan cost: (\d+)')]}
assert work(raw)==work(old);assert (original/'sas_plan').read_bytes()==(parent/'sas_plan').read_bytes()
source=r/'data/R008-observer-source-manifest-v1.json';binary=r/'results/R008-executable-preparation-v1/downward';witness=original/'split-witness.tsv';compressed=out/'split-witness.tsv.zst'
with witness.open('rb') as src,compressed.open('wb') as dst:zstandard.ZstdCompressor(level=6).copy_stream(src,dst)
result={'valid':True,'native_run_reused':True,'planner_invoked_in_this_task':False,'original_native_task':'R008-split-witness-native-W5-v2','original_native_exit_code':0,'original_wrapper_exit_failed_at_final_auditor_argument_not_solver':True,'trajectory_audit_sha256':sha(original/'trajectory-audit.json'),'trajectory_audit_source_sha256':sha(r/'scripts/audit_r008_split_witness_v2.py'),'final_audit_valid':json.loads((out/'final-audit.json').read_text())['valid'],'VAL_valid':True,'work_exact':work(raw),'plan_sha256':sha(original/'sas_plan'),'original_final_graph_sha256':sha(original/'final-graph.tsv'),'source_manifest_sha256':sha(source),'binary_sha256':sha(binary),'SAS_sha256':sha(r/'results/R005-profile-blocksworld-p05-states_ops-v1/output.sas'),'post_refine_count':a['post_refine_count'],'snapshot_count':a['snapshot_count'],'SP_updated_count':a['sp_updated_count'],'excess_reporting_splits':a['excess_reporting_splits'],'excess_reported_coordinates':a['excess_reported_coordinates'],'reported_coordinates':a['reported_coordinates'],'actually_changed_coordinates':a['actually_changed_coordinates'],'raw_witness_sha256':sha(witness),'raw_witness_bytes':witness.stat().st_size,'compressed_witness_sha256':sha(compressed),'compressed_witness_bytes':compressed.stat().st_size,'scope':'One exposed exact1000 native diagnostic, 999 actual committed splits, independent graph/domain/order/mirror checks and Dijkstra, native SP999stable milestones+final, original final graph/work/plan and VAL. Not independent operator-applicability oracle, no algorithm comparison/efficiency/novelty. Observer-inclusive timings ineligible. Failed wrapper remains failed, final evaluation repaired as separate no-planner task.'}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
