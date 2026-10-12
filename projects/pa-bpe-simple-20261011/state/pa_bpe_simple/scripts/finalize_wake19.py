import hashlib
import json
from pathlib import Path

STATE = Path(__file__).resolve().parents[1]
PROJECT = STATE.parents[1]
manifest_path = STATE / 'manifest.json'
current_path = PROJECT / 'CURRENT.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


old = json.loads(manifest_path.read_text())
files = dict(old['files'])
for path in sorted(STATE.rglob('*')):
    if path.is_file() and path != manifest_path:
        files[path.relative_to(STATE).as_posix()] = sha(path)

manifest = {
    'generation': 20,
    'created_utc': '2026-10-12T14:33:00+00:00',
    'library_file_id': old['library_file_id'],
    'previous_generation': 19,
    'previous_library_version': old['previous_library_version'],
    'previous_archive_sha256': old['previous_archive_sha256'],
    'goal_mode': 'continuous_research',
    'science_identity': 'one active idea; exact hybrid merge mechanism verified; delayed parity exposure supported, smoother-tail account falsified; hybrid-window development candidate next',
    'files': dict(sorted(files.items())),
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
current = json.loads(current_path.read_text())
assert current['generation'] == 20 and current['manifest_sha256'] == 'PENDING_FINALIZE'
current['manifest_sha256'] = sha(manifest_path)
current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'generation': 20, 'files': len(files), 'manifest_sha256': current['manifest_sha256']}, indent=2))
