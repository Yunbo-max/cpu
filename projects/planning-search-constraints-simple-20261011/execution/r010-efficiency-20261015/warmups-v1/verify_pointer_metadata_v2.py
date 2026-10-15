"""Immutable HTTP proof-pointer bytes + SHA256 + Git blob identity, explicit NUL byte."""
import pathlib,json,urllib.request,hashlib,sys,datetime
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';commit=sys.argv[1];rows=json.loads((B/'r010-warmup-publication/proof-publish/uploads.json').read_text());done=[]
for x in rows:
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as r:data=r.read()
 assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['sha256'],('HTTPcontent',x['path'])
 actual=hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest();assert actual==x['git_sha'],('Gitblob',x['path'],actual,x['git_sha']);done.append({'path':x['path'],'bytes':len(data),'sha256':x['sha256'],'git_sha':actual})
out={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'metadata_files':len(done),'all_SHA256_bytes_GitSHA_match':True,'files':done,'v1_incident':'Inline v1 passed HTTP bytes/SHA256 then failed Git blob hash because escaped separator was backslash+0 instead of NUL. This v2 uses bytes([0]); verifier error, not remote corruption/nativefailure.'};p=B/'recovery-20261015/warmup-pointer-independent-readback-v2.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
