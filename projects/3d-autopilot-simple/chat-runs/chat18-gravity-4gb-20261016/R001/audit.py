"""R001: read-only audit of recovered historical evidence; never runs a solver."""
import ast
import csv
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import statistics
import sys
import time

root = Path(__file__).resolve().parent
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
t0, c0 = time.monotonic(), time.process_time()
resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
os.sched_setaffinity(0, [min(os.sched_getaffinity(0))])
cgroup = Path('/sys/fs/cgroup')
current = int((cgroup/'memory.current').read_text())
maximum = int((cgroup/'memory.max').read_text())
assert min(4000000000, maximum) - current >= 134217728, 'insufficient fresh headroom'
expected = {
 'handoff-wake24.md': '2313c7549cb80d230c9f2436f483f1838ee3d9122011e215ed2b80d8d456deda',
 'gravity_pose_tum_fr1xyz_v3.py': '8be5b35797b77e295f6dc7f4fe3f4bb31f69f7b7141aef47ac60cf2fc1c54e55',
 'raw.csv': '7e1edc3cd60752577facadc35ac055c2d84ef3aa8e3292f1eaf5682510496e6d'
}
for name, digest in expected.items():
 assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
with (root/'raw.csv').open(newline='') as f:
 rows = list(csv.DictReader(f))
assert len(rows) == 16
arms = ['up2pf_ori_ransac', 'p3p_ransac']
by = {a: {} for a in arms}
for r in rows:
 a, k = r['arm'], int(r['pair'])
 assert a in by and k not in by[a] and r['valid'] == '1'
 by[a][k] = r
assert all(set(by[a]) == set(range(8)) for a in arms)
metrics = ['rotation_error_deg', 'center_error_m', 'inliers']
medians = {a: {m: statistics.median(float(r[m]) for r in by[a].values()) for m in metrics} for a in arms}
wins = {m: sum((float(by[arms[0]][k][m]) > float(by[arms[1]][k][m])) if m == 'inliers' else (float(by[arms[0]][k][m]) < float(by[arms[1]][k][m])) for k in range(8)) for m in metrics}
# Check prior report, not a new efficacy criterion or tuned threshold.
reported = {'up2pf_ori_ransac': [0.378074, 0.025534, 46.5], 'p3p_ransac': [0.579298, 0.007348, 63.0]}
assert all(abs(medians[a][m]-v) <= 0.0000005 for a in arms for m,v in zip(metrics,reported[a]))
assert wins == {'rotation_error_deg': 5, 'center_error_m': 1, 'inliers': 0}
source = (root/'gravity_pose_tum_fr1xyz_v3.py').read_text()
tree = ast.parse(source)
def constant_value(n):
 if isinstance(n, ast.Constant) and isinstance(n.value, (int,float)): return n.value
 if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult): return constant_value(n.left)*constant_value(n.right)
 if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow): return constant_value(n.left)**constant_value(n.right)
 raise ValueError('nonconstant arithmetic')
limits=[]
for node in ast.walk(tree):
 if isinstance(node,ast.Call) and ast.unparse(node.func)=='resource.setrlimit':
  limits.append([constant_value(x) for x in node.args[1].elts])
K = next(ast.literal_eval(n.value.args[0]) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='K' for t in n.targets))
gravity = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='G' for t in n.targets)]
result = {
 'task_id':'R001-wake24-recovery-audit','scope':'historical data restoration and protocol-readiness audit; not new pose estimation',
 'claim_commit':'bd13765af9d19d790288ccce44def6eb63e67612',
 'source_archive_commit':'ca20639f3a44118d6807c471b2c6b9a2e73a6c22',
 'input_sha256':expected,'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'historical_rows':len(rows),'historical_pairs':8,'medians':medians,'up2_pair_wins':wins,'prior_report_rounding_reproduced':True,
 'source_audit':{'legacy_address_space_limits':limits,'user_ram_cap_bytes':4000000000,'legacy_limit_exceeds_new_cap':any(x>4000000000 for lim in limits for x in lim),'calibration_K':K,'gravity_assignment':gravity,'gravity_is_groundtruth_derived_in_this_script':True,'legacy_eigen_path_exists':Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/casadi/include/eigen3').exists(),'system_eigen_path_exists':Path('/usr/include/eigen3').exists()},
 'host':{'python':sys.version.split()[0],'cpu_affinity':list(os.sched_getaffinity(0)),'threads':int(next(s.split()[1] for s in Path('/proc/self/status').read_text().splitlines() if s.startswith('Threads:'))),'memory_current_before':current,'memory_max':maximum,'cpu_max':(cgroup/'cpu.max').read_text().strip(),'disk_free_bytes':shutil.disk_usage(root).free,'gpp':shutil.which('g++'),'numpy_installed':importlib.util.find_spec('numpy') is not None,'scipy_installed':importlib.util.find_spec('scipy') is not None,'oom_events':(cgroup/'memory.events').read_text().strip()},
 'start_utc':started,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'measured_wall_seconds':time.monotonic()-t0,'measured_cpu_seconds':time.process_time()-c0,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
 'new_solver_experiments':0,'new_scientific_cycles':0,'independent_reviewer_used':False,
 'next_action':'Preserve this recovered evidence. Recover original plans/solver pins; qualify a versioned 4 GB runtime and dataset-specific camera model before fresh fr2/xyz comparison. No retuning fr1, no claim that gravity intrinsically improves or harms deployment.'
}
with (root/'audit_result.json').open('x') as f: json.dump(result,f,indent=2); f.write('\n')
print(json.dumps(result,indent=2))
