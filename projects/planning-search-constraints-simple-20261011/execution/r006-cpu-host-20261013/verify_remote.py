"""Immutable remote-byte readback followed by all new ZIP member identities; resumable part receipts."""
import pathlib,subprocess,json,hashlib,datetime,importlib.util,zipfile,os,time
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');repo=B/'archive-repo';commit='f2f16f6fedf3cf3093d37dc1ce81e138d479ea0c';ns='projects/planning-search-constraints-simple-20261011';rp=B/'r006-cpu-core-remote-verification.json';started=time.monotonic()
def read(path):return subprocess.check_output(['git','-c','core.packedGitWindowSize=8m','-c','core.packedGitLimit=64m','-C',str(repo),'show',commit+':'+path],stderr=subprocess.PIPE)
latest=json.loads(read(ns+'/LATEST.json'));raw=read(ns+'/'+latest['manifest']);assert hashlib.sha256(raw).hexdigest()==latest['sha256']=='ac5527d9cb4dd502df0a02e72b612c006537464b2e09b79a7294027a0986eb50';m=json.loads(raw);pack=ns+'/packs/r006-cpu-host-core-w4-20261013T2212';index=json.loads(read(pack+'/index.json'));receipt={'commit':commit,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':latest['sha256'],'parts':[],'scope':'New immutable remote pack+manifest/direct copies; old packs retained by reference. ZIP member read uses local parts whose full bytes equal immutable remote readback. No experimental or mathematical certification.'};aggregate=hashlib.sha256();total=0
for x in index['parts']:
 path=pack+'/'+x['path'];p=subprocess.Popen(['git','-c','core.packedGitWindowSize=8m','-c','core.packedGitLimit=64m','-C',str(repo),'show',commit+':'+path],stdout=subprocess.PIPE,stderr=subprocess.PIPE);h=hashlib.sha256();size=0
 while q:=p.stdout.read(1048576):h.update(q);aggregate.update(q);size+=len(q)
 err=p.stderr.read();assert p.wait()==0,err.decode(errors='replace');assert h.hexdigest()==x['sha256'] and size==x['bytes'];total+=size;receipt['parts'].append({'path':path,'sha256':h.hexdigest(),'bytes':size});rp.write_text(json.dumps(receipt,indent=2)+'\n');print('remote-part-verified',x['path'],flush=True)
assert aggregate.hexdigest()==index['sha256'] and total==index['bytes'];receipt['aggregate_pack']={'sha256':aggregate.hexdigest(),'bytes':total};lookup={x['path']:x for x in m['files']};copies=[]
for name,member in [('CPU-wall-analysis.json','windows/W0004/results/R006-cpu-overhead-analysis-v1.json'),('USER_MEMORY_POLICY.json','windows/W0004/evidence/USER_MEMORY_POLICY_20261013T2144Z.json'),('orphan-forensic-catalog.json','windows/W0004/evidence/R006-orphan-sqlite-forensic-catalog-v1.json'),('R007_longer_window_pilot_contract_v1.md','windows/W0004/plans/R007_longer_window_pilot_contract_v1.md')]:
 raw=read(ns+'/execution/r006-cpu-host-20261013/'+name);assert hashlib.sha256(raw).hexdigest()==lookup[member]['sha256'];copies.append({'path':name,'member':member,'sha256':lookup[member]['sha256']})
spec=importlib.util.spec_from_file_location('archive',repo/ns/'archive_store.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);os.posix_fadvise=lambda *args:None;members=[x for x in m['files'] if x['pack']==pack];rawtotal=0
with zipfile.ZipFile(mod.PartsReader(repo,pack)) as z:
 assert {x['member'] for x in members}==set(z.namelist())
 for x in members:
  h=hashlib.sha256();size=0
  with z.open(x['member']) as f:
   while q:=f.read(1048576):h.update(q);size+=len(q)
  assert h.hexdigest()==x['sha256'] and size==x['bytes'],x['path'];rawtotal+=size
receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-started,direct_copies=copies,all_new_zip_members={'count':len(members),'raw_bytes':rawtotal,'sha256_and_bytes_all_verified':True},complete=True,complete_scope='Currentvalidcontrol/source/scientificoutputs/native12CPUwalland3qualification/oldhistoryoverlay only;23invalid orphanrawfiles explicitlydeferred and retainedlocal, notcompleteallsourcebytes',forensic_deferred_count=23,forensic_deferred_raw_bytes=4352901120);rp.write_text(json.dumps(receipt,indent=2)+'\n');print('complete13parts-and-all-new-core-members',len(members),rawtotal,flush=True)
