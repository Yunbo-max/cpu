"""Bind independently verified packet/proof to latest current observations, no source/queue change."""
import pathlib,json,sys,hashlib,datetime,urllib.request
B=pathlib.Path(__file__).resolve().parent;R=B/'project/windows/W0005';O=B/'r008-relation-publication';commit=sys.argv[1];sys.path.insert(0,str(B/'rsi-simple-13/scripts'));from simple_runner import SimpleRunner
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
proof=json.loads((O/'remote-proof-v1.json').read_text());assert proof['complete'] and proof['packet_commit']==commit
man=json.loads((O/'manifest.json').read_text());s=SimpleRunner(R).status();assert not s['stop_requested'] and not s['budget']['reserved_seconds'] and all(a['state']=='terminal' for a in s['attempts'])
cur=json.loads((O/'CURRENT_EXECUTION.json').read_text());health=SimpleRunner(R).health();cur.update(updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_health=health,status_observed=s['status'],window_budget=s['budget'],current_accepted_decision=s['journal']['current_research_review'])
cur['active_coordinator'].update(observed_health=health)
cur['R008']['attempts']=[{k:a.get(k) for k in ['task_id','attempt_id','state','result','receipt_ref']} for a in s['attempts'] if a['task_id'].startswith('R008')];cur['R008']['actual_active_or_unknown']=[]
cur['R008_independent_cartesian_relation']['remote_verification']={'packet_commit':commit,'proof_path':'execution/r008-cartesian-20261014/relation-v1/remote-proof-v1.json','proof_sha256':sha(O/'remote-proof-v1.json'),'complete':True,'new_members':proof['new_members_verified'],'unchanged_alias_bindings':proof['unchanged_alias_bindings_verified']}
for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json']:write(O/n,cur)
base='https://raw.githubusercontent.com/Yunbo-max/cpu/b7603e7a3fd63b8f7667ce79818820aacac8e605/projects/planning-search-constraints-simple-20261011/'
old=json.loads(urllib.request.urlopen(base+'R008_OBSERVER_LATEST.json').read())
pointer={'window':'W0005','updated_utc':cur['updated_utc'],'archive':None,'archive_format':'split_zip_incremental_with_immutable_prior_aliases','archive_directory':'execution/r008-cartesian-20261014/relation-v1/','archive_commit':commit,'manifest':'execution/r008-cartesian-20261014/relation-v1/manifest.json','manifest_sha256':sha(O/'manifest.json'),'archive_sha256':man['archive_sha256'],'archive_bytes':man['archive_bytes'],'archive_parts':[p['path'] for p in man['parts']],'remote_proof':'execution/r008-cartesian-20261014/relation-v1/remote-proof-v1.json','remote_proof_sha256':sha(O/'remote-proof-v1.json'),'remote_verified_complete':True,'new_members':proof['new_members_verified'],'unchanged_alias_bindings':proof['unchanged_alias_bindings_verified'],'terminal_attempts':10,'reservation_seconds':0,'scoped_research_cycles':7,'previous_R008_observer_pointer':old,'scope':man['scope'],'restore_notice':'Fetch exact manifest first. Reassemble all11parts in order and verify wholeSHA, then selected members. Unchanged paths follow prior immutable manifests/verified derived mappings. No overwrite of live/unknown controls. .o explicitly local deferred; all historical stops/failures/packs preserved.'}
for n in ['R008_CARTESIAN_LATEST.json','R008_OBSERVER_LATEST.json','W5_SUCCESSOR_LATEST.json']:write(O/n,pointer)
files=[]
prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r008-cartesian-20261014/relation-v1/'
for name in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','RESUME.md','R008_CARTESIAN_LATEST.json','R008_OBSERVER_LATEST.json','W5_SUCCESSOR_LATEST.json']:
 files.append((O/name,prefix+name))
files +=[(O/'remote-proof-v1.json',folder+'remote-proof-v1.json'),(B/'verify_r008_relation_remote_v1.py',prefix+'execution/r008-cartesian-20261014/verification/verify_v1.py'),(O/'verification-guard/metrics.json',prefix+'execution/r008-cartesian-20261014/verification/metrics.json'),(O/'verification-guard/stdout.log',prefix+'execution/r008-cartesian-20261014/verification/stdout.log'),(O/'verification-guard/stderr.log',prefix+'execution/r008-cartesian-20261014/verification/stderr.log')]
files +=[(O/'SAS-universe-crosswalk-v1.json',prefix+'execution/r008-cartesian-20261014/verification/SAS-universe-crosswalk-v1.json'),(B/'check_r008_sas_operator_universe_v1.py',prefix+'execution/r008-cartesian-20261014/verification/check_SAS_universe_v1.py'),(O/'additional-fixtures.stderr.log',prefix+'execution/r008-cartesian-20261014/verification/additional-fixtures.stderr.log')]
files +=[(B/'prepare_r008_relation_proof_metadata_v1.py',prefix+'execution/r008-cartesian-20261014/verification/prepare_proof_metadata_v1.py'),(O/'next-prompt-template.txt',prefix+'execution/r008-cartesian-20261014/verification/next-prompt-template.txt')]
files +=[(B/'verify_r008_relation_control_cycles_v1.py',prefix+'execution/r008-cartesian-20261014/verification/verify_control_cycles_v1.py'),(O/'remote-control-journal-supplement-v1.json',prefix+'execution/r008-cartesian-20261014/verification/remote-control-journal-supplement-v1.json')]
a=[]
for p,path in files:
 raw=p.read_bytes();a.append({'local':str(p),'path':path,'bytes':len(raw),'sha256':sha(p),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()})
write(O/'proof-upload-files.json',a);print(json.dumps(a))
