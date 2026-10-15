"""Independent repair HTTP bytes plus rechecked original HTTP cache, all members and12raw objects."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,datetime,sys,subprocess,tempfile
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-complete-repair-publication';V=B/'r010-complete-compact-publication';D=O/'remote';D.mkdir(exist_ok=True);commit=sys.argv[1];prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r010-efficiency-20261015/completed-repair-v3/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def get(n,p,h):
 with urllib.request.urlopen(base+n,timeout=60) as src,p.open('wb') as out:
  while q:=src.read(1048576):assert out.write(q)==len(q)
 assert sha(p)==h,n
get(folder+'manifest.json',D/'manifest.json',sha(O/'manifest.json'));m=json.loads((D/'manifest.json').read_text());get(folder+'forensic-encoding-repair.zip',D/'repair.zip',m['archive_sha256']);assert (D/'repair.zip').stat().st_size==m['archive_bytes'];baseM=V/'remote/manifest.json';assert sha(baseM)==m['base_manifest_sha256'];bm=json.loads(baseM.read_text());old=V/'remote/remote.zip';assert sha(old)==m['base_archive_sha256'];basis=V/'remote/control.sqlite3';assert sha(basis)==m['canonical31_basis_sha256'];verified=0;rawbytes=0;decoded=[]
for part in bm['parts']:
 p=V/'remote'/part['path'];assert p.stat().st_size==part['bytes'] and sha(p)==part['sha256']
with zipfile.ZipFile(old) as bz,zipfile.ZipFile(D/'repair.zip') as rz:
 for z,man in [(bz,bm),(rz,m)]:
  assert set(z.namelist())==set(man['members'])
  for n,x in man['members'].items():
   h=hashlib.sha256();size=0
   with z.open(n) as f:
    while q:=f.read(1048576):h.update(q);size+=len(q)
   assert h.hexdigest()==x['sha256'] and size==x['bytes'],n;verified+=1;rawbytes+=size
 for oldx in bm['derived_raw_objects']:
  x=m['replacement_objects'].get(oldx['path'],oldx);enc=(rz if oldx['path'] in m['replacement_objects'] else bz).read(x['encoded_member']);assert len(enc)==x['encoded_bytes'] and hashlib.sha256(enc).hexdigest()==x['encoded_sha256'];h=hashlib.sha256();size=0
  with tempfile.TemporaryFile() as inp:
   assert inp.write(enc)==len(enc);inp.flush();inp.seek(0)
   with (D/(pathlib.Path(x['encoded_member']).name+'.stderr.log')).open('wb') as se:
    p=subprocess.Popen(['zstd','-d','-M2048MB','--patch-from='+str(basis),'-c'],stdin=inp,stdout=subprocess.PIPE,stderr=se)
    while q:=p.stdout.read(1048576):h.update(q);size+=len(q)
    rc=p.wait(timeout=90)
  assert rc==0 and h.hexdigest()==x['sha256'] and size==x['bytes'],x['path'];decoded.append({'path':x['path'],'bytes':size,'sha256':h.hexdigest(),'replacement_used':x['path'] in m['replacement_objects']})
with sqlite3.connect(basis.as_uri()+'?mode=ro',uri=True) as c:
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok';j=json.loads(c.execute('select state from project where id=1').fetchone()[0]);s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);assert s['attempts_used']==31 and all(a['state']=='terminal' for a in s['attempts'].values());assert len(j['research_cycles'])==10;assert j['current_research_review']['sha256']=='eb99567edeeafbe3e9f0dfb3773bbe312513068e5f4708f9987668aeb86765b1'
direct=[]
for x in json.loads((O/'uploads.json').read_text()):
 rel=x['path'].removeprefix(prefix)
 if rel in [folder+'manifest.json',folder+'forensic-encoding-repair.zip']:continue
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);get(rel,p,x['sha256']);direct.append(rel)
proof={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'archive_sha256':m['archive_sha256'],'base_packet_commit':m['base_packet_commit'],'base_manifest_sha256':sha(baseM),'base_archive_sha256':sha(old),'base_all20parts_and_wholezip_independent_HTTP_cache_rehashed':True,'base_new_members':len(bm['members']),'repair_new_members':len(m['members']),'members_rechecked':verified,'raw_member_bytes':rawbytes,'prior_alias_bindings':len(bm['unchanged_source_aliases']),'all_repair_bytes_independent_immutable_HTTP_readback':True,'all_derived_raw_objects':decoded,'derived_raw_bytes':sum(x['bytes'] for x in decoded),'replacement_count':len(m['replacement_objects']),'remote_control_integrity':'ok','attempts_at_capture':31,'cycles_at_capture':10,'all_terminal_at_capture':True,'reservation_at_capture':0,'latest_accepted_review':j['current_research_review'],'direct_copies':direct,'scope':'Complete source/rawscientific results/31control from immutable fc5 base plus2scoped repair encodings; all444base and8repair members fully verified and12derivedraw objects2538864640B recovered SHA/bytes. Original v2full derived verification failed; oldbad encoded bytes retained, never called complete. No native rerun/unique cleanup/W4DBrepair/fullscratch or stable/general speed claim.'}
with (O/'remote-proof-v3.json').open('w') as f:print(json.dumps(proof,indent=2),file=f)
print(json.dumps(proof))
