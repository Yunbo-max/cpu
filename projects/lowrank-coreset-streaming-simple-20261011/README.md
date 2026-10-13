# 低秩、Coreset 与流式统计：完整科研历史

固定工作流：Research Autopilot Simple 0.3.0-simple.9；源摘要 `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`。CPU 单线程串行，项目内存上限 8,000,000,000 字节，数值进程地址空间上限 4 GiB。长期授权继续有效，归档边界不是科研结束。

可直接阅读 [当前检查点](current/CHECKPOINT.json)、[研究历史与恢复说明](current/START_HERE.md)、[累计窗口账本](current/execution_windows/ledger.json)。当前最新研究结论与下一步以这些文件和已保存 runner inbox 为准。保留全部正负结果、失败记录、原始结果、代码、固定运行器和收据。没有已确认的新算法。

`LATEST.json` 指向一个 SHA-256 校验的快照清单；`objects/` 按内容哈希保存文件，新写入且超过512KiB的单个对象放入 `chunked/` 的256KiB分块，旧快照的4MiB分块仍可原样读取，`snapshots/` 保留每次完整文件映射。相同文件不重复上传，不删除旧快照对象。对象的原始路径（包括运行账本和嵌套作者仓库历史）均在清单内，恢复后字节不变。可重新获取的依赖、原始 Parquet 和未授予再分发许可的临时材料仍按原项目规则排除，精确来源和哈希保留。

## 恢复—运行—保存—清理

1. 读取远端最新 main 和本目录 LATEST；若本地已有工作，先比较检查点时间、sequence、证据哈希，禁止覆盖更新现场。
2. 在独立临时 checkout 中只恢复本项目。可使用 `git clone --depth 1 --filter=blob:none --sparse https://github.com/Yunbo-max/cpu.git checkout` 后，在 checkout 中执行 `git sparse-checkout set projects/lowrank-coreset-streaming-simple-20261011`。克隆记录实际 commit。
3. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py restore /absolute/path/lowrank_coreset_streaming_rsi_simple`。目标必须不存在；脚本校验每个对象及恢复后的每个文件。随后阅读 START_HERE 和固定 runtime 技能，重新检查资源/身份/收据。归档停止的 w001–w008 全部保留，下一可用窗口从 w009 接续，不修改旧预算。
4. 数值任务通过固定 runner 和 cpu_guard；代码和真实结果先在工作目录保存。结束前调和所有任务/收据，监督器退出或处于已证实安静边界，运行项目 `scripts/build_checkpoint.py`。
5. 执行 `python3 projects/lowrank-coreset-streaming-simple-20261011/archive_store.py pack /absolute/path/LowRank_Coreset_Streaming_Simple_Checkpoint.zip`；它验证 ZIP 成员，新增变更对象与完整快照。更新本项目摘要。
6. 基于最新 main 提交本项目目录，普通非强推。冲突时重新获取最新 main 并只调和本项目变化，不覆盖其他项目。不得 force/reset 远端。失败时保留唯一现场。
7. 从远端精确新提交获取并运行 verify，实际恢复后核验所有成员；确认 main 包含该提交。写下 Git commit、快照哈希、恢复收据，然后才清理本项目已归档的工作副本、下载包和临时 checkout。只留小型本地定位文件。禁止删除其他项目或杀未知进程。

每次只按需恢复可再生成数据/依赖；禁止把下载、归档、资源检查记作 research_cycle。文件清理可降低磁盘和部分文件缓存占用，但不等于释放其他项目的进程内存。不要承诺两次唤醒之间 CPU 常驻运行。

## 本次新结果

w010 已完成论文尺度的 Nyström/RFF 决策比较及状态口径审查，累计36个研究周期。坐标匹配 RFF 相对发布轴双宽 RFF 的三个配对分歧率差区间均包含0；Nyström只保留局部精度信号，而合法协议会产生不同的“等内存”匹配宽度。因此该比较家族已经关闭，不再从中选择有利口径继续扫参。

w011 转向内生固定状态的 Frequent Directions 合并拓扑。来源与数学审查确认任意合并顺序已有相同形式的空间/误差保证，但文献保证不要求不同合并树得到完全相同的实际 sketch、累计丢弃质量、投影误差或时间。已冻结一个512行 Landmark 原生比较：8个固定连续叶块、目标秩25、`ell=32,48,64`，比较平衡树、左深树、中央逐行 FD 与精确 SVD；生产与独立审计脚本均已保存。

该数值实验在两个不同唤醒中均未运行。第二次真实复查的共享 cgroup 余量由345,829,376字节降至224,468,992字节，低于预注册的1 GiB启动门槛；文件页仍占主要部分，但既未假定可立即回收，也未当成永久不可用。没有 OOM、任务尝试或新增研究周期。

结果出现前的静态审查发现原审计器会信任生产脚本的方法标签，因而不能独立发现合并树构造或标签错配。已前瞻冻结审计修订，并改为不导入生产脚本、独立重建中央逐行、平衡树和左深树三条路径，同时核对协方差算子、累计丢弃量与 shrink 次数；科学假设和否证标准未改变。等待状态、审计修订和恢复条件均在最新快照中。后续实际唤醒只有在余量恢复且排除重复/未知尝试后才通过4 GiB保护器串行启动。详细状态与证据见 `current/CHECKPOINT.json`、`current/START_HERE.md` 和最新快照。
