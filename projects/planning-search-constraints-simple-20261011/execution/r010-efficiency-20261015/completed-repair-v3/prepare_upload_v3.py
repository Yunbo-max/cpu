import pathlib,json,hashlib
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';O=B/'r010-complete-repair-publication';prefix='projects/planning-search-constraints-simple-20261011/execution/r010-efficiency-20261015/completed-repair-v3/'
files=[(O/'manifest.json','manifest.json'),(O/'forensic-encoding-repair.zip','forensic-encoding-repair.zip'),(pathlib.Path(__file__).parent/'verify_r010_complete_recovery_v3.py','verify_remote_v3.py'),(pathlib.Path(__file__),'prepare_upload_v3.py'),(B/'recovery-20261015/r010-encoding-binding-green-v1.log','encoding-binding-green-v1.log'),(B/'recovery-20261015/r010-encoding-repair-v3.log','encoding-repair-v3.log'),(B/'project/windows/W0005/evidence/R010-complete-publication-engineering-incidents-v1.json','engineering-incidents-v1.json')];rows=[]
for p,n in files:
 raw=p.read_bytes();rows.append({'local':str(p),'path':prefix+n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()})
with (O/'uploads.json').open('w') as f:print(json.dumps(rows,indent=2),file=f)
print(json.dumps({'files':len(rows),'bytes':sum(x['bytes'] for x in rows)}))
