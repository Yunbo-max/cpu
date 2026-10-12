import sys,json,runpy,datetime,hashlib
from pathlib import Path as P
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/damped_retry_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':536870912}));assert free>=536870912,'memory_wait_required'
sys.path.insert(0,json.loads(P('evidence/parent.json').read_text())['deps'])
plan=json.loads(P('candidate_plan.json').read_text())
argv=['scripts/damped_native.py','--input']+['../wake16/inputs/'+l+'.dict' for l in ['en','fr','es']]+['--dev']+['../wake16/output/v3_dev.'+l+'.dict' for l in ['en','fr','es']]+['--output','output/damped.codes','--dict-input','--symbols','1000','--num-workers','1','--variant','base']
sys.argv=argv
try:runpy.run_path('scripts/damped_native.py',run_name='__main__',init_globals={'TARGET_WEIGHTS':plan['weights']})
except SystemExit as e:
 if e.code not in (None,0):raise
assert len(P('output/damped.codes').read_text().splitlines())==1001
P('output/damped_result.json').write_text(json.dumps({'argv':argv,'weights':plan['weights'],'codes_sha256':hashlib.sha256(P('output/damped.codes').read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(P('candidate_plan.json').read_bytes()).hexdigest()},indent=2))
