"""Independent immutable HTTP retrieval of complete new additive raw ZIP and control."""
import pathlib,json,hashlib,urllib.request,zipfile,sqlite3,datetime,sys
C=pathlib.Path(__file__).resolve().parent;B=C/'planning-resume-20261014';O=B/'r012-terminal-publication';D=O/'remote';D.mkdir(exist_ok=True);commit=sys.argv[1];prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r012-primary-boundary-20261015/completed-v1/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+prefix
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while q:=f.read(1048576):h.update(q)
    return h.hexdigest()
def get(n,p,h,size=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(base+n,timeout=60) as src,p.open('wb') as out:
        while q:=src.read(1048576):assert out.write(q)==len(q)
    assert sha(p)==h,n
    if size is not None:assert p.stat().st_size==size,n
get(folder+'manifest.json',D/'manifest.json',sha(O/'manifest.json'));m=json.loads((D/'manifest.json').read_text())
with (D/'archive.zip').open('wb') as out:
    for x in m['parts']:
        p=D/x['path'];get(folder+x['path'],p,x['sha256'],x['bytes'])
        with p.open('rb') as f:
            while q:=f.read(1048576):assert out.write(q)==len(q)
assert sha(D/'archive.zip')==m['archive_sha256'] and (D/'archive.zip').stat().st_size==m['archive_bytes']
rawbytes=0
with zipfile.ZipFile(D/'archive.zip') as z:
    assert set(z.namelist())==set(m['members'])
    for n,x in m['members'].items():
        h=hashlib.sha256();size=0
        with z.open(n) as f:
            while q:=f.read(1048576):h.update(q);size+=len(q)
        assert h.hexdigest()==x['sha256'] and size==x['bytes'],n
        assert ((z.getinfo(n).external_attr>>16)&0o777)==x['mode'],n;rawbytes+=size
    with z.open('windows/W0005/.research-autopilot/simple-loop.sqlite3') as f,(D/'control.sqlite3').open('wb') as out:
        while q:=f.read(1048576):assert out.write(q)==len(q)
# Decode each NEW derived object from exact final remotely retrieved member/basis.
decoded=[]
with zipfile.ZipFile(D/'archive.zip') as z:
    import tempfile,subprocess
    for i,x in enumerate(m['derived_raw_objects']):
        assert sha(D/'control.sqlite3')==x['basis_sha256']
        enc=z.read(x['encoded_member']);assert (len(enc),hashlib.sha256(enc).hexdigest())==(x['encoded_bytes'],x['encoded_sha256'])
        member=m['members'][x['encoded_member']];assert (member['bytes'],member['sha256'])==(x['encoded_bytes'],x['encoded_sha256'])
        with tempfile.TemporaryFile() as inp,(D/f'decode-{i:02d}.stderr.log').open('wb') as se:
            inp.write(enc);inp.seek(0);p=subprocess.Popen(['zstd','-d','-M2048MB','--patch-from='+str(D/'control.sqlite3'),'-c'],stdin=inp,stdout=subprocess.PIPE,stderr=se);h=hashlib.sha256();count=0
            while q:=p.stdout.read(1048576):h.update(q);count+=len(q)
            assert p.wait(timeout=180)==0
        assert (h.hexdigest(),count)==(x['sha256'],x['bytes']),x['path']
        decoded.append({'path':x['path'],'bytes':count,'sha256':h.hexdigest(),'encoded_member_join_verified':True})
# Bind unchanged aliases to exact already independently verified recovery chain,
# not a new claim to download/decode all historical raw source objects again.
chain=m['prior_recovery']
prior=B/'r011-terminal-compact-publication/remote/manifest.json';assert sha(prior)==chain['manifest_sha256']
bm=json.loads(prior.read_text());proof=B/'r011-terminal-compact-publication/remote-proof-v2.json';assert sha(proof)==chain['proof_sha256'] and json.loads(proof.read_text())['complete'] is True
idx=dict(bm['members']);idx.update({x['path']:x for x in bm['unchanged_source_aliases']});idx.update({x['path']:x for x in bm['derived_raw_objects']})
for x in m['unchanged_source_aliases']:
    old=idx[x['prior_path']];assert (x['sha256'],x['bytes'])==(old['sha256'],old['bytes']),x['path']
with sqlite3.connect((D/'control.sqlite3').as_uri()+'?mode=ro',uri=True) as c:
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok';j=json.loads(c.execute('select state from project where id=1').fetchone()[0]);s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0])
    assert s['attempts_used']==m['window_budget']['attempts_used'] and all(x['state']=='terminal' for x in s['attempts'].values())
    assert len(j['research_cycles'])==m['cycles'] and j['current_research_review']==m['latest_accepted_review'];assert m['window_budget']['reserved_seconds']==0
direct=[]
for x in json.loads((O/'uploads.json').read_text()):
    rel=x['path'].removeprefix(prefix)
    if rel==folder+'manifest.json' or any(rel==folder+p['path'] for p in m['parts']):continue
    get(rel,D/'direct'/rel,x['sha256'],x['bytes']);direct.append({'path':rel,'bytes':x['bytes'],'sha256':x['sha256']})
external=[]
for x in m.get('external_exact_inputs',[]):
    p=D/'external'/pathlib.Path(x['path']).name;p.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(x['url'],timeout=90) as src,p.open('wb') as out:
        while q:=src.read(1048576):assert out.write(q)==len(q)
    assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes']
    assert hashlib.md5(p.read_bytes()).hexdigest()==x['published_md5']
    external.append({'path':x['path'],'bytes':x['bytes'],'sha256':x['sha256'],'actual_authenticated_external_HTTP_readback':True})
p={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet_commit':commit,'manifest_sha256':sha(D/'manifest.json'),'parts':len(m['parts']),'archive_bytes':m['archive_bytes'],'archive_sha256':sha(D/'archive.zip'),'all_new_parts_wholeZIP_and_members_independent_immutable_HTTP_readback':True,'new_members':len(m['members']),'new_raw_bytes':rawbytes,'new_member_modes_verified':True,'unchanged_aliases_bound_to_verified_prior_chain':len(m['unchanged_source_aliases']),'prior_recovery':chain,'new_derived_objects':len(decoded),'derived_raw_objects_verified':decoded,'derived_raw_bytes':sum(x['bytes'] for x in decoded),'remote_control_integrity':'ok','all_terminal_at_capture':True,'attempts_at_capture':s['attempts_used'],'reservation_at_capture':0,'cycles_at_capture':len(j['research_cycles']),'latest_accepted_review':j['current_research_review'],'direct_copies':direct,'scope':m['object_scope'],'no_native_rerun_or_cleanup':True}
p['external_exact_inputs_verified']=external
with (O/'remote-proof-v1.json').open('w') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps(p))

