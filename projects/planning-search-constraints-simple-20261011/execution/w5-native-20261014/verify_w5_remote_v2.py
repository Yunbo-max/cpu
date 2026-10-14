import pathlib,json,urllib.request,hashlib,zipfile,io,sqlite3
BASE=pathlib.Path(__file__).resolve().parent
COMMIT='b24f8f4bde8da307677ab340df004823bb4cc563'
PREFIX='https://raw.githubusercontent.com/Yunbo-max/cpu/'+COMMIT+'/projects/planning-search-constraints-simple-20261011/'
m=json.loads((BASE/'publication/supplement-manifest.json').read_text())
with urllib.request.urlopen(PREFIX+'execution/w5-recovery-20261014/control-supplement.zip',timeout=60) as f:data=f.read()
assert len(data)==m['bytes'] and hashlib.sha256(data).hexdigest()==m['sha256']
z=zipfile.ZipFile(io.BytesIO(data));assert set(z.namelist())==set(m['members'])
for name,meta in m['members'].items():
    b=z.read(name);assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256']
p=BASE/'remote-readback-W5-control-v2.sqlite3';p.write_bytes(z.read('windows/W0005/.research-autopilot/simple-loop.sqlite3'))
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as connection:
    assert connection.execute('pragma integrity_check').fetchone()[0]=='ok'
    state=json.loads(connection.execute('select payload from runner_state where id=1').fetchone()[0]);assert state['attempts_used']==0
proof={'commit':COMMIT,'remote_zip_bytes':len(data),'remote_zip_sha256':hashlib.sha256(data).hexdigest(),'all_member_hashes_verified':len(m['members']),
       'remote_control_integrity_check':'ok','remote_control_attempts':0,'complete':True,'scope':m['scope'],
       'verifier_v1_failure':'Relative path as_uri raised after member SHA loop; v2 uses resolved absolute path. Verification-tool repair, not a native failure or archive corruption.'}
(BASE/'project/windows/W0005/evidence/W5-initial-supplement-remote-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
