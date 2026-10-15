"""Same-channel independent HTTP is now observed available on new v5 packet.
Preserve original cancelled authorization; verify old/current immutable batches separately.
"""
import pathlib,json,hashlib,urllib.request,datetime,concurrent.futures
O=pathlib.Path('/dev/shm/r014-terminal-publication-v5');D=O/'metadata-remote-v2';D.mkdir(exist_ok=False)
cases=[('db1e7841891c2f6c25672ceee470c6846b38740f',pathlib.Path('/dev/shm/r014-queued-publication-v1/proof-publish-v2/uploads.json')),('77e560719816c1163d75853c3d145f9f5b9d27e5',pathlib.Path('/dev/shm/r014-queued-publication-v1/readback-pending-v1/uploads.json')),('1a8e3de69169fc1e441f9ca323e728f848585274',O/'metadata-v5/uploads.json')]
# Fresh evidence of permitted access on this exact HTTP channel, not alternate connector retry.
m=json.loads((O/'manifest.json').read_text());f=O/'remote/part-000.bin';assert f.stat().st_size==m['parts'][0]['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==m['parts'][0]['sha256']
def get(item):
 commit,x=item
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as f:b=f.read()
 assert (len(b),hashlib.sha256(b).hexdigest(),hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest())==(x['bytes'],x['sha256'],x['git_sha']),x['path']
 p=D/commit/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return {'commit':commit,**{k:x[k] for k in ['path','bytes','sha256','git_sha']}}
items=[(c,x) for c,p in cases for x in json.loads(p.read_text())]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:checked=list(pool.map(get,items))
p={'complete':True,'verified_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'access_recovery_basis':'New v5 packet independent immutableHTTP manifest/part SHA success observed first on same urllib channel. Prior authorization cancellation retained; no alternate-channel bypass.','batches':[{'commit':c,'files':sum(x['commit']==c for x in checked)} for c,_ in cases],'all_changed_metadata_bytes_SHA256_GitSHA_independent_HTTP_verified':True,'files':checked,'scope':'Metadata only, does not turn native/witness/audit into success; new packet whole-member verification separate. Original cancellation is an historical failure, now old metadata gap independently closed.'}
with (O/'metadata-readback-recovered-proof-v2.json').open('x') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps({'complete':True,'batches':p['batches']}))
