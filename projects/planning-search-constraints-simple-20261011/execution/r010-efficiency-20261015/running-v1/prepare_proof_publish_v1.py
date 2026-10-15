import pathlib,json,hashlib
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-running-publication';D=O/'proof-publish';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=O/'remote-proof-v2.json';assert json.loads(proof.read_text())['complete'];prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r010-efficiency-20261015/running-v1/'
pointer={'packet_commit':'018d5086f5f0098a3373c703d336a07f7cdcc6b6','manifest':'execution/r010-efficiency-20261015/running-v1/manifest.json','manifest_sha256':sha(O/'manifest.json'),'remote_proof':'execution/r010-efficiency-20261015/running-v1/remote-proof-v2.json','remote_proof_sha256':sha(proof),'independent_remote_verification_complete':True,'scope':'Light post22 native/dispatch evidence only. Actual sole coordinator continues; new consistent-control recovery still22, do not restore over active/unknown. Full scored batch analysis not yet available.'}
p=D/'R010_RUNNING_LATEST.json'
with p.open('w') as f:print(json.dumps(pointer,indent=2),file=f)
files=[(proof,folder+'remote-proof-v2.json'),(O/'remote-proof-v1.json',folder+'remote-proof-v1-malformed-retained.json'),(B/'recovery-20261015/running-addendum-remote-proof-v1.log',folder+'remote-proof-v1.stdout.log'),(B/'recovery-20261015/warmup-pointer-independent-readback-v2.json',prefix+'execution/r010-efficiency-20261015/warmups-v1/pointer-independent-readback-v2.json'),(pathlib.Path(__file__).parent/'verify_r010_pointer_metadata_v2.py',prefix+'execution/r010-efficiency-20261015/warmups-v1/verify_pointer_metadata_v2.py'),(pathlib.Path(__file__).parent/'verify_r010_running_addendum_v2.py',folder+'verify_remote_v2.py'),(pathlib.Path(__file__),folder+'prepare_proof_publish_v1.py'),(p,prefix+'R010_RUNNING_LATEST.json')];rows=[]
for p,n in files:
 raw=p.read_bytes();rows.append({'local':str(p),'path':n,'bytes':len(raw),'sha256':sha(p),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()})
with (D/'uploads.json').open('w') as f:print(json.dumps(rows,indent=2),file=f)
print(json.dumps({'files':len(rows)}))
