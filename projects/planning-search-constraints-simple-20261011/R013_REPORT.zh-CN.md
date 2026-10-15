# R013：强作者配置的启发式评估成本诊断

固定Simple13/原作者source/thread1/单队列；新一次插桩诊断，不重跑旧R012原生ID，不是方法加速对比。

先更正旧记录单位：固定Linux源utils::Timer使用CLOCK_PROCESS_CPUTIME_ID；R012两个author_internal_*_wall_seconds字段及报告的wall称呼不正确，原字段/数值保留，追加更正。独立wait4 CPU和真实wall不受影响。

## 实际测得

同真实h2-p06/作者additiveDo，nativeCPU 98.353001s、wall 99.222480s、nativeRSS 717410304B。全部1764次online创建块实际合计CPU 12.139181s，占这个插桩native总CPU 12.342%。该边界包括greedy order、残余cost复制、SCP计算、新h计算/条件存储及块内临时对象销毁；不称单谓词或原版无插桩固有占比。

普通调用总数17637803，确定性hash选中的普通样本17154；四段原始CPU ns为[15953454, 24358206, 7857590, 7914743]，样本提前返回计数[0, 0, 17154]，各段达到分母[17154, 17154, 17154, 17154]。四段和精确等于样本query总CPU56083993ns；样本内online尾段重叠完整online计时，不能相加。只有样本均值及明确条件外推，没有随机抽样无偏/CI/跨阶段稳定性/精确全搜索分解。

真实work为{'cartesian_abstractions': 28, 'cartesian_states': 33061, 'cartesian_transitions': 1000002, 'expanded': 9830440, 'evaluated': 17639567, 'cost': 26, 'plan_length': 26}，planSHA3e216bbefad0615165dff294a3b50d69a916b5bb29862c4612a586a80403993f，和保留R012粗粒度work/plan一致，独立原PDDL VAL有效，未触发200CPU内部改善停止。粗粒度相等不等于逐次h轨迹证明；原author默认cache已有，compute调用不是所有evaluator请求。

## 决策与范围

Online creation does not alone dominate this native; interpret ordinary phase sample cautiously and select focused broader-search or ID/max measurement, not an unsupported exact residual。保留所有采样/observer/sharedhost限制，不从插桩运行对R012作速度比，也不把build/link/软件fixture算新科学周期。一次真实成本诊断已publicrecord；其他public域/真正新方法/closestprimary/作者baseline旧rawproperties仍欠。独立源审查在派发前发现缺少样本提前返回分母，v2先补齐再入场，v1未执行且保留。当前单TU不改header/layout/旧binary或.o，所有复用对象/flags已鲜hash。
