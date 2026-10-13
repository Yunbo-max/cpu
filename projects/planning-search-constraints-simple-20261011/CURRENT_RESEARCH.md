# 当前研究状态

同一Simple13持续CPU项目；W3真实停止/取消保留，W4为已授权后继，目标未结束。

原R006第一fine-clock1000屏幕：applicability3.2132%、conditional equal-call saved2.1696%<1/11，仅此已暴露fine-clock条件不优先普通适用性缓存；最初final1000多重图/orderedadjacency/独立shortestpaths一致，cost24 VAL通过，不是每split证明。

已新增实际12次coarse/counts/fine native对照，3warmups+9scored/1条件，全部cost24且独立VAL、计数/expanded161440/evaluated336855/plan相同。Fine/counts0.815–1.040出现方向反转，counts/coarse1.060–1.355；共同宿主wall噪声和memory-wait gap使计时/谓词成本仍未分清。完整guard拒绝和编译失败保留。

接着实际完成CPU观测source-boundary/API审计，并成功构建两份只增加2threadCPU boundary reads的coarse/fine_counts二进制。还未native资格，下一任务R006-cpu-clock-counts-qualification-v1完整源码和accepted decision已准备；先fresh资源/实际状态，再同W4派发，随后fine/coarse资格和新的CPU/wall设计。不得因本批结束关闭持续研究，也不重跑已完成旧native对照。细节和所有限制见R006_REPORT.zh-CN.md、CURRENT_EXECUTION.json、RESUME.md、LATEST及manifest。

## 最新接续 2026-10-13T20:41:07.019482+00:00

CPU资格v1/v2/v3均在prelaunch资源保护拒绝，solver没有启动，未产生nativeCPU字段、图或VAL新结果。v3实际guard前共享charge7481118720B，750MB案例余量不能满足。此前非常驻supervisor启动后计账增长524488704B，因此恢复条件已版本化：无live supervisor时current<=6.1e9；有真实核验resident supervisor时<=6.6e9，并鲜测CPU/anon/file/cache/events/其他或未知活动。仍保持shared abort7.8e9/project8e9及全部native限制。快照不是全局资源预留。新R006-cpu-clock-counts-qualification-after-memory-v4已准备但未提交，先消费所有最新probes/newprevious_ref才派发；不重复已失败ID，不以空队列/局部失败结束持续目标。

W4实际37attempts/769.783455120014结算秒/reservation0；项目累计下界251/15217.320935790012。保守1823秒、losthostreported19次/1042.6368527140294秒和旧W3真实stop/cancel保留；不是精确CPU或科研周期。所有native任务terminal，旧supervisor身份当前不存活，session不可连接但不伪造exit130。已有12次旧native对照不重跑。完整7104归档已独立回读31parts、全部3731新members/817741509B和4直接rawcopy；最新37状态与三个拒绝作为独立操作补充提交，旧LATEST保留，完整37全窗口overlay待归档余量满足。
