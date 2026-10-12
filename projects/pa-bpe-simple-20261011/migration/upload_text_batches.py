"""Migration transport optimization: upload UTF-8 blobs in bounded tree batches.

This creates objects only, never changes a branch. The guarded publisher owns
the final commit. Every returned Git blob identity must match the source bytes.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--helper-dir', required=True)
ap.add_argument('--connector-id', required=True)
ap.add_argument('--receipts', type=Path, required=True)
args = ap.parse_args()
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from publish import unpack, save
sys.path.insert(0, args.helper_dir)
from library_hosted_apps import HostedAppsClient
client = HostedAppsClient()
receipts = json.loads(args.receipts.read_text())
index = json.loads((root / 'archives/index.json').read_text())
parts = {p['path'] for a in index['archives'].values() for p in a['chunks']}
pending = []
seen = set(receipts)
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.is_symlink():
        continue
    rel = p.relative_to(root).as_posix()
    if rel.startswith('archives/objects/') and rel not in parts:
        continue
    if p.stat().st_size > 3 * 1024 * 1024:
        continue
    data = p.read_bytes()
    identity = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if identity in seen:
        continue
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError:
        continue
    pending.append((identity, content, len(data)))
    seen.add(identity)

start = time.monotonic()
uploaded = 0
while pending and time.monotonic() - start < 95:
    group, size = [], 0
    while pending and len(group) < 50 and size + pending[0][2] <= 3 * 1024 * 1024:
        row = pending.pop(0)
        group.append(row)
        size += row[2]
    result = unpack(client.call_tool(args.connector_id, 'create_tree', {
        'repository_full_name': 'Yunbo-max/cpu',
        'tree_elements': [{'path': row[0], 'mode': '100644', 'type': 'blob', 'content': row[1]} for row in group]
    }))
    if 'tree' not in result:
        result = unpack(client.call_tool(args.connector_id, 'fetch', {
            'url': 'https://api.github.com/repos/Yunbo-max/cpu/git/trees/' + result['sha']
        }))
    returned = {row['path']: row['sha'] for row in result['tree']}
    for identity, content, length in group:
        if returned.get(identity) != identity:
            raise RuntimeError('Remote blob identity mismatch: ' + identity)
        receipts[identity] = {'bytes': length, 'via': 'bounded_text_tree',
                              'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save(args.receipts, receipts)
    uploaded += len(group)
    print(json.dumps({'uploaded_text_files': uploaded, 'batch_bytes': size, 'remaining_text_files': len(pending)}), flush=True)
print(json.dumps({'wall': time.monotonic() - start, 'uploaded': uploaded}))
