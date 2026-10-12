"""Verify Wake 11 state and build generation 12 of the canonical checkpoint."""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
def load(rel): return json.loads((root/rel).read_text())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

old=load('manifest.json')
if old['generation']!=11: raise RuntimeError('Expected generation 11 parent')
owner=load('.writer.lock/owner.json')
if owner['owner']!='automation-wake11-20261012T0433Z': raise RuntimeError('Wake 11 does not own writer lock')
changed=[name for name,h in old['files'].items() if not (root/name).is_file() or digest(root/name)!=h]
allowed={'PA_BPE_Simple_Checkpoint.md','phase_budget.json','next_research_action.json'}
if set(changed)-allowed: raise RuntimeError(f'Unexpected historical changes: {sorted(set(changed)-allowed)}')

state=load('execution_windows/wake11/output/final_status.json')
if state['budget']['attempts_used']!=6 or state['budget']['reserved_seconds']!=0: raise RuntimeError('Wake 11 ledger mismatch')
results=[a['result'] for a in state['attempts']]
if results.count('succeeded')!=4 or results.count('failed')!=2 or any(a['state']!='terminal' for a in state['attempts']): raise RuntimeError('Wake 11 terminal-result mismatch')
verification=load('execution_windows/wake11/output/decontam_selector_verification.json')
if not verification['all_checks_passed'] or len(verification['checks'])!=25: raise RuntimeError('Final verifier mismatch')
review=load('review/wake11_decontam_selector_acceptance.json')
if review['final_decision']!='PASS_AS_PROSPECTIVE_SOFTWARE_MILESTONE_FORMAL_GATES_HOLD': raise RuntimeError('Independent review scope mismatch')
budget=load('phase_budget.json')
if abs(budget['cumulative_charged_seconds']-877.6923487709736)>1e-12: raise RuntimeError('Cumulative wall mismatch')

members=[]
for path in sorted(root.rglob('*')):
    rel=path.relative_to(root)
    if any(part in ('.writer.lock','__pycache__','.venv') for part in rel.parts): continue
    if path.is_symlink(): raise RuntimeError(f'Unreviewed symlink: {rel}')
    if not path.is_file(): continue
    if path.suffix in ('.pyc','.lock') or path.name.endswith(('-wal','-shm')): continue
    if rel.as_posix()=='manifest.json': continue
    members.append(path)

manifest={
  'generation':12,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'library_file_id':'libfile_8bb70b367b948191bfed83a45933917f',
  'previous_generation':11,
  'previous_library_version':11,
  'previous_archive_sha256':'6ef4c0be3a093e370841b0b48805298e82ed1833d15d22be840f4abc862db480',
  'goal_mode':'continuous_research',
  'science_identity':'pa-bpe-domain-robustness revision1; result-blind decontamination and disk-backed ranked-row stream software milestone PASS, every formal payload/training/fairness gate HOLD',
  'files':{str(p.relative_to(root)):digest(p) for p in members}
}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if destination.exists(): raise RuntimeError('Refuse to replace local archive')
destination.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in members+[root/'manifest.json']: z.write(p,'pa_bpe_simple/'+str(p.relative_to(root)))
with zipfile.ZipFile(destination) as z:
    if z.testzip() is not None: raise RuntimeError('Archive CRC failure')
    for name,h in manifest['files'].items():
        if hashlib.sha256(z.read('pa_bpe_simple/'+name)).hexdigest()!=h: raise RuntimeError(f'Archive member mismatch: {name}')
print(json.dumps({'archive':str(destination),'sha256':digest(destination),'size_bytes':destination.stat().st_size,'generation':12,'manifest_files':len(members),'manifest_sha256':digest(root/'manifest.json'),'historical_members_checked':len(old['files']),'changed_historical_members':changed}))
