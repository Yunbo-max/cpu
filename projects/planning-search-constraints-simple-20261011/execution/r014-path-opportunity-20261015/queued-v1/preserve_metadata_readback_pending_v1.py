"""Preserve actual readback permission failure; no alternate read-channel retry."""
import pathlib,json,hashlib,datetime
O=pathlib.Path('/dev/shm/r014-queued-publication-v1');P=O/'readback-pending-v1';P.mkdir(exist_ok=False);B=O/'proof-publish-v2'
incident={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'metadata_commit':'db1e7841891c2f6c25672ceee470c6846b38740f','owned_metadata_verifier_session':34955,'actual_tool_error':'Unified exec process failed: network approval was cancelled before a decision was returned','complete_metadata_readback_proof_exists':False,'scope':'Network permission failure during independent HTTP readback of15newmetadata files. No fullverification claimed. Do not bypass or retry via alternate channel. Previously completed packet19parts/128members and four-runtime-input supplement were already independently HTTPverified. This is not native/remote-data corruption evidence.','new_metadata_verification':'pending; upload Gitblob SHA was checked, not substitute for independent HTTP readback','R014_state':'queued/noattempt/no native,37terminal/reserve0/cycle14','continuity':'Actual transient storage failure remains; retain existing authorized future entry, no newautomation/run_now/goalstop. Next fresh status/stop, respect network authorization boundary; retry only when authorized access available.'}
with (P/'metadata-readback-pending-v1.json').open('x') as f:print(json.dumps(incident,indent=2),file=f)
note='# R014 最新元数据回读未完成\n\n恢复包体和四个runtime输入补充已独立HTTP核验。db1e7841891c2f6c25672ceee470c6846b38740f的15新metadata回读遇到network approval cancelled，尚无complete metadata-readback proof，不能称全部元数据验收。保留权限边界，不换通道绕过。此补记自身同样尚未独立HTTP回读。R014仍queued/noattempt，37terminal/0reserve/14cycle，没有编译/native结果。磁盘故障未解除，不盲重启。\n\n'
for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json']:
 x=json.loads((B/n).read_text());x['metadata_readback_status']=incident;x['R014']['metadata_independent_HTTP_acceptance']='pending after authorization cancellation; packet bodies already verified';
 with (P/n).open('x') as f:print(json.dumps(x,indent=2),file=f)
for n in ['CURRENT_RESEARCH.md','RESUME.md']:(P/n).write_text(note+(B/n).read_text())
(P/'R014_METADATA_READBACK_PENDING.zh-CN.md').write_text(note)
prefix='projects/planning-search-constraints-simple-20261011/';folder='execution/r014-path-opportunity-20261015/queued-v1/';files=[(P/n,prefix+n) for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','RESUME.md','R014_METADATA_READBACK_PENDING.zh-CN.md']]+[(P/'metadata-readback-pending-v1.json',prefix+folder+'metadata-readback-pending-v1.json'),(pathlib.Path(__file__),prefix+folder+'preserve_metadata_readback_pending_v1.py')];u=[]
for p,n in files:
 b=p.read_bytes();u.append({'local':str(p),'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()})
with (P/'uploads.json').open('x') as f:print(json.dumps(u,indent=2),file=f)
print(json.dumps({'files':len(u),'HTTP_readback':'not retried; pending','scope':'publish truthful failure note only'}))
