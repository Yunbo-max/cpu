"""Read-only forensic diagnosis; no SQL writes, recovery or experiment dispatch."""
import argparse
import hashlib
import json
import pathlib
import sqlite3
import struct
import zstandard


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def inspect(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    for member in manifest['members']:
        p = root / member['member']
        assert p.stat().st_size == member['bytes']
        assert sha(p) == member['sha256']
    db = root / 'canonical-W4-after-failed-official-recovery.sqlite3.raw'
    before = sha(db)
    connection = sqlite3.connect(db.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    connection.text_factory = bytes
    checks = [row[0].decode('utf-8', errors='replace') for row in connection.execute('PRAGMA quick_check(10)')]
    state = connection.execute('SELECT state FROM project WHERE id=1').fetchone()[0]
    try:
        json.loads(state)
        journal_error = None
    except (UnicodeDecodeError, ValueError) as error:
        journal_error = str(error)
    try:
        connection.execute('SELECT payload FROM runner_state WHERE id=1').fetchone()
        runner_error = None
    except sqlite3.DatabaseError as error:
        runner_error = str(error)
    physical_events = list(connection.execute('SELECT version,event_id,payload FROM events ORDER BY version'))
    connection.close()
    with (root / 'accepted-v3-complete-stdout.json.zst').open('rb') as f:
        with zstandard.ZstdDecompressor().stream_reader(f) as stream:
            exported = json.load(stream)
    attempts = exported['attempts']
    assert len(attempts) == exported['budget']['attempts_used'] == 69
    assert len({a['attempt_id'] for a in attempts}) == 69
    assert exported['budget']['reserved_seconds'] == 0
    active = [a['attempt_id'] for a in attempts if a['state'] in {'reserved', 'dispatched', 'running', 'reconcile_required'}]
    assert not active
    history = exported['journal']['history']
    history_by_version = {e['version']: e for e in history}
    mismatches = []
    for version, event_id, payload in physical_events:
        entry = history_by_version.get(version)
        expected_id = '__initialize__' if version == 0 else entry['event'].get('event_id') if entry else None
        if not entry or expected_id != event_id.decode() or entry['event'] != json.loads(payload):
            mismatches.append(version)
    assert not mismatches
    assert sha(db) == before
    return {
        'schema': 1, 'sqlite_version': sqlite3.sqlite_version,
        'input_commit': '1be044320c95ef1080fc72577c8d6a4bb5913908',
        'manifest_sha256': sha(root / 'manifest.json'),
        'canonical_raw_sha256_before_and_after': before,
        'readonly_immutable': True, 'quick_check': checks,
        'journal_utf8_json_error': journal_error, 'runner_table_error': runner_error,
        'readable_physical_events': len(physical_events),
        'exported_history_events': len(history), 'shared_event_mismatches': mismatches,
        'exported_attempts': len(attempts), 'active_exported_attempts': active,
        'budget': exported['budget'], 'queued_tasks': [t['task_id'] for t in exported['tasks'] if t['state'] == 'queued'],
        'exported_scoped_cycles': exported['research_cycle_count'],
        'preserved_export_source_digest': exported['source']['digest'],
        'valid_control_restoration': False, 'solver_launched': False,
        'reason': 'Public JSON export preserves observations and intent but omits private runner fields needed for an exact writable controller restoration. No production state was rebuilt or overwritten.',
        'origin_of_corruption': 'unresolved; current structural and text corruption reproduced independently; not evidence of insufficient CPU',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=pathlib.Path)
    args = parser.parse_args()
    result = inspect(args.root)
    (args.root / 'debug-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['readonly_immutable', 'runner_table_error', 'readable_physical_events', 'exported_history_events', 'shared_event_mismatches', 'exported_attempts', 'valid_control_restoration']}))
