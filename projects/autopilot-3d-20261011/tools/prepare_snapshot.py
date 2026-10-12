#!/usr/bin/env python3
"""Build a small working snapshot and chunk immutable ZIPs for Git storage."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import zipfile

PROJECT = 'autopilot-3d-20261011'
PREFIX = 'projects/' + PROJECT
CHUNK = 4 * 1024 * 1024

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def split(path, kind, output):
    sha = digest(path)
    parts = []
    with path.open('rb') as stream:
        for index in range((path.stat().st_size + CHUNK - 1) // CHUNK):
            b = stream.read(CHUNK)
            part_sha = hashlib.sha256(b).hexdigest()
            rel = f'{PREFIX}/objects/{part_sha}.part'
            target = output / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if digest(target) != part_sha:
                    raise ValueError('Existing content-addressed part is corrupt')
            else:
                target.write_bytes(b)
            parts.append({'path': rel, 'bytes': len(b), 'sha256': part_sha})
    return {'name': path.name, 'kind': kind, 'bytes': path.stat().st_size,
            'sha256': sha, 'parts': parts}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True, type=Path)
    choice = p.add_mutually_exclusive_group(required=True)
    choice.add_argument('--history', type=Path, help='Initial complete historical ZIP')
    choice.add_argument('--previous-manifest', type=Path, help='Latest manifest for subsequent incremental snapshots')
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    root = a.root.resolve()
    checkpoint = json.loads((root / 'CHECKPOINT.json').read_text())
    if checkpoint['project_id'] != PROJECT or checkpoint['active_task_ids']:
        raise ValueError('Wrong project or active tasks')
    # Keep a nonblocking exclusive project lock for the entire snapshot.
    project_lock = (root / '.research-autopilot/runner/supervisor.lock').open('a+')
    fcntl.flock(project_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    a.output.mkdir(parents=True, exist_ok=True)
    active = a.output / 'active-working.zip'
    files, omitted = [], []
    known_history = {}
    previous = None
    if a.history:
        with zipfile.ZipFile(a.history) as z:
            known_history = {x['path']: x for x in json.loads(z.read('CHECKPOINT_INVENTORY.json'))['files']}
    else:
        previous = json.loads(a.previous_manifest.read_text())
        if previous['project_id'] != PROJECT:
            raise ValueError('Previous manifest project mismatch')
    excluded = {'.venv', '.git', '__pycache__', 'data'}
    with tempfile.TemporaryDirectory() as td:
        backup = Path(td) / 'state.sqlite3'
        with sqlite3.connect(root / '.research-autopilot/simple-loop.sqlite3') as src, sqlite3.connect(backup) as dst:
            state = json.loads(src.execute('select payload from runner_state').fetchone()[0])
            if any(x['state'] != 'terminal' for x in state['attempts'].values()):
                raise ValueError('Unsettled attempts')
            if src.execute('pragma integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Database integrity failure')
            src.backup(dst)
        with zipfile.ZipFile(active, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in sorted(root.rglob('*')):
                rel = f.relative_to(root)
                if not f.is_file() or f.is_symlink():
                    continue
                if any(x in excluded for x in rel.parts) or f.name.endswith(('-wal', '-shm', '.lock')):
                    continue
                # Initial cold separation requires exact archived bytes. Later snapshots
                # retain ALL non-reproducible working files, including every new result.
                candidate_cold = rel.parts[0] in ('notes', 'logs') and (f.stat().st_size > 1024*1024 or f.suffix == '.sqlite3' or f.name.endswith('.sqlite3-journal'))
                candidate_cold |= rel.parts[0] == 'results' and len(rel.parts) > 2 and rel.parts[1] not in ('R015', 'R016')
                known = known_history.get(str(rel))
                if candidate_cold and known and known['bytes'] == f.stat().st_size and known['sha256'] == digest(f):
                    omitted.append(str(rel)); continue
                source = backup if str(rel) == '.research-autopilot/simple-loop.sqlite3' else f
                b = source.read_bytes()
                info = zipfile.ZipInfo('autopilot_3d/' + str(rel))
                info.external_attr = (f.stat().st_mode & 0xFFFF) << 16
                z.writestr(info, b, compress_type=zipfile.ZIP_DEFLATED)
                files.append({'path': str(rel), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
            z.writestr('ARCHIVE_INVENTORY.json', json.dumps({'project_id': PROJECT, 'files': files, 'omitted_historical_paths': omitted, 'history_archive_sha256': digest(a.history) if a.history else None}, indent=2))
    active_record = split(active, 'active', a.output)
    active_record['name'] = f'active-seq{state["sequence"]}-{active_record["sha256"][:12]}.zip'
    if previous:
        archives = [dict(x, kind='snapshot') if x['kind'] == 'active' else x for x in previous['archives']]
        archives = [x for x in archives if x['sha256'] != active_record['sha256']]
    else:
        archives = [split(a.history, 'history', a.output)]
    archives.append(active_record)
    manifest = {'schema_version': 1, 'project_id': PROJECT, 'sequence': state['sequence'],
                'active_idea': checkpoint['idea'], 'library_fallback': previous.get('library_fallback') if previous else {'id': checkpoint['checkpoint_library_id'], 'version': 17, 'historical_only': True},
                'archives': archives,
                'policy': 'History is immutable. Restore active for routine work; fetch history only for missing evidence. Never delete local unuploaded changes.'}
    target = a.output / PREFIX / 'archive-manifest.json'
    target.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'manifest': str(target), 'active_files': len(files), 'omitted_historical_files': len(omitted), 'archives': [{k:v for k,v in x.items() if k != 'parts'} for x in archives]}))

if __name__ == '__main__':
    main()
