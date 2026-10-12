import concurrent.futures,datetime,hashlib,json,pathlib,sqlite3,sys,urllib.request,zipfile
ROOT=pathlib.Path('/workspace/scratch/faa0880830cd/3d_autopilot_simple');OUT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from restore_github_checkpoint import download,load
commit=sys.argv[1];mp='projects/3d-autopilot-simple/snapshots/2026-10-12-wake18/manifest.json'
m=json.loads(download(commit,mp));assert m==json.loads((OUT/'manifest.json').read_text())
stage=OUT/'remote_verify';stage.mkdir(exist_ok=False)
def part(p):
 b=download(commit,p['path']);assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==p['sha'];q=stage/str(p['index']);q.write_bytes(b);return q
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(part,m['parts']))
h=hashlib.sha256();zpath=stage/'overlay.zip'
with zpath.open('wb') as f:
 for p in m['parts']:
  b=(stage/str(p['index'])).read_bytes();h.update(b);f.write(b)
assert h.hexdigest()==m['archive_sha256']
with zipfile.ZipFile(zpath) as z:
 index=json.loads(z.read('CHECKPOINT_MANIFEST.json'))['files'];assert len(index)==m['file_count']
 for row in index:
  b=z.read('3d_autopilot_simple/'+row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 db=stage/'verified.sqlite3';db.write_bytes(z.read('3d_autopilot_simple/.research-autopilot/simple-loop.sqlite3'))
def logical(p):
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as c:
  assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
  return hashlib.sha256('\n'.join(c.iterdump()).encode()).hexdigest()
a=logical(db);assert a==logical(ROOT/'checkpoints/database-backup.sqlite3')==logical(ROOT/'.research-autopilot/simple-loop.sqlite3')
latest,archives,old=load(m['parent_latest_commit'],stage/'old_index_cache')
new=[r for r in index if r['path'] not in old];(OUT/'new-project-files.json').write_text(json.dumps(new,indent=2)+'\n')
r={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overlay_commit':commit,'manifest_path':mp,'parts_verified':len(m['parts']),'archive_bytes':m['archive_bytes'],'archive_sha256':h.hexdigest(),'files_verified':len(index),'new_files':len(new),'replaced_files':len(index)-len(new),'combined_index_files':len(set(old)|{r['path'] for r in index}),'sqlite_integrity':'ok','sqlite_logical_dump_sha256':a,'sqlite_live_equals_coherent_backup':True,'attempts_used':74,'command_seconds':3543.3067777360347,'empirical_research_cycles':28,'scope':'All new overlay bytes and files read from immutable GitHub commit; historical base+overlay verification retained; latest composed restore still to verify.'}
(OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
