"""Immutable remote parts/ZIP/members/derived raw verification. No current controller mutation."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,tempfile,datetime,time,sys,zstandard,resource
B=pathlib.Path(__file__).resolve().parent;O=B/'r008-publication/completed-witness-v1';commit=sys.argv[1];direct_commit=sys.argv[2];direct_base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+direct_commit+'/projects/planning-search-constraints-simple-20261011/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/projects/planning-search-constraints-simple-20261011/';started=time.monotonic();cpu0=time.process_time()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def get(path,dest=None,direct=False):
 for k in range(4):
  try:
   with urllib.request.urlopen((direct_base if direct else base)+path,timeout=45) as f:
    if dest:
     with dest.open('wb') as out:
      while b:=f.read(1048576):out.write(b)
     return dest
    return f.read()
  except Exception:
   if k==3:raise
   time.sleep(2)
raw=get('execution/r008-observer-20261014/completed-witness-v1/manifest.json');assert raw==(O/'manifest.json').read_bytes();m=json.loads(raw);verify=O/'remote-readback';verify.mkdir(exist_ok=True)
assembled=verify/'complete.zip';h=hashlib.sha256();size=0
with assembled.open('wb') as out:
 for x in m['parts']:
  p=verify/x['path']
  if not p.exists() or p.stat().st_size!=x['bytes'] or digest(p)!=x['sha256']:get('execution/r008-observer-20261014/completed-witness-v1/'+x['path'],p)
  assert p.stat().st_size==x['bytes'] and digest(p)==x['sha256']
  with p.open('rb') as f:
   while b:=f.read(1048576):out.write(b);h.update(b);size+=len(b)
assert size==m['archive_bytes'] and h.hexdigest()==m['archive_sha256']
verified={};derived={};raw_bytes=0
with zipfile.ZipFile(assembled) as z:
 assert set(z.namelist())==set(m['members'])
 for name,x in m['members'].items():
  h=hashlib.sha256();n=0
  with z.open(name) as f:
   while b:=f.read(1048576):h.update(b);n+=len(b)
  assert n==x['bytes'] and h.hexdigest()==x['sha256'],name;verified[name]={'bytes':n,'sha256':h.hexdigest()};raw_bytes+=n
 for name,x in m['derived_members'].items():
  if x['kind']=='byte-copy':
   source=verified[x['source_member']];assert source['bytes']==x['bytes'] and source['sha256']==x['sha256'];derived[name]={'verified':True,'kind':x['kind'],'bytes':x['bytes'],'sha256':x['sha256'],'restore_mode':x['mode']}
  elif x['kind']=='zstd-decompress':
   prefixes={a:y for a,y in m['derived_members'].items() if y['kind']=='prefix' and y['source_derived_member']==name};thresholds=sorted({y['bytes'] for y in prefixes.values()});h=hashlib.sha256();n=0;at={}
   with z.open(x['source_member']) as compressed,zstandard.ZstdDecompressor().stream_reader(compressed) as f:
    while block:=f.read(1048576):
     offset=0
     for target in thresholds:
      if n<target<=n+len(block)-offset:
       take=target-n;h.update(block[offset:offset+take]);offset+=take;n+=take;at[target]=h.copy().hexdigest()
     h.update(block[offset:]);n+=len(block)-offset
   assert n==x['bytes'] and h.hexdigest()==x['sha256'];derived[name]={'verified':True,'kind':x['kind'],'bytes':n,'sha256':h.hexdigest()}
   for a,y in prefixes.items():assert y['offset']==0 and at[y['bytes']]==y['sha256'];derived[a]={'verified':True,'kind':'prefix','bytes':y['bytes'],'sha256':y['sha256'],'restore_mode':y['mode']}
 assert set(derived)==set(m['derived_members'])
 with tempfile.TemporaryDirectory() as t:
  p=pathlib.Path(t)/'c.sqlite3'
  with z.open('windows/W0005/.research-autopilot/simple-loop.sqlite3') as f,p.open('wb') as out:
   while b:=f.read(1048576):out.write(b)
  with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
   assert c.execute('pragma integrity_check').fetchone()[0]=='ok';st=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert st['attempts_used']==7 and all(a['state']=='terminal' for a in st['attempts'].values());journal=json.loads(c.execute('select state from project where id=1').fetchone()[0]);assert len(journal['research_cycles'])==6 and st.get('stop_requested') is None
core_path=B/'core68-manifest.json';assert digest(core_path)==m['core68_manifest_sha256'];core=json.loads(core_path.read_text());known={(x['pack'],x['member'],x['sha256'],x['bytes']) for x in core['files']}
for a in m['unchanged_source_aliases']:assert (a['pack'],a['member'],a['sha256'],a['bytes']) in known
files=json.loads((B/'r008-publication/completed-upload-files.json').read_text())
for x in files:assert get(x['remote'],direct=True)==pathlib.Path(x['local']).read_bytes(),x['remote']
proof={'complete':True,'commit':commit,'corrected_direct_copy_commit':direct_commit,'archive_bytes_independently_downloaded_from':commit,'archive_cached_origin':'Verifier v1 actually downloaded all13parts and passed ZIP/member/derived/control checks before the direct-copy-only assertion. v1 source/traceback/guard retained. v2 rehashes the full immutable-origin cache and repeats part/member/derived verification, with fresh corrected direct-copy HTTP reads.','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256(raw).hexdigest(),'archive_sha256':m['archive_sha256'],'archive_bytes':m['archive_bytes'],'parts':len(m['parts']),'all_new_members':len(verified),'new_member_raw_bytes':raw_bytes,'derived_members':derived,'derived_recoverable_bytes':sum(x['bytes'] for x in derived.values()),'unchanged_aliases_bound_to_verified_core68':len(m['unchanged_source_aliases']),'remote_control_integrity':'ok','control_attempts':st['attempts_used'],'all_attempts_terminal':True,'remote_journal_scoped_cycles':len(journal['research_cycles']),'recorded_window_budget':m['window_budget'],'direct_files_exact':len(files),'prior_CMake_and_active_packet_proof':'execution/r008-observer-20261014/build-active-v1/remote-proof.json','scope':'Complete new R008 packet parts/members and lossless derived900MBtrace/prefix/byte-copy identities independently reread from immutable HTTP. Source aliases and all prior packs by immutable reference; generated .o explicitly deferred. No cleanup and no claim of full scratch or oldW4DBrepair.','verification_wall_seconds':time.monotonic()-started,'verification_self_cpu_seconds':time.process_time()-cpu0}
(O/'remote-proof-v2.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='derived_members'}))
