"""Only this wake's new verified files; never retry legacy eviction failures."""
import datetime,hashlib,json,os,pathlib,sqlite3,subprocess
BASE=pathlib.Path('/workspace/scratch/faa0880830cd');ROOT=BASE/'3d_autopilot_simple';OUT=BASE/'github_delta_wake18';STAGE=BASE/'restore_wake18_composed_verify'
v=json.loads((OUT/'verification.json').read_text());assert v['composed_restore_verified']
s=json.loads(subprocess.check_output(['python3','runtime/scripts/simple_runner.py','--root','.','status'],cwd=ROOT));h=json.loads(subprocess.check_output(['python3','runtime/scripts/simple_runner.py','--root','.','health'],cwd=ROOT))
assert s['budget']['reserved_seconds']==0 and not any(a.get('result') is None for a in s['attempts']) and not h['identity_observed_alive'] and s['stop_requested'] is None
items=[]
for r in json.loads((OUT/'new-project-files.json').read_text()):
 p=ROOT/r['path']
 if p.exists():
  assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];items.append(p)
# Owned fresh verification copies and binary transport staging only.
for directory in [STAGE,OUT/'remote_verify']:
 items.extend(p for p in directory.rglob('*') if p.is_file() and not p.is_symlink())
items.extend(OUT/p['path'].split('/')[-2]/p['path'].split('/')[-1] for p in json.loads((OUT/'manifest.json').read_text())['parts'])
items.extend([OUT/'delta.zip',BASE/'3D_Autopilot_Simple_Checkpoint.zip',OUT/'remote_restore.py'])
rows=[]
for p in dict.fromkeys(items):
 if not p.exists():continue
 b=p.read_bytes();r={'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'inode_before':p.stat().st_ino}
 p.unlink();r['absent_immediately']=not p.exists();rows.append(r)
r={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'One pass only on wake18 newly verified project files and owned fresh staging; legacy files/dependencies/other projects/global caches untouched. Deletion is not equivalent RAM reclamation.','supervisor_stopped':True,'unknown_attempts':0,'files':rows,'deleted_files':sum(x['absent_immediately'] for x in rows),'deleted_bytes':sum(x['bytes'] for x in rows if x['absent_immediately']),'persistent_deletion':'not_yet_observed'}
(OUT/'cleanup.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='files'}))
