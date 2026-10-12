"""Run unchanged restore --verify-only, additionally restore/check the DB from its verified ZIP."""
import hashlib, importlib.util, json, pathlib, sqlite3, sys, tempfile, zipfile

HERE=pathlib.Path(__file__).resolve().parent
source=HERE/'restore_3d_seq186.py'
if hashlib.sha256(source.read_bytes()).hexdigest()!='4126c4cddf04f36c12e63466be9fe29ee1c3ac48a4072782bd48d704e096ec56':
    raise RuntimeError('restore source changed')
spec=importlib.util.spec_from_file_location('pinned_restore',source)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
original=r.validate_zip
report={}
def extended_validate(path):
    result=original(path)
    with zipfile.ZipFile(path) as z, tempfile.TemporaryDirectory(prefix='cpu-db-check-') as td:
        checkpoint=json.loads(z.read('autopilot_3d/CHECKPOINT.json'))
        if checkpoint['project_id']!='autopilot-3d-20261011' or checkpoint['last_runner_sequence']!=190:
            raise RuntimeError('checkpoint mismatch')
        target=pathlib.Path(td)/'verified.sqlite3'
        target.write_bytes(z.read('autopilot_3d/.research-autopilot/simple-loop.sqlite3'))
        db=sqlite3.connect('file:'+str(target)+'?mode=ro',uri=True)
        local=sqlite3.connect('file:'+str(HERE/'autopilot_3d/.research-autopilot/simple-loop.sqlite3')+'?mode=ro',uri=True)
        if db.execute('pragma integrity_check').fetchone()[0]!='ok':raise RuntimeError('database integrity failed')
        for table in ['events','project','runner_state']:
            if db.execute('select * from '+table).fetchall()!=local.execute('select * from '+table).fetchall():
                raise RuntimeError('logical database differs: '+table)
        state=json.loads(db.execute('select payload from runner_state').fetchone()[0])
        if state['sequence']!=190 or state['attempts_used']!=146 or state['elapsed_seconds']!=13211.193054299029:
            raise RuntimeError('cumulative identity mismatch')
        if any(a['state']!='terminal' for a in state['attempts'].values()):raise RuntimeError('unsettled attempt')
        report.update(status='verified',project_id=checkpoint['project_id'],sequence=190,attempts=146,command_seconds=state['elapsed_seconds'],database_integrity='ok',logical_tables_match=True,files_verified=result[0],zip_crc='passed',cleanup='not_performed_residual_path_anomaly')
        db.close();local.close()
    return result
r.validate_zip=extended_validate
r.main()
report['commit']=sys.argv[sys.argv.index('--commit')+1]
(HERE/'3d_seq190_remote_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,sort_keys=True))
