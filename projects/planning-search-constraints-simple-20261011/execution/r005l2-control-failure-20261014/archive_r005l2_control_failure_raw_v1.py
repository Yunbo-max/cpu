import pathlib,json,tarfile,zstandard,hashlib,datetime,time
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');R=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple/windows/W0004');files=[(R/'.research-autopilot/simple-loop.sqlite3','canonical-W4-after-failed-official-recovery.sqlite3.raw'),(B/'r005l2-v3-control-journal-before-official-recovery-v1.bin','rollback-journal-before-official-recovery.bin'),(B/'accepted-R005L2-depots-p05-states_ops-600s-3000M-host-v3-hostv10.json.zst','accepted-v3-complete-stdout.json.zst'),(B/'r005l2-v3-idempotent-response-recovery-v1.json.zst','failed-idempotent-recovery-stdout.json.zst')];pack=B/'r005l2-control-failure-raw-v1.tar.zst';assert not pack.exists();rows=[]
class H:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):q=self.f.read(n);self.h.update(q);self.n+=len(q);return q
with pack.open('wb') as f,zstandard.ZstdCompressor(level=3,threads=0).stream_writer(f,closefd=False) as z,tarfile.open(fileobj=z,mode='w|') as t:
 for p,name in files:
  st=p.stat();ti=t.gettarinfo(str(p),arcname=name)
  with p.open('rb') as src:q=H(src);t.addfile(ti,q)
  after=p.stat();assert st.st_size==after.st_size==q.n and st.st_mtime_ns==after.st_mtime_ns;rows.append({'path':str(p),'member':name,'bytes':q.n,'sha256':q.h.hexdigest()})
whole=hashlib.sha256();parts=[];o=0;ns='projects/planning-search-constraints-simple-20261011/execution/r005l2-control-failure-20261014'
with pack.open('rb') as f:
 while q:=f.read(8388608):whole.update(q);parts.append({'offset':o,'bytes':len(q),'sha256':hashlib.sha256(q).hexdigest(),'git_sha':hashlib.sha1(f'blob {len(q)}\0'.encode()+q).hexdigest(),'path':ns+f'/parts/part-{len(parts):05d}.bin'});o+=len(q)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pack_file':str(pack),'format':'complete tar.zst forensic raw bytes, NOT valid SQLite snapshot','bytes':o,'sha256':whole.hexdigest(),'raw_bytes':sum(x['bytes'] for x in rows),'members':rows,'parts':parts,'scope':'Preserved actual unreadable/corrupt canonicalW4 raw SQLite after officialidempotentRW recovery failed, oldrollbackjournalbytes, entirepreviouslyacceptedv3stdout and failedrecoverystdout. CanonicalbadDB/originalfiles NOT deleted/edited; no validcontrol69 or scientificnativev3 execution claim. Validcore68 remains independent lastknown safe snapshot; native69failed/RSSguard and queuedv3 contracts separately archived.'};(B/'r005l2-control-failure-raw-manifest-v1.json').write_text(json.dumps(r,indent=2));print({'bytes':o,'raw_bytes':r['raw_bytes'],'parts':len(parts),'members':len(rows)})
