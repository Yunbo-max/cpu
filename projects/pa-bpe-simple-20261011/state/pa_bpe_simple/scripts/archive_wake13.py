"""Build recovery-only generation 14 after the wake13 scratch-root erasure."""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
def load(rel): return json.loads((root/rel).read_text())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

old=load('manifest.json')
if old['generation']!=13: raise RuntimeError('Expected generation 13 parent')
owner=load('.writer.lock/owner.json')
if owner['owner']!='automation-wake13-recovery-20261012T0750Z': raise RuntimeError('Wake 13 recovery does not own writer lock')
changed=[name for name,h in old['files'].items() if not (root/name).is_file() or digest(root/name)!=h]
allowed={'PA_BPE_Simple_Checkpoint.md','phase_budget.json','next_research_action.json'}
if set(changed)-allowed: raise RuntimeError(f'Unexpected historical changes: {sorted(set(changed)-allowed)}')
budget=load('phase_budget.json')
if abs(budget['cumulative_charged_seconds']-996.4486420159973)>1e-12: raise RuntimeError('Cumulative wall mismatch')
handoff=load('evidence/wake13_handoff.json')
if handoff['artifacts_survived'] or handoff['certified_adapter_result']!='HOLD': raise RuntimeError('Host-loss scope mismatch')

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
  'generation':14,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'library_file_id':'libfile_8bb70b367b948191bfed83a45933917f',
  'previous_generation':13,
  'previous_library_version':13,
  'previous_archive_sha256':'8c0c6b716d093d7b78b58c83516e5396a03f8bd5ec8a6030a6e31699510a200a',
  'goal_mode':'continuous_research',
  'science_identity':'pa-bpe-domain-robustness revision1; wake13 adapter observations lost before persistence, recovery specification retained, production adapter/row provenance/training/fairness gates HOLD',
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
print(json.dumps({'archive':str(destination),'sha256':digest(destination),'size_bytes':destination.stat().st_size,'generation':14,'manifest_files':len(members),'manifest_sha256':digest(root/'manifest.json'),'historical_members_checked':len(old['files']),'changed_historical_members':changed}))
