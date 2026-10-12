import sys,resource,time,json,runpy
from pathlib import Path
output=Path(sys.argv[1]);script=sys.argv[2];sys.argv=sys.argv[2:]
start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF);code=0
try:runpy.run_path(script,run_name='__main__')
except BaseException as e:
 code=e.code if isinstance(e,SystemExit) and isinstance(e.code,int) else 1
 raise
finally:
 after=resource.getrusage(resource.RUSAGE_SELF)
 output.write_text(json.dumps({'argv':sys.argv,'exit_code':code,'wall_seconds':time.monotonic()-start,'user_cpu_seconds':after.ru_utime-before.ru_utime,'system_cpu_seconds':after.ru_stime-before.ru_stime,'peak_rss_bytes':after.ru_maxrss*1024,'scope':'single Python scientific process including wrapper; no subprocesses'},indent=2)+'\n')
