import pathlib,json,subprocess,hashlib,zipfile,datetime,resource,time
resource.setrlimit(resource.RLIMIT_AS,(384*1024**2,384*1024**2));B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');D=B/'memory-wait-publication';repo=B/'archive-repo';commit='d3f93e71c2f2ada7ac4f5a39a064fe9fb120600c';es=json.loads((D/'publish-files.json').read_text());manifest=json.loads((D/'supplement-manifest.json').read_text());t=time.monotonic();peak=0;checked=[];zip_path=D/'remote-readback-supplement.zip';parts={x['path'] for x in manifest['parts']}
with zip_path.open('wb') as out:
 for row in es:
  m=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());peak=max(peak,m);assert m<7800000000
  p=subprocess.Popen(['git','-c','core.packedGitLimit=64m','-c','core.packedGitWindowSize=8m','-C',str(repo),'show',commit+':'+row['path']],stdout=subprocess.PIPE);h=hashlib.sha256();n=0
  for b in iter(lambda:p.stdout.read(1024*1024),b''):
   h.update(b);n+=len(b)
   if row['path'] in parts:out.write(b)
  assert p.wait()==0 and n==row['bytes'] and h.hexdigest()==row['sha256'],row['path'];checked.append({'path':row['path'],'bytes':n,'sha256':h.hexdigest()})
h=hashlib.sha256()
with zip_path.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
assert h.hexdigest()==manifest['zip_sha256'] and zip_path.stat().st_size==manifest['zip_bytes']
members=[]
with zipfile.ZipFile(zip_path) as z:
 assert set(z.namelist())=={x['path'] for x in manifest['members']}
 for row in manifest['members']:
  h=hashlib.sha256();n=0
  with z.open(row['path']) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
  assert n==row['bytes'] and h.hexdigest()==row['sha256'],row['path'];members.append({'path':row['path'],'bytes':n,'sha256':h.hexdigest()})
receipt={'complete':True,'commit':commit,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_source':'immutable remote Git objects fetched after publication; gitshow streaming, no local artifact substitution','files':checked,'zip_bytes':manifest['zip_bytes'],'zip_sha256':manifest['zip_sha256'],'members_verified':len(members),'member_raw_bytes':sum(x['bytes'] for x in members),'members':members,'scope':manifest['scope'],'full_window37_overlay':'pending headroom; this proof only supplemental72members/17directrecords, base7104 whole archive independently verified separately','verifier_recovery':'v1 gitshow mmap failed under inherited384MBAS limit before first read; v2 limits Gitpack mapping windows to8MB/64MB total, same raw identities. No corruption or native experiment failure.', 'maintenance_wall_seconds':time.monotonic()-t,'shared_peak_observed_bytes':peak};(D/'remote-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['files','members']}))
