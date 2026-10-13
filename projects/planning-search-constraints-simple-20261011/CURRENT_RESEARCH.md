# 当前研究状态

同一Simple13持续CPU项目；W3真实停止/取消保留，W4为已授权后继，目标未结束。

原R006第一fine-clock1000屏幕：applicability3.2132%、conditional equal-call saved2.1696%<1/11，仅此已暴露fine-clock条件不优先普通适用性缓存；最初final1000多重图/orderedadjacency/独立shortestpaths一致，cost24 VAL通过，不是每split证明。

已新增实际12次coarse/counts/fine native对照，3warmups+9scored/1条件，全部cost24且独立VAL、计数/expanded161440/evaluated336855/plan相同。Fine/counts0.815–1.040出现方向反转，counts/coarse1.060–1.355；共同宿主wall噪声和memory-wait gap使计时/谓词成本仍未分清。完整guard拒绝和编译失败保留。

接着实际完成CPU观测source-boundary/API审计，并成功构建两份只增加2threadCPU boundary reads的coarse/fine_counts二进制。还未native资格，下一任务R006-cpu-clock-counts-qualification-v1完整源码和accepted decision已准备；先fresh资源/实际状态，再同W4派发，随后fine/coarse资格和新的CPU/wall设计。不得因本批结束关闭持续研究，也不重跑已完成旧native对照。细节和所有限制见R006_REPORT.zh-CN.md、CURRENT_EXECUTION.json、RESUME.md、LATEST及manifest。

## 最新接续 2026-10-13T20:41:07.019482+00:00

CPU资格v1/v2/v3均在prelaunch资源保护拒绝，solver没有启动，未产生nativeCPU字段、图或VAL新结果。v3实际guard前共享charge7481118720B，750MB案例余量不能满足。此前非常驻supervisor启动后计账增长524488704B，因此恢复条件已版本化：无live supervisor时current<=6.1e9；有真实核验resident supervisor时<=6.6e9，并鲜测CPU/anon/file/cache/events/其他或未知活动。仍保持shared abort7.8e9/project8e9及全部native限制。快照不是全局资源预留。新R006-cpu-clock-counts-qualification-after-memory-v4已准备但未提交，先消费所有最新probes/newprevious_ref才派发；不重复已失败ID，不以空队列/局部失败结束持续目标。

W4实际37attempts/769.783455120014结算秒/reservation0；项目累计下界251/15217.320935790012。保守1823秒、losthostreported19次/1042.6368527140294秒和旧W3真实stop/cancel保留；不是精确CPU或科研周期。所有native任务terminal，旧supervisor身份当前不存活，session不可连接但不伪造exit130。已有12次旧native对照不重跑。完整7104归档已独立回读31parts、全部3731新members/817741509B和4直接rawcopy；最新37状态与三个拒绝作为独立操作补充提交，旧LATEST保留，完整37全窗口overlay待归档余量满足。

## 最新真实接续 2026-10-13T22:03:07.185548+00:00

用户22:44BST明确取消人为8GB总量/7.8GB shared保护及任何启动余量等待，仅真实失败后才诊断、等待或修复。此新授权覆盖旧6.1/6.6GB和750MB门槛；历史限额/三次拒绝结果保持不改。实际host memory.max8589934592B(8GiB约8.59GB)由内核执行，CPU配额8核。版本化host-only wrapper禁用prelaunch与shared人为abort，记录actualhost/events，不清全局cache/杀他者/买资源。原native比较120CPU/2500MAS、145wall/2.8GBprocessRSS/3.5GBAS、thread1/affinity0仍冻结。

三种新C++CPU观测mode均实际qualified：final1000 TSV SHA6d8625...完全一致、cost24各自独立VAL、CPUinteger/ns/phase/pairedwall/boundary2reads有效。counts guard前8.194GB/peak8.197GB、groupRSS29.36MB，exit0，无OOM/kill。原先人工门槛过度阻塞了这个实际可行的小任务；不能由此无限扩大native内存或称其它失败都来自保护。

新12CPUwall对照(3warmup+9score/同一暴露publiccase)全部成功cost24独立VAL/commoncounts/fine-countsfullcounts/expanded161440/evaluated336855/planhash exact，graphexportOFF。CPU fine/counts比值1.099502/0.904726/1.275065，counts/coarse1.516484/1.153790/0.947320仍反转，wall与CPU基本共同波动；单纯wall等待不是充分解释，CPUfrequency/cache/短阶段variance和instrumentation未分清，无intrinsicindividualpredicate成本、算法速度或novelty结论。guardchildCPUsum9.564565s/wallsum10.005935s只是本12wrapper/fullsolve，排除preflight与独立VAL，非全项目成本。

首项overhead提交曾因重复evidence引用被官方原子拒绝，native未启动，旧v6proposal/response/source保留；v7去重相同path/hash、新decision/response接纳后首项native只执行一次，12冻结order/IDs/条件未改。细节evidence/R006-cpu-overhead-submission-rejection-v1.json。

下一actualaccepted R007仅一个counts nativepilot、max_states10000(沿用作者固定大小设计允许早concrete solution)、同SAS/search/policy/seed/binary/nativecaps，graphexportOFF；不是独立病例或新算法，也不能用原1000资格替代新frontier图资格。记录实际frontier/CPUwall/早解/失败，判断是否值得更长matchedwindow。计划已准备，归档回读后再submit，不重复R005/R005L1或两批旧R006开销/已完成资格。W4实际52attempts/801.2934207180151结算秒/reservation0；项目lowerfloor266/15248.830901388013，scoped研究周期3；旧1823保守秒/lost19reported/W3true stop取消完整保留，不是精确CPU，模型unknown，长期目标未停止。
