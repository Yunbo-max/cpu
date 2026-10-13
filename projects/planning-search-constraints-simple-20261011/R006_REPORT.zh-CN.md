# R006：固定工作量的成本细分与最终图见证（2026-10-13）

R006已实际执行公开Autoscale21.11 Blocksworld p05 states_ops开发配置，沿用原SAS、NONE策略和默认seed2011；只将构建前沿冻结为1000状态。原生搜索解出成本24、24步的计划，独立VAL通过。全部整数分区、生命周期、短路计数、零工作和精确前沿核验有效。

| 细粒度测量 | 构建占比 |
|---|---:|
| 出边适用性 | 3.2132% |
| 入边＋出边可达性 | 13.1911% |
| 入边＋出边策略判断 | 1.2026% |
| 入边＋出边写入 | 2.4886% |
| 入边＋出边生成残余 | 40.1657% |

构建为134,628,252ns；适用性4,325,892ns。出边发生次数m=23,178、每次重连的不同算子数之和d=7,528，m/d=3.0789；999次闭合重连含1次零出边。按相同调用成本模型估算可省2.1696%构建，低于冻结的1/11（9.0909%）优先门槛；适用性也被可达性／残余占比超过。因此不优先实现普通per-call适用性缓存。该估算有相同调用成本假设，不是异质调用的无条件上界；这是已暴露、细粒度插桩开发前沿上的优先级负结果，不证明所有规模均无效。

独立构建了粗计时父版本与细计时版本的只读图导出器。两份1000状态最终TSV字节相同，具有16,422条非环边、7,186个环、每状态19个变量。独立Python核验精确出／反向入边多重集、存储计数、域与空状态标记、初始／目标、算子成本、出入邻接及环顺序；从初态与反向目标重算的最短路和两份原生64位距离完全一致。该例没有零成本算子，也无不可达状态。最终见证不证明每次分裂、所有实例或完整轨迹等价。图导出开销排除在性能结论之外。

40.1657%生成残余仍包含细粒度时钟、计数和新不同算子集合构建，不能直接归因于原算法。下一具体任务为R006-clock-control-build-v1：同计数的fine/counts模式，先图资格再按已冻结粗／计数／细控制协议执行；没有加速或新颖性结论。

W0003按真实17:21停止指令保持停止，取消回执保留；更新的17:25:54授权只接续未来W0004工作。W4保留全部原窗口和累计账本，未重跑R005/R005L1。恢复遇到真实目标文件／二进制内容变空或变零、链接及SHA身份失败；所有失败与消耗保留，当前正常产物采用新路径、明确对象库存、fsync、重复哈希和真实原生回执。根因尚未确定，不将无OOM或成功重链当作永久修复证明。未删除项目文件，未清全局缓存。

原R005四行、原120秒Depots超时与R005L1两项600秒／2500M原生内存删失均留在分母；3000M L2仍未执行。CPU-only、单队列单线程、8,000,000,000字节项目限制与7.8GB保护保持。完整失败分母、原始日志、VAL、图、分析代码和源码身份随增量快照归档；尝试数与含保守结算的命令秒数不是科研周期或精确CPU实耗。

## 2026-10-13新增计时控制与CPU观测依赖

在相同公开Blocksworld p05开发SAS、1000 frontier、原policy/search/seed/单线程下，新fine/counts modes先分别以真实native图快照、Counter/orderedadjacency/独立最短路和cost24独立VAL核验；与原图SHA6d8625...一致。counts mode关闭14细clock reads，全部计数/新operator-summary set/原coarse stageclock保留，duration0代表关闭测量而不是谓词成本0。coarse comparator继承只读audit hook；计时禁止export，hook argument的共同开销仍存在。

冻结3arms×(1warmup+3rotations)，实际12个成功native执行、1个开发条件，不是12独立样本或周期。每次native120CPU/2500M、wall145、RSS2.8GB/outerAS3.5GB、shared7.8GB、affinity0。全部计划cost24/VAL；所有共同计数、fine/counts全计数、expanded161440/evaluated336855和plan hash一致。

| rotation | coarse construction ns | counts construction ns | fine construction ns | fine/counts | counts/coarse |
|---|---:|---:|---:|---:|---:|
| 1 | 90319876 | 117664757 | 95869540 | 0.814769 | 1.302756 |
| 2 | 86572900 | 91746964 | 91651765 | 0.998962 | 1.059765 |
| 3 | 93103470 | 126152377 | 131179090 | 1.039846 | 1.354970 |

Fine/counts方向跨轮反转，median0.998962；counts/coarse较大但不能从这些wall ratios确定因果开销。宿主未独占、短阶段噪声和一次memory-wait gap均保留。不可把aggregate差值减给individual predicates；没有intrinsic residual、全native速度优势或新颖性结论。12成功native guard childCPU合计9.581757s、monotonic wall合计10.166104s；包含wrapper/native完整solve，排除hash/source preflight和独立VAL，不是项目总成本。

clock-control build-v1在旧fine-audit CEGAR对象0bytes身份检查失败，solver未启动。新build-v2重编受影响对象/source-isolated control成功。r2counts-v1在6685921280B共享charge触发原prelaunch资源拒绝，未启动solver；独立IDv2恢复成功，原失败回执不删除。有限观察器最初receipt先到、supervisor尚未结算的竞态也保留，修为等待official终态并保留已经完成项，未重跑旧成功任务。无hostOOM/kill证据。

下一步实际做了CPU-clock source-boundary/API审计，随后两份source-isolated C++ controls成功构建。只在原begin/print construction边界增加2次CLOCK_THREAD_CPUTIME_ID，原steady wall/component clocks不更换；CPU interval为wall outer bracket，含边界读取开销，不能直接两者相减当纯等待/谓词成本。coarse binary e6b21554b4f7c08288236c54f56f4fb3b5ca928400e267bec4ac6000a0cf51be，fine_counts30d810ab1b5cbb642eb486a3ad4a8ce8963333aa4e52154ef80a34bf7f7eaa10；guardwall12.933846s、sampled groupRSS582545408B、shared peak7431770112B、exit0/无guard。**尚未执行native CPU-clock/graph/VAL资格或CPU比较。** 下一份counts资格已有完整代码和accepted decision，资源鲜测后同W4接续。

旧d75e3e6归档36parts/301462889B、整体SHAf2d701e...和manifest已独立从不可变Git对象回读；新pack全部4970members/914070498B逐成员SHA/bytes核验，5直接raw复制也核验。没有删除本地唯一数据。只对已核验、hash不变、闲置的3份published duplicate binaries和pack做cachehint，当次7185457152→6292717568B，无truncate/byte mutation/global cache clear；不把这个观察当对象损坏原因。

## 最新接续 2026-10-13T20:41:07.019482+00:00

CPU资格v1/v2/v3均在prelaunch资源保护拒绝，solver没有启动，未产生nativeCPU字段、图或VAL新结果。v3实际guard前共享charge7481118720B，750MB案例余量不能满足。此前非常驻supervisor启动后计账增长524488704B，因此恢复条件已版本化：无live supervisor时current<=6.1e9；有真实核验resident supervisor时<=6.6e9，并鲜测CPU/anon/file/cache/events/其他或未知活动。仍保持shared abort7.8e9/project8e9及全部native限制。快照不是全局资源预留。新R006-cpu-clock-counts-qualification-after-memory-v4已准备但未提交，先消费所有最新probes/newprevious_ref才派发；不重复已失败ID，不以空队列/局部失败结束持续目标。

W4实际37attempts/769.783455120014结算秒/reservation0；项目累计下界251/15217.320935790012。保守1823秒、losthostreported19次/1042.6368527140294秒和旧W3真实stop/cancel保留；不是精确CPU或科研周期。所有native任务terminal，旧supervisor身份当前不存活，session不可连接但不伪造exit130。已有12次旧native对照不重跑。完整7104归档已独立回读31parts、全部3731新members/817741509B和4直接rawcopy；最新37状态与三个拒绝作为独立操作补充提交，旧LATEST保留，完整37全窗口overlay待归档余量满足。
