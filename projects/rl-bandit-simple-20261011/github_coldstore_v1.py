"""Project-scoped GitHub checkpoint packing, recovery verification and eviction.

Publication uses the connected GitHub app (see GITHUB_STORAGE.md); this script
never reads credentials. Science still uses the unchanged rsi-simple runner.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import subprocess
import tempfile
import zipfile

PROJECT = 'rl-bandit-simple-20261011'
ROOT = Path('/workspace/scratch/41d88df23405/rl_bandit_simple')
PREFIX = 'projects/' + PROJECT
REPO = 'https://github.com/Yunbo-max/cpu.git'
EXCLUDED = ('env', 'env-daac')
PART_SIZE = 4 * 1024 * 1024


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def safe_name(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or not p.parts or '\\' in name:
        raise ValueError('Unsafe archive path: ' + name)
    return p


def included(path):
    parts = path.parts
    return not (parts[0] in EXCLUDED or '__pycache__' in parts
                or parts[:2] == ('cache', 'numba')
                or path.name.endswith(('-wal', '-shm', '.lock'))
                or str(path) == 'ARCHIVE_MANIFEST.json')


def quiet(root):
    # /proc cmdline plus actual cwd/executable; inspect all visible identities.
    active = []
    self_proc_pid = int(os.readlink('/proc/self'))
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == self_proc_pid:
            continue
        try:
            # Project launches use the current UID; other owners are out of scope.
            owner = next(line for line in (proc / 'status').read_text().splitlines()
                         if line.startswith('Uid:')).split()[1:]
            if os.getuid() not in [int(value) for value in owner]:
                continue
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            rooted = lambda s: s == str(root) or s.startswith(str(root) + '/')
            arg_strings = [a.decode(errors='replace') for a in args]
            if any(rooted(a) for a in arg_strings):
                active.append(int(proc.name))
                continue
            try:
                cwd = os.readlink(proc / 'cwd')
                exe = os.readlink(proc / 'exe')
            except PermissionError:
                # Managed host services/other execution surfaces may hide cwd.
                # An ambiguous project launcher is held, not assumed unrelated.
                launchers = ('simple_runner.py', 'bounded_exec.py', 'daac_probe_v3.py')
                if any(Path(a).name in launchers for a in arg_strings):
                    if '--root' in arg_strings:
                        other = arg_strings[arg_strings.index('--root') + 1]
                        q = Path(other)
                        if (q.is_absolute() and q != root) or (other not in ('.', '..', '') and q.name != root.name):
                            continue
                    scripts = [Path(a) for a in arg_strings if Path(a).name in launchers]
                    if scripts and all(s.is_absolute() and root not in s.parents for s in scripts):
                        continue
                    raise RuntimeError('Unobservable possible project launcher: ' + proc.name)
                continue
            if rooted(cwd) or rooted(exe):
                active.append(int(proc.name))
        except FileNotFoundError:
            pass
        except PermissionError:
            raise RuntimeError('Cannot establish process quiescence')
    if active:
        raise RuntimeError('Project processes still visible: ' + str(active))
    status = json.loads(subprocess.check_output([
        'python3', str(root / 'runtime/scripts/simple_runner.py'),
        '--root', str(root), 'status']))
    nonterminal = [t['task_id'] for t in status['tasks']
                   if t['state'] not in ('succeeded', 'failed', 'blocked', 'cancelled')]
    if nonterminal or status['budget']['reserved_seconds']:
        raise RuntimeError('Nonterminal work or reserved resources: ' + str(nonterminal))
    return {'sequence': status['sequence'], 'status': status['status'],
            'attempts_used': status['budget']['attempts_used'],
            'elapsed_seconds': status['budget']['elapsed_seconds']}


def pack(args):
    root, out = Path(args.root).resolve(), Path(args.out).resolve()
    if root != ROOT or out == root or root in out.parents:
        raise ValueError('Use the original project root and an external staging directory')
    state = quiet(root)
    old = json.loads(Path(args.previous).read_text()) if args.previous else None
    if old and old['project_id'] != PROJECT:
        raise ValueError('Wrong previous project')
    # The approved builder creates a consistent SQLite backup and full manifest.
    subprocess.run(['python3', str(root / 'scripts/build_checkpoint.py')],
                   check=True, stdout=subprocess.DEVNULL)
    full = root.parent / 'RL_Bandit_Simple_Checkpoint.zip'
    with zipfile.ZipFile(full) as z:
        manifest = json.loads(z.read('rl_bandit_simple/ARCHIVE_MANIFEST.json'))
        old_files = old['files'] if old else {}
        deleted = sorted(set(old_files) - set(manifest['files']))
        if deleted:
            raise RuntimeError('Durable historical files are missing: ' + str(deleted[:20]))
        changed = [n for n, m in manifest['files'].items() if m != old_files.get(n)]
        out.mkdir(parents=True, exist_ok=True)
        payload = out / 'checkpoint-delta.zip'
        with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as d:
            for name in changed:
                safe_name(name)
                data = z.read('rl_bandit_simple/' + name)
                if hashlib.sha256(data).hexdigest() != manifest['files'][name]['sha256']:
                    raise RuntimeError('Builder archive hash mismatch')
                d.writestr('rl_bandit_simple/' + name, data)
            d.writestr('rl_bandit_simple/ARCHIVE_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    sha = digest_file(payload)
    sid = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + sha[:12]
    uploads, parts = [], []
    with payload.open('rb') as f:
        i = 0
        while data := f.read(PART_SIZE):
            rel = f'snapshots/{sid}/part-{i:04d}.zip.bin'
            p = out / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            meta = {'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            parts.append(meta)
            uploads.append({'path': PREFIX + '/' + rel, 'local': str(p), **{k: meta[k] for k in ('bytes', 'sha256')}})
            i += 1
    snap = {'id': sid, 'sha256': sha, 'bytes': payload.stat().st_size,
            'changed_files': len(changed), 'parts': parts}
    latest = {'schema_version': 1, 'project_id': PROJECT, 'original_root': str(ROOT),
              'created_at_utc': manifest['created_at_utc'], 'state': state,
              'excluded_reproducible_directories': list(EXCLUDED),
              'chain': (old['chain'] if old else []) + [snap], 'files': manifest['files']}
    latest_path = out / 'LATEST.json'
    dump(latest_path, latest)
    uploads.append({'path': PREFIX + '/LATEST.json', 'local': str(latest_path),
                    'bytes': latest_path.stat().st_size, 'sha256': digest_file(latest_path)})
    # Recovery and readable summaries are small copies, not additional authority.
    for src, rel in [(root / 'scripts/github_coldstore_v1.py', 'github_coldstore_v1.py'),
                     (root / 'notes/GITHUB_STORAGE.md', 'GITHUB_STORAGE.md'),
                     (root / 'START_HERE.md', 'START_HERE.md'),
                     (root / 'notes/next-action.txt', 'NEXT_ACTION.txt')]:
        uploads.append({'path': PREFIX + '/' + rel, 'local': str(src),
                        'bytes': src.stat().st_size, 'sha256': digest_file(src)})
    dump(out / 'UPLOAD_PLAN.json', {'project_id': PROJECT, 'snapshot_id': sid,
                                   'uploads': uploads, 'latest': str(latest_path)})
    print(json.dumps({'plan': str(out / 'UPLOAD_PLAN.json'), 'files': len(latest['files']),
                      'changed_files': len(changed), 'payload_bytes': snap['bytes'], 'parts': len(parts)}))


def materialize(checkout, destination):
    namespace = checkout / PREFIX
    latest = json.loads((namespace / 'LATEST.json').read_text())
    if latest['project_id'] != PROJECT or latest['original_root'] != str(ROOT):
        raise ValueError('Wrong project identity')
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(dir=destination.parent) as td:
        payload = Path(td) / 'delta.zip'
        for snap in latest['chain']:
            with payload.open('wb') as out:
                for part in snap['parts']:
                    safe_name(part['path'])
                    p = namespace / part['path']
                    if p.is_symlink() or p.stat().st_size != part['bytes'] or digest_file(p) != part['sha256']:
                        raise RuntimeError('Remote part failed verification: ' + part['path'])
                    with p.open('rb') as f:
                        shutil.copyfileobj(f, out, 1024 * 1024)
            if payload.stat().st_size != snap['bytes'] or digest_file(payload) != snap['sha256']:
                raise RuntimeError('Remote snapshot hash mismatch')
            with zipfile.ZipFile(payload) as z:
                seen = set()
                for info in z.infolist():
                    p = safe_name(info.filename)
                    if p.parts[0] != 'rl_bandit_simple' or info.filename in seen or info.is_dir():
                        raise ValueError('Invalid/duplicate ZIP member')
                    seen.add(info.filename)
                    rel = Path(*p.parts[1:])
                    if str(rel) != 'ARCHIVE_MANIFEST.json' and str(rel) not in latest['files']:
                        raise ValueError('Undeclared snapshot file: ' + str(rel))
                    target = destination / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info) as src, target.open('wb') as dst:
                        shutil.copyfileobj(src, dst, 1024 * 1024)
    actual = json.loads((destination / 'ARCHIVE_MANIFEST.json').read_text())['files']
    if actual != latest['files']:
        raise RuntimeError('Latest manifest differs from reconstructed manifest')
    verify_inventory(destination, latest['files'], database_backup=False)
    return latest


def verify_inventory(root, files, database_backup=True):
    paths = {str(p.relative_to(root)): p for p in root.rglob('*')
             if p.is_file() and included(p.relative_to(root))}
    if set(paths) != set(files):
        raise RuntimeError('Live inventory differs; keep local data. Missing/extra: ' +
                           str(sorted(set(paths) ^ set(files))[:20]))
    with tempfile.TemporaryDirectory() as td:
        for name, p in paths.items():
            if p.is_symlink():
                raise RuntimeError('Unexpected durable symlink: ' + name)
            compare = p
            if database_backup and p.suffix == '.sqlite3':
                compare = Path(td) / p.name
                if compare.exists():
                    compare.unlink()
                with sqlite3.connect(p) as src, sqlite3.connect(compare) as dst:
                    src.backup(dst)
            if compare.stat().st_size != files[name]['bytes'] or digest_file(compare) != files[name]['sha256']:
                raise RuntimeError('Live file changed since upload; keep it: ' + name)


def check_remote_checkout(checkout):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(checkout), *args], text=True).strip()
    if git('remote', 'get-url', 'origin') != REPO or git('status', '--porcelain', '--untracked-files=all'):
        raise RuntimeError('Require a clean, independently cloned canonical repository')
    commit = git('rev-parse', 'HEAD')
    current = subprocess.check_output(['git', 'ls-remote', REPO, 'refs/heads/main'], text=True).split()[0]
    if commit != current:
        # A concurrent commit may preserve this namespace. Fetch before checking.
        raise RuntimeError('Remote main moved; refresh checkout and reverify')
    return commit


def verify(args):
    checkout = Path(args.checkout).resolve()
    commit = check_remote_checkout(checkout)
    with tempfile.TemporaryDirectory(prefix='rl-remote-verify-', dir=ROOT.parent) as td:
        latest = materialize(checkout, Path(td) / 'restored')
    receipt = {'project_id': PROJECT, 'commit': commit, 'repository': REPO,
               'checked_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'latest_sha256': digest_file(checkout / PREFIX / 'LATEST.json'),
               'file_count': len(latest['files']), 'all_remote_bytes_verified': True}
    dump(Path(args.receipt), receipt)
    print(json.dumps(receipt))


def restore(args):
    checkout = Path(args.checkout).resolve()
    check_remote_checkout(checkout)
    if ROOT.exists():
        raise RuntimeError('Original root exists; reconcile newer live state, never overwrite it')
    temp = Path(tempfile.mkdtemp(prefix='rl-restore-', dir=ROOT.parent))
    try:
        materialize(checkout, temp / 'project')
        (temp / 'project').rename(ROOT)
    finally:
        shutil.rmtree(temp)
    print(json.dumps({'restored': str(ROOT), 'environments': 'excluded; rebuild only the required environment'}))


def cleanup(args):
    checkout = Path(args.checkout).resolve()
    commit = check_remote_checkout(checkout)
    receipt = json.loads(Path(args.receipt).read_text())
    latest_path = checkout / PREFIX / 'LATEST.json'
    if not receipt.get('all_remote_bytes_verified') or receipt['commit'] != commit or receipt['latest_sha256'] != digest_file(latest_path):
        raise RuntimeError('Missing matching complete remote verification')
    latest = json.loads(latest_path.read_text())
    state = quiet(ROOT)
    if state != latest['state']:
        raise RuntimeError('Runner state changed since upload')
    verify_inventory(ROOT, latest['files'])
    marker = ROOT.parent / 'RL_Bandit_GitHub_Recovery.json'
    dump(marker, {**receipt, 'original_root': str(ROOT), 'namespace': PREFIX,
                  'state': state, 'cleanup_authority': 'User request 2026-10-12: upload history to Yunbo-max/cpu then delete local copies; download to run and upload results before cleanup.',
                  'next_action': 'Clone latest main, read GITHUB_STORAGE.md, verify and restore without init; rebuild only the required environment.'})
    if args.apply:
        shutil.rmtree(ROOT)
    print(json.dumps({'would_remove': str(ROOT), 'applied': args.apply, 'recovery_marker': str(marker)}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('pack'); s.add_argument('--root', default=str(ROOT)); s.add_argument('--out', required=True); s.add_argument('--previous')
    for name in ('verify', 'restore', 'cleanup'):
        s = sub.add_parser(name); s.add_argument('--checkout', required=True)
        if name in ('verify', 'cleanup'): s.add_argument('--receipt', required=True)
        if name == 'cleanup': s.add_argument('--apply', action='store_true')
    args = p.parse_args()
    globals()[args.command](args)


if __name__ == '__main__':
    main()
