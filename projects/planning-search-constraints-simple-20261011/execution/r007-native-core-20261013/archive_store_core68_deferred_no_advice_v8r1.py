"""Officialoverlay snapshot; explicitly defer pinnedinvalid orphan images, preserve allprior members and raw originals."""
import pathlib,json,os,sys,importlib.util,hashlib,resource
resource.setrlimit(resource.RLIMIT_AS,(384000000,384000000));B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');P=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple');repo=B/'archive-repo';ns='projects/planning-search-constraints-simple-20261011';tag=sys.argv[1];catalog=json.loads((P/'windows/W0004/evidence/R007-core68-deferred-temporary-catalog-v2.json').read_text());bad={x['path'] for x in catalog['files']};assert len(bad)>0;assert all('/.research-autopilot/.simple-loop.sqlite3.' in x or '.rsync-tmp' in x for x in bad);assert 'windows/W0004/.research-autopilot/simple-loop.sqlite3' not in bad
# Allsha identities already measured atquietboundary; noactivecontrol excluded, nooriginal mutation.
realwalk=os.walk

def walk(root,*args,**kwargs):
 for here,ds,fs in realwalk(root,*args,**kwargs):
  filtered=[]
  for name in fs:
   p=pathlib.Path(here)/name
   try:rel=str(p.relative_to(P))
   except ValueError:rel=None
   if rel not in bad:filtered.append(name)
  yield here,ds,filtered
os.walk=walk;os.posix_fadvise=lambda *args:None
spec=importlib.util.spec_from_file_location('archive_official',repo/ns/'archive_store.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);out=a.snapshot(repo,P,'planning-search-constraints-simple-20261011',tag,overlay=True);mp=repo/ns/out['manifest'];m=json.loads(mp.read_text());m['forensic_deferred']=catalog;m['excluded'] +=[{'path':x['path'],'bytes':x['bytes'],'sha256':x['sha256'],'reason':'Pinned noncanonical idle temporary/staging raw object; validity/cause not asserted; newrawbytes retained local, deferredexplicitly, canonical control DB/currentscientificresults archived; prior manifestmember retained byoverlay if present'} for x in catalog['files']];mp.write_text(json.dumps(m,indent=2)+'\n');out['sha256']=hashlib.sha256(mp.read_bytes()).hexdigest();out['forensic_deferred_count']=len(bad);out['forensic_deferred_raw_bytes']=catalog['raw_bytes'];out['snapshot_scope']='Currentvalidcontrol/source/contracts/nativeoutputs/receipts/VAL/logs/budgets, allpriorhistoryoverlay;Pinned raw noncanonical temporary/staging objects explicitlydeferred, not allsourcebytes complete';(repo/ns/'LATEST.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
