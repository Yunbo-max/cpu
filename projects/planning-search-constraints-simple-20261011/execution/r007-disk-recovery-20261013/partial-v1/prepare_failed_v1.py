import pathlib,json,datetime,hashlib,subprocess,sqlite3,tarfile,zstandard,os,time,io
B=pathlib.Path('/workspace/scratch/d503fbbd44e2/planning-restart');P=pathlib.Path('/workspace/scratch/1389522c4edd/planning_simple');R=P/'windows/W0004';CLI=B/'rsi-simple-13/scripts/simple_runner.py';NS='projects/planning-search-constraints-simple-20261011';start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
s=json.loads(subprocess.check_output(['python',str(CLI),'--root',str(R),'status']));assert s['budget']['reserved_seconds']==0 and all(a['state']=='terminal' for a in s['attempts']);assert s['budget']['attempts_used']==62;health=json.loads(subprocess.check_output(['python',str(CLI),'--root',str(R),'health']));assert not health['identity_observed_alive'];ledger={'prior_attempt_floor':214,'prior_command_seconds_floor':14447.537480669998,'window_attempts':62,'window_command_seconds':s['budget']['elapsed_seconds'],'combined_attempt_floor':276,'combined_command_seconds_floor':14447.537480669998+s['budget']['elapsed_seconds'],'scope':'Command accounting includes historical conservative/reported entries, not precise CPU or science cycles','actual_scoped_research_cycles':s['research_cycle_count'],'native_model_usage':'unknown'}
incident={'utc':utc,'error':'OSError28 No space left on device while writing next decision','native_attempts':62,'all_terminal':True,'reserved_seconds':0,'native_solver_for_r2_counts_started':False,'completed_R007_timing_tasks':[p.parent.name for p in (R/'results').glob('R007-cpu-overhead*/result.json')],'finite_batch_complete':False,'original_error_coordinator_session':65103,'supervisor_owned_session':28129,'supervisor_actual_exit_status':130,'goal_stop_issued':False,'canonical_control_not_modified':True,'retained_source_objects':'Current control, all orphan raw files, response files, raw outputs remain; remote proof before removing only hash-unchanged idle duplicate objects','memory_policy':'Latest user host-only kernel limit; disk failure is not CPU unavailability or prelaunch memory refusal'};(R/'evidence/R007-disk-space-exhaustion-v1.json').write_text(json.dumps(incident,indent=2)+'\n')
for name in ['CURRENT_EXECUTION.json','CHECKPOINT.json']:
 j=json.loads((P/name).read_text());j['updated_utc']=utc;j['active_or_unknown_attempts']=0;j['waiting_for_memory']=None;j['waiting_for_storage']=incident;j['current_memory_policy']=json.loads((P/'CURRENT_MEMORY_POLICY.json').read_text());j['accepted_decision' if name=='CHECKPOINT.json' else 'current_accepted_decision']=s['journal']['current_research_review'];j['ledger' if name=='CHECKPOINT.json' else 'project_ledger']=ledger
 if name=='CURRENT_EXECUTION.json':
  j['window_budget']=s['budget'];j['actual_health']=health;j['active_coordinator']={'owned_supervisor_session':28129,'actual_quiet_exit_status':130,'native_active_or_unknown':0,'goal_stop_issued':False,'state':'No live coordinator; actual disk failure after six timing successes'};j['guards']={'cpu_only':True,'threads':1,'max_concurrency':1,'project_memory_limit_bytes':None,'shared_abort_bytes':None,'prelaunch_headroom_gate':False,'actual_kernel_memory_max_bytes':8589934592,'native_frozen_comparison':'120CPU/2500M_AS,145wall/2.8GBprocessRSS/3.5GBouterAS'};j['next_task']='Resume only unexecuted frozen R007 rotations2/3 after actual disk repair';j['R007_native_results']={'pilot':'10000 reached, cost24/VAL, feasibility only','qualification':'coarse independently audited; counts/fine genuinely compared to coarse; all graphSHA7c141bddef4d6f14ba5449c5922e43263ccb2a2111aab36217a3890fff841c12, cost24/VAL','timing_successes':6,'timing_target':12,'full_comparison':'incomplete; no R007 overhead conclusion yet'}
 else:
  j['stage']='R007 modes qualified; six of twelve frozen timings succeeded; actual disk failure before next solver';j['next_task_id']='R007-cpu-overhead-r2-counts-host-v1';j['next_dispatch']='After remote-verified forensic/bookkeeping offload, sameW4 official run and resume frozen inventory, preserve original six successes. No artificial memory gate.';j['next_submission']=None;j['unfinished']=['R007 remaining six timing executions and complete analysis','Per-split witness and transformed operator oracle','Full native efficiency/more public conditions/novelty evidence','Depots L2 remains draft','Orphan SQLite/source/binary corruption cause unresolved'];j['full_window_snapshot']='f2f16f6 core at52 verified, explicitly deferred23 orphan raw images; latest R007/control62 supplemental disk-recovery package preparing';j.pop('lowRAM_progress',None)
 if 'published_supplement' in j:j['published_supplement']['historical_only']=True;j['published_supplement']['current_native_state']='Historical37 state, superseded by current62; user removed old memory gates; do not use as current worker state'
 (P/name).write_text(json.dumps(j,indent=2)+'\n')
(P/'RESUME.md').write_text('''# 接续状态（2026-10-13）

Simple13 同一 W0004/constraint-propagation-cost-v1；旧 W3 stop、失败和累计预算保留。用户22:44BST已撤销人为8GB/shared/prelaunch阈值，按内核实际8589934592B执行。当前62 attempts均终态、reservation0；CPU可用，R007三模式10000-state图/VAL核验已真实通过，12次新计时只完成前6次。实际磁盘满使第7项决策写入失败，求解器未启动。owned supervisor28129在全终态边界SIGINT真实exit130，没有goalstop。

先核验最新 GitHub metadata、LATEST core52及最新补充manifest/所有parts/full raw hashes，再结合本地真实status/health/receipts。正在准备把闲置孤立SQLite原始对象和膨胀response副本完整存档；不得把它们当current SQLite删掉。只有远端完整原始字节核验后才清理同hash的闲置副本。当前canonical simple-loop.sqlite3不删除不编辑；补充采用readonly在线backup。source/JSON膨胀根因尚未确认。

空间恢复后继续原R007 frozen inventory尚未执行的r2/r3六项，使用同W4官方run、唯一helper和有限resume observer。已有r0/r1六项禁止重跑；R007尚无完整性能结论。完成后核验全部12原始计数/计划/VAL/整数CPUwall/分母，更新accepted previous_ref和probe链。下一科学工作是逐split图见证；旧final snapshots只证明终态，不伪称trajectory。当前没有新R008 native结果。
''')
(P/'CURRENT_RESEARCH.md').write_text('''# 当前规划约束研究

CPU真实可用；最新用户内存政策为只服从宿主内核硬限额、真实失败后诊断，不按高共享file-cache提前等待。R0061000-state新12次CPU/wall对照完整成功，但fine/counts三比例1.0995/0.9047/1.2751仍反转，不能认定intrinsic谓词成本或算法速度收益。此前wall批次、失败和预算全部保留。

R007同一公开BWp05开发条件仅改max_states10000：pilot真实达到10000，计划cost24独立VAL；coarse/counts/fine真实finalgraph一致（SHA7c141bddef4d6f14ba5449c5922e43263ccb2a2111aab36217a3890fff841c12），线性独立auditor核验mirror/multiplicity/domain/order/64bit shortest paths。Coarse独立无peer，counts/fine实际对比coarse，不把旧字段graph_exact_peer标签当不存在peer的证据。资格export时间不eligible performance。

新12次CPUwall冻结对照当前只执行前6次（3warmup+rotation1三项），均cost24/VAL；其余6项未启动。协调脚本实际遭磁盘空间不足，第7项decision写入失败，无新增native attempt/科学失败。保留当前62 attempts/0reserve和原始错误；先完整远端保存闲置raw forensic/bookkeeping字节，核验后清理相同hash副本，再接续。此时不发表R007全部比较结论或计新周期。项目仍是continuous_research，没有goalstop。

完整native效率、多public条件、每split图见证及变换算子oracle、主要原文/作者代码新颖性证据仍欠。旧W3取消/保守账本、R005/R005L1超时与native内存删失不改写。R007的最终图见证同样不推出中间每split等价。
''')
# Supported read-only online backup; no private DB edit or deadline reset.
backup=B/'r007-control62-readonly-backup.sqlite3';assert not backup.exists();src=sqlite3.connect((R/'.research-autopilot/simple-loop.sqlite3').as_uri()+'?mode=ro',uri=True);assert src.execute('pragma quick_check').fetchone()[0]=='ok';dst=sqlite3.connect(backup);src.backup(dst);assert dst.execute('pragma quick_check').fetchone()[0]=='ok';dst.close();src.close()
files={}
def add(p,member,cleanup=False):
 p=pathlib.Path(p);assert p.is_file();files[str(p)]={'file':str(p),'member':member,'cleanup_after_remote_verification_only':cleanup}
for p in (R/'.research-autopilot').glob('.simple-loop.sqlite3.*'):add(p,'project/'+str(p.relative_to(P)),True)
for p in B.iterdir():
 if p.is_file() and ((p.suffix=='.json' and p.stat().st_size>1048576) or (p.name.startswith('r006-db-') and p.suffix=='.sqlite3')):add(p,'coordinator/'+p.name,True)
add(backup,'project/windows/W0004/.research-autopilot/simple-loop.sqlite3')
for p in (R/'.research-autopilot/runner').rglob('*'):
 if p.is_file():add(p,'project/'+str(p.relative_to(P)))
for folder in ['results','plans','scripts','evidence']:
 for p in (R/folder).rglob('*'):
  if p.is_file() and ('R007' in str(p.relative_to(R)) or 'r007' in str(p.relative_to(R))) and '__pycache__' not in str(p):add(p,'project/'+str(p.relative_to(P)))
for n in ['CURRENT_EXECUTION.json','CHECKPOINT.json','CURRENT_RESEARCH.md','RESUME.md','CURRENT_MEMORY_POLICY.json']:
 add(P/n,'project/'+n)
for n in ['r006-cpu-core-remote-verification.json','verify_remote_r006_cpu_core_archive_v1.py','r007-disk-space-recovery-published-packs-v1.json','prepare_r007_disk_recovery_archive_v1.py']:
 add(B/n,'coordinator/'+n)
pack=B/'r007-disk-recovery-control62-v1.tar.zst';assert not pack.exists();rows=[]
class HR:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):q=self.f.read(n);self.h.update(q);self.n+=len(q);return q
with pack.open('wb') as out, zstandard.ZstdCompressor(level=3,threads=0).stream_writer(out,closefd=False) as compressor, tarfile.open(fileobj=compressor,mode='w|') as archive:
 for idx,x in enumerate(files.values()):
  p=pathlib.Path(x['file']);before=p.stat();info=archive.gettarinfo(str(p),arcname=x['member']);info.uid=info.gid=0;info.uname=info.gname=''
  with p.open('rb') as raw:
   reader=HR(raw);archive.addfile(info,reader)
  after=p.stat();assert before.st_size==after.st_size==reader.n and before.st_mtime_ns==after.st_mtime_ns;rows.append(dict(x,bytes=reader.n,sha256=reader.h.hexdigest()))
  if idx%20==0:print(json.dumps({'archived_members':idx+1,'compressed_bytes_so_far':pack.stat().st_size}),flush=True)
  assert time.monotonic()-start<600,'Bounded forensic archive exceeded600 wall, preserve partial pack'
h=hashlib.sha256();parts=[];offset=0
with pack.open('rb') as stream:
 while chunk:=stream.read(8388608):
  h.update(chunk);parts.append({'part_index':len(parts),'offset':offset,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest(),'git_sha':hashlib.sha1(f'blob {len(chunk)}\0'.encode()+chunk).hexdigest(),'remote_path':NS+f'/execution/r007-disk-recovery-20261013/parts/part-{len(parts):05d}.bin'});offset+=len(chunk)
manifest={'schema_version':1,'project_id':NS.split('/')[-1],'utc':utc,'base_core_commit':'f2f16f6fedf3cf3093d37dc1ce81e138d479ea0c','base_core_manifest':'snapshots/r006-cpu-host-core-w4-20261013T2212.json','archive_format':'tar.zst','pack_file':str(pack),'pack_bytes':pack.stat().st_size,'pack_sha256':h.hexdigest(),'parts':parts,'members':rows,'raw_bytes':sum(x['bytes'] for x in rows),'canonical_control_backup':'project/windows/W0004/.research-autopilot/simple-loop.sqlite3','canonical_backup_quick_check':'ok','actual_window_attempts':62,'reserved_seconds':0,'scope':'Supplemental recovery at62: current valid control read-only backup; complete runner receipts/requests; all current R007 code/contracts/config/raw results/graphs/VAL and all explicit listed idle forensic/header copies and large coordinator snapshots. Preserve every historical base member/pack by reference. Not a new native result or full vendor-tree snapshot. Source orphan cause unconfirmed. Remote complete raw SHA verification is required before cleanup; current canonical SQLite/control/source/results are never cleanup targets.'};(B/'r007-disk-recovery-control62-manifest-v1.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'archive_complete':True,'compressed_bytes':manifest['pack_bytes'],'raw_bytes':manifest['raw_bytes'],'members':len(rows),'parts':len(parts),'wall_seconds':time.monotonic()-start,'space_free':os.statvfs(B).f_bfree*os.statvfs(B).f_frsize}),flush=True)
