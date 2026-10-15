"""Independent immutable HTTP archive/member/mode/control/alias/direct-copy verification."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,datetime,sys,gc
C=pathlib.Path('/workspace/scratch/d503fbbd44e2');B=C/'planning-resume-20261014';O=pathlib.Path('/dev/shm/r014-terminal-publication-v5');D=O/'remote';D.mkdir(exist_ok=False);commit=sys.argv[1];prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r014-path-opportunity-20261015/incomplete-evidence-v5/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def get(n,p,h,size=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen(base+n,timeout=60) as f,p.open('xb') as out:
  while b:=f.read(1048576):assert out.write(b)==len(b)
 assert sha(p)==h and (size is None or p.stat().st_size==size),n
get(folder+'manifest.json',D/'manifest.json',sha(O/'manifest.json'));m=json.loads((D/'manifest.json').read_text())
with (D/'archive.zip').open('xb') as out:
 for x in m['parts']:
  p=D/x['path'];get(folder+x['path'],p,x['sha256'],x['bytes'])
  with p.open('rb') as f:
   while b:=f.read(1048576):assert out.write(b)==len(b)
assert sha(D/'archive.zip')==m['archive_sha256'] and (D/'archive.zip').stat().st_size==m['archive_bytes'];total=0
with zipfile.ZipFile(D/'archive.zip') as z:
 assert set(z.namelist())==set(m['members'])
 for n,x in m['members'].items():
  h=hashlib.sha256();sz=0
  with z.open(n) as f:
   while b:=f.read(1048576):h.update(b);sz+=len(b)
  assert (h.hexdigest(),sz)==(x['sha256'],x['bytes']) and (z.getinfo(n).external_attr>>16)&0o777==x['mode'],n;total+=sz
 raw=z.read('windows/W0005/.research-autopilot/simple-loop.sqlite3')
with sqlite3.connect(':memory:') as c:
 c.deserialize(raw);del raw;gc.collect();assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);j=json.loads(c.execute('select state from project where id=1').fetchone()[0]);assert s['attempts_used']==39 and all(x['state']=='terminal' for x in s['attempts'].values());assert len(j['research_cycles'])==m['cycles'] and j['current_research_review']==m['latest_accepted_review'];del s,j
gc.collect();prior=B/'r013-terminal-publication/manifest.json';pr=B/'r013-terminal-publication/remote-proof-v1.json';assert sha(prior)==m['prior_recovery']['manifest_sha256'] and sha(pr)==m['prior_recovery']['proof_sha256'] and json.loads(pr.read_text())['complete']
p=json.loads(prior.read_text());idx=dict(p['members']);idx.update({x['path']:x for x in p['unchanged_source_aliases']})
for x in m['unchanged_source_aliases']:assert (x['bytes'],x['sha256'])==(idx[x['prior_path']]['bytes'],idx[x['prior_path']]['sha256'])
direct=[]
for x in json.loads((O/'uploads.json').read_text()):
 n=x['path'].removeprefix(prefix)
 if n==folder+'manifest.json' or any(n==folder+a['path'] for a in m['parts']):continue
 get(n,D/'direct'/n,x['sha256'],x['bytes']);direct.append({'path':n,'bytes':x['bytes'],'sha256':x['sha256']})
p={'complete':True,'verified_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'parts':len(m['parts']),'archive_bytes':m['archive_bytes'],'archive_sha256':m['archive_sha256'],'all_new_parts_wholeZIP_members_modes_independent_immutable_HTTP_verified':True,'new_members':len(m['members']),'new_raw_bytes':total,'unchanged_aliases_bound_to_verified_prior_chain':len(m['unchanged_source_aliases']),'prior_recovery':m['prior_recovery'],'opaque_tempobjects_deferred_not_archived':m['opaque_raw_objects_deferred_local'],'remote_SQL_integrity':'ok','terminal_attempts':39,'reservation':0,'cycles':m['cycles'],'latest_accepted':m['latest_accepted_review'],'direct_copies':direct,'scope':m['scope'],'no_native_rerun_or_unique_control_SQL_cleanup':True}
with (O/'remote-proof-v1.json').open('x') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps({'complete':True,'members':p['new_members'],'archive_bytes':p['archive_bytes'],'terminal':39,'cycles':p['cycles'],'opaque_deferred_entries':len(p['opaque_tempobjects_deferred_not_archived'])}))
