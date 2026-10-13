from pathlib import Path
import importlib.util,json,hashlib,zipfile,sqlite3,resource,datetime,subprocess,os
resource.setrlimit(resource.RLIMIT_AS,(384000000,384000000))
s=importlib.util.spec_from_file_location('arc','planning_recovery_26/projects/planning-search-constraints-simple-20261011/archive_store.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
r=Path('planning_verify_r005').resolve();b=r/'projects/planning-search-constraints-simple-20261011';latest=json.loads((b/'LATEST.json').read_text());mp=b/latest['manifest'];assert a.digest(mp)==latest['sha256'];m=json.loads(mp.read_text());tags=['r005-executed-20261013T1500','r006-source-audit-20261013T1510'];zs={};n=0;db=[];parts=[]
for tag in tags:
 pack='projects/planning-search-constraints-simple-20261011/packs/'+tag;reader=a.PartsReader(r,pack)
 for p in reader.meta['parts']:
  f=reader._path(pack+'/'+p['path']);assert f.stat().st_size==p['bytes'] and a.digest(f)==p['sha256'];parts.append({'path':pack+'/'+p['path'],'sha256':p['sha256'],'bytes':p['bytes']})
 zs[pack]=zipfile.ZipFile(reader)
for x in m['files']:
 if x['pack'] not in zs:continue
 h=hashlib.sha256();size=0;dbbytes=bytearray() if x.get('sqlite_backup') else None
 with zs[x['pack']].open(x['member']) as f:
  while chunk:=f.read(1048576):
   h.update(chunk);size+=len(chunk)
   if dbbytes is not None:dbbytes.extend(chunk)
 assert h.hexdigest()==x['sha256'] and size==x['bytes'],x['path'];n+=1
 if dbbytes is not None:
  p=Path('/tmp/planning-verify-db.sqlite');p.write_bytes(dbbytes);c=sqlite3.connect(str(p));v=c.execute('pragma integrity_check').fetchall();c.close();p.unlink();assert v==[('ok',)],v;db.append({'path':x['path'],'integrity_check':'ok'})
for z in zs.values():z.close()
report={'commit':subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip(),'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_network_clone':True,'manifest_sha256':latest['sha256'],'total_manifest_members':len(m['files']),'new_pack_members_stream_verified':n,'parts':parts,'databases':db,'historical_objects':'preserved by overlay; not redownloaded in this new-pack verification','status':'verified'}
Path('planning_simple/windows/W0003/evidence/github-independent-r005-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
