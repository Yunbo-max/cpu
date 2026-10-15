"""New immutable metadata readback destination; never overwrite earlier proof files."""
import pathlib,json,urllib.request,hashlib,sys,datetime
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';commit=sys.argv[1];rows=json.loads((B/sys.argv[2]).read_text());done=[]
for x in rows:
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as r:data=r.read()
 assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['sha256'],('HTTPcontent',x['path'])
 actual=hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest();assert actual==x['git_sha'],('Gitblob',x['path']);done.append({'path':x['path'],'bytes':len(data),'sha256':x['sha256'],'git_sha':actual})
out={'complete':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'metadata_files':len(done),'all_SHA256_bytes_GitSHA_match':True,'files':done,'scope':'Exact immutable published completion metadata/proof/verifier bytes and Git identities; not scientific approval or cleanup authorization'}
p=B/sys.argv[3]
with p.open('x') as f:print(json.dumps(out,indent=2),file=f)
print(json.dumps(out))
