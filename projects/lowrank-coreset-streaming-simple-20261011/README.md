# 当前采用策略：Simple 0.3.0-simple.13

2026-10-13：按用户明确要求，本条 **Simple** 研究线的后续科研决策采用 `rsi-simple` 分支 **`0.3.0-simple.13`**，固定来源为 `Yunbo-max/Research_Autopilot@f397d3f93893e66d57e4ca5566cd414782e5b71b`。当前会话已实际读取安装版 `.13` 入口及策略迁移、source-adoption 指南。

**恢复入口先读 [CURRENT_POLICY.json](CURRENT_POLICY.json)，再读 `LATEST.json` 和历史检查点。** 该记录区分科学策略、执行器与调度状态：`.13` 已被选为后续策略；旧执行器的 `adopt-source` 尚未执行，恢复真实运行状态并核实安静边界后，必须完成并核验 `.13` 源采用，才能派发新任务。不能仅改版本字符串或把 Git commit 当成运行器 source digest。

**研究仍按用户要求暂停；这次版本采用没有启动实验、创建 w015 或修改定时任务。** 旧窗口、结果、冻结协议、原始 `.9` 源码摘要和累计账本保持原样；不改其他 Chat 参与者。本次是策略采用记录，不是新的科研周期，也不是运行器迁移成功回执。

以下完整保留原始 w014 归档说明；其中 `.9`、持续授权和恢复步骤属于历史记录。后续策略选择以 `CURRENT_POLICY.json` 为准，明确的用户停止指令始终优先。

---

# 低秩、Coreset 与流式统计：完整科研历史

> **2026-10-13：用户要求更新 GitHub 后停止。对应续研定时任务已停用，w014 已退出，无需自动创建 w015。以下持续授权和恢复步骤仅为历史记录；恢复本任务需要用户新的明确授权。**

固定工作流：Research Autopilot Simple 0.3.0-simple.9；源摘要 `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`。CPU 单线程串行，项目内存上限 8,000,000,000 字节，数值进程地址空间上限 4 GiB。长期授权继续有效，归档边界不是科研结束。

可直接阅读 [当前检查点](current/CHECKPOINT.json)、[研究历史与恢复说明](current/START_HERE.md)、[累计窗口账本](current/execution_windows/ledger.json)。当前最新研究结论与下一步以这些文件和已保存 runner inbox 为准。保留全部正负结果、失败记录、原始结果、代码、固定运行器和收据。没有已确认的新算法。

`LATEST.json` 指向一个 SHA-256 校验的快照清单；`objects/` 按内容哈希保存文件，新写入且超过512KiB的单个对象放入 `chunked/` 的256KiB分块，旧快照的4MiB分块仍可原样读取，`snapshots/` 保留每次完整文件映射。相同文件不重复上传，不删除旧快照对象。对象的原始路径（包括运行账本和嵌套作者仓库历史）均在清单内，恢复后字节不变。可重新获取的依赖、原始 Parquet 和未授予再分发许可的临时材料仍按原项目规则排除，精确来源和哈希保留。

## 恢复—运行—保存—清理

1. 读取远端最新 main 和本目录 LATEST；若本地已有工作，先比较检查点时间、sequence、证据哈希，禁止覆盖更新现场。
2. 在独立临时 checkout 中只恢复本项目。可使用 `git clone --depth 1 --filter=blob:none --sparse https://github.com/Yunbo-max/cpu.git checkout` 后，在 checkout 中执行 `git sparse-checkout set projects/lowrank-coreset-streaming-simple-20261011`。克隆记录实际 commit。
3. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py restore /absolute/path/lowrank_coreset_streaming_rsi_simple`。目标必须不存在；脚本校验每个对象及恢复后的每个文件。随后阅读 START_HERE 和固定 runtime 技能，重新检查资源/身份/收据。全部旧窗口和失败记录均须保留；下一编号窗口以最新 CHECKPOINT 和 ledger 为准，不修改旧预算。
4. 数值任务通过固定 runner 和 cpu_guard；代码和真实结果先在工作目录保存。结束前调和所有任务/收据，监督器退出或处于已证实安静边界，运行项目 `scripts/build_checkpoint.py`。
5. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py pack /absolute/path/LowRank_Coreset_Streaming_Simple_Checkpoint.zip`；它验证 ZIP 成员，新增变更对象与完整快照。更新本项目摘要。
6. 基于最新 main 提交本项目目录，普通非强推。冲突时重新获取最新 main 并只调和本项目变化，不覆盖其他项目。不得 force/reset 远端。失败时保留唯一现场。
7. 从远端精确新提交获取并运行 verify，实际恢复后核验所有成员；确认 main 包含该提交。写下 Git commit、快照哈希、恢复收据，然后才清理本项目已归档的工作副本、下载包和临时 checkout。只留小型本地定位文件。禁止删除其他项目或杀未知进程。

每次只按需恢复可再生成数据/依赖；禁止把下载、归档、资源检查记作 research_cycle。文件清理可降低磁盘和部分文件缓存占用，但不等于释放其他项目的进程内存。不要承诺两次唤醒之间 CPU 常驻运行。

## 本次新结果

w014 冻结并检验了大偏移量下的流式方差与协方差稳定性。标量构造中，原始未中心化公式在偏移指数21首次失败；Welford 对交替顺序到指数53才失败、对分块顺序在指数11即失败，显示明显次序敏感性。平衡 Chan 合并与首值平移在所有仍可表示的输入（至指数53）保持精确；指数54时输入本身已浮点塌缩，所有方法都返回零。

八维、4096行的完全平衡 Rademacher 协方差构造中，原始和/Gram公式在指数23首次失败，Welford 在自然/Gray顺序分别于指数15/14首次失败；普通中心化两遍法在指数46首次失败，而平衡 Chan 与首行平移至指数53仍精确恢复 `1024 I`。指数53时，两遍法的对角和非对角最大误差均为1024，原始自然顺序结果出现约 `-2.33e20` 的最小特征值。冻结审计独立重算550行结果并确认这些边界，同时否定了预注册的“原始法至迟指数21失败、两遍法指数53才失败”两个精确阈值预测；该审计以科学预测不符而非实现异常退出。

w014 共5次尝试、2个研究周期，命令时间6.283977039秒，峰值28,464 KiB，无内存等待或OOM；当前累计40个研究周期。这些结果只证明冻结合成构造上的有限精度边界与次序效应，不是新算法、分布无关保证或原创性结论。w014已在可归档边界停止，长期授权继续。下一窗口从w015接续，先检查真实特征尺度/条件数能否形成新的可证伪问题；若没有，不再扩大同一偏移指数网格。详细状态与证据见 `current/CHECKPOINT.json`、`current/START_HERE.md` 和最新快照。
