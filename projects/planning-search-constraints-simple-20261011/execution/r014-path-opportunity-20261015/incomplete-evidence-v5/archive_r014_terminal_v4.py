"""Explicit R014 overlay with canonical read-only consistent control, no opaque-raw deletion."""
import pathlib,json,hashlib,sqlite3,zipfile,sys,shutil,datetime,gc
C=pathlib.Path('/workspace/scratch/d503fbbd44e2');B=C/'planning-resume-20261014';R=B/'project/windows/W0005';O=pathlib.Path('/dev/shm/r014-terminal-publication-v4');O.mkdir(exist_ok=False);sys.path.insert(0,str(B/'rsi-simple-13/scripts'))
from simple_runner import SimpleRunner
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def save(p,x):
 with p.open('x') as f:print(json.dumps(x,indent=2),file=f)
r=SimpleRunner(R);s=r.status();assert not s['stop_requested'] and not s['budget']['reserved_seconds'] and all(x['state']=='terminal' for x in s['attempts']);assert s['budget']['attempts_used']==39
budget=s['budget'];latest=s['journal']['current_research_review'];cycles=len(s['journal']['research_cycles']);assert cycles==14;health=r.health();del s;gc.collect()
co=R/'scripts/coordinator'
external=[]
for p in B.glob('*r014*.py'):external.append((p,'windows/W0005/scripts/coordinator/'+p.name))
for p in [pathlib.Path(__file__),pathlib.Path('/dev/shm/verify_r014_terminal_v4.py')]:external.append((p,'windows/W0005/scripts/coordinator/'+p.name))
for p in pathlib.Path('/dev/shm/r014-disk-recovery-20261015-v1').glob('*'):
 if p.is_file() and p.suffix in ['.json','.log']:external.append((p,'windows/W0005/evidence/R014-storage-recovery-v2/'+p.name))
for pattern in ['r014-archive-copy-ENOSPC*','r014-final-idle-parts-cleanup*']:
 for p in pathlib.Path('/dev/shm').glob(pattern):
  if p.is_file():external.append((p,'windows/W0005/evidence/R014-storage-recovery-v2/'+p.name))
for p in pathlib.Path('/dev/shm/r014-terminal-archive-guard-v3').glob('*'):
 if p.is_file():external.append((p,'windows/W0005/evidence/R014-archive-ENOSPC-guard-v3/'+p.name))
prior=B/'r013-terminal-publication/manifest.json';assert sha(prior)=='2c96b81218a30a6ef03310fb9009e30b075fa22bddac34d39078551bf565a454';pm=json.loads(prior.read_text());idx=dict(pm['members']);idx.update({x['path']:x for x in pm['unchanged_source_aliases']})
chain={'packet_commit':'abedbda6763ff073c7802cc2e76ecbda1e50aaf9','manifest':'execution/r013-eval-cost-20261015/incomplete-evidence-v4/manifest.json','manifest_sha256':sha(prior),'proof_commit':'755726c775741e5bd3acd0ba130147e66afabadb','proof':'execution/r013-eval-cost-20261015/incomplete-evidence-v4/remote-proof-v1.json','proof_sha256':'898ed1164f73861be12d8f93531d2ae6590213d20faa1a98c8665d5b605b6472'}
members={};replaced=set();deferred=[];archive=O/'terminal-scientific-control.zip'
def add(z,n,b,mode=0o644):
 assert n not in members;zi=zipfile.ZipInfo(n);zi.external_attr=(0o100000|mode)<<16;zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,b);members[n]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mode':mode};replaced.add(n)
with sqlite3.connect((R/'.research-autopilot/simple-loop.sqlite3').as_uri()+'?mode=ro',uri=True) as c:c.execute('BEGIN');raw=c.serialize();c.commit()
with sqlite3.connect(':memory:') as c:
 c.deserialize(raw);assert c.execute('pragma integrity_check').fetchone()[0]=='ok';ctl=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);j=json.loads(c.execute('select state from project where id=1').fetchone()[0]);assert ctl['attempts_used']==39 and all(x['state']=='terminal' for x in ctl['attempts'].values());assert len(j['research_cycles'])==cycles and j['current_research_review']==latest;del ctl,j
gc.collect()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,n in external:add(z,n,p.read_bytes(),p.stat().st_mode&0o777)
 add(z,'windows/W0005/.research-autopilot/simple-loop.sqlite3',raw);del raw;gc.collect()
 for p in R.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.is_symlink():continue
  rel=str(p.relative_to(R));n='windows/W0005/'+rel
  if n in members:continue
  if rel.startswith('.research-autopilot/.simple-loop.sqlite3.'):
   if n not in idx:deferred.append({'path':n,'bytes_at_observation':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'reason':'Opaque SQL-like temporary raw bytes remain local; may include prior-deferred entries, origin unknown, not assertedvalidDB or fullraw archive'})
   continue
  if rel.startswith('.research-autopilot/simple-loop.sqlite3') or rel.endswith('.lock'):continue
  if not (rel.startswith('.research-autopilot/') or 'r014' in rel.lower() or rel in ['plans/R015_next_inquiry_draft_v1.md','plans/R015_next_inquiry_draft_v2.md','plans/R015_chain_membership_inquiry_draft_v1.md']):continue
  h=sha(p);sz=p.stat().st_size;mode=p.stat().st_mode&0o777
  if n in idx and (h,sz)==(idx[n]['sha256'],idx[n]['bytes']):continue
  if rel.startswith('.research-autopilot/runner/diagnostics/'):add(z,n,p.read_bytes(),mode)
  else:
   z.write(p,n);assert sha(p)==h and p.stat().st_size==sz,(n,'changed during capture');members[n]={'bytes':sz,'sha256':h,'mode':mode};replaced.add(n)
aliases=[{'path':n,'prior_path':n,'bytes':x['bytes'],'sha256':x['sha256'],'mode':x.get('mode',0o644)} for n,x in idx.items() if n not in replaced]
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==set(members)
 for n,x in members.items():
  h=hashlib.sha256();sz=0
  with z.open(n) as f:
   while b:=f.read(1048576):h.update(b);sz+=len(b)
  assert (h.hexdigest(),sz)==(x['sha256'],x['bytes']) and (z.getinfo(n).external_attr>>16)&0o777==x['mode'],n
parts=[]
with archive.open('rb') as f:
 while b:=f.read(8388608):p=O/f'part-{len(parts):03d}.bin';p.write_bytes(b);parts.append({'path':p.name,'bytes':len(b),'sha256':sha(p)})
m={'format':'r014-incomplete-evidence-explicit-control-overlay-v4','external_coordinator_capture':'B full source helpers and RAM evidence injected directly into ZIP; no root copy. Own failed v3 copy truncated one coordinator helper0B, restored exact SHA before capture; no active native/audit inputs at that moment.','archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'parts':parts,'members':members,'unchanged_source_aliases':aliases,'prior_recovery':chain,'opaque_raw_objects_deferred_local':deferred,'window_budget':budget,'cycles':cycles,'latest_accepted_review':latest,'control_integrity':'ok','actual_active_unknown':[],'all_new_ZIP_members_bytes_SHA_mode_verified_locally':True,'scope':'Original R014 wrapper remains failed (native exit0); retained DAG-audit fails on incomplete prefix with no E marker; no solver rerun, no opportunity conclusion/cycle15; all cleanup/schema/reference failures retained. All new R014 selected source/protocol/reviewer revisions and red-green failures, three isolated objects/binary, native rawusage/argv/log/selected event-path witnesses/failed independent replay/retained plan/VAL and incomplete-evidence diagnosis and consistent canonical39 SQL. Prior aliases/proofs retain full history. Opaque temporary rawbytes and full296oldobjects explicitly localdeferred. Not fullscratch/oldW4DBrepair. Only receipted remoteverified idle compressed duplicate cleanup; no current/unique/raw/SQL/.o deletion.'}
save(O/'manifest.json',m);save(O/'capture-state.json',{'observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'budget':budget,'cycles':cycles,'latest_review':latest,'health_sample':health,'all_terminal':True,'stop':None,'sqlite_capture':'readonly transaction serialize exact consistent canonical39; no private SQL edits or raw backup duplicate'})
post=r.status();assert post['budget']['attempts_used']==39 and post['budget']['elapsed_seconds']==budget['elapsed_seconds'] and post['budget']['reserved_seconds']==0;assert all(x['state']=='terminal' for x in post['attempts']) and post['journal']['current_research_review']==latest
prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r014-path-opportunity-20261015/incomplete-evidence-v4/'
files=[(O/'manifest.json',folder+'manifest.json'),(O/'capture-state.json',folder+'capture-state.json'),(pathlib.Path('/dev/shm/verify_r014_terminal_v4.py'),folder+'verify_remote_v4.py')]+[(O/x['path'],folder+x['path']) for x in parts]+[(R/'R014_REPORT.zh-CN.md',prefix+'R014_REPORT.zh-CN.md'),(R/'plans/R015_chain_membership_inquiry_draft_v1.md',prefix+'plans/R015_chain_membership_inquiry_draft_v1.md')]
for n in ['evidence/R014-incomplete-witness-diagnosis-v1/diagnosis.json','results/R014-parent-path-opportunity-diagnostic-W5-v1/result.json','results/R014-parent-path-retained-DAG-audit-W5-v1/path-reference-v4.json','results/R014-parent-path-retained-DAG-audit-W5-v1/result.json','plans/R014_parent_path_opportunity_protocol_v4.md']:
 if (R/n).exists():files.append((R/n,folder+pathlib.Path(n).name))
files=[(p,(n.replace(folder+'result.json',folder+('original-failed-result.json' if 'opportunity-diagnostic' in str(p) else 'retained-audit-result.json')))) for p,n in files]
assert len({n for p,n in files})==len(files)
u=[]
for p,n in files:
 b=p.read_bytes();u.append({'local':str(p),'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()})
save(O/'uploads.json',u);print(json.dumps({'parts':len(parts),'archive_bytes':m['archive_bytes'],'members':len(members),'aliases':len(aliases),'opaque_deferred_entries':len(deferred),'budget':budget,'cycles':cycles}))
