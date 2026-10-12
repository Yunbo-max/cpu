import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("cpio", Path(__file__).with_name("checkpoint_io.py"))
cpio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpio)


class CheckpointTests(unittest.TestCase):
    def test_reject_unsafe_paths(self):
        for value in ("/tmp/x", "../x", "a/../x", "a//x", "a\\x"):
            with self.assertRaises(ValueError):
                cpio.relative(value)
        self.assertEqual(cpio.relative("a/b.json").as_posix(), "a/b.json")

    def test_backup_is_repeatable_and_preserves_new_wal_data(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.sqlite3"
            c = sqlite3.connect(path)
            try:
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("CREATE TABLE receipts(id INTEGER PRIMARY KEY, outcome TEXT)")
                c.execute("INSERT INTO receipts VALUES(1, 'retained failure')")
                c.commit()
                before = cpio.sqlite_backup_digest(path)
                self.assertEqual(before, cpio.sqlite_backup_digest(path))
                c.execute("INSERT INTO receipts VALUES(2, 'new record must block cleanup')")
                c.commit()
                self.assertNotEqual(before, cpio.sqlite_backup_digest(path))
            finally:
                c.close()


if __name__ == "__main__":
    unittest.main()
