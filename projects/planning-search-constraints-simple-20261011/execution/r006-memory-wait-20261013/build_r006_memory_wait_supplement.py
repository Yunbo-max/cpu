import pathlib,json,hashlib,sqlite3,zipfile,datetime,resource,time,shutil
resource.setrlimit(resource.RLIMIT_AS,(384*1024**2,384*1024**2))
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');P=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple');R=P/'windows/W0004';D=B/'memory-wait-publication';D.mkdir(exist_ok=True);repo=B/'archive-repo/projects/planning-search-constraints-simple-20261011';base=json.loads((repo/'snapshots/r006-overhead-cpu-w4-20261013T1912.json').read_text());old={x['path']:x for x in base['files']};t=time.monotonic();before=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());peak=before
assert before+350000000+250000000<7800000000,'waiting_for_memory for low-memory supplementary backup'
def check():
 global peak
 m=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());peak=max(peak,m);assert m<7800000000,'shared guard reached';assert time.monotonic()-t<90,'bounded supplement deadline'
paths=list(P.glob('*.json'))+list(P.glob('*.md'))
for sub in ['plans','scripts','evidence','.research-autopilot']:
 paths+=list((R/sub).rglob('*'))
for version in ['v1','v2','v3']:
 paths+=list((R/('results/R006-cpu-clock-counts-qualification-'+version)).rglob('*'))
changed=[];temps=[]
for p in sorted(set(paths)):
 if not p.is_file() or p.is_symlink() or p.name.endswith(('-wal','-shm','.pyc','.o','.a')) or '__pycache__' in p.parts:continue
 check();rel=str(p.relative_to(P));src=p
 if p.name.endswith('.sqlite3'):
  dst=D/(p.name+'.readonly-backup');a=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True);a.execute('PRAGMA cache_size=-2048');c=sqlite3.connect(dst);a.backup(c,pages=128,progress=lambda *args:check());c.close();a.close();src=dst;temps.append(dst)
 h=hashlib.sha256();n=0
 with src.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);n+=len(chunk);check()
 if rel in old and old[rel]['sha256']==h.hexdigest() and old[rel]['bytes']==n:continue
 changed.append({'path':rel,'source':str(src),'sha256':h.hexdigest(),'bytes':n,'sqlite_backup':src!=p})
zip_path=D/'r006-memory-wait-control-supplement.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for row in changed:
  with z.open(row['path'],'w',force_zip64=True) as out,open(row['source'],'rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):out.write(chunk);check()
manifest={'schema_version':1,'scope':'Supplemental changed project top-level records plus W4 control/scripts/plans/evidence and3new refused CPU qualification directories, against verified7104 snapshot. Not full-window archive; old full LATEST and all history preserved. No new scientific results.','base_commit':'7104b194ebcfa3dcf436a887d88c398c7437c1c4','base_manifest':'snapshots/r006-overhead-cpu-w4-20261013T1912.json','base_manifest_sha256':'fccfcccc33d629862f70a5584ac30d2a6d97b7bb795d1b9530bd0639b74f6bff','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'members':[{k:v for k,v in x.items() if k!='source'} for x in changed],'zip_bytes':zip_path.stat().st_size,'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'full37_window_overlay':'pending sufficient original archive headroom','maintenance_scope':{'bounded_address_space_bytes':384*1024**2,'bounded_wall_seconds':90,'shared_before_bytes':before,'shared_peak_bytes':peak,'shared_abort_bytes':7800000000,'wall_seconds':time.monotonic()-t,'not_native_attempt_or_total_project_usage':True}}
(D/'supplement-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Direct reviewable operational records plus compressed control recovery pack.
files=[(P/n,n) for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','RESUME.md','R006_REPORT.zh-CN.md','PROJECT_LEDGER_20261013T2037.json']]
for n in ['R006-cpu-qualification-waiting-for-memory-v4.json','R006-memory-wait-health-v4.json','R006-7104-remote-archive-verification.json']:
 files.append((R/'evidence'/n,'execution/r006-memory-wait-20261013/'+n))
files +=[(D/'supplement-manifest.json','execution/r006-memory-wait-20261013/supplement-manifest.json'),(zip_path,'execution/r006-memory-wait-20261013/'+zip_path.name)]
entries=[]
for src,dest in files:
 b=src.read_bytes();entries.append({'file':str(src),'path':'projects/planning-search-constraints-simple-20261011/'+dest,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
(D/'publish-files.json').write_text(json.dumps(entries,indent=2)+'\n');print(json.dumps({'members':len(changed),'zip_bytes':manifest['zip_bytes'],'shared_peak':peak,'files':len(entries),'wall':time.monotonic()-t}))
