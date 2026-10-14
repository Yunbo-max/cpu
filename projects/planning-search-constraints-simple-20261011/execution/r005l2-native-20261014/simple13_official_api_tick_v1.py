"""Call frozen Simple13 public supervised tick API; no CLI/source/SQLite changes."""
import pathlib,sys,json
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart')
sys.path.insert(0,str(B/'rsi-simple-13/scripts'))
from simple_runner import SimpleRunner
assert len(sys.argv)==2
print(json.dumps(SimpleRunner(sys.argv[1]).tick()))
