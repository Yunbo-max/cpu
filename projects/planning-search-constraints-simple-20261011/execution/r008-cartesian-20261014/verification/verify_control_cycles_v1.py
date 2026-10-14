"""Read-only scientific event check on the already independently downloaded control member."""
import pathlib,json,sqlite3,hashlib
B=pathlib.Path(__file__).resolve().parent;O=B/'r008-relation-publication';p=O/'remote-verification-v1/control.sqlite3';m=json.loads((O/'manifest.json').read_text());expected=m['members']['windows/W0005/.research-autopilot/simple-loop.sqlite3'];assert p.stat().st_size==expected['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==expected['sha256']
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
 events=[json.loads(x[0]) for x in c.execute('select payload from events order by version')];cycles=[e for e in events if e.get('kind')=='research_cycle'];assert len(cycles)==7
 assert cycles[-1]['event_id']=='W5-R008-independent-cartesian-relation-cycle-v1'
 result={'valid':True,'remote_control_member_sha256':expected['sha256'],'cycle_count':len(cycles),'cycle_event_ids':[e['event_id'] for e in cycles],'scope':'Read-only check of exact control member already fully downloaded and ZIP-member SHA verified at immutable packet a186bb10491a157d0bdb8e839012c40234b4eb9e. Journal declarations are not automatic scientific certification;4inherited+L2+observer+Cartesian relation cycles retained.'}
(O/'remote-control-journal-supplement-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
