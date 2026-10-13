import pathlib,json,hashlib,urllib.request,time,tarfile,zstandard,datetime
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');m=json.loads((B/'r007-idle-coordinator-copies-manifest-v1.json').read_text());commit=__import__('sys').argv[1];start=time.monotonic();whole=hashlib.sha256();parts=[]
for x in m['parts']:
 url=f'https://raw.githubusercontent.com/Yunbo-max/cpu/{commit}/{x["path"]}';h=hashlib.sha256();n=0
 with urllib.request.urlopen(url,timeout=60) as source:
  assert source.status==200
  while q:=source.read(1048576):h.update(q);whole.update(q);n+=len(q)
 assert n==x['bytes'] and h.hexdigest()==x['sha256'];parts.append({'path':x['path'],'bytes':n,'sha256':h.hexdigest()})
 if len(parts)%4==0:print(json.dumps({'independent_immutable_remote_parts':len(parts)}),flush=True)
assert sum(x['bytes'] for x in parts)==m['bytes'] and whole.hexdigest()==m['sha256'];expected=m['members'];seen=[]
# Full local compressed bytes must equal the full independently downloaded immutable remote stream.
lh=hashlib.sha256()
with open(m['pack_file'],'rb') as p:
 while q:=p.read(1048576):lh.update(q)
assert lh.hexdigest()==whole.hexdigest()
with open(m['pack_file'],'rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded,tarfile.open(fileobj=decoded,mode='r|') as tar:
 for index,item in enumerate(tar):
  assert index<len(expected);original=expected[index]
  assert item.name==original['member'] and item.size==original['bytes'];h=hashlib.sha256();n=0
  with tar.extractfile(item) as raw:
   while q:=raw.read(1048576):h.update(q);n+=len(q)
  assert n==original['bytes'] and h.hexdigest()==original['sha256'];seen.append({'member':item.name,'bytes':n,'sha256':h.hexdigest()})
assert len(seen)==len(expected)==136
proof={'commit':commit,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'scope':'Full immutable remote compressed-byte readback and complete136 decompressed raw member identity proof. This is idle coordinator operational evidence, not full68 window or native experiment. Current control and native results excluded from cleanup targets','parts':parts,'pack_sha256':whole.hexdigest(),'pack_bytes':m['bytes'],'verified_complete_prefix_count':len(seen),'verified_complete_prefix_raw_bytes':sum(x['bytes'] for x in seen),'verified_complete_prefix_members':seen,'wall_seconds':time.monotonic()-start};(B/'r007-idle-coordinator-copies-remote-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k not in ['parts','verified_complete_prefix_members']},indent=2))
