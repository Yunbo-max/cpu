"""Independent immutable HTTP archive and full lossless forensic-object verification."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,datetime,sys,subprocess
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-complete-compact-publication';D=O/'remote';D.mkdir(exist_ok=True);commit=sys.argv[1]
prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r010-efficiency-20261015/completed-v2/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
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
assert sha(archive)==m['archive_sha256'] and archive.stat().st_size==m['archive_bytes'];total=0;derived=[]
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==set(m['members'])
 for n,x in m['members'].items():
  h=hashlib.sha256();size=0
  with z.open(n) as f:
   while q:=f.read(1048576):h.update(q);size+=len(q)
  assert size==x['bytes'] and h.hexdigest()==x['sha256'],n;total+=size
 p=D/'control.sqlite3'
 with z.open('windows/W0005/.research-autopilot/simple-loop.sqlite3') as src,p.open('wb') as out:
  while q:=src.read(1048576):out.write(q)
 for x in m['derived_raw_objects']:
  assert sha(p)==x['basis_sha256'];enc=D/pathlib.Path(x['encoded_member']).name;enc.write_bytes(z.read(x['encoded_member']));assert sha(enc)==x['encoded_sha256'];cmd=['zstd','-d','-M2048MB','--patch-from='+str(p),str(enc),'-c'];h=hashlib.sha256();n=0
  with (D/(enc.name+'.decode.stderr.log')).open('wb') as se:
   proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=se)
   while q:=proc.stdout.read(1048576):h.update(q);n+=len(q)
   rc=proc.wait(timeout=90)
  assert rc==0 and n==x['bytes'] and h.hexdigest()==x['sha256'],x['path'];derived.append({'path':x['path'],'bytes':n,'sha256':h.hexdigest(),'exit':rc})
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert s['attempts_used']==m['window_budget']['attempts_used']==31;assert all(a['state']=='terminal' for a in s['attempts'].values())
direct=[]
for x in json.loads((O/'uploads.json').read_text()):
 rel=x['path'].removeprefix(prefix)
 if rel.startswith(folder+'part-') or rel==folder+'manifest.json':continue
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);assert get(rel,p,x['sha256'])==x['bytes'];direct.append(rel)
proof={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'archive_sha256':sha(archive),'parts':len(m['parts']),'new_members':len(m['members']),'raw_member_bytes':total,'prior_alias_bindings':len(m['unchanged_source_aliases']),'all_new_parts_whole_zip_members_independent_immutable_HTTP_readback':True,'derived_raw_objects':derived,'all_derived_raw_bytes':sum(x['bytes'] for x in derived),'remote_control_integrity':'ok','attempts_at_capture':31,'cycles_at_capture':10,'active_at_capture':0,'reservation_at_capture':0,'direct_copies':direct,'scope':m['scope'],'limits':'Prior aliases bind verified607/898chain, not fresh fullhistory download. Tempraw integrity not SQLitevalidity/rootcause. No unique/control/.o cleanup, no W4 repair or stable/general speed assertion.'}
with (O/'remote-proof-v2.json').open('w') as f:print(json.dumps(proof,indent=2),file=f)
print(json.dumps(proof))
