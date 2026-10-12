import sys,runpy
from pathlib import Path
assert int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())>=402653184,'memory_wait_required'
sys.argv=['pip','install','--disable-pip-version-check','--no-deps','--target','native_deps','--report','output/numpy_dependency.json','numpy==2.2.6']
runpy.run_module('pip',run_name='__main__')
