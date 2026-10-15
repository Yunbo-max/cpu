"""Independently read every latest proof/metadata file at immutable commit, including exact Git blob identity."""
import pathlib,json,hashlib,urllib.request,sys,time
B=pathlib.Path(__file__).resolve().parent;O=B/'r009-publication-v2';commit=sys.argv[1];started=time.monotonic();entries=[]
for x in json.loads((O/'proof-upload-files.json').read_text()):
 url='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'];raw=urllib.request.urlopen(url,timeout=60).read();h=hashlib.sha256(raw).hexdigest();g=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert len(raw)==x['bytes'] and h==x['sha256'] and g==x['git_sha'],x['path'];entries.append({'path':x['path'],'bytes':len(raw),'sha256':h,'git_sha':g})
proof={'complete':True,'commit':commit,'independent_immutable_HTTP_files':len(entries),'entries':entries,'wall_seconds':time.monotonic()-started,'scope':'Every one of19 latest metadata/proof/verifier/guard/design files independently HTTP-read with bytes/SHA256/GitblobSHA. Full scientific packet verified separately. No solver or cleanup.'}
(O/'metadata-http-readback-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'complete':True,'files':len(entries),'commit':commit}))
