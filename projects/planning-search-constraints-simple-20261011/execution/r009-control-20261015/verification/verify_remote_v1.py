"""Independent immutable HTTP readback, all members and full lossless binary/trace restoration."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,sys,time,shutil,zstandard,io
B=pathlib.Path(__file__).resolve().parent;O=B/'r009-publication-v2';commit=sys.argv[1];prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r009-control-20261015/qualification-v1/'
base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix;V=O/'remote-readback-v1';V.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def digest(stream):
 h=hashlib.sha256();n=0
 while q:=stream.read(1048576):h.update(q);n+=len(q)
 return n,h.hexdigest()
def download(rel,p):
 with urllib.request.urlopen(base+rel,timeout=120) as src,p.open('wb') as dst:shutil.copyfileobj(src,dst,1048576)
started=time.monotonic();cpu=time.process_time();download(folder+'manifest.json',V/'manifest.json');assert sha(V/'manifest.json')==sha(O/'manifest.json');m=json.loads((V/'manifest.json').read_text())
joined=V/'complete.zip'
with joined.open('wb') as dst:
 for x in m['parts']:
  p=V/x['path'];download(folder+x['path'],p);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
  with p.open('rb') as src:shutil.copyfileobj(src,dst,1048576)
assert joined.stat().st_size==m['archive_bytes'] and sha(joined)==m['archive_sha256']
count=rawbytes=0;restored=[]
with zipfile.ZipFile(joined) as z:
 assert set(z.namelist())==set(m['members']) and len(z.namelist())==len(m['members'])
 for name,x in m['members'].items():
  with z.open(name) as f:n,h=digest(f)
  assert n==x['bytes'] and h==x['sha256'],name;count+=1;rawbytes+=n
 with z.open('windows/W0005/.research-autopilot/simple-loop.sqlite3') as src,(V/'control.sqlite3').open('wb') as dst:shutil.copyfileobj(src,dst,1048576)
 # This prior archive was originally independently HTTP-fetched and fully verified.
 # Rehash every cached immutable byte and exact basis now; do not claim re-downloading it.
 priorzip=B/'r008-publication/completed-witness-v1/remote-readback/complete.zip';assert sha(priorzip)=='968a426ed1a6fe15610177c56a04ece9567a8004a73ecce790c3ff6f19049bcc'
 with zipfile.ZipFile(priorzip) as oldzip:
  for name,x in m['derived_members'].items():
   if x['format']=='verified-prefix-v1':
    source=m['derived_members'][x['source_member']];assert source['sha256']==x['source_sha256'] and any(v['path']==x['source_member'] for v in restored)
    h=hashlib.sha256();left=x['bytes']
    with z.open(source['source_member']) as src,zstandard.ZstdDecompressor().stream_reader(src) as stream:
     while left:
      q=stream.read(min(left,1048576));assert q;h.update(q);left-=len(q)
    assert h.hexdigest()==x['sha256'];restored.append({'path':name,'bytes':x['bytes'],'sha256':h.hexdigest(),'format':x['format']});continue
   assert m['members'][x['source_member']]['sha256']==x['source_sha256']
   if x['format']=='zstd-v1':dec=zstandard.ZstdDecompressor()
   else:
    assert x['format']=='zstd-rawcontent-dictionary-v1';basis=oldzip.read(x['basis_prior_member']);assert len(basis)==x['basis_bytes'] and hashlib.sha256(basis).hexdigest()==x['basis_sha256']
    dec=zstandard.ZstdDecompressor(dict_data=zstandard.ZstdCompressionDict(basis,dict_type=zstandard.DICT_TYPE_RAWCONTENT),max_window_size=268435456)
   with z.open(x['source_member']) as src,dec.stream_reader(src) as stream:n,h=digest(stream)
   assert n==x['bytes'] and h==x['sha256'],name;restored.append({'path':name,'bytes':n,'sha256':h,'format':x['format']})
with sqlite3.connect((V/'control.sqlite3').as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';st=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert st['attempts_used']==12
 attempts=st['attempts'].values() if isinstance(st['attempts'],dict) else st['attempts'];assert all(a['state']=='terminal' for a in attempts)
 events=[json.loads(v[0]) for v in c.execute('select payload from events order by version')];cycles=[e for e in events if e.get('kind')=='research_cycle'];assert len(cycles)==8 and cycles[-1]['event_id']=='W5-R009-minimal-coordinate-qualification-cycle-v1'
priorraw=urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+m['prior_manifest_commit']+'/'+prefix+m['prior_manifest'],timeout=60).read();assert hashlib.sha256(priorraw).hexdigest()==m['prior_manifest_sha256'];prior=json.loads(priorraw);idx=dict(prior['members']);idx.update({x['path']:x for x in prior['unchanged_source_aliases']})
for x in m['unchanged_source_aliases']:
 old=idx[x['prior_path']];assert x['sha256']==old['sha256'] and x['bytes']==old['bytes'],x['path']
direct=[]
for name in json.loads((O/'direct-paths.json').read_text()):
 rel='execution/r009-control-20261015/direct/'+name;raw=urllib.request.urlopen(base+rel,timeout=60).read();expected=m['members']['windows/W0005/'+name];assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'];direct.append({'path':rel,'bytes':len(raw),'sha256':expected['sha256']})
for name in ['R009_REPORT.zh-CN.md','CURRENT_RESEARCH.md','RESUME.md','CURRENT_EXECUTION.json','CHECKPOINT.json']:
 raw=urllib.request.urlopen(base+name,timeout=60).read();assert hashlib.sha256(raw).hexdigest()==sha(O/name);direct.append({'path':name,'bytes':len(raw),'sha256':sha(O/name)})
proof={'complete':True,'packet_commit':commit,'manifest_sha256':sha(V/'manifest.json'),'parts_independently_HTTP_read':len(m['parts']),'archive_bytes':m['archive_bytes'],'archive_sha256':m['archive_sha256'],'new_members_verified':count,'new_member_raw_bytes':rawbytes,'derived_members_fully_restored_and_SHA_verified':restored,'prior_basis_archive_fully_rehashed':str(priorzip),'prior_basis_provenance':'Previously independently immutable HTTP-read archive; exact whole compressed SHA and extracted194010960-byte basis rechecked now. Not claimed re-downloaded.','unchanged_alias_bindings_verified':len(m['unchanged_source_aliases']),'prior_manifest_independently_HTTP_read':m['prior_manifest_commit'],'control_integrity_check':'ok','control_attempts':12,'all_attempts_terminal':True,'direct_copies':direct,'wall_seconds':time.monotonic()-started,'self_cpu_seconds':time.process_time()-cpu,'scope':'All new packet HTTP parts/wholeZIP/members and both complete lossless derived native objects restored withSHA/bytes. Aliases bound to previously verified immutable manifests. Generated.o explicitly not archived; no cleanup, no oldW4 repair.'}
(O/'remote-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
