"""Recheck light addendum remotely and serialize valid JSON proof (no inline escaping)."""
import pathlib,json,urllib.request,hashlib,zipfile,io,datetime,sys
B=pathlib.Path(__file__).resolve().parent/'planning-resume-20261014';commit=sys.argv[1];rows=json.loads((B/'r010-running-publication/uploads.json').read_text());contents={}
for x in rows:
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['path'],timeout=60) as src:data=src.read()
 assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['sha256'],x['path']
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()==x['git_sha'];contents[pathlib.PurePosixPath(x['path']).name]=data
m=json.loads(contents['manifest.json']);z=zipfile.ZipFile(io.BytesIO(contents['running-evidence-addendum.zip']));assert set(z.namelist())==set(m['members'])
for n,x in m['members'].items():
 data=z.read(n);assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['sha256'],n
out={'complete':True,'commit':commit,'metadata_files':len(rows),'new_zip_members':len(m['members']),'scope':'Light post22 evidence only; not consistent post22 control or complete scored batch','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'v1_serialization_incident':'Remote verification succeeded, but inline proof writer appended literal backslash+n causing invalid trailing JSON. Original proof/log retained. v2 rechecks all remote bytes and writes proper JSON; engineering serializer error, not native/data corruption.'}
p=B/'r010-running-publication/remote-proof-v2.json'
with p.open('x') as f:print(json.dumps(out,indent=2),file=f)
assert json.loads(p.read_text())==out;print(json.dumps(out))
