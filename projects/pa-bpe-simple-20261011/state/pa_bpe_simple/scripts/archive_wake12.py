"""Verify Wake 12 state and build generation 13 of the canonical checkpoint."""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
def load(rel): return json.loads((root/rel).read_text())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

old=load('manifest.json')
if old['generation']!=12: raise RuntimeError('Expected generation 12 parent')
owner=load('.writer.lock/owner.json')
if owner['owner']!='automation-wake12-20261012T0526Z': raise RuntimeError('Wake 12 does not own writer lock')
changed=[name for name,h in old['files'].items() if not (root/name).is_file() or digest(root/name)!=h]
allowed={'PA_BPE_Simple_Checkpoint.md','phase_budget.json','next_research_action.json'}
if set(changed)-allowed: raise RuntimeError(f'Unexpected historical changes: {sorted(set(changed)-allowed)}')

state=load('execution_windows/wake12/output/stop_wake12.json')
if state['budget']['attempts_used']!=10 or state['budget']['reserved_seconds']!=0: raise RuntimeError('Wake 12 ledger mismatch')
results=[a['result'] for a in state['attempts']]
if results.count('succeeded')!=8 or results.count('failed')!=2 or any(a['state']!='terminal' for a in state['attempts']): raise RuntimeError('Wake 12 terminal-result mismatch')
verification=load('execution_windows/wake12/output/blinded_index_verification_v2.json')
if verification['checks_passed']!=2286 or verification['sqlite_integrity']!='ok': raise RuntimeError('Final verifier mismatch')
review=load('review/wake12_blinded_index_acceptance.json')
if review['verdict']!='PASS' or len(review['findings'])!=5: raise RuntimeError('Independent review scope mismatch')
budget=load('phase_budget.json')
if abs(budget['cumulative_charged_seconds']-994.4588047509768)>1e-12: raise RuntimeError('Cumulative wall mismatch')

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
  'generation':13,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'library_file_id':'libfile_8bb70b367b948191bfed83a45933917f',
  'previous_generation':12,
  'previous_library_version':12,
  'previous_archive_sha256':'8cc548d96af4eff85c50f543f2e732d642f9d55fa0967b0d10d1eb1cc1ced04c',
  'goal_mode':'continuous_research',
  'science_identity':'pa-bpe-domain-robustness revision1; fail-closed result-blind GlobalVoices confirmation fingerprint index PASS, production adapter/row provenance/training/fairness gates HOLD',
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
print(json.dumps({'archive':str(destination),'sha256':digest(destination),'size_bytes':destination.stat().st_size,'generation':13,'manifest_files':len(members),'manifest_sha256':digest(root/'manifest.json'),'historical_members_checked':len(old['files']),'changed_historical_members':changed}))
