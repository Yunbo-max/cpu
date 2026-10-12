# 低秩、Coreset 与流式统计：完整科研历史

固定工作流：Research Autopilot Simple 0.3.0-simple.9；源摘要 `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`。CPU 单线程串行，项目内存上限 8,000,000,000 字节，数值进程地址空间上限 4 GiB。长期授权继续有效，归档边界不是科研结束。

可直接阅读 [当前检查点](current/CHECKPOINT.json)、[研究历史与恢复说明](current/START_HERE.md)、[累计窗口账本](current/execution_windows/ledger.json)。当前最新研究结论与下一步以这些文件和已保存 runner inbox 为准。保留全部正负结果、失败记录、原始结果、代码、固定运行器和收据。没有已确认的新算法。

`LATEST.json` 指向一个 SHA-256 校验的快照清单；`objects/` 按内容哈希保存文件，超过8MiB的单个对象放入 `chunked/` 的4MiB分块，`snapshots/` 保留每次完整文件映射。相同文件不重复上传，不删除旧快照对象。对象的原始路径（包括运行账本和嵌套作者仓库历史）均在清单内，恢复后字节不变。可重新获取的依赖、原始 Parquet 和未授予再分发许可的临时材料仍按原项目规则排除，精确来源和哈希保留。

## 恢复—运行—保存—清理

1. 读取远端最新 main 和本目录 LATEST；若本地已有工作，先比较检查点时间、sequence、证据哈希，禁止覆盖更新现场。
2. 在独立临时 checkout 中只恢复本项目。可使用 `git clone --depth 1 --filter=blob:none --sparse https://github.com/Yunbo-max/cpu.git checkout` 后，在 checkout 中执行 `git sparse-checkout set projects/lowrank-coreset-streaming-simple-20261011`。克隆记录实际 commit。
3. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py restore /absolute/path/lowrank_coreset_streaming_rsi_simple`。目标必须不存在；脚本校验每个对象及恢复后的每个文件。随后阅读 START_HERE 和固定 runtime 技能，重新检查资源/身份/收据。归档停止的 w001–w006 全部保留，下一可用窗口从 w007 接续，不修改旧预算。
4. 数值任务通过固定 runner 和 cpu_guard；代码和真实结果先在工作目录保存。结束前调和所有任务/收据，监督器退出或处于已证实安静边界，运行项目 `scripts/build_checkpoint.py`。
5. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py pack /absolute/path/LowRank_Coreset_Streaming_Simple_Checkpoint.zip`；它验证 ZIP 成员，新增变更对象与完整快照。更新本项目摘要。
6. 基于最新 main 提交本项目目录，普通非强推。冲突时重新获取最新 main 并只调和本项目变化，不覆盖其他项目。不得 force/reset 远端。失败时保留唯一现场。
7. 从远端精确新提交获取并运行 verify，实际恢复后核验所有成员；确认 main 包含该提交。写下 Git commit、快照哈希、恢复收据，然后才清理本项目已归档的工作副本、下载包和临时 checkout。只留小型本地定位文件。禁止删除其他项目或杀未知进程。

每次只按需恢复可再生成数据/依赖；禁止把下载、归档、资源检查记作 research_cycle。文件清理可降低磁盘和部分文件缓存占用，但不等于释放其他项目的进程内存。不要承诺两次唤醒之间 CPU 常驻运行。

## 本次新结果

w006 已完成原生 CTT/RFF 归一化和强简单基线成本诊断，累计28个研究周期。47行归一化检验中，平衡组仅相差公共正尺度；不等组的原生有符号和与标准MMD不同。固定6点、15种2对4分配出现31/105对严格排序反转；这不是平衡组论文结果或总体误报率的反证。

36行成本测量加6次预热：本次设置中 CTT 置换有符号和算术仅占0.21%–2.10%，单独优化这一部分无法达到20%提速目标。作者 CheapRFF 已直接按bin聚合；4096点/组时约为普通RFF的3.39倍速度。本轮不宣称功效优势或新算法。最大数值进程 RSS 672,350,208 字节；保留一次缺少clang的构建失败及GCC重建记录。计时是原生统计辅助函数加轻量结果处理，未包含完整发布测试入口的jitter/全局随机决策流程。

下一步：审查并预注册 Nyström 原生投影MMD、近重合landmark下伪逆处理、随机性与决策语义，再决定与CheapRFF的质量匹配实验。已知论文已有流式聚合，不作为创新。所有代码、逐行结果、分析、失败与收据在最新快照内；详细状态见 current/CHECKPOINT.json。
