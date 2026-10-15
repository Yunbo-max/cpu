"""Independent immutable HTTP readback of every new part/member and control integrity."""
import pathlib,json,urllib.request,hashlib,zipfile,sqlite3,datetime
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-recovery-publication';D=O/'remote';D.mkdir(exist_ok=True)
commit='b8fdddbc3ce3fb8c17860523a99eeceffc5fded6';prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r010-recovery-20261015/checkpoint-v1/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while x:=f.read(1048576):h.update(x)
 return h.hexdigest()
def get(name,p,expected):
 h=hashlib.sha256();n=0
 with urllib.request.urlopen(base+name,timeout=60) as src,p.open('wb') as out:
  while x:=src.read(1048576):out.write(x);h.update(x);n+=len(x)
 assert h.hexdigest()==expected,(name,h.hexdigest(),expected);return n
get(folder+'manifest.json',D/'manifest.json',sha(O/'manifest.json'));m=json.loads((D/'manifest.json').read_text());archive=D/'remote.zip'
with archive.open('wb') as out:
 for x in m['parts']:
  p=D/x['path'];assert get(folder+x['path'],p,x['sha256'])==x['bytes']
  with p.open('rb') as f:
   while q:=f.read(1048576):out.write(q)
assert archive.stat().st_size==m['archive_bytes'] and sha(archive)==m['archive_sha256'];rawbytes=0
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==set(m['members'])
 for name,x in m['members'].items():
  h=hashlib.sha256();n=0
  with z.open(name) as f:
   while q:=f.read(1048576):h.update(q);n+=len(q)
  assert n==x['bytes'] and h.hexdigest()==x['sha256'],name;rawbytes+=n
 name='windows/W0005/.research-autopilot/simple-loop.sqlite3';p=D/'remote-control.sqlite3';p.write_bytes(z.read(name))
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert s['attempts_used']==14;assert all(a['state']=='terminal' for a in s['attempts'].values());assert s['reserved_seconds']==0
direct=[]
for x in json.loads((O/'upload-files.json').read_text()):
 rel=x['path'].removeprefix(prefix)
 if rel.startswith(folder):continue
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);assert get(rel,p,x['sha256'])==x['bytes'];direct.append(rel)
proof={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'archive_sha256':sha(archive),'parts':len(m['parts']),'new_members':len(m['members']),'raw_member_bytes':rawbytes,'prior_alias_bindings':len(m['unchanged_source_aliases']),'all_parts_whole_archive_and_members_immutable_HTTP_independently_reread':True,'remote_control_integrity':'ok','terminal_attempts':14,'reservation_seconds':0,'direct_copies':direct,'scope':'Entire new additive recovery packet only. Prior aliases bound to old immutable manifests, not all history re-downloaded. No new scientific result/no cleanup/no oldW4 repair.'}
(O/'remote-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
