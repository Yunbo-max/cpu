"""Independently fetch only a published planning delta; verify streams and DB."""
import argparse,hashlib,importlib.util,json,os,pathlib,resource,sqlite3,subprocess,time,zipfile
resource.setrlimit(resource.RLIMIT_AS,(256_000_000,256_000_000))
a=argparse.ArgumentParser();a.add_argument('--commit',required=True);a.add_argument('--queue',required=True);a.add_argument('--dest',required=True);a.add_argument('--output',required=True);x=a.parse_args()
dest=pathlib.Path(x.dest).resolve();dest.mkdir(exist_ok=False)
ns='projects/planning-search-constraints-simple-20261011/'
queue=json.loads(pathlib.Path(x.queue).read_text())
assert all(v['path'].startswith(ns) for v in queue)
def run(args,stdout=None):return subprocess.run(args,stdout=stdout or subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=45)
def advise(p):
 with p.open('rb') as f:os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
def cache():
 for p in (dest/'.git/objects').rglob('*.pack'):advise(p)
run(['git','init',str(dest)])
run(['git','-C',str(dest),'remote','add','origin','https://github.com/Yunbo-max/cpu.git'])
run(['git','-C',str(dest),'config','remote.origin.promisor','true'])
run(['git','-C',str(dest),'config','remote.origin.partialclonefilter','blob:none'])
run(['git','-C',str(dest),'fetch','--filter=blob:none','--depth=1','origin',x.commit]);cache()
resources=[]
for q in queue:
 p=dest/q['path'];p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('wb') as f:
  run(['git','-C',str(dest),'show',x.commit+':'+q['path']],stdout=f);f.flush();os.fsync(f.fileno())
 h=hashlib.sha1(b'blob '+str(q['bytes']).encode()+b'\0')
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 assert p.stat().st_size==q['bytes'] and h.hexdigest()==q['sha'],q['path']
 advise(p);cache();resources.append(int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text()))
base=dest/ns;latest=json.loads((base/'LATEST.json').read_text());raw=(base/latest['manifest']).read_bytes();assert hashlib.sha256(raw).hexdigest()==latest['sha256'];manifest=json.loads(raw);indexed={i['path']:i for i in manifest['files']}
# Require all old entries retained and nonempty evictions preserved; base already independently verified.
oldpath=pathlib.Path(__file__).parent/'snapshots/wake0015-qualified-accounting.json'
old=json.loads(oldpath.read_text());assert all(v['path'] in indexed for v in old['files'])
assert all(indexed[v['path']]['bytes']>0 for v in old['files'] if v['bytes']>0)
spec=importlib.util.spec_from_file_location('archive_store',pathlib.Path(__file__).with_name('archive_store.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checked=[];db_checks=[]
for packdir in sorted((base/'packs').iterdir()):
 packrel=str(packdir.relative_to(dest));meta=json.loads((packdir/'index.json').read_text());total=hashlib.sha256()
 for part in meta['parts']:
  p=packdir/part['path'];assert m.digest(p)==part['sha256']
  with p.open('rb') as f:
   while b:=f.read(1048576):total.update(b)
 assert total.hexdigest()==meta['sha256']
 with zipfile.ZipFile(m.PartsReader(dest,packrel)) as z:
  for info in z.infolist():
   h=hashlib.sha256();count=0;db=None;dbpath=dest/'verified.sqlite3'
   with z.open(info) as f:
    first=True
    while b:=f.read(1048576):
     if first and b.startswith(b'SQLite format 3\0'):db=dbpath.open('wb')
     first=False;h.update(b);count+=len(b)
     if db:
      db.write(b)
      if count%4194304==0:db.flush();os.fsync(db.fileno());os.posix_fadvise(db.fileno(),0,0,os.POSIX_FADV_DONTNEED)
   entry=indexed.get(info.filename)
   # The earlier pending handoff can be superseded by a later member; still validate ZIP CRC.
   current=bool(entry and entry['pack']==packrel)
   if current:assert count==entry['bytes'] and h.hexdigest()==entry['sha256'],info.filename
   if db:
    db.flush();os.fsync(db.fileno());db.close();advise(dbpath)
    with sqlite3.connect('file:'+str(dbpath)+'?mode=ro',uri=True) as conn:result=conn.execute('pragma integrity_check').fetchone()[0]
    assert result=='ok';db_checks.append({'path':info.filename,'integrity_check':result});advise(dbpath);dbpath.unlink()
   checked.append({'path':info.filename,'bytes':count,'sha256':h.hexdigest(),'current_manifest_member':current})
receipt={'status':'verified','commit':x.commit,'git_paths_verified':len(queue),'manifest_sha256':latest['sha256'],'manifest_files':len(indexed),'all_prior_paths_retained':True,'no_prior_nonempty_file_zeroed':True,'delta_members_verified':len(checked),'sqlite':db_checks,'resource_samples_bytes':resources,'members':checked,'scope':'Independent network fetch of new delta only; old pack identities inherited from verified base, not redownloaded. No scientific evaluation or solver run.'}
pathlib.Path(x.output).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['members','resource_samples_bytes']}))
