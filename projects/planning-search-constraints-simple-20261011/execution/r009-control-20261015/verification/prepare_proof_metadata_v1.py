"""Bind verified immutable packet to current metadata; no new experiments or source adoption."""
import pathlib,json,hashlib,sys,datetime
B=pathlib.Path(__file__).resolve().parent;R=B/'project/windows/W0005';O=B/'r009-publication-v2';commit=sys.argv[1]
sys.path.insert(0,str(B/'rsi-simple-13/scripts'));from simple_runner import SimpleRunner
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
proof=json.loads((O/'remote-proof-v1.json').read_text());assert proof['complete'] and proof['packet_commit']==commit
man=json.loads((O/'manifest.json').read_text());runner=SimpleRunner(R);s=runner.status();assert not s['stop_requested'] and not s['budget']['reserved_seconds'] and all(a['state']=='terminal' for a in s['attempts']) and s['budget']['attempts_used']==12
cur=json.loads((O/'CURRENT_EXECUTION.json').read_text());health=runner.health();cur.update(updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_health=health,status_observed=s['status'],window_budget=s['budget'],current_accepted_decision=s['journal']['current_research_review']);cur['active_coordinator'].update(observed_health=health)
cur['R009']['remote_verification']={'packet_commit':commit,'complete':True,'proof_path':'execution/r009-control-20261015/qualification-v1/remote-proof-v1.json','proof_sha256':sha(O/'remote-proof-v1.json'),'new_members':proof['new_members_verified'],'derived_members':proof['derived_members_fully_restored_and_SHA_verified'],'alias_bindings':proof['unchanged_alias_bindings_verified']}
for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json']:write(O/n,cur)
prior=json.loads((B/'r008-relation-publication/W5_SUCCESSOR_LATEST.json').read_text())
pointer={'window':'W0005','updated_utc':cur['updated_utc'],'archive':None,'archive_format':man['format'],'archive_directory':'execution/r009-control-20261015/qualification-v1/','archive_commit':commit,'manifest':'execution/r009-control-20261015/qualification-v1/manifest.json','manifest_sha256':sha(O/'manifest.json'),'archive_sha256':man['archive_sha256'],'archive_bytes':man['archive_bytes'],'archive_parts':[p['path'] for p in man['parts']],'remote_proof':'execution/r009-control-20261015/qualification-v1/remote-proof-v1.json','remote_proof_sha256':sha(O/'remote-proof-v1.json'),'remote_verified_complete':True,'new_members':proof['new_members_verified'],'derived_members':4,'unchanged_alias_bindings':proof['unchanged_alias_bindings_verified'],'terminal_attempts':12,'reservation_seconds':0,'scoped_research_cycles':8,'previous_W5_pointer':prior,'scope':man['scope'],'restore_notice':'Manifest first; reassemble all13parts with wholeSHA, select members and follow immutable prior aliases. Restore new binary using exact old parent raw-content dictionary; decoder explicit max_window_size argument268435456. Restore fulltrace fromZstd then two exact prefix files preserving mode. Verify allbytes/SHA. Never overwrite active/unknown control. All.o deferred locally; oldLATESTcore68 and allhistoricalpacks/stops/failures retained.'}
for n in ['R009_CONTROL_LATEST.json','W5_SUCCESSOR_LATEST.json']:write(O/n,pointer)
prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r009-control-20261015/qualification-v1/'
files=[(O/n,prefix+n) for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','RESUME.md','R009_CONTROL_LATEST.json','W5_SUCCESSOR_LATEST.json']]
files +=[(O/'remote-proof-v1.json',folder+'remote-proof-v1.json'),(B/'verify_r009_packet_remote_v1.py',prefix+'execution/r009-control-20261015/verification/verify_remote_v1.py'),(B/'prepare_r009_proof_metadata_v1.py',prefix+'execution/r009-control-20261015/verification/prepare_proof_metadata_v1.py'),(B/'R010_observer_off_efficiency_design_draft_v1.md',prefix+'plans/R010_observer_off_efficiency_design_draft_v1.md')]
for foldername in ['r009-archive-guard','r009-archive-v2-guard']:
 for p in (B/foldername).iterdir():
  if p.is_file():files.append((p,prefix+'execution/r009-control-20261015/verification/'+foldername+'/'+p.name))
for p in (O/'verification-guard').iterdir():
 if p.is_file():files.append((p,prefix+'execution/r009-control-20261015/verification/http-readback/'+p.name))
a=[]
for p,path in files:
 raw=p.read_bytes();a.append({'local':str(p),'path':path,'bytes':len(raw),'sha256':sha(p),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()})
write(O/'proof-upload-files.json',a);print(json.dumps({'files':len(a),'proof_sha256':sha(O/'remote-proof-v1.json'),'manifest_sha256':sha(O/'manifest.json'),'health':health,'budget':s['budget'],'cycles':len(s['journal']['research_cycles'])}))
