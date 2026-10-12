#!/usr/bin/env python3
"""Publish staged project files through the authenticated GitHub connector.

One writer, content-addressed blobs, optimistic main-head update, no force push.
The helper directory must contain the current platform HostedAppsClient.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
import sys

def unpack(r):
    for _ in range(8):
        if isinstance(r, dict) and r.get('isError'):
            raise RuntimeError(str(r)[:1500])
        if isinstance(r, dict) and 'sha' in r:
            return r
        if isinstance(r, dict) and 'structuredContent' in r:
            r = r['structuredContent']; continue
        if isinstance(r, dict) and isinstance(r.get('content'), str):
            r = json.loads(r['content']); continue
        if isinstance(r, dict) and isinstance(r.get('content'), list):
            texts = [x['text'] for x in r['content'] if x.get('type') == 'text']
            if len(texts) == 1:
                try: r = json.loads(texts[0]); continue
                except json.JSONDecodeError: pass
        return r
    raise RuntimeError('Unexpected nested response')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--staging', type=Path, required=True)
    p.add_argument('--helper-dir', required=True)
    p.add_argument('--connector-id', required=True)
    p.add_argument('--repo', default='Yunbo-max/cpu')
    p.add_argument('--message', required=True)
    p.add_argument('--upload-only', action='store_true')
    p.add_argument('--expected-project-commit', help='Immutable reviewed commit whose project subtree may be replaced')
    a = p.parse_args()
    sys.path.insert(0, a.helper_dir)
    from library_hosted_apps import HostedAppsClient
    client = HostedAppsClient()
    def call(name, args):
        return unpack(client.call_tool(a.connector_id, name, args))
    def fetch(suffix):
        return call('fetch', {'url': f'https://api.github.com/repos/{a.repo}/{suffix}'})
    def namespace(commit):
        rows = fetch('contents/projects/autopilot-3d-20261011?ref=' + commit)
        if not isinstance(rows, list):
            raise RuntimeError('Cannot inspect the project namespace')
        return {x['path']: x['sha'] for x in rows}
    baseline = None
    if not a.upload_only:
        if not a.expected_project_commit or not re.fullmatch(r'[0-9a-fA-F]{40}', a.expected_project_commit):
            raise ValueError('--expected-project-commit must be an immutable full40 hexadecimal SHA')
        baseline = namespace(a.expected_project_commit)
    receipt = a.staging / 'upload-receipts.json'
    previous = json.loads(receipt.read_text()) if receipt.exists() else {}
    entries = []
    namespace_root = a.staging / 'projects' / 'autopilot-3d-20261011'
    files = sorted(namespace_root.rglob('*'))
    for f in files:
        if not f.is_file(): continue
        rel = f.relative_to(a.staging).as_posix()
        if f.stat().st_size > 8 * 1024 * 1024:
            raise ValueError('File exceeds 8 MiB; chunk it before upload: ' + rel)
        b = f.read_bytes()
        expected = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        if previous.get(rel, {}).get('git_sha') != expected:
            result = call('create_blob', {'repository_full_name': a.repo, 'content': base64.b64encode(b).decode(), 'encoding': 'base64'})
            if result.get('sha') != expected:
                raise RuntimeError(f'Blob identity mismatch: {rel}: {result}')
            previous[rel] = {'git_sha': expected, 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
            temp = receipt.with_suffix('.tmp')
            temp.write_text(json.dumps(previous, indent=2) + '\n'); temp.replace(receipt)
            print(json.dumps({'uploaded': rel, 'bytes': len(b)}), flush=True)
        entries.append({'path': rel, 'mode': '100755' if f.suffix == '.py' else '100644', 'type': 'blob', 'sha': expected})
    if a.upload_only:
        print(json.dumps({'status': 'blobs_uploaded', 'files': len(entries)})); return
    # Unrelated project writers may advance main. Rebase only our disjoint paths.
    for retry in range(5):
        head = fetch('git/ref/heads/main')['object']['sha']
        if namespace(head) != baseline:
            raise RuntimeError('Same-project remote changes detected; reconcile before publishing. Local evidence retained.')
        tree = fetch('git/commits/' + head)['tree']['sha']
        made_tree = call('create_tree', {'repository_full_name': a.repo, 'base_tree_sha': tree, 'tree_elements': entries})
        commit = call('create_commit', {'repository_full_name': a.repo, 'parent_sha': head, 'tree_sha': made_tree['sha'], 'message': a.message})
        # Record candidate before the branch mutation so an uncertain acknowledgement is queryable.
        pending = {'parent': head, 'commit': commit['sha'], 'tree': made_tree['sha'], 'files': len(entries)}
        (a.staging / 'pending-publish.json').write_text(json.dumps(pending, indent=2) + '\n')
        try:
            call('update_ref', {'repository_full_name': a.repo, 'branch_name': 'main', 'expected_sha': head, 'sha': commit['sha'], 'force': False})
        except Exception:
            actual = fetch('git/ref/heads/main')['object']['sha']
            if actual == commit['sha']:
                pass
            elif actual != head:
                # If our commit landed and another writer followed, it remains reachable.
                comparison = fetch('compare/' + commit['sha'] + '...' + actual)
                if comparison.get('status') not in ('ahead', 'identical'):
                    continue
            else:
                raise
        pending['status'] = 'published'
        (a.staging / 'publish-receipt.json').write_text(json.dumps(pending, indent=2) + '\n')
        print(json.dumps(pending), flush=True)
        return
    raise RuntimeError('Main advanced repeatedly; local evidence retained')

if __name__ == '__main__':
    main()
