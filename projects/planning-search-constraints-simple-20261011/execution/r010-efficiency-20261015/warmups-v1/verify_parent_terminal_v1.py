"""Independent immutable HTTP readback of every new ZIP byte/member and direct copy."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,datetime,sys
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-terminal-publication';D=O/'remote';D.mkdir(exist_ok=True);commit=sys.argv[1]
prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r010-build-20261015/qualified-v1/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def get(rel,p,digest):
 h=hashlib.sha256();n=0
 with urllib.request.urlopen(base+rel,timeout=60) as src,p.open('wb') as dst:
  while q:=src.read(1048576):h.update(q);n+=len(q);dst.write(q)
 assert h.hexdigest()==digest,rel;return n
get(folder+'manifest.json',D/'manifest.json',sha(O/'manifest.json'));m=json.loads((D/'manifest.json').read_text());archive=D/'remote.zip'
with archive.open('wb') as out:
 for x in m['parts']:
  p=D/x['path'];assert get(folder+x['path'],p,x['sha256'])==x['bytes']
  with p.open('rb') as f:
   while q:=f.read(1048576):out.write(q)
assert sha(archive)==m['archive_sha256'] and archive.stat().st_size==m['archive_bytes'];total=0
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==set(m['members'])
 for n,x in m['members'].items():
  h=hashlib.sha256();size=0
  with z.open(n) as f:
   while q:=f.read(1048576):h.update(q);size+=len(q)
  assert size==x['bytes'] and h.hexdigest()==x['sha256'],n;total+=size
 p=D/'control.sqlite3';p.write_bytes(z.read('windows/W0005/.research-autopilot/simple-loop.sqlite3'))
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert s['attempts_used']==m['window_budget']['attempts_used'];assert all(a['state']=='terminal' for a in s['attempts'].values())
direct=[]
for x in json.loads((O/'uploads.json').read_text()):
 rel=x['path'].removeprefix(prefix)
 if rel.startswith(folder):continue
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);assert get(rel,p,x['sha256'])==x['bytes'];direct.append(rel)
proof={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'archive_sha256':sha(archive),'parts':len(m['parts']),'new_members':len(m['members']),'raw_member_bytes':total,'prior_alias_bindings':len(m['unchanged_source_aliases']),'all_new_parts_whole_zip_members_independent_immutable_HTTP_readback':True,'remote_control_integrity':'ok','attempts_at_capture':s['attempts_used'],'active_at_capture':0,'reservation_at_capture':0,'direct_copies':direct,'scope':'Complete additive terminal R010 source/build/native-qualification core, not fullscratch. Four new binaries included as actual ZIP members; inherited aliases reference already independently verified immutable manifests, not a fresh historical download. Generated objects explicitly deferred, old empty object forensic retained. No speed result/cleanup/W4 repair.'};(O/'remote-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
