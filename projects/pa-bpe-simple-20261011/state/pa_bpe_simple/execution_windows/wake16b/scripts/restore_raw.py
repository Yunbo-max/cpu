import sys,json,zipfile,shutil,datetime
from pathlib import Path as P
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/restore_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':805306368}));assert free>=805306368,'memory_wait_required'
sys.path.insert(0,json.loads(P('evidence/archive_binding.json').read_text())['archive_root'])
import cache_io
P('raw').mkdir(exist_ok=True)
r=cache_io.restore_archive('825a8c063b19d4b1dc21f8a540ea2acbe5e11fa1da1cd6bfdeac5200c6805b6c',str(P('raw/bundle.zip').resolve()))
z=zipfile.ZipFile('raw/bundle.zip');names=z.namelist();out={}
for l in ['en','fr','es']:
 matches=[n for n in names if n.endswith('/'+l+'.zip') or n==l+'.zip'];assert len(matches)==1
 with z.open(matches[0]) as src,P('raw/'+l+'.zip').open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
 out[l]={'member':matches[0],'sha256':cache_io.sha256(P('raw/'+l+'.zip'))}
 spec=json.loads(P('inputs/source_manifest.json').read_text())['archives'][l];assert out[l]['sha256']==spec['expected_sha256']
P('output/archive_restore.json').write_text(json.dumps({'bundle':r,'archives':out,'raw_text_inspected':False},indent=2))
