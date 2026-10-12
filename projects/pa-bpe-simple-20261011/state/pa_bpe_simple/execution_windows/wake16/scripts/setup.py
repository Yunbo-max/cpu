import subprocess,sys,json,time,resource
from pathlib import Path as P
start=time.monotonic();r=subprocess.run([sys.executable,'-m','pip','install','--target','deps','--no-cache-dir','--disable-pip-version-check','--report','output/install_report.json','tokenizers==0.22.1','numpy==2.2.6'],capture_output=True,text=True,timeout=100)
P('output/install.stdout').write_text(r.stdout);P('output/install.stderr').write_text(r.stderr);P('output/setup.json').write_text(json.dumps({'argv':r.args,'exit_code':r.returncode,'wall':time.monotonic()-start,'child_usage':list(resource.getrusage(resource.RUSAGE_CHILDREN))}));r.check_returncode()
