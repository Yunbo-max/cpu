from pathlib import Path
import datetime, hashlib, json, subprocess, sys

ROOT = Path('/workspace/scratch/42f1128b703b')
STAGE = ROOT / 'cpu_migration_stage'
REPO = ROOT / 'cpu_migration_verify'
PROJECT = REPO / 'projects/pa-bpe-simple-20261011'
receipt = json.loads((STAGE / 'publish-receipt.json').read_text())
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
assert commit == receipt['commit'], (commit, receipt['commit'])

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

for name, rec in receipt['identities'].items():
    p = PROJECT / name
    assert p.is_file() and p.stat().st_size == rec['size'] and sha(p) == rec['sha256'], name

payload = json.loads((PROJECT / 'migration/payload_sha256.json').read_text())
for name, rec in payload['files'].items():
    assert sha(PROJECT / name) == rec['sha256'], name

current = json.loads((PROJECT / 'CURRENT.json').read_text())
state = PROJECT / current['checkpoint_directory']
assert sha(state / 'manifest.json') == current['manifest_sha256']
manifest = json.loads((state / 'manifest.json').read_text())
for name, expected in manifest['files'].items():
    assert sha(state / name) == expected, name

index = json.loads((PROJECT / 'archives/index.json').read_text())
chunk_count = set()
for identity, rec in index['archives'].items():
    whole, total = hashlib.sha256(), 0
    for part in rec['chunks']:
        p = PROJECT / part['path']
        assert sha(p) == part['sha256'] and p.stat().st_size == part['size']
        chunk_count.add(part['sha256'])
        with p.open('rb') as f:
            while data := f.read(1024 * 1024):
                whole.update(data); total += len(data)
    assert total == rec['size'] and whole.hexdigest() == identity, rec['name']

known = set(index['archives'])
for p in (PROJECT / 'archives/inventories').glob('*.json'):
    known.update(row['sha256'] for row in json.loads(p.read_text()).values())
known.update(row['sha256'] for row in json.loads((PROJECT / 'migration/local_addenda_inventory.json').read_text()))
inventory = json.loads((PROJECT / 'migration/local_file_inventory.json').read_text())
for row in inventory:
    assert row['sha256'] in known, row['path']
    local = ROOT / row['path']
    assert local.is_file() and local.stat().st_size == row['size'] and sha(local) == row['sha256'], row['path']

out = {'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'remote_repository': 'https://github.com/Yunbo-max/cpu', 'remote_commit': commit,
       'remote_project_tree': receipt['project_tree'], 'remote_readback': 'independent HTTPS git clone, pinned commit, complete project sparse checkout',
       'published_files_verified': len(receipt['identities']), 'payload_entries_verified': len(payload['files']),
       'state_manifest_entries_verified': len(manifest['files']), 'archives_reassembled_and_hashed': len(index['archives']),
       'unique_chunks_verified': len(chunk_count), 'original_local_files_covered_and_unchanged': len(inventory),
       'original_local_logical_bytes': sum(r['size'] for r in inventory),
       'status': 'PASS', 'scientific_commands_executed': 0,
       'cleanup_condition': 'A final no-active-job and unchanged-source check is still required before deletion.'}
(STAGE / 'remote_verification.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out))
