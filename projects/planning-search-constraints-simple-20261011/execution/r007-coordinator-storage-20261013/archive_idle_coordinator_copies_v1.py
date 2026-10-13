import pathlib,json,tarfile,zstandard,hashlib,datetime,os,time
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');start=time.monotonic();files=[p for p in B.iterdir() if p.is_file() and ((p.suffix=='.json' and p.stat().st_size>1048576) or (p.name.startswith('.accepted-') and p.stat().st_size>0) or (p.name.startswith('r006-db-') and p.suffix=='.sqlite3'))];pack=B/'r007-idle-coordinator-copies-v1.tar.zst';assert not pack.exists();rows=[]
class H:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):q=self.f.read(n);self.h.update(q);self.n+=len(q);return q
with pack.open('wb') as sink,zstandard.ZstdCompressor(level=3,threads=0).stream_writer(sink,closefd=False) as zw,tarfile.open(fileobj=zw,mode='w|') as tf:
 for k,p in enumerate(files):
  st=p.stat();ti=tf.gettarinfo(str(p),arcname=p.name);ti.uid=ti.gid=0;ti.uname=ti.gname=''
  with p.open('rb') as f:q=H(f);tf.addfile(ti,q)
  after=p.stat();assert q.n==st.st_size==after.st_size and after.st_mtime_ns==st.st_mtime_ns;rows.append({'path':str(p),'member':p.name,'bytes':q.n,'sha256':q.h.hexdigest(),'cleanup_eligible_after_remote_full_raw_proof':True})
  if k%15==0:print(json.dumps({'idle_copies_archived':k+1,'compressed_bytes':pack.stat().st_size}),flush=True)
  assert time.monotonic()-start<600
parts=[];whole=hashlib.sha256();offset=0;ns='projects/planning-search-constraints-simple-20261011/execution/r007-coordinator-storage-20261013'
with pack.open('rb') as f:
 while q:=f.read(8388608):whole.update(q);parts.append({'offset':offset,'bytes':len(q),'sha256':hashlib.sha256(q).hexdigest(),'git_sha':hashlib.sha1(f'blob {len(q)}\0'.encode()+q).hexdigest(),'path':ns+f'/parts/part-{len(parts):05d}.bin'});offset+=len(q)
j={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pack_file':str(pack),'format':'complete tar.zst','bytes':offset,'sha256':whole.hexdigest(),'members':rows,'raw_bytes':sum(x['bytes'] for x in rows),'parts':parts,'scope':'Complete explicit-file idle same-project coordinator full-response/status JSON copies, original failed temporary response files and previous read-only diagnostic SQLite backup outputs. No current project SQLite/control, native source/binaries/results or other projects included as cleanup targets. This is supplemental operational evidence, not native science or a full project snapshot. Every raw member is required to pass immutable remote full-pack plus decompressed raw SHA verification before local duplicate deletion.'};(B/'r007-idle-coordinator-copies-manifest-v1.json').write_text(json.dumps(j,indent=2)+'\n');print({'complete':True,'members':len(rows),'compressed_bytes':offset,'raw_bytes':j['raw_bytes'],'parts':len(parts),'wall':time.monotonic()-start,'free':os.statvfs(B).f_bfree*os.statvfs(B).f_frsize})
