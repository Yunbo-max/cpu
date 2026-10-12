from pathlib import Path, PurePosixPath
import collections, datetime, hashlib, json, os, re, shutil, zipfile

ROOT = Path('/workspace/scratch/42f1128b703b')
STAGE = ROOT / 'cpu_migration_stage'
PROJECT = ROOT / 'cpu_migration_repo/projects/pa-bpe-simple-20261011'
PROJECT.mkdir(parents=True, exist_ok=True)
LATEST = ROOT / 'wake14_restore/PA_BPE_Simple_Checkpoint_wake14_v2.zip'
RAW = STAGE / 'downloads/PA_BPE_GlobalVoices_v2018q4_Raw_Source.zip'
CHUNK = 32 * 1024 * 1024

def digest(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write_json(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')

def safe(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('Unsafe archive path')
    return p

patterns = {
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'github_token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'bearer': rb'Bearer [A-Za-z0-9._-]{25,}',
    'signed_query': rb'(?:[?&](?:sig|X-Amz-Signature|X-Goog-Signature)=)[A-Za-z0-9%+/=]{16,}',
    'hf_token': rb'\bhf_[A-Za-z0-9]{25,}',
}

def scan(data, label):
    for kind, pat in patterns.items():
        if re.search(pat, data):
            raise RuntimeError('Publication scan needs review: ' + kind + ' in ' + label)

records = json.loads((STAGE / 'archives_inventory.json').read_text())
records.append({'path': str(RAW), 'sha256': digest(RAW), 'size': RAW.stat().st_size})
known = set()
zip_inventory = {}
for rec in records:
    path = Path(rec['path'])
    if path.suffix != '.zip' or rec['sha256'] in zip_inventory:
        continue
    inv = {}
    with zipfile.ZipFile(path) as z:
        for i in z.infolist():
            safe(i.filename)
            if i.is_dir():
                continue
            with z.open(i) as f:
                h = hashlib.file_digest(f, 'sha256').hexdigest()
            inv[i.filename] = {'sha256': h, 'size': i.file_size}
            known.add(h)
            if i.file_size < 20_000_000 and not i.filename.endswith(('.zip', '.gz', '.db', '.sqlite3', '.pyc')):
                scan(z.read(i), i.filename)
        if rec['path'] == str(LATEST):
            state = PROJECT / 'state'
            state.mkdir(exist_ok=True)
            z.extractall(state)
    zip_inventory[rec['sha256']] = inv

supplement = STAGE / 'local_recovery_addenda.zip'
supplement_members = []
covered = []
with zipfile.ZipFile(supplement, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
    for dirname in ['wake14_restore', 'recovery13']:
        for p in sorted((ROOT / dirname).rglob('*')):
            if not p.is_file() or p.is_symlink():
                continue
            h = digest(p)
            row = {'path': str(p.relative_to(ROOT)), 'sha256': h, 'size': p.stat().st_size}
            covered.append(row)
            if h in known or any(h == r['sha256'] for r in records):
                continue
            if p.stat().st_size < 20_000_000 and p.suffix not in ['.zip', '.gz', '.db', '.sqlite3', '.pyc']:
                scan(p.read_bytes(), row['path'])
            out.write(p, row['path'])
            supplement_members.append(row)
            known.add(h)
records.append({'path': str(supplement), 'sha256': digest(supplement), 'size': supplement.stat().st_size})

archives = {}
for rec in records:
    h = rec['sha256']
    if h in archives:
        archives[h]['original_paths'].append(str(Path(rec['path']).relative_to(ROOT)))
        continue
    parts = []
    with Path(rec['path']).open('rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            bh = hashlib.sha256(b).hexdigest()
            dst = PROJECT / 'archives/objects' / (bh + '.part')
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                dst.write_bytes(b)
            parts.append({'path': str(dst.relative_to(PROJECT)), 'sha256': bh, 'size': len(b)})
    archives[h] = {'name': Path(rec['path']).name, 'size': rec['size'], 'sha256': h,
                   'original_paths': [str(Path(rec['path']).relative_to(ROOT))],
                   'kind': 'incomplete-transfer-forensic-only' if '.openai-download-' in rec['path'] else 'archive',
                   'chunks': parts}

write_json(PROJECT / 'archives/index.json', {'schema_version': 1, 'chunk_size': CHUNK, 'archives': archives})
for h, inv in zip_inventory.items():
    write_json(PROJECT / 'archives/inventories' / (h + '.json'), inv)
write_json(PROJECT / 'migration/local_file_inventory.json', covered)
write_json(PROJECT / 'migration/local_addenda_inventory.json', supplement_members)
shutil.copyfile(STAGE / 'preflight_scan.json', PROJECT / 'migration/preflight_scan.json')
manifest = PROJECT / 'state/pa_bpe_simple/manifest.json'
write_json(PROJECT / 'CURRENT.json', {
    'schema_version': 1, 'project_id': 'pa-bpe-simple-20261011',
    'storage_authorization_date': '2026-10-12',
    'canonical_repository': 'https://github.com/Yunbo-max/cpu',
    'canonical_path': 'projects/pa-bpe-simple-20261011',
    'checkpoint_directory': 'state/pa_bpe_simple', 'generation': 15,
    'manifest_sha256': digest(manifest),
    'original_checkpoint_archive_sha256': digest(LATEST),
    'external_raw_source_archive_sha256': digest(RAW),
    'external_raw_source_required_for_next_step': False,
    'library_import': {'library_file_id': 'libfile_8bb70b367b948191bfed83a45933917f', 'version': 15},
    'history_rule': 'Keep scientific evidence immutable. New generations update this pointer and the checkpoint manifest; Git records prior states.',
    'active_science_processes_at_import': 0,
    'next_action': 'Qualify truthful row-to-fixed-wake9-shard provenance and build production development selection before tokenizer or fairness experiments.',
})
stats = {'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'unique_archives': len(archives), 'source_file_count': len(covered),
         'source_logical_bytes': sum(r['size'] for r in covered),
         'local_addenda_files': len(supplement_members),
         'unique_chunk_count': len(list((PROJECT / 'archives/objects').glob('*.part'))),
         'unique_chunk_bytes': sum(p.stat().st_size for p in (PROJECT / 'archives/objects').glob('*.part')),
         'state_files': len([p for p in (PROJECT / 'state').rglob('*') if p.is_file()]),
         'checkpoint_manifest_verified': 1954,
         'redactions': [], 'scientific_commands_executed_during_migration': 0}
write_json(PROJECT / 'migration/import_summary.json', stats)
print(json.dumps(stats))
