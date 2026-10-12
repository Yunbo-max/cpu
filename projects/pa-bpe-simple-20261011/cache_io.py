#!/usr/bin/env python3
"""Bounded-memory hash verification and archive restoration for PA-BPE."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile

ROOT = Path(__file__).resolve().parent

def sha256(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def under(root, name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name:
        raise ValueError('Unsafe relative path')
    p = root.joinpath(*rel.parts)
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes root')
    return p

def verify_state(partial):
    current = json.loads((ROOT / 'CURRENT.json').read_text())
    state = under(ROOT, current['checkpoint_directory'])
    manifest = state / 'manifest.json'
    if sha256(manifest) != current['manifest_sha256']:
        raise ValueError('CURRENT/manifest hash mismatch')
    doc = json.loads(manifest.read_text())
    if doc['generation'] != current['generation']:
        raise ValueError('Generation mismatch')
    verified, missing = 0, []
    for name, expected in doc['files'].items():
        p = under(state, name)
        if not p.is_file():
            missing.append(name)
        elif sha256(p) != expected:
            raise ValueError('State hash mismatch: ' + name)
        else:
            verified += 1
    if missing and not partial:
        raise ValueError('Missing state files: ' + str(len(missing)))
    return {'generation': current['generation'], 'verified_files': verified,
            'missing_files': len(missing), 'scope': 'partial' if missing else 'complete'}

def restore_archive(identity, output):
    index = json.loads((ROOT / 'archives/index.json').read_text())
    rec = index['archives'][identity]
    if rec['kind'] == 'incomplete-transfer-forensic-only':
        raise ValueError('Forensic partial download is not a restorable archive')
    dst = Path(output).absolute()
    if dst.exists():
        raise FileExistsError(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmpname = tempfile.mkstemp(prefix=dst.name + '.', suffix='.partial', dir=dst.parent)
    tmp = Path(tmpname)
    whole, total = hashlib.sha256(), 0
    try:
        with os.fdopen(fd, 'wb') as out:
            for part in rec['chunks']:
                local = under(ROOT, part['path'])
                ph, size = hashlib.sha256(), 0
                with local.open('rb') as src:
                    while block := src.read(1024 * 1024):
                        out.write(block)
                        ph.update(block)
                        whole.update(block)
                        size += len(block)
                        total += len(block)
                if ph.hexdigest() != part['sha256'] or size != part['size']:
                    raise ValueError('Archive chunk hash/size mismatch')
            out.flush()
            os.fsync(out.fileno())
        if whole.hexdigest() != identity or total != rec['size']:
            raise ValueError('Whole archive hash/size mismatch')
        os.link(tmp, dst)  # no overwriting even if another writer appeared
        return {'output': str(dst), 'sha256': whole.hexdigest(), 'size': total}
    finally:
        tmp.unlink(missing_ok=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    verify = sub.add_parser('verify-state')
    verify.add_argument('--allow-partial', action='store_true')
    restore = sub.add_parser('restore-archive')
    restore.add_argument('sha256')
    restore.add_argument('--output', required=True)
    args = parser.parse_args()
    result = verify_state(args.allow_partial) if args.command == 'verify-state' else restore_archive(args.sha256, args.output)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
