"""Original overlay protocol; unique outputs never advised, only unchanged remotely verified idle duplicates."""
import pathlib,json,hashlib,os,importlib.util,sys
repo=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart/archive-repo');root=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple');ns='projects/planning-search-constraints-simple-20261011';receipt=json.loads((root/'windows/W0004/evidence/R006-d75-remote-archive-verification.json').read_text());assert receipt['new_pack_member_verification']['all_zip_members_sha256_bytes_verified'];mp=repo/ns/'snapshots/r006-screen-graph-w4-20261013T1817.json';assert hashlib.sha256(mp.read_bytes()).hexdigest()==receipt['manifest_sha256'];manifest=json.loads(mp.read_text());allowed={x['path']:x for x in manifest['files'] if x['pack'].endswith('/r006-screen-graph-w4-20261013T1817') and x['bytes']>0};advice=os.posix_fadvise;os.posix_fadvise=lambda *args:None
spec=importlib.util.spec_from_file_location('archive',repo/ns/'archive_store.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);original=m.digest;hints=[]
def digest(p):
 result=original(p)
 try:rel=str(pathlib.Path(p).resolve().relative_to(root))
 except ValueError:return result
 x=allowed.get(rel)
 if x and x['sha256']==result and pathlib.Path(p).stat().st_size==x['bytes'] and '.research-autopilot/' not in rel and not rel.endswith(('.sqlite3','.db')) and pathlib.Path(p).name not in ['CHECKPOINT.json','CURRENT_EXECUTION.json','CURRENT_WINDOW.json','RESUME.md']:
  with pathlib.Path(p).open('rb') as f:advice(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
  hints.append({'path':rel,'sha256':result,'bytes':x['bytes']})
 return result
m.digest=digest
try:m.main()
finally:
 (repo/ns/'execution/r006-overhead-cpu-20261013/archive-cache-hints.json').parent.mkdir(parents=True,exist_ok=True)
 (repo/ns/'execution/r006-overhead-cpu-20261013/archive-cache-hints.json').write_text(json.dumps({'scope':'Hints only for unchanged idle same-project files with independently verified durable d75 new-pack members; no unique output/control/SQLite/global cache clear or deletion. This is not a corruption-cause conclusion.','hints':hints},indent=2)+'\n')
