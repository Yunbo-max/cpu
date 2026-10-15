"""Full changed metadata byte/SHA256/Git blob readback at immutable commit."""
import pathlib,json,hashlib,urllib.request,sys,datetime,concurrent.futures
C=pathlib.Path(__file__).resolve().parent;O=C/'planning-resume-20261014/r012-terminal-publication';P=O/'proof-publish';D=O/'metadata-remote';D.mkdir(exist_ok=False);commit=sys.argv[1]
uploads=json.loads((P/'uploads.json').read_text())
def get(x):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as f:raw=f.read()
 assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256']
 git=hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest();assert git==x['git_sha']
 p=D/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 return {'path':x['path'],'bytes':len(raw),'sha256':x['sha256'],'git_sha':git}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:checked=list(pool.map(get,uploads))
proof={'complete':True,'metadata_commit':commit,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_changed_metadata_full_independent_immutable_HTTP_bytes_SHA256_GitSHA_verified':True,'files':checked,'scope':'Only this metadata/proof/engineering source batch; packet21parts/138members/9derived have separate complete remote proof, no native rerun or historical bulk redownload'}
with (O/'metadata-readback-proof-v1.json').open('x') as f:print(json.dumps(proof,indent=2),file=f)
print(json.dumps({'complete':True,'files':len(checked),'metadata_commit':commit}))
