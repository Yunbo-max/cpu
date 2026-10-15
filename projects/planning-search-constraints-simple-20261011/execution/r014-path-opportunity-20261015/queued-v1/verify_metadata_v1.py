import pathlib,json,hashlib,urllib.request,sys,datetime,concurrent.futures
O=pathlib.Path('/dev/shm/r014-queued-publication-v1');D=O/'metadata-remote';D.mkdir(exist_ok=False);commit=sys.argv[1];u=json.loads((O/'proof-publish-v2/uploads.json').read_text())
def get(x):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as f:b=f.read()
 assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'] and hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()==x['git_sha']
 p=D/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return {k:x[k] for k in ['path','bytes','sha256','git_sha']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:checked=list(pool.map(get,u))
p={'complete':True,'metadata_commit':commit,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_changed_metadata_proof_source_bytes_SHA256_GitSHA_independent_immutable_HTTP_verified':True,'files':checked,'scope':'New queuedR014 metadata batch; no R014 native or cycle, packet fullverification separate'}
with (O/'metadata-readback-proof-v1.json').open('x') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps({'complete':True,'files':len(checked),'metadata_commit':commit}))
