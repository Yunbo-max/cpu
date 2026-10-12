"""Append additional resolved CPU history without replacing prior entries."""
import importlib.util,json,os,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(256000000,256000000))
repo=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('archive',repo/'projects/planning-search-constraints-simple-20261011/archive_store.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
origin=repo.parent/'cpu_historical_extra_import';target=repo/'historical/MANIFEST.json';manifest=json.loads(target.read_text())
sources=json.loads((repo/'historical/EXTRA_SOURCES.json').read_text())['items'];by_id={x['library_file_id']:x for x in manifest['files']}
for x in sources:
    p=origin/x['name'];sha=a.digest(p);assert p.stat().st_size==x['size_bytes']
    d=repo/'historical/objects'/sha
    if not d.exists():a.split_file(p,d)
    assert json.loads((d/'index.json').read_text())['sha256']==sha
    entry={k:x.get(k) for k in ['name','library_file_id','file_id','version_id','size_bytes','created_at','modified_at']}
    entry.update(sha256=sha,object=str(d.relative_to(repo)));by_id[x['library_file_id']]=entry
    if p.suffix in {'.md','.json','.html'} and p.stat().st_size<200000:
        dst=repo/'historical/reports'/x['name']
        if dst.exists() and a.digest(dst)!=sha:raise ValueError('Report basename collision')
        dst.write_bytes(p.read_bytes())
manifest.update(files=list(by_id.values()),total_original_bytes=sum(x['size_bytes'] for x in by_id.values()),unique_objects=len({x['sha256'] for x in by_id.values()}))
a.write_json(target,manifest);print(json.dumps({'historical_files':len(by_id),'total_original_bytes':manifest['total_original_bytes'],'unique_objects':manifest['unique_objects']}))
