"""Immutable HTTP independent readback of all new packet bytes/members/control/direct copies."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,sys,time,shutil
B=pathlib.Path(__file__).resolve().parent;O=B/'r008-relation-publication';commit=sys.argv[1];prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r008-cartesian-20261014/relation-v1/'
base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
V=O/'remote-verification-v1';V.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def download(rel,p):
 with urllib.request.urlopen(base+rel,timeout=120) as src,p.open('wb') as dst:shutil.copyfileobj(src,dst,1048576)
download(folder+'manifest.json',V/'manifest.json');assert sha(V/'manifest.json')==sha(O/'manifest.json');m=json.loads((V/'manifest.json').read_text());started=time.monotonic();cpu=time.process_time()
joined=V/'complete.zip'
with joined.open('wb') as dst:
 for x in m['parts']:
  p=V/x['path'];download(folder+x['path'],p);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'];
  with p.open('rb') as src:shutil.copyfileobj(src,dst,1048576)
assert joined.stat().st_size==m['archive_bytes'] and sha(joined)==m['archive_sha256']
count=rawbytes=0
with zipfile.ZipFile(joined) as z:
 assert set(z.namelist())==set(m['members']) and len(z.namelist())==len(m['members'])
 for name,x in m['members'].items():
  h=hashlib.sha256();n=0
  with z.open(name) as f:
   while q:=f.read(1048576):h.update(q);n+=len(q)
  assert n==x['bytes'] and h.hexdigest()==x['sha256'],name;count+=1;rawbytes+=n
 with z.open('windows/W0005/.research-autopilot/simple-loop.sqlite3') as src,(V/'control.sqlite3').open('wb') as dst:shutil.copyfileobj(src,dst,1048576)
with sqlite3.connect((V/'control.sqlite3').as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';st=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert st['attempts_used']==10
 assert all(a['state']=='terminal' for a in st['attempts'].values()) if isinstance(st['attempts'],dict) else all(a['state']=='terminal' for a in st['attempts'])
priorurl='https://raw.githubusercontent.com/Yunbo-max/cpu/'+m['prior_manifest_commit']+'/'+prefix+m['prior_manifest'];priorraw=urllib.request.urlopen(priorurl,timeout=60).read();assert hashlib.sha256(priorraw).hexdigest()==m['prior_manifest_sha256'];prior=json.loads(priorraw);idx=dict(prior['members']);idx.update({x['path']:x for x in prior['unchanged_source_aliases']});idx.update(prior['derived_members'])
corepath=B/'core68-manifest.json';assert sha(corepath)=='af0708304697337f7c36b1cac238167fa2522bee75a4aad5df12b909484b328f';core=json.loads(corepath.read_text());cidx={(x['pack'],x['member']):x for x in core['files']}
for a in m['unchanged_source_aliases']:
 old=idx[a['prior_path']] if 'prior_path' in a else cidx[a['pack'],a['member']]
 assert a['sha256']==old['sha256'] and a['bytes']==old['bytes'],a['path']
# Read every directly published human-readable copy by immutable HTTP, not local checkout.
direct=[]
for name,member in [('R008_CARTESIAN_REPORT.zh-CN.md',None)]+[('execution/r008-cartesian-20261014/direct/'+p,'windows/W0005/'+p) for p in ['results/R008-native-operator-object-export-W5-v2/operators.tsv','results/R008-native-operator-object-export-W5-v2/result.json','results/R008-cartesian-retained-trace-audit-W5-v1/result.json','evidence/R008-operator-reference-review-result-v1.json','evidence/R008-schema-test-input-handling-incident-v1.json','plans/R009_minimal_coordinate_strong_control_draft_v1.md','scripts/r008_cartesian_reference_v2.py']]:
 raw=urllib.request.urlopen(base+name,timeout=60).read();expected=m['members'][member]['sha256'] if member else sha(O/'R008_CARTESIAN_REPORT.zh-CN.md');assert hashlib.sha256(raw).hexdigest()==expected;direct.append({'path':name,'bytes':len(raw),'sha256':expected})
proof={'complete':True,'packet_commit':commit,'manifest_sha256':sha(V/'manifest.json'),'parts_independently_HTTP_read':len(m['parts']),'archive_bytes':m['archive_bytes'],'archive_sha256':m['archive_sha256'],'new_members_verified':count,'new_member_raw_bytes':rawbytes,'unchanged_alias_bindings_verified':len(m['unchanged_source_aliases']),'prior_manifest_independently_HTTP_read':m['prior_manifest_commit'],'alias_scope':'Hash/bytes mapped to already fully verified prior packet/derived raw/core68. No claim of redownloading all historical raw objects.','control_integrity_check':'ok','control_attempts':st['attempts_used'],'all_attempts_terminal':True,'direct_copies':direct,'wall_seconds':time.monotonic()-started,'self_cpu_seconds':time.process_time()-cpu,'scope':'New packet all immutable HTTP parts/wholeZIP/all95members/control10 and8directcopies, explicit aliases bound to retained prior manifests; generated.o not archived, no scratch cleanup or oldW4 repair.'}
(O/'remote-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
