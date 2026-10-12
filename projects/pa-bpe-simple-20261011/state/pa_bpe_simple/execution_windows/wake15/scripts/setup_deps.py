import sys,runpy
from pathlib import Path
assert int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())>=536870912, 'memory_wait_required'
sys.argv=['pip','install','--disable-pip-version-check','--no-deps','--target','deps','--report','output/dependencies.json','pyarrow==21.0.0','tokenizers==0.22.1']
runpy.run_module('pip',run_name='__main__')
