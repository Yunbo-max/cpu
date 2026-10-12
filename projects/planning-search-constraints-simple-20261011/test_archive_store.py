import contextlib,importlib.util,io,json,os,sqlite3,tempfile,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('archive',Path(__file__).with_name('archive_store.py'));a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

class ArchiveChecks(unittest.TestCase):
 def test_roundtrip_incremental_and_live_wal(self):
  with tempfile.TemporaryDirectory() as td,contextlib.redirect_stdout(io.StringIO()):
   p=Path(td);src=p/'src';src.mkdir();repo=p/'repo';repo.mkdir()
   (src/'binary').write_bytes(os.urandom(200000));(src/'note').write_text('negative result retained')
   db=sqlite3.connect(src/'live.sqlite3');db.execute('pragma journal_mode=wal');db.execute('create table t(x)');db.execute('insert into t values(42)');db.commit()
   a.snapshot(repo,src,'test','s1');a.restore(repo,'test',p/'restored')
   self.assertEqual((p/'restored/binary').read_bytes(),(src/'binary').read_bytes())
   self.assertEqual(sqlite3.connect(p/'restored/live.sqlite3').execute('select x from t').fetchone()[0],42)
   old=json.loads((repo/'projects/test/snapshots/s1.json').read_text());(src/'note').write_text('new note');a.snapshot(repo,src,'test','s2')
   new=json.loads((repo/'projects/test/snapshots/s2.json').read_text());b1=next(x for x in old['files'] if x['path']=='binary');b2=next(x for x in new['files'] if x['path']=='binary');self.assertEqual(b1['pack'],b2['pack']);self.assertEqual(a.restore(repo,'test',None,verify=True),3);db.close()
 def test_corruption_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as td,contextlib.redirect_stdout(io.StringIO()):
   p=Path(td);src=p/'src';src.mkdir();repo=p/'repo';repo.mkdir();(src/'x').write_text('abc');a.snapshot(repo,src,'test','s1')
   dst=p/'dst';dst.mkdir();(dst/'x').write_text('irreplaceable')
   with self.assertRaises(ValueError):a.restore(repo,'test',dst)
   part=next(repo.rglob('part-*.bin'));part.write_bytes(b'bad')
   with self.assertRaises(ValueError):a.restore(repo,'test',None,verify=True)
 def test_paths(self):
  for x in ['../x','/x','a/../../x','a\\x','']:
   with self.assertRaises(ValueError):a.safe(x)
 def test_selective_workspace_overlay(self):
  with tempfile.TemporaryDirectory() as td,contextlib.redirect_stdout(io.StringIO()):
   p=Path(td);src=p/'src';src.mkdir();repo=p/'repo';repo.mkdir()
   (src/'history').write_bytes(os.urandom(2000));(src/'control').write_text('old')
   a.snapshot(repo,src,'test','full');subset=p/'subset'
   a.restore(repo,'test',subset,prefix='control');(subset/'control').write_text('new')
   a.snapshot(repo,subset,'test','delta',overlay=True);a.restore(repo,'test',p/'roundtrip')
   self.assertEqual((p/'roundtrip/history').read_bytes(),(src/'history').read_bytes())
   self.assertEqual((p/'roundtrip/control').read_text(),'new')
 def test_segment_boundary(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);data=os.urandom(33333);(p/'x').write_bytes(data);old=a.CHUNK;a.CHUNK=4096
   try:
    a.split_file(p/'x',p/'pack');r=a.PartsReader(p,'pack');r.seek(4000);self.assertEqual(r.read(12000),data[4000:16000]);r.seek(-20,2);self.assertEqual(r.read(),data[-20:])
   finally:a.CHUNK=old
if __name__=='__main__':unittest.main()
