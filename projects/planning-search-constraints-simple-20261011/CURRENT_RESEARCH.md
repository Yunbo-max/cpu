# R007：长构建窗口的真实 CPU / wall 对照

同一公开 Blocksworld p05 开发条件，仅将 max_states1000 调至作者支持的10000，其他源、SAS、搜索/种子/线程和原生资源条件不变。Pilot 和三个资格模式实际达到10000；coarse 独立审计，counts/fine 实际对比coarse；finalgraph SHA7c141bddef4d6f14ba5449c5922e43263ccb2a2111aab36217a3890fff841c12 完全一致。计划成本24、独立VAL通过；finalgraph见证不证明中间每split。

冻结12次全部执行：3warmups+9评分、三种顺序、一个暴露公开问题，不能称12独立样本或周期。全部cost24/VAL、9999closed rewires、common/fullfinecounts/expanded18657/evaluated43157/plan hash一致，整数CPU/wall和阶段加和检查通过。

| 评分rotation | CPU fine/counts | CPU counts/coarse |
| --- | ---: | ---: |
| 1 | 1.146037803 | 1.209067277 |
| 2 | 0.907236651 | 1.318456063 |
| 3 | 1.087403551 | 0.970587866 |

方向仍反转。更长窗口并未在这个非独占宿主上建立稳定的clock开销或intrinsic谓词成本；不能把CPU聚合差值减到单个wall谓词计时，不能宣称算法加速/新颖性。12次guard childCPU合15.871629s、wall16.31205761s，含包装器和原生求解，排除输入hash/preflight、翻译、VAL和归档；不是全项目CPU总账。

保留连接丢失和真实磁盘满：前六项成功不重跑，第七项decision写入OSError28，solver未启动；完成远端raw42prefix核验后只删同hash闲置临时SQLite副本，source13/currentcanonicalSQLite/unique科学结果未删。剩余六项从原inventory接续，native代码/参数没改；coordinator stdout改为完整zstd保存。间隔/宿主变化限制因果归因。原analysis-v1模板遗漏gap限定，独立v1r1补正，原数值和原文件保留。

探索性回看同case的coarse：1000→10000 搜索expanded减少88.4434%、evaluated减少87.1883%，但guard childCPU median0.700917→1.245861s。两组不是同时间独占配对，不能作为严格速度比较；它提示搜索节点下降不是整个求解阶段效率的充分代理。不能据此拿纯构建或节点统计代替完整native成本。

下一步已在最新v4决策中选择原Depots p05 nativeAS3000M/600CPU边界诊断：复用原v3r2二进制（不可变恢复后完整SHA验证）和R005/L1同SAS，states_ops/none两个预冻结串行配置；不重跑旧2500M结果，不重新翻译PDDL，明确native-SAS-only范围、全部删失/失败分母与独立VAL。此报告生成时两项尚未提交/没有native结果。每split见证、变换算子oracle、多公开条件完整native效率和新颖性仍欠；没有宣布整个持续研究完成。

后续执行：原 Depots states_ops600CPU/3000M 新SAS-only任务已实际运行；None对照尚未提交，现没有新终态结果。R007报告和上述12项结论保持。
