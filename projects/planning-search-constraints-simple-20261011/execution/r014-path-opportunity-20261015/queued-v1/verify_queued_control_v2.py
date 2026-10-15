"""Additional literal canonicalqueued/task-input join over freshly HTTP verified ZIP.

Does not rerun the native or claim fresh download of historical alias bodies.
"""
import pathlib,json,zipfile,sqlite3,hashlib,gc,datetime
O=pathlib.Path('/dev/shm/r014-queued-publication-v1');p=json.loads((O/'remote-proof-v1.json').read_text());assert p['complete']
m=json.loads((O/'remote/manifest.json').read_text());idx=dict(m['members']);idx.update({x['path']:x for x in m['unchanged_source_aliases']})
with zipfile.ZipFile(O/'remote/archive.zip') as z:
 raw=z.read('windows/W0005/.research-autopilot/simple-loop.sqlite3')
 with sqlite3.connect(':memory:') as c:
  c.deserialize(raw);del raw;gc.collect();assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);j=json.loads(c.execute('select state from project where id=1').fetchone()[0])
 t=s['tasks']['R014-parent-path-opportunity-diagnostic-W5-v1'];assert t['state']=='queued' and t['attempt_id'] is None and not any(a['task_id']==t['task_id'] for a in s['attempts'].values());assert s['attempts_used']==37 and all(a['state']=='terminal' for a in s['attempts'].values()) and len(j['research_cycles'])==14
 assert t['reasoning_ref']==m['latest_accepted_review']==j['current_research_review']
 refs=t['input_refs']+[t['reasoning_ref']]
 for x in refs:
  n='windows/W0005/'+x['path'];assert n in idx and idx[n]['sha256']==x['sha256'],n
  if n in m['members']:assert hashlib.sha256(z.read(n)).hexdigest()==x['sha256'],n
 assert not any('/results/R014-parent-path-opportunity-diagnostic' in n for n in m['members'])
p.update(queued_control_checked_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),R014_task_id=t['task_id'],R014_task_state='queued',R014_attempt_id=None,R014_attempt_count=0,R014_native_result_members=0,task_input_ref_count=len(t['input_refs']),all_task_input_refs_bound_to_exact_new_members_or_verified_prior_alias_SHA=True,queued_control_verifier='verify_queued_control_v2.py',scope=p['scope']+' Additional canonical task queued/noattempt and every admitted task inputref joined to new verified member or exact prior verified alias SHA; historical alias bodies not re-downloaded.')
with (O/'remote-proof-v2.json').open('x') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps({'complete':True,'R014':'queued/noattempt','task_input_refs':len(t['input_refs']),'terminal':37,'cycles':14}))
