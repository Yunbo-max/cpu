"""Capture settings-migration evidence and build the canonical checkpoint archive.

Administrative work only: this script does not submit or run scientific tasks.
"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

root = Path(__file__).resolve().parents[1]
destination = Path(sys.argv[1]).resolve()
old_manifest = json.loads((root / 'manifest.json').read_text())
assert old_manifest['generation'] == 2
owner = json.loads((root / '.writer.lock/owner.json').read_text())
assert owner['owner'] == 'user-continuous-authorization-20261011T2002Z'
observations = []
for entry in ('simple_runner', 'simple_loop'):
    argv = ['python3', str(root / f'runtime/scripts/{entry}.py'), '--root',
            str(root / 'execution_windows/wake2'), 'status']
    start = time.monotonic()
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    observations.append({'argv': argv, 'exit_code': completed.returncode,
                         'administrative_wall_seconds': time.monotonic() - start,
                         'scientific_attempt': False})
    assert completed.returncode == 0, completed.stderr
    (root / f'evidence/continuous_{entry}_status.json').write_text(completed.stdout)
    state = json.loads(completed.stdout)
    if entry == 'simple_runner':
        assert state['goal_contract']['mode'] == 'continuous_research'
        assert state['goal_contract_version'] == 2
        assert state['budget']['attempts_used'] == 10
        assert state['budget']['reserved_seconds'] == 0
        assert state['budget']['elapsed_seconds'] == 352.62387728596514
        assert all(a['state'] == 'terminal' for a in state['attempts'])
        assert state['complete_goal'] is False
        assert state['stop_requested'] is None
        summary = {k: state[k] for k in ('status', 'sequence', 'goal_contract',
                    'goal_contract_version', 'complete_goal', 'budget')}
    else:
        assert state['pending_launch'] is None
        assert state['status'] == 'active'

budget = json.loads((root / 'phase_budget.json').read_text())
assert budget['phase_limit_seconds'] is None
assert budget['remaining_seconds'] is None
assert budget['cumulative_charged_seconds'] == 402.0276058989711
automation = json.loads((root / 'evidence/continuous_automation_update_receipt.json').read_text())
assert automation['success'] and automation['is_enabled']
assert automation['schedule_unchanged']
assert 'continuous_research' in automation['new_prompt']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

changed_existing = [name for name, sha in old_manifest['files'].items()
                    if not (root / name).is_file() or digest(root / name) != sha]
allowed_changes = {'PA_BPE_Simple_Checkpoint.md', 'phase_budget.json',
                   'execution_windows/wake2/.research-autopilot/simple-loop.sqlite3'}
unexpected = [name for name in changed_existing if name not in allowed_changes]
assert not unexpected, f'Unexpected changes to historical artifacts: {unexpected}'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
verification = {'observed_utc': now, 'scope': 'authorization/settings only; no new experiment',
                'commands': observations, 'runner': summary,
                'historical_members_checked': len(old_manifest['files']),
                'changed_existing_members': changed_existing,
                'historical_scientific_artifacts_unchanged': True,
                'ledger_cumulative_seconds': budget['cumulative_charged_seconds'],
                'automation_enabled': automation['is_enabled'],
                'same_automation_schedule': automation['schedule_unchanged']}
(root / 'evidence/continuous_authorization_verification.json').write_text(
    json.dumps(verification, ensure_ascii=False, indent=2) + '\n')

members = []
for path in sorted(root.rglob('*')):
    relative = path.relative_to(root)
    if any(part in ('.writer.lock', '__pycache__') for part in relative.parts):
        continue
    if path.is_symlink():
        raise RuntimeError(f'Unreviewed symlink in checkpoint: {relative}')
    if path.is_file() and path.suffix not in ('.pyc', '.lock') and str(relative) != 'manifest.json':
        members.append(path)
manifest = {'generation': 3, 'created_utc': now,
            'library_file_id': 'libfile_8bb70b367b948191bfed83a45933917f',
            'previous_generation': 2, 'previous_library_version': 2,
            'previous_archive_sha256': '88bb68d836554b392b711486232974f373ede4c8f8cbccdaa30bd439b7b1367f',
            'files': {str(p.relative_to(root)): digest(p) for p in members}}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
destination.parent.mkdir(parents=True, exist_ok=True)
assert not destination.exists(), 'Refuse to replace a local archive'
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in members + [root / 'manifest.json']:
        z.write(path, 'pa_bpe_simple/' + str(path.relative_to(root)))
with zipfile.ZipFile(destination) as z:
    assert z.testzip() is None
    for name, sha in manifest['files'].items():
        assert hashlib.sha256(z.read('pa_bpe_simple/' + name)).hexdigest() == sha
print(json.dumps({'archive': str(destination), 'sha256': digest(destination),
                  'size_bytes': destination.stat().st_size, 'generation': 3,
                  'manifest_files': len(members), 'verification': verification}, ensure_ascii=False))
