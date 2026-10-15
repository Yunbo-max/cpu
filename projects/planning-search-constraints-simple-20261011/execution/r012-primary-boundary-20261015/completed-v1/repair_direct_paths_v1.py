"""Before any Git upload, repair duplicate direct-copy basenames; archive bytes unchanged."""
import pathlib,json,hashlib
C=pathlib.Path(__file__).resolve().parent;B=C/'planning-resume-20261014';O=B/'r012-terminal-publication'
u=json.loads((O/'uploads.json').read_text());folder='projects/planning-search-constraints-simple-20261011/execution/r012-primary-boundary-20261015/completed-v1/'
old=[x['path'] for x in u];assert len(old)-len(set(old))==1
for x in u:
 if x['path'].endswith('/result.json'):
  x['path']=folder+('source-crosswalk-result.json' if 'R012-primary-recipe-source-crosswalk' in x['local'] else 'author-ops-pilot-result.json')
def add(p,n):
 raw=p.read_bytes();u.append({'local':str(p),'path':folder+n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()})
add(C/'verify_r012_terminal_v2.py','verify_remote_v2.py');add(pathlib.Path(__file__),'repair_direct_paths_v1.py');add(O/'uploads.json','original-preupload-duplicate-paths-v1.json')
for name in ['metrics.json','stdout.log','stderr.log']:add(B/'recovery-20261015/r012-terminal-archive-v1-guard'/name,'archive-guard-'+name)
assert len(u)==len({x['path'] for x in u})
with (O/'uploads-v2.json').open('x') as f:print(json.dumps(u,indent=2),file=f)
with (O/'direct-copy-path-repair-v1.json').open('x') as f:print(json.dumps({'original_duplicate_count':1,'corrected_duplicate_count':0,'detected_before_any_upload_or_commit':True,'full_ZIP_members_and_scientific_outputs_unchanged':True,'meaning':'Only preupload direct-copy path collision; not native or data corruption'},indent=2),file=f)
print(json.dumps({'files':len(u),'unique_paths':len({x['path'] for x in u})}))
