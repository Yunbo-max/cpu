"""Reuse only immutable HTTP bytes already fetched by v1; fully rehash every byte/member."""
import pathlib,json,hashlib,zipfile,sqlite3,urllib.request,datetime
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-recovery-publication';D=O/'remote'
commit='b8fdddbc3ce3fb8c17860523a99eeceffc5fded6';prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r010-recovery-20261015/checkpoint-v1/'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
assert sha(D/'manifest.json')==sha(O/'manifest.json');m=json.loads((D/'manifest.json').read_text());archive=D/'remote.zip'
for x in m['parts']:assert (D/x['path']).stat().st_size==x['bytes'] and sha(D/x['path'])==x['sha256']
assert archive.stat().st_size==m['archive_bytes'] and sha(archive)==m['archive_sha256'];total=0
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==set(m['members'])
 for name,x in m['members'].items():
  h=hashlib.sha256();n=0
  with z.open(name) as f:
   while q:=f.read(1048576):h.update(q);n+=len(q)
  assert n==x['bytes'] and h.hexdigest()==x['sha256'],name;total+=n
 p=D/'remote-control.sqlite3';assert sha(p)==m['members']['windows/W0005/.research-autopilot/simple-loop.sqlite3']['sha256']
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert s['attempts_used']==14;assert all(a['state']=='terminal' for a in s['attempts'].values())
 reserved=sum(a['reservation_seconds'] for a in s['attempts'].values() if a['state']!='terminal');assert reserved==0
direct=[]
for x in json.loads((O/'upload-files.json').read_text()):
 rel=x['path'].removeprefix(prefix)
 if rel.startswith(folder):continue
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);raw=urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60).read();assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'];p.write_bytes(raw);direct.append(rel)
proof={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'archive_sha256':sha(archive),'parts':len(m['parts']),'new_members':len(m['members']),'raw_member_bytes':total,'prior_alias_bindings':len(m['unchanged_source_aliases']),'immutable_HTTP_source':'All4parts and manifest independently fetched in v1. v2 rehashes all original HTTP bytes/wholeZIP/allmembers and freshly HTTP reads5directcopies. No claimed historical full download.','remote_control_integrity':'ok','terminal_attempts':14,'reservation_seconds':reserved,'direct_copies':direct,'verifier_v1_failure':'Incorrect assumption runner_state contained reserved_seconds; actual reservation derived from active attempt states. All14 terminal; no experiment/data failure. Original verifier/log retained.','scope':'Entire additive new recovery packet, not fullscratch/newscience/oldW4repair. No cleanup.'}
(O/'remote-proof-v2.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
