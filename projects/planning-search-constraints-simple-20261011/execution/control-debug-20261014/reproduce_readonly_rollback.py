"""Distinguish a pending rollback from permissions using a disposable database."""
import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory(prefix='sqlite-hot-journal-') as directory:
    path = pathlib.Path(directory) / 'test.sqlite3'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, data BLOB)')
        connection.executemany('INSERT INTO t VALUES (?,?)', [(i, b'x' * 4096) for i in range(128)])
    code = """
import sqlite3,sys,os
c=sqlite3.connect(sys.argv[1])
c.execute('PRAGMA cache_size=2')
c.execute('BEGIN IMMEDIATE')
c.execute('UPDATE t SET data=?', (b'y'*4096,))
os._exit(0)
"""
    subprocess.run([sys.executable, '-c', code, str(path)], check=True)
    journal = pathlib.Path(str(path) + '-journal')
    assert journal.exists()
    result = {'disposable_fixture': True, 'journal_present_before': True, 'database_owner_writable': bool(path.stat().st_mode & 0o200)}
    try:
        connection = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
        connection.execute('SELECT count(*) FROM t').fetchone()
        result['readonly_error'] = None
    except sqlite3.DatabaseError as error:
        result['readonly_error'] = str(error)
        result['readonly_error_code'] = getattr(error, 'sqlite_errorcode', None)
        result['readonly_error_name'] = getattr(error, 'sqlite_errorname', None)
    finally:
        connection.close()
    assert result['readonly_error_name'] == 'SQLITE_READONLY_ROLLBACK'
    with sqlite3.connect(path) as connection:
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert connection.execute('SELECT count(*) FROM t WHERE data=?', (b'x'*4096,)).fetchone()[0] == 128
    result['normal_rw_recovery_fixture_valid'] = True
    result['scope'] = 'Explains how a readonly read can require rollback despite writable permissions. Does not reproduce or establish the original corruption cause; actual forensic DB separately fails structural checks.'
    output = pathlib.Path(__file__).with_name('readonly-rollback-reproduction.json')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
