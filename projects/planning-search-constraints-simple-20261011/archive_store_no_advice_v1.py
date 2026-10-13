"""Use original overlay/SQLite/identity snapshot protocol, without cache advice on unique new outputs."""
import os,runpy
from pathlib import Path
os.posix_fadvise = lambda *args: None
runpy.run_path(str(Path(__file__).with_name('archive_store.py')),run_name='__main__')
