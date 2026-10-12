import importlib.util,json,resource,os
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(384000000,384000000))
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:1])
repo=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('archive',repo/'projects/planning-search-constraints-simple-20261011/archive_store.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
origin=repo.parent/'cpu_historical_import'
sources=json.loads((repo/'historical/IMPORT_SOURCES.json').read_text());entries=[]
manifest_path=repo/'historical/MANIFEST.json'
existing=json.loads(manifest_path.read_text())['files'] if manifest_path.exists() else []
for x in sources:
 p=origin/x['name'];sha=a.digest(p)
 if p.stat().st_size!=x['size_bytes']:raise ValueError('Downloaded size mismatch: '+x['name'])
 d=repo/'historical/objects'/sha
 if not d.exists():a.split_file(p,d)
 index=json.loads((d/'index.json').read_text())
 if index['sha256']!=sha:raise ValueError('Object collision')
 entries.append({**x,'sha256':sha,'object':str(d.relative_to(repo))})
 if p.suffix in {'.md','.json'} and p.stat().st_size<200000:
  dst=repo/'historical/reports'/x['name'];dst.parent.mkdir(exist_ok=True);dst.write_bytes(p.read_bytes())
 print(json.dumps({'file':x['name'],'bytes':x['size_bytes'],'parts':len(index['parts'])}),flush=True)
by_id={x['library_file_id']:x for x in existing}
by_id.update({x['library_file_id']:x for x in entries});entries=list(by_id.values())
a.write_json(manifest_path,{'source':'Current versions retrieved on2026-10-12; Library originals retained','files':entries,'total_original_bytes':sum(x['size_bytes'] for x in entries),'unique_objects':len({x['sha256'] for x in entries})})
