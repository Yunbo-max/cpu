#!/usr/bin/env python3
"""Publish this namespace with the current authenticated HostedAppsClient.

Use --upload-only to resume bounded batches, then --publish for a guarded commit.
No credentials are read or exported; the current platform connector owns auth.
"""
import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

NAMESPACE = 'projects/pa-bpe-simple-20261011'

def unpack(value):
    for _ in range(8):
        if isinstance(value, dict) and value.get('isError'):
            raise RuntimeError(str(value)[:1500])
        if isinstance(value, dict) and 'sha' in value:
            return value
        if isinstance(value, dict) and 'structuredContent' in value:
            value = value['structuredContent']
        elif isinstance(value, dict) and isinstance(value.get('content'), str):
            value = json.loads(value['content'])
        elif isinstance(value, dict) and isinstance(value.get('content'), list):
            text = [b['text'] for b in value['content'] if b.get('type') == 'text']
            if len(text) != 1:
                return value
            try:
                value = json.loads(text[0])
            except json.JSONDecodeError:
                return value
        else:
            return value
    raise RuntimeError('Unexpected response wrapper')

def save(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument('--helper-dir', required=True)
    ap.add_argument('--connector-id', required=True, help='Observed GitHub connector ID from legitimate tool metadata')
    ap.add_argument('--receipts', type=Path, required=True, help='Outside the published project root')
    ap.add_argument('--max-files', type=int, default=30)
    ap.add_argument('--max-seconds', type=int, default=100)
    ap.add_argument('--upload-only', action='store_true')
    ap.add_argument('--publish', action='store_true')
    ap.add_argument('--expected-project-tree', default='absent')
    ap.add_argument('--message', default='Save PA-BPE evidence with verified archive identities')
    args = ap.parse_args()
    root = args.root.resolve()
    if args.receipts.resolve().is_relative_to(root):
        raise ValueError('Upload receipts must be outside the mutable upload tree')
    sys.path.insert(0, args.helper_dir)
    from library_hosted_apps import HostedAppsClient
    client = HostedAppsClient()
    def call(tool, body):
        try:
            return unpack(client.call_tool(args.connector_id, tool, body))
        except Exception as exc:
            detail = getattr(exc, 'result', None)
            error = {'tool': tool, 'error': str(exc), 'detail': detail,
                     'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            save(args.receipts.with_name('last-upload-error.json'), error)
            print(json.dumps(error)[:3000], flush=True)
            raise
    def fetch(suffix):
        return call('fetch', {'url': 'https://api.github.com/repos/Yunbo-max/cpu/' + suffix})
    def subtree(tree):
        for part in NAMESPACE.split('/'):
            row = next((e for e in fetch('git/trees/' + tree)['tree'] if e['path'] == part), None)
            if row is None:
                return 'absent'
            if row['type'] != 'tree':
                raise RuntimeError('Namespace is not a directory')
            tree = row['sha']
        return tree

    receipts = json.loads(args.receipts.read_text()) if args.receipts.exists() else {}
    entries, missing, identities = [], [], {}
    archive_index = json.loads((root / 'archives/index.json').read_text())
    referenced_parts = {c['path'] for a in archive_index['archives'].values() for c in a['chunks']}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not accepted in this export')
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith('archives/objects/') and rel not in referenced_parts:
            continue  # superseded derived chunks, never source evidence
        size = path.stat().st_size
        if size > 32 * 1024 * 1024:
            raise ValueError('Split files above 32 MiB before publishing')
        sha = hashlib.sha1(b'blob ' + str(size).encode() + b'\0')
        digest = hashlib.sha256()
        with path.open('rb') as f:
            while block := f.read(1024 * 1024):
                sha.update(block); digest.update(block)
        blob_sha = sha.hexdigest()
        rel = path.relative_to(root).as_posix()
        entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob_sha})
        identities[rel] = {'sha256': digest.hexdigest(), 'size': size, 'git_sha': blob_sha}
        if blob_sha not in receipts and not any(row[1] == blob_sha for row in missing):
            missing.append((path, blob_sha, size))

    start, count, sent = time.monotonic(), 0, 0
    for path, expected, size in missing:
        if count >= args.max_files or time.monotonic() - start >= args.max_seconds:
            break
        data = path.read_bytes()
        result = call('create_blob', {'repository_full_name': 'Yunbo-max/cpu', 'encoding': 'base64', 'content': base64.b64encode(data).decode()})
        if result.get('sha') != expected:
            raise RuntimeError('Uploaded blob identity mismatch: ' + str(path))
        receipts[expected] = {'bytes': size, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        save(args.receipts, receipts)
        count += 1; sent += size
        if count % 10 == 0:
            print(json.dumps({'uploaded_in_batch': count, 'bytes_in_batch': sent, 'last_file': path.relative_to(root).as_posix()}), flush=True)
    remaining = sum(e['sha'] not in receipts for e in entries)
    print(json.dumps({'uploaded_this_batch': count, 'bytes_this_batch': sent, 'remaining_file_references': remaining, 'wall': time.monotonic() - start}), flush=True)
    if remaining or args.upload_only or not args.publish:
        return

    # Deep imports can time out as one tree request. Build resumable objects in
    # small batches; no branch is changed until the complete tree is available.
    fingerprint = hashlib.sha256(json.dumps(
        {'base': args.expected_project_tree, 'entries': entries},
        sort_keys=True).encode()).hexdigest()
    progress_path = args.receipts.with_name('project-tree-progress.json')
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
    if progress.get('fingerprint') != fingerprint:
        progress = {'fingerprint': fingerprint, 'next_entry': 0,
                    'tree': None if args.expected_project_tree == 'absent' else args.expected_project_tree}
    while progress['next_entry'] < len(entries):
        offset = progress['next_entry']
        batch = entries[offset:offset + 200]
        project_body = {'repository_full_name': 'Yunbo-max/cpu', 'tree_elements': batch}
        if progress['tree']:
            project_body['base_tree_sha'] = progress['tree']
        progress['tree'] = call('create_tree', project_body)['sha']
        progress['next_entry'] += len(batch)
        save(progress_path, progress)
        print(json.dumps({'tree_entries_complete': progress['next_entry'], 'total': len(entries)}), flush=True)
    project = progress['tree']
    for _ in range(5):
        head = fetch('git/ref/heads/main')['object']['sha']
        base = fetch('git/commits/' + head)['tree']['sha']
        if subtree(base) != args.expected_project_tree:
            raise RuntimeError('Same-project remote change; reconcile before publishing')
        tree = call('create_tree', {'repository_full_name': 'Yunbo-max/cpu', 'base_tree_sha': base,
                    'tree_elements': [{'path': NAMESPACE, 'mode': '040000', 'type': 'tree', 'sha': project}]})['sha']
        commit = call('create_commit', {'repository_full_name': 'Yunbo-max/cpu', 'parent_sha': head, 'tree_sha': tree, 'message': args.message})['sha']
        receipt = {'parent': head, 'commit': commit, 'project_tree': project, 'files': len(entries), 'identities': identities, 'status': 'pending'}
        publish_receipt = args.receipts.with_name('publish-receipt.json')
        save(publish_receipt, receipt)
        try:
            call('update_ref', {'repository_full_name': 'Yunbo-max/cpu', 'branch_name': 'main', 'expected_sha': head, 'sha': commit, 'force': False})
        except Exception:
            actual = fetch('git/ref/heads/main')['object']['sha']
            if actual != commit:
                comparison = fetch('compare/' + commit + '...' + actual)
                if comparison.get('status') not in ['ahead', 'identical']:
                    continue
        receipt['status'] = 'published'; save(publish_receipt, receipt)
        print(json.dumps({k: v for k, v in receipt.items() if k != 'identities'}), flush=True)
        return
    raise RuntimeError('Repeated remote movement; retain local evidence')

if __name__ == '__main__':
    main()
