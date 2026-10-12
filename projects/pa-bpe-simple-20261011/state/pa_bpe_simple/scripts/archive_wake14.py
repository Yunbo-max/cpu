"""Build generation 15 after certified wake14 adapter recovery and verification."""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
def load(rel): return json.loads((root/rel).read_text())
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

parent_archive=root.parents[1]/'PA_BPE_Simple_Checkpoint_wake13_recovery.zip'
with zipfile.ZipFile(parent_archive) as parent_zip:
    old=json.loads(parent_zip.read('pa_bpe_simple/manifest.json'))
if old['generation']!=14: raise RuntimeError('Expected generation 14 parent')
owner=load('.writer.lock/owner.json')
if owner['owner']!='automation-wake14-20261012T0833Z': raise RuntimeError('Wake 14 does not own writer lock')
changed=[name for name,h in old['files'].items() if not (root/name).is_file() or digest(root/name)!=h]
allowed={'PA_BPE_Simple_Checkpoint.md','phase_budget.json','next_research_action.json'}
if set(changed)-allowed: raise RuntimeError(f'Unexpected historical changes: {sorted(set(changed)-allowed)}')

budget=load('phase_budget.json')
if abs(budget['cumulative_charged_seconds']-996.9883702889974)>1e-12: raise RuntimeError('Cumulative wall mismatch')
handoff=load('evidence/wake14_handoff.json')
if not handoff['artifacts_survived'] or handoff['certified_adapter_result']!='PASS': raise RuntimeError('Adapter scope mismatch')
verification=load('execution_windows/wake14/output/blinded_adapter_verification.json')
if not verification['all_checks_passed'] or len(verification['checks'])!=20: raise RuntimeError('Verification gate mismatch')
review=load('execution_windows/wake14/evidence/independent_review.json')
if review['verdict']!='PASS' or review['blocking_defects']: raise RuntimeError('Independent review gate mismatch')
status=load('execution_windows/wake14/evidence/final_status.json')
if status['status']!='stopped' or any(t['state']!='succeeded' for t in status['tasks']): raise RuntimeError('Runner is not cleanly settled')
if any(a['state']!='terminal' or a.get('result')!='succeeded' for a in status['attempts']): raise RuntimeError('Attempt identity remains unsettled')

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
  'generation':15,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'library_file_id':'libfile_8bb70b367b948191bfed83a45933917f',
  'previous_generation':14,
  'previous_library_version':14,
  'previous_archive_sha256':'911121ca7d8d5f65e2c8fa30674f8268a95629f113d0e383d2281f790d1c827f',
  'goal_mode':'continuous_research',
  'science_identity':'pa-bpe-domain-robustness revision1; wake14 hash-only confirmation adapter mechanics and frozen-index preservation PASS after 20 checks and independent review; row provenance, production development selection, tokenizer and fairness gates HOLD',
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
print(json.dumps({'archive':str(destination),'sha256':digest(destination),'size_bytes':destination.stat().st_size,'generation':15,'manifest_files':len(members),'manifest_sha256':digest(root/'manifest.json'),'historical_members_checked':len(old['files']),'changed_historical_members':changed}))
