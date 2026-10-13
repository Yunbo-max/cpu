import argparse,resource,subprocess,sys,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--sas',required=True);p.add_argument('--binary',required=True);p.add_argument('--search',required=True);a=p.parse_args()
resource.setrlimit(resource.RLIMIT_CPU,(600,601));resource.setrlimit(resource.RLIMIT_AS,(3145728000,3145728000))
with open(a.sas,'rb') as f:r=subprocess.run([a.binary,'--search',a.search],stdin=f)
code=r.returncode if r.returncode>=0 else 128-r.returncode
pathlib.Path('native-exit-status.json').write_text(json.dumps({'native_process_returncode':r.returncode,'wrapper_exit_code':code,'native_CPU_soft_seconds':600,'native_CPU_hard_seconds':601,'native_AS_bytes':3145728000,'scope':'Frozen SAS-only native solver, no PDDL translation rerun'},indent=2)+'\n');sys.exit(code)
