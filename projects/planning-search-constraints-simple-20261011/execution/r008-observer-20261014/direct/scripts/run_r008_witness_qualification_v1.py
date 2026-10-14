"""Actual native readonly trajectory qualifier; all exports are ineligible timings."""
import pathlib,json,hashlib,subprocess,sys,os,re,zstandard
r=pathlib.Path(__file__).resolve().parents[1];tid='R008-split-witness-native-W5-v1';out=r/'results'/tid;out.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
bp=r/'results/R008-observer-build-W5-v2/build_identity.json';b=json.loads(bp.read_text());binary=r/b['binary'];assert sha(binary)==b['binary_sha256'];mp=r/b['source_manifest'];assert sha(mp)==b['source_manifest_sha256']
for x in json.loads(mp.read_text())['files']:assert sha(r/x['path'])==x['sha256']
cp=r/'plans/configs/R006-fixed1000-blocksworld-p05-states_ops-v1.json';cfg=json.loads(cp.read_text());sas=r/cfg['sas'];assert sha(sas)=='11454e2d4aea5bab34fc39877ed2db950d4252c1a4f14c94ba800267a7be3391'
env=dict(os.environ);env['RSI_SPLIT_WITNESS_PATH']=str(out/'split-witness.tsv');env['RSI_GRAPH_AUDIT_PATH']=str(out/'final-graph.tsv')
cmd=[sys.executable,str(r/'scripts/bounded_command_host_limit_v5.py'),'--cwd',str(out),'--output',str(out/'command'),'--timeout','145','--rss-mb','2800','--address-space-mb','3500','--threads','1','--host-memory-only','--',sys.executable,str(r/'scripts/r006_native_stdin_v1.py'),'--sas',str(sas),'--binary',str(binary),'--search',cfg['search']]
(out/'command-argv.json').write_text(json.dumps(cmd,indent=2)+'\n');rc=subprocess.call(cmd,env=env);assert rc==0,'native failed: '+str(rc)
raw=(out/'command/stdout.log').read_text();assert 'Total number of Cartesian states: 1000' in raw and 'Plan cost: 24' in raw
assert sha(out/'final-graph.tsv')=='6d8625157b472ac3c372bfda6afc6124f1468c70a8e6cf8a0e6df2926bb39d3a','original final graph mismatch'
subprocess.run([sys.executable,str(r/'scripts/audit_r008_split_witness_v2.py'),'--input',str(out/'split-witness.tsv'),'--expected-states','1000','--expected-sp-updates',str(sum(int(re.findall(k+r': (\d+)',raw)[-1]) for k in ['Forward refinements','Backward refinements'])),'--output',str(out/'trajectory-audit.json')],check=True,timeout=300)
subprocess.run([sys.executable,str(r/'scripts/audit_r007_graph_linear_v1.py'),'--input',str(out/'final-graph.tsv'),'--peer',str(r/'results/R006-graph-export-coarse-v2/graph.tsv'),'--expected-states','1000','--expected-sp-updates',str(sum(int(re.findall(k+r': (\d+)',raw)[-1]) for k in ['Forward refinements','Backward refinements'])),'--output',str(out/'final-audit.json')],check=True,timeout=40)
v=r/'vendor/val/builds/release/bin/Validate';env['LD_LIBRARY_PATH']=str(v.parent);val=subprocess.run([str(v),str(r/'data/autoscale21.11/blocksworld/domain.pddl'),str(r/'data/autoscale21.11/blocksworld/p05.pddl'),str(out/'sas_plan')],env=env,capture_output=True,text=True,timeout=10);(out/'VAL.stdout.log').write_text(val.stdout);(out/'VAL.stderr.log').write_text(val.stderr);assert val.returncode==0 and 'Plan valid' in val.stdout
parent=r/'results/R006-overhead-r1-coarse-v1';old=(parent/'command/stdout.log').read_text()
def work(t):
 return {name:int(re.search(pattern,t).group(1)) for name,pattern in [('expanded',r'Expanded (\d+) state'),('evaluated',r'Evaluated (\d+) state'),('cost',r'Plan cost: (\d+)')]}
assert work(raw)==work(old);assert (out/'sas_plan').read_bytes()==(parent/'sas_plan').read_bytes(),'plan mismatch'
a=json.loads((out/'trajectory-audit.json').read_text());result={'valid':True,'native_exit_code':rc,'VAL_valid':True,'work_exact':work(raw),'plan_sha256':sha(out/'sas_plan'),'original_final_graph_sha256':sha(out/'final-graph.tsv'),'source_manifest_sha256':sha(mp),'binary_sha256':sha(binary),'SAS_sha256':sha(sas),'config_sha256':sha(cp),'post_refine_count':a['post_refine_count'],'snapshot_count':a['snapshot_count'],'excess_reporting_splits':a['excess_reporting_splits'],'excess_reported_coordinates':a['excess_reported_coordinates'],'reported_coordinates':a['reported_coordinates'],'actually_changed_coordinates':a['actually_changed_coordinates'],'raw_witness_sha256':sha(out/'split-witness.tsv'),'raw_witness_bytes':(out/'split-witness.tsv').stat().st_size,'scope':'One exposed exact1000 native diagnostic: committed per-split graph invariants and independent Dijkstra, native SP at stable milestones, unchanged final graph/work/plan. No independent operator-applicability oracle, no algorithm comparison/efficiency/novelty claim. Observer-inclusive costs not eligible timing.'}
# Retain original raw trace; compress separate copy for archival, do not delete unique bytes.
with (out/'split-witness.tsv').open('rb') as src,(out/'split-witness.tsv.zst').open('wb') as dst:zstandard.ZstdCompressor(level=6).copy_stream(src,dst)
result['compressed_witness_sha256']=sha(out/'split-witness.tsv.zst');result['compressed_witness_bytes']=(out/'split-witness.tsv.zst').stat().st_size
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
