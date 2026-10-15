"""Read all newly published metadata from immutable commit, exact SHA256/Git object binding."""
import pathlib,json,hashlib,urllib.request,datetime,sys
C=pathlib.Path(__file__).resolve().parent;O=C/'planning-resume-20261014/r011-terminal-compact-publication';P=O/'proof-publish';commit=sys.argv[1];rows=json.loads((P/'uploads.json').read_text());verified=[]
for x in rows:
    url='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path']
    with urllib.request.urlopen(url,timeout=60) as f:raw=f.read()
    assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'],x['path']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()==x['git_sha'],x['path']
    verified.append({k:x[k] for k in ['path','bytes','sha256','git_sha']})
proof={'complete':True,'commit':commit,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_metadata_and_proof_bytes_independent_immutable_HTTP':True,'files':verified}
with (O/'proof-metadata-readback-v2.json').open('w') as f:print(json.dumps(proof,indent=2),file=f)
print(json.dumps({'complete':True,'commit':commit,'files':len(verified)}))

