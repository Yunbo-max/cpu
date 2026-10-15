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
