import pathlib,json,hashlib,urllib.request,time,datetime,sys,zipfile,importlib.util,os
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');repo=B/'archive-repo';meta=json.loads((B/'r007-core68-upload-metadata-v1.json').read_text());commit=sys.argv[1];ns='projects/planning-search-constraints-simple-20261011';started=time.monotonic();rp=B/'r007-core68-remote-proof-v1.json'
def read(path):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+path,timeout=60) as f:return f.read()
latest=json.loads(read(ns+'/LATEST.json'));assert latest['sha256']==meta['latest']['sha256'];raw=read(ns+'/'+latest['manifest']);assert hashlib.sha256(raw).hexdigest()==latest['sha256'];m=json.loads(raw);index=json.loads(read(meta['pack']+'/index.json'));assert index==meta['index'];agg=hashlib.sha256();localagg=hashlib.sha256();parts=[]
for x in meta['parts']:
 h=hashlib.sha256();n=0
 with urllib.request.urlopen('https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/'+x['remote'],timeout=60) as f:
  while q:=f.read(1048576):h.update(q);agg.update(q);n+=len(q)
 assert n==x['bytes'] and h.hexdigest()==x['sha256'];lh=hashlib.sha256()
 with open(x['local'],'rb') as f:
  while q:=f.read(1048576):lh.update(q);localagg.update(q)
 assert lh.hexdigest()==h.hexdigest();parts.append({'path':x['remote'],'bytes':n,'sha256':h.hexdigest()});rp.write_text(json.dumps({'commit':commit,'complete':False,'manifest_sha256':latest['sha256'],'parts':parts},indent=2));print(json.dumps({'remote_parts_verified':len(parts),'total':len(meta['parts'])}),flush=True)
assert agg.hexdigest()==localagg.hexdigest()==index['sha256'] and sum(x['bytes'] for x in parts)==index['bytes'];spec=importlib.util.spec_from_file_location('official_archive',repo/ns/'archive_store.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);os.posix_fadvise=lambda *args:None;members=[x for x in m['files'] if x['pack']==meta['pack']];rawtotal=0
with zipfile.ZipFile(a.PartsReader(repo,meta['pack'])) as z:
 assert set(z.namelist())=={x['member'] for x in members}
 for x in members:
  h=hashlib.sha256();n=0
  with z.open(x['member']) as f:
   while q:=f.read(1048576):h.update(q);n+=len(q)
  assert n==x['bytes'] and h.hexdigest()==x['sha256'],x['path'];rawtotal+=n
p={'commit':commit,'complete':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':latest['sha256'],'parts':parts,'whole_pack_sha256':agg.hexdigest(),'whole_pack_bytes':index['bytes'],'all_new_members':len(members),'all_new_raw_bytes':rawtotal,'forensic_deferred_count':latest['forensic_deferred_count'],'forensic_deferred_raw_bytes':latest['forensic_deferred_raw_bytes'],'scope':'Immutable remote full manifest/index/all29 new compressedparts and wholeSHA readback, matched localcompressedbytes then all374 new ZIPmembers rawbytes/SHA verified. Core68 current canonical control, source/contracts/nativeR007complete12results/logs/VAL/graphqualifications/ledger and prepared unexecuted L2, allpriorhistoryoverlay. Explicit42 noncanonical rawtemporary/staging objects retained locally/deferred; not full allrawfilesystem or per-split graph proof. No new native measurement from archival.','wall_seconds':time.monotonic()-started};rp.write_text(json.dumps(p,indent=2));print(json.dumps({k:v for k,v in p.items() if k!='parts'}),flush=True)
