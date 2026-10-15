"""Lossless replacement encoding for idle raw temp SQLite bytes; not database repair."""
import pathlib,json,hashlib,zipfile,subprocess,time,shutil,datetime,resource
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';V=B/'r010-complete-publication';O=B/'r010-complete-compact-publication';O.mkdir(exist_ok=False);M=json.loads((V/'manifest.json').read_text());basis=V/'consistent-W5.sqlite3';rows=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def decode(p,digest,size):
 start=time.monotonic();cmd=['zstd','-d','-M2048MB','--patch-from='+str(basis),str(p),'-c'];h=hashlib.sha256();n=0
 with (O/(p.name+'.decode.stderr.log')).open('wb') as se:
  proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=se)
  while q:=proc.stdout.read(1048576):h.update(q);n+=len(q)
  rc=proc.wait(timeout=90)
 assert rc==0 and h.hexdigest()==digest and n==size,(p,rc,n,h.hexdigest());return {'argv':cmd,'wall_seconds':time.monotonic()-start,'exit':rc,'decoded_bytes':n,'decoded_sha256':h.hexdigest()}
assert sha(basis)==M['members']['windows/W0005/.research-autopilot/simple-loop.sqlite3']['sha256']
for i,(n,x) in enumerate(M['members'].items()):
 if '/.simple-loop.sqlite3.' not in n:continue
 raw=B/'project'/n;assert sha(raw)==x['sha256'] and raw.stat().st_size==x['bytes'];p=O/f'temp-sqlite-{len(rows):02d}.zst';cmd=['zstd','-T1','-3','--patch-from='+str(basis),str(raw),'-o',str(p)];start=time.monotonic()
 with (O/(p.name+'.encode.stdout.log')).open('wb') as so,(O/(p.name+'.encode.stderr.log')).open('wb') as se:rc=subprocess.call(cmd,stdout=so,stderr=se,timeout=90)
 assert rc==0;check=decode(p,x['sha256'],x['bytes']);assert sha(raw)==x['sha256'];rows.append({'path':n,**x,'basis_member':'windows/W0005/.research-autopilot/simple-loop.sqlite3','basis_sha256':sha(basis),'encoding':'zstd-patch-from','encoded_member':'forensic-deltas/'+p.name,'encoded_bytes':p.stat().st_size,'encoded_sha256':sha(p),'encode_argv':cmd,'encode_wall_seconds':time.monotonic()-start,'local_roundtrip':check});print(json.dumps({'encoded':n,'raw':x['bytes'],'encoded_bytes':p.stat().st_size}),flush=True)
assert len(rows)==12
mapping={'format':'lossless-forensic-raw-recovery-map-v1','meaning':'Idle temporary SQLite rawbytes only; origin unknown, not asserted valid databases. No source deletion or currentDB mutation. Decoding needs exact canonical31backup basis member, not liveDB.','derived_objects':rows};write(O/'derived-raw-map.json',mapping)
members={};archive=O/'completed-lossless-compact-overlay.zip';derived={x['path'] for x in rows}
with zipfile.ZipFile(V/'complete-native-and-terminal-control.zip') as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
 for n,x in M['members'].items():
  if n in derived:continue
  with src.open(n) as a,dst.open(n,'w',force_zip64=True) as b:shutil.copyfileobj(a,b,1048576)
  members[n]=x
 for p,n in [(O/'derived-raw-map.json','recovery/derived-raw-map.json')]+[(O/pathlib.Path(x['encoded_member']).name,x['encoded_member']) for x in rows]+[(pathlib.Path(__file__),'recovery/compact_r010_complete_overlay_v2.py'),(pathlib.Path(__file__).parent/'verify_r010_complete_compact_remote_v2.py','recovery/verify_r010_complete_compact_remote_v2.py')]+[(p,'recovery/logs/'+p.name) for p in O.glob('*.log')]:
  dst.write(p,n);members[n]={'bytes':p.stat().st_size,'sha256':sha(p),'mode':p.stat().st_mode&0o777}
parts=[]
with archive.open('rb') as f:
 i=0
 while q:=f.read(8388608):
  p=O/f'part-{i:03d}.bin';p.write_bytes(q);parts.append({'path':p.name,'bytes':len(q),'sha256':sha(p)});i+=1
m={**M,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'parts':parts,'members':members,'derived_raw_objects':rows,'superseded_local_v1_manifest_sha256':sha(V/'manifest.json'),'superseded_local_v1_archive_sha256':M['archive_sha256'],'superseded_local_v1_archive_bytes':M['archive_bytes'],'new_forensic_raw_bytes':sum(x['bytes'] for x in rows),'scope':M['scope']+' Twelve newly observed idle tempSQLite raw objects2538864640B additionally included via exact lossless basis-bound Zstdpatches; local full-byte decode/hash verified, not validDB/rootcause assertions. V1uncompacted archive retained locally, superseded encoding not an execution failure.','maintenance_usage':{'child_cpu_seconds_since_process_start':resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,'not_native_experiment_or_allproject_CPU':True}};write(O/'manifest.json',m)
for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','R010_REPORT.zh-CN.md','RESUME.md']:shutil.copyfile(V/n,O/n)
prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r010-efficiency-20261015/completed-v2/';files=[(O/'manifest.json',folder+'manifest.json'),(O/'derived-raw-map.json',folder+'derived-raw-map.json'),(V/'manifest.json',folder+'superseded-local-v1-manifest.json'),(pathlib.Path(__file__),folder+'compact_v2.py'),(pathlib.Path(__file__).parent/'verify_r010_complete_compact_remote_v2.py',folder+'verify_remote_v2.py')]+[(O/x['path'],folder+x['path']) for x in parts]+[(B/'project/windows/W0005/results/R010-complete-native-efficiency-analysis-v1.json',folder+'analysis-v1.json'),(B/'r010-running-publication/proof-metadata-readback-v3.json',prefix+'execution/r010-efficiency-20261015/running-v1/proof-metadata-readback-v3.json')]+[(O/n,prefix+n) for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','RESUME.md','CURRENT_RESEARCH.md','R010_REPORT.zh-CN.md']];uploads=[]
for p,n in files:
 raw=p.read_bytes();uploads.append({'local':str(p),'path':n,'bytes':len(raw),'sha256':sha(p),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()})
write(O/'uploads.json',uploads);print(json.dumps({'parts':len(parts),'bytes':m['archive_bytes'],'new_members':len(members),'derived_raw_objects':len(rows),'derived_raw_bytes':m['new_forensic_raw_bytes']}))
