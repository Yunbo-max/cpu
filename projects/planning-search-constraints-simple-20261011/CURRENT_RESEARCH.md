# R014：原生完成，但轨迹不完整，未通过原机会检验

2026-10-15 最新实际状态：39个W5 attempt全terminal/0reserve，14个科学cycle。R014原生只运行一次；没有重跑求解器/h2，也没有记录cycle15。

原生 exit0，wait4 user103687205+system5534325=109221530us，wall110260517137ns，maxRSS717303808B。粗work为28components/33061states/1000002nonloops/expanded9830440/evaluated17639567，plan26/cost26/计划SHA3e216bbefad0615165dff294a3b50d69a916b5bb29862c4612a586a80403993f；新的只读保留计划检查已对原PDDL独立VAL成功，粗work/计划与保留R012相同。仅此范围有效，不是完整路径机会、每组件图、启发式轨迹或最优性证明。

第一次官方wrapper在原生完成后失败：旧参考v3误要求物理child index大于parent；作者split合法共享较小编号right child，28实际DAG中12个复现误拒绝。新v4严格保留类型/范围/叶/无环/可达检查，独立只读源审查和有限正负fixture通过；独立Kahn与DFS在28914个小图一致，64个有限路径不变量statepairs通过。这些不冒充完整原生参考验收。

第二个官方任务R014-parent-path-retained-DAG-audit-W5-v1/attempt-8cce651c2bbf41aeb3b98a1bbd33023c只读重放旧轨迹，真实失败。它发现保留path-witness.txt只有13385728B，SHA3b4fcdfe0bcccfbccec5c8e420f379d57967700164a13339bc153cf04bbf2634；第101665行在G7883757内中断为 `N 788375`，缺少最终E标记，故严格拒绝。文件在两次审计输入绑定期间哈希相同。项目目录和R014 RAM staging只发现这一副本，没有发现完整alternate。

native.stderr虽有write_error0及完整source-observed汇总，源码也检查ferror/fflush/fclose；但无法据此确定缺失发生何时/为何，不能归因为同步、磁盘、原生exporter或远端corruption。不能拼写尾部、删掉最后组伪称完成或放宽complete检查。

原生汇总记录S1348465/P1920815（差-572350）、reusable258791/486108只是未通过完整独立轨迹绑定的观察线索。本报告不把它当经核验的负结果、park依据、CPU收益或科学cycle。两次失败回执、完整原始前缀、源/编译/.o/binary/日志、DAG修复/审查及新的不完整证据诊断均保留。成功专用analysisv2脚本未执行，不能引用其未生成的成功结果。

此前中断已证实一次ENOSPC，第二次exit120原因未知。此后同W5原队列恢复一次才有以上native；本次仅清理3639956472B重新hash匹配且远端已完整verified的idle压缩重复（包括可逐SHA识别的完整临时压缩副本），三份不符副本保留。部分清理与只读诊断native重叠，因此109.221530s不能与R012/R013作速度/观察器开销比。未删raw/unique/currentcontrol/SQLite/.o/其他项目/globalcache，没有停改平台同步。旧296fullbuild.o仍localdeferred；新3TU对象/binary需随本次恢复包明确归档，不预称全scratch。

下一问题改为原作者DAG中连续同变量/同right-child测试的普通membership融合是否有值得进一步检查的结构空间。它不依赖缺失的事件尾部或免费parentcache，不冒称新算法；先数学/quality/强简单对照/源身份和完整28H提取资格，再决定是否构建。R014完整机会结论保持incomplete，不重复原生。旧元数据HTTP授权取消缺口继续明示，未换通道重试。

本次补记：归档v3在任何SQL/ZIP/上传前又遇ENOSPC，并因不安全的同名copyfile使一个既有coordinator准备脚本暂时变0B。发现后保留错误与0B取证身份，原B副本哈希未变，39terminal/0reserve且无active输入执行时已恢复原3278B exactSHA；不能隐瞒为普通文件更新。仅再清理22份181300525B已完整verified且现SHA匹配的闲置R011压缩HTTP分片。本接续累计285files/3821256997B，旧queued轮2119696855B另计。v4生成完整本地437019796B包但包含未需归档的同步raw，未上传；v5缩小为metadata-only defer同步raw，完整原包保留，不称v4远端验收。v5工程archive33.674338s，与nativeCPU分开。

以下为历史接续，冲突以上述当前状态为准。

# R014 最新元数据回读未完成

恢复包体和四个runtime输入补充已独立HTTP核验。db1e7841891c2f6c25672ceee470c6846b38740f的15新metadata回读遇到network approval cancelled，尚无complete metadata-readback proof，不能称全部元数据验收。保留权限边界，不换通道绕过。此补记自身同样尚未独立HTTP回读。R014仍queued/noattempt，37terminal/0reserve/14cycle，没有编译/native结果。磁盘故障未解除，不盲重启。

# R014：已接纳，尚无原生结果

R014-parent-path-opportunity-diagnostic-W5-v1已由固定Simple13两公共接口实际gaps=[]后officialrespond接纳；任务queued、未分配attempt、无编译/native。37历史attempt全terminal/reservation0/cycle14不变，不能称新科研结果或cycle15。

问题为：固定hierarchy实际父路径坐标和实际值变化不相交时，能否节省足够子路径节点S支付一次冷父回退节点P，并计全部通知/new/old/dead、实际compute、父不可用分母。充分非必要条件、节点量不等于CPU收益。已有值缓存保留，原始unseq变换和返回IDs不变，额外见证在其后独立顺序执行、不供应求解IDs。

早期独立只读审查发现替代原遍历、unseq共享记录、参考failopen及计量范围问题，入场前版本化修复。源v3为限定源审查，最终referencev3/protocolv4由主协调者按实际有限red/green反例修正，不冒充独立原生验收。866inputs、数学/quality/trajectory、106真实反馈及全部版本/失败/审查保留。

首次官方run于07:56Z实际Errno28 ENOSPC，尚无R014attempt。成功删除57files/690698226B及8files/1428998629B重新逐SHA核对、远端完整verified的闲置压缩副本，均可从GitHub恢复，部分为最后本地压缩缓存。两旧warmup缓存分片变短/hash不符，清理v2在删除前拒绝，分片保留，原因未知。未删raw/unique/currentSQLite/.o/opaque raw/globalcache。

第二次owned8730实际exit120/空日志/无新healthidentity/无attempt或native，原因未定位。释放空间重新耗尽，同时观察到同步临时目录写入；不推断完整因果，不更改平台同步或删除临时控制数据。本次只在RAM中制作恢复包，无控制SQL编辑/覆盖，不称实验完成/全scratch/旧W4DB修复。

恢复先读manifest/proofs、freshactualstatus/health/stop。若仍37terminal0reserve、R014queued，只恢复同W5官方run，不重跑selector或R005–R013。若active/unknown先协调保留identity/reservation。短存储故障不终止长期目标，不保证进程常驻。


恢复入口 R014_OPPORTUNITY_LATEST/W5_SUCCESSOR_LATEST；新包已独立HTTP完整核验。以下旧R013科学结果/恢复切点仅作历史，R014不可据旧draft重新提交。

# 当前：R013强作者配置的真实成本诊断完成

固定Simple13/同source/CPU-only/thread1/单队列；一次新插桩诊断，非候选加速对比。1764次online创建块完整CPU12.139181209s，占此插桩native98.353001CPU s的12.34246%，不能单独解释主耗时。普通17154个确定性样本中ID段最大；其原始分段包括clock/allocation/observer，非无偏普查、原版固有占比、CI或跨阶段稳定性。真实work/plan/cost26/独立VAL与R012保留对照一致，内部200CPU停止未触发。

计量更正：原作者Linux Timer是PROCESS_CPUTIME_ID；R012两个author_internal_*_wall_seconds字段及wall文字错标，原字段/数值/日志保留并追加sourcebound correction，独立wait4CPU和真wall不变。

恢复入口R013_EVAL_COST_LATEST/W5_SUCCESSOR_LATEST，manifestfirst新37terminal/14cycle一致控制+父R01236链；新28parts/133members已独立immutableHTTP完整核验，2774旧aliases保持。六个新opaque SQL临时raw对象仅metadata并明确localdeferred，不称全scratch或根因修复。只删除1,427,524,786B已远端核验/hash不变/闲置压缩pack重复副本，可恢复；没有删除unique/current/raw/SQLite/.o/globalcache。

下一步读plans/R014_local_path_reuse_inquiry_draft_v2.md；源码已排除“纯目标修改总会拷贝状态值”解释，现有needs_to_convert检查已跳过该转换。选择真正IDallocation/hierarchy/parentavailability或更优质量路径，不盲造约2GBperstateIDcache、不为Do未触发exactU分支计时。R014仍draft，先latestaccepted/all106feedback/newuserstop/health，不能重跑R005–R013或重复recordcycle14。全部closestprimary/强baseline旧rawproperties/多public域/新颖性义务保留。

以下R012及更早切点只作历史，不覆盖当前37点/计量更正。

# 当前：R012作者强additive配置源边界与可行性完成

按固定Simple13推进。Zenodo实际源码746文件全部与现作者pin一致；实际归档additive脚本不是网页projectionensemble，未用变量不能当生效参数。最强总体Do无状态消歧，ordinary exact-U改动分支inactive，不展开无效patched计时网格。

原生h2后作者Do真正exit0：28组件/33061Cartesianstates/1000002实际transitions，cost26独立原PDDLVAL；直接CPU92.205939s/wall92.222327950s/nativeRSS717451264B。作者build/search内部wall3.147884/89.015953s只是日志口径；不同配方+h2不与R011混算速度。一次暴露任务可行性，不是论文全复现/组件图等价/新颖性或加速。

恢复入口R012_PRIMARY_LATEST.json/W5_SUCCESSOR_LATEST.json，manifest-first读新36terminal/13cycle一致控制及父34链。21parts/138newmembers/9derivedraw和直接副本已独立immutableHTTP完整核验；补充PDF为精确外部URL/hash恢复，不重分发全文。所有旧packs/stop/失败/账本保留；296full-build.o本地deferred，3隔离.o/0BHM已旧898归档。非全scratch或旧W4DB修复，无清理。

下一步读plans/R013_next_author_bottleneck_draft_v1.md、真实analysis、最新accepted review与69old+36W5=105完整反馈；一个writer，先actualstatus/health/inbox/alerts/newuserstop。R013未accepted/run；不要重跑R005–R012完成部分或重复recordcycle13。若选择state-heavy转移，先补const instance-safe每component任务/operators/cost/domain/goal/graph和quality；若目标inactive/成本无价值，选择真实搜索/启发式瓶颈或可证伪不同机制，不任意网格/无限升配。源35digest/CPU-only单线程/唯一队列/kernel-only总内存和用户授权不变。

旧34点以下记录仅历史，不覆盖此36点当前状态。

# R011：原始 BW p06 的资格与完整原生 CPU 检验

固定 Simple13/源版本、CPU-only/thread1、单队列，延续同一项目。原始p06是先按相邻公开序号选定，再取得PDDL/SAS；不是按运行时间换有利例。SAS SHA337284c808bc03350bba2be4ae250f04cd116d310384def6ab5034b4d869afac，configSHA37b4a1b530999e66bc10a29e760a25d0169762c06e918c0808f922e2021b36f5。

## 两臂资格

原版和普通最小变化坐标强简单对照均真正nativeexit0。实际10000状态（cap10000）、成本26、expanded20544/evaluated52981。最终有序图/重数/domain/独立64位最短路、计划和独立原PDDL VAL完全一致。图SHA0c00f31767ceee52ae2870f2c52ef4d30faa47dc7091b10465bf7fe868433e32，计划SHAff6dfac7b253381ef59ac1e7c3357db828b780e4a3467b86109142da2539804c。没有把p05成本24或work/hash抄作p06答案。只最终快照，不是p06每split/具体动作oracle/转换正确性或最优性证明，资格export计时不可用于性能。

## 前瞻完整原生 CPU

使用同一R010真正移除额外observer/profiler的两个timingbinary，不重编、不改ABI。一个officialtask内部串行10个唯一nativeID：2预热排除评分，4配对AB/BA/BA/AB。原生120CPU/2500M_AS/145wall/2.8GBgroupRSS/thread1/affinity0不变，总内存仅kernel执行。所有10项exit0、同实际p06work/plan、独立VAL；失败0/未执行0，没有挑选有利重跑。

|配对|原版CPU(us)|对照CPU(us)|对照/原版CPU|对照/原版wall|UTC启动间隔(s，诊断)|
|---|---:|---:|---:|---:|---:|
|p1|966303|857327|0.887223780|0.886989726|1.361|
|p2|814017|827052|1.016013179|1.018751128|1.240|
|p3|812813|773887|0.952109526|0.951435732|1.136|
|p4|906672|829357|0.914726605|0.914443783|1.341|

CPU比几何平均0.941299187713，范围[0.8872237797047096, 1.0160131790859406]；wall比几何平均0.941631092407。主指标是直接native子进程wait4 user+system，包含exec/init/construction/search/exit，排除parent/hash/VAL；wall含Popen/marker。全部10项childCPU8506250us、最大nativeRSS30081024B，不是全项目CPU或共享cache。串行block去掉了逐行官方决策造成的长间隔，仍含每行二进制hash/解析/VAL；UTC启动间隔不是等待或谓词成本分解。评分期间本方没有重型归档/上传/远端核验，但共享宿主频率/cache/contention仍未控制。

这只是新增一个同域原始任务，10次执行不是10独立cases，不构造CI、不声明稳定/整体加速、新颖性或单谓词收益。普通最小U是强简单对照，不是新算法；主作者combined/additive强配置、closest-primary和更广公开条件义务仍保留。原p05结果单列，不合并挑有利效应。

## 工程分母和账本

两次selector预检查拒绝均在native前：初版不支持equivalence类型，v2虽改formal却返回旧v1引用。v3修正引用后两接口真正gaps=[]，保留旧文档/拒绝/回归旧red新green。不是CPU或内存失败。3项规则测试和引用测试是软件fixture，不是nativecase或科研周期。无旧实验重跑、unique/control/SQLite/.o删除或globalcache清理。原历史/失败/保守结算/modelunknown保留。

已各record一次真实p06源资格和完整native周期。窗口/总账以CURRENT和官方真实状态为准，commandaccounting不是精确CPU/科研周期。新归档为明确增量overlay和一致控制切点，旧R01031base+两编码repair映射仍保留；296全编译.o本地deferred，不称全scratch或旧W4坏库修复。下一步是核对作者强combined/additive原配置并前瞻选择可证伪比较，不无限重复p05/p06或Depots升配。

