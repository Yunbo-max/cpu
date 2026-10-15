"""Verify literal queued control plus operative869refs; no flat old-feedback closure claim."""
import pathlib,json,zipfile,sqlite3,hashlib,gc,datetime,urllib.request
O=pathlib.Path('/dev/shm/r014-queued-publication-v1');D=O/'runtime-inputs-v4';V=D/'remote';V.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bp=json.loads((O/'remote-proof-v1.json').read_text());assert bp['complete'];m=json.loads((O/'manifest.json').read_text());assert sha(O/'remote/archive.zip')==m['archive_sha256']
commit=json.loads((D/'packet-commit.json').read_text())['commit'];folder='execution/r014-path-opportunity-20261015/queued-runtime-inputs-v4/';base='https://raw.githubusercontent.com/Yunbo-max/cpu/'+commit+'/projects/planning-search-constraints-simple-20261011/'
def get(n,h):
 with urllib.request.urlopen(base+folder+n,timeout=60) as f:b=f.read()
 assert hashlib.sha256(b).hexdigest()==h;npath=V/n;npath.write_bytes(b);return b
cm=json.loads(get('manifest.json',sha(D/'manifest.json')));allparts=[]
for x in cm['parts']:
 b=get(x['path'],x['sha256']);assert len(b)==x['bytes'];allparts.append(b)
(V/'archive.zip').write_bytes(b''.join(allparts));assert sha(V/'archive.zip')==cm['archive_sha256'] and (V/'archive.zip').stat().st_size==cm['archive_bytes'];del allparts
idx=dict(m['members']);idx.update({x['path']:x for x in m['unchanged_source_aliases']});idx.update(cm['members'])
with zipfile.ZipFile(O/'remote/archive.zip') as z,zipfile.ZipFile(V/'archive.zip') as extra:
 assert set(extra.namelist())==set(cm['members'])
 for n,x in cm['members'].items():
  b=extra.read(n);assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'] and (extra.getinfo(n).external_attr>>16)&0o777==x['mode']
 raw=z.read('windows/W0005/.research-autopilot/simple-loop.sqlite3')
 with sqlite3.connect(':memory:') as c:
  c.deserialize(raw);del raw;gc.collect();assert c.execute('pragma integrity_check').fetchone()[0]=='ok';s=json.loads(c.execute('select payload from runner_state where id=1').fetchone()[0]);j=json.loads(c.execute('select state from project where id=1').fetchone()[0])
 t=s['tasks']['R014-parent-path-opportunity-diagnostic-W5-v1'];assert t['state']=='queued' and t['attempt_id'] is None and not any(a['task_id']==t['task_id'] for a in s['attempts'].values());assert s['attempts_used']==37 and all(a['state']=='terminal' for a in s['attempts'].values()) and len(j['research_cycles'])==14
 assert t['reasoning_ref']==m['latest_accepted_review']==j['current_research_review']
 submitted=json.loads(z.read('windows/W0005/plans/R014-parent-path-opportunity-diagnostic-W5-v1-task-v2.json'));refs=submitted['input_refs'];assert len(refs)==869
 canonical={(x['path'],x['sha256']) for x in t['input_refs']}
 for x in refs:
  assert (x['path'],x['sha256']) in canonical;n='windows/W0005/'+x['path'];assert idx[n]['sha256']==x['sha256'],n
  if n in cm['members']:assert hashlib.sha256(extra.read(n)).hexdigest()==x['sha256']
  elif n in m['members']:assert hashlib.sha256(z.read(n)).hexdigest()==x['sha256']
 assert not any('/results/R014-parent-path-opportunity-diagnostic' in n for n in m['members'])
p=dict(bp);p.update(queued_control_checked_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),R014_task_id=t['task_id'],R014_task_state='queued',R014_attempt_id=None,R014_attempt_count=0,R014_native_result_members=0,submitted_runtime_input_refs=len(refs),inventory_input_refs=866,canonical_input_refs_including_inherited_feedback=len(t['input_refs']),all_submitted_runtime_input_refs_bound_to_new_members_or_verified_prior_alias_SHA=True,runtime_input_supplement={'commit':commit,'manifest':folder+'manifest.json','manifest_sha256':sha(V/'manifest.json'),'archive_bytes':cm['archive_bytes'],'archive_sha256':cm['archive_sha256'],'members':len(cm['members']),'new_raw_bytes':sum(x['bytes'] for x in cm['members'].values()),'all_parts_members_modes_independent_immutable_HTTP_verified':True},queued_control_verifier='verify_runtime_control_v4.py',v2_failed_assumption='All inherited historical feedback raw bodies need not be directly addressed by flattened current alias index. v2failure preserved, no oldarchive corruption inference.',v3_generator_failure='Assert866 incorrectly used for submitted869=inventory866+3admissiondocs; failed before supplement creation, v4versionedfix.',scope=bp['scope']+' Operative869submitted runtime refs (866inventory+3admissiondocs) joined against verified base/aliases plus freshHTTPfour-input supplement. Canonical1537 also includes inherited historical feedback refs; full historical body/derived resolution is retained prior recovery chain, NOT asserted fresh flat-index closure. No native result or scientific cycle. Original base HTTPcache wholeSHA rechecked, not re-downloaded.')
with (O/'remote-proof-v4.json').open('x') as f:print(json.dumps(p,indent=2),file=f)
print(json.dumps({'complete':True,'R014':'queued/noattempt','runtime_refs':869,'canonical_refs':len(t['input_refs']),'supplement_members':len(cm['members']),'terminal':37,'cycles':14}))
