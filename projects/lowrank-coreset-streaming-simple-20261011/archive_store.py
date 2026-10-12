#!/usr/bin/env python3
"""Lossless per-file content-addressed research snapshots; stdlib only.

Run pack only on a verified quiet-boundary checkpoint ZIP. Git publication and
remote readback remain separate mandatory steps before local deletion.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
PROJECT = 'lowrank-coreset-streaming-simple-20261011'
SOURCE_ROOT = 'lowrank_coreset_streaming_rsi_simple'
CHUNK = 4 * 1024 * 1024


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_rel(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value:
        raise ValueError('Unsafe member path')
    return p


def object_path(digest):
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid object digest')
    return ROOT / 'objects' / digest[:2] / digest[2:]


def object_parts(digest):
    path = object_path(digest)
    if path.exists():
        return [path]
    folder = ROOT / 'chunked' / digest
    parts = sorted(folder.glob('*'))
    if not parts or [p.name for p in parts] != [f'{i:06d}' for i in range(len(parts))]:
        raise ValueError('Missing or noncontiguous object chunks')
    return parts


def object_identity(digest):
    h = hashlib.sha256()
    size = 0
    for path in object_parts(digest):
        if path.is_symlink() or not path.is_file():
            raise ValueError('Unsafe object')
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
                size += len(block)
    return h.hexdigest(), size


def pack(archive):
    archive = Path(archive)
    entries = []
    with zipfile.ZipFile(archive) as z:
        manifest_name = SOURCE_ROOT + '/archive_manifest.json'
        manifest = json.loads(z.read(manifest_name))
        if manifest['project_id'] != PROJECT:
            raise ValueError('Wrong project')
        expected = {x['path']: x for x in manifest['members']}
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected) | {manifest_name}:
            raise ValueError('Archive membership mismatch')
        for name in sorted(names):
            p = safe_rel(name)
            if p.parts[0] != SOURCE_ROOT:
                raise ValueError('Wrong archive root')
            rel = str(PurePosixPath(*p.parts[1:]))
            safe_rel(rel)
            with tempfile.NamedTemporaryFile(dir=ROOT, delete=False) as f:
                temp = Path(f.name)
                with z.open(name) as src:
                    shutil.copyfileobj(src, f, length=1024 * 1024)
            digest = sha_file(temp)
            size = temp.stat().st_size
            if name in expected and (digest != expected[name]['sha256'] or size != expected[name]['bytes']):
                temp.unlink()
                raise ValueError('Archive hash mismatch: ' + name)
            dest = object_path(digest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                if sha_file(dest) != digest:
                    temp.unlink()
                    raise ValueError('Corrupted existing object')
                temp.unlink()
            else:
                os.replace(temp, dest)
            if size > 2 * CHUNK:
                folder = ROOT / 'chunked' / digest
                folder.mkdir(parents=True, exist_ok=True)
                with dest.open('rb') as src:
                    index = 0
                    while True:
                        block = src.read(CHUNK)
                        if not block:
                            break
                        part = folder / f'{index:06d}'
                        if part.exists() and part.read_bytes() != block:
                            raise ValueError('Conflicting chunk')
                        part.write_bytes(block)
                        index += 1
                # The original checkpoint and working source remain untouched.
                dest.unlink()
                if object_identity(digest) != (digest, size):
                    raise ValueError('Chunked-object mismatch')
            entries.append({'path': rel, 'sha256': digest, 'bytes': size})
        checkpoint = json.loads(z.read(SOURCE_ROOT + '/CHECKPOINT.json'))
    snapshot = {'schema_version': 1, 'project_id': PROJECT,
                'checkpoint_updated_at': checkpoint['updated_at'],
                'original_archive_sha256': sha_file(archive),
                'original_archive_bytes': archive.stat().st_size,
                'source_digest': checkpoint['source_digest'],
                'execution': checkpoint['execution'],
                'excluded_reproducible': manifest['excluded_reproducible'],
                'files': entries}
    data = (json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n').encode()
    digest = hashlib.sha256(data).hexdigest()
    path = ROOT / 'snapshots' / (digest + '.json')
    path.parent.mkdir(exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError('Snapshot collision')
    path.write_bytes(data)
    latest = {'project_id': PROJECT, 'snapshot': str(path.relative_to(ROOT)),
              'sha256': digest, 'files': len(entries),
              'checkpoint_updated_at': checkpoint['updated_at'],
              'source_digest': checkpoint['source_digest']}
    (ROOT / 'LATEST.json').write_text(json.dumps(latest, indent=2) + '\n')
    for name in ('CHECKPOINT.json', 'START_HERE.md', 'execution_windows/ledger.json'):
        with zipfile.ZipFile(archive) as z:
            dest = ROOT / 'current' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(SOURCE_ROOT + '/' + name))
    print(json.dumps(latest))


def read_snapshot():
    latest = json.loads((ROOT / 'LATEST.json').read_text())
    path = ROOT / str(safe_rel(latest['snapshot']))
    if sha_file(path) != latest['sha256']:
        raise ValueError('Snapshot digest mismatch')
    snap = json.loads(path.read_text())
    if snap['project_id'] != PROJECT or len(snap['files']) != latest['files']:
        raise ValueError('Snapshot identity mismatch')
    paths = [x['path'] for x in snap['files']]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate member')
    for item in snap['files']:
        safe_rel(item['path'])
        if object_identity(item['sha256']) != (item['sha256'], item['bytes']):
            raise ValueError('Object mismatch: ' + item['path'])
    return latest, snap


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='command', required=True)
    sp.add_parser('pack').add_argument('archive')
    sp.add_parser('verify')
    sp.add_parser('restore').add_argument('destination')
    args = ap.parse_args()
    if args.command == 'pack':
        pack(args.archive)
        return
    latest, snap = read_snapshot()
    if args.command == 'restore':
        dest = Path(args.destination).absolute()
        if dest.exists() or dest.is_symlink():
            raise ValueError('Restore destination must not exist; compare existing work before restore')
        dest.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=dest.name + '.restore-', dir=dest.parent))
        try:
            for item in snap['files']:
                target = stage / item['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('wb') as dst:
                    for part in object_parts(item['sha256']):
                        with part.open('rb') as src:
                            shutil.copyfileobj(src, dst, length=1024 * 1024)
                if sha_file(target) != item['sha256']:
                    raise ValueError('Restored member mismatch')
            stage.rename(dest)
        except BaseException:
            shutil.rmtree(stage)
            raise
    print(json.dumps({'verified': True, **latest, 'restored': args.command == 'restore'}))


if __name__ == '__main__':
    main()
