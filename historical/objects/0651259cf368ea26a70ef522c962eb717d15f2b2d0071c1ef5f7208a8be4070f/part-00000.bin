# B15：原生 Landmark-512 warm-LOBPCG 强比较器审计

## 结论

B15 得到可复核的负结果：冻结的“上一端点零扩展 + SciPy LOBPCG”比较器不能在原生 Landmark-512 的严格端点精度要求下替代 exact SVD。

在 `eta=0.1` 的完整策略回放中，B09 V2 共有 205 次增长后精确查询和 100 次刷新。前 `t<125` 按合同使用 exact SVD；其后 71/71 个刷新点的 LOBPCG 活动残差块都不能达到 `1e-8` 残差门槛，全部触发 exact-SVD fallback。因此没有任何后期 LOBPCG 端点被实际接受，冻结 falsifier 已成立，未继续消耗预算跑 `eta=0.01` 和其余重复。

首个后期刷新 `t=126` 的独立检查表明：初始 25 维块本身满秩且正交误差约 `5.35e-15`，但在仅新增两行后，活动残差块数值秩只有 2；安装版 SciPy 的 Cholesky 正交化因此在 iteration 0 退出。加入种子固定、幅度 `1e-4` 的扰动并把残差门槛放宽至 `1e-4` 后虽能结束，但端点目标 excess 达到原冻结容差的 `412.2206` 倍。这只否定这一项扰动修复，不是一般 LOBPCG 不可能性结论。

## 公平性和审计

两臂共享输入、cached-Gram 更新、exact-Gram OPT 查询、gate 算术、rank、eta 和单线程环境，仅端点刷新例程不同。exact-SVD 与 warm-with-fallback 两臂相对 B09 V2 的 query、update、incoming loss、queried OPT 均逐元素一致，实际 fallback 后端点容差违例为零。

单次进程 CPU 为 exact `6.9278s`、warm-with-fallback `6.8916s`，比值 `1.00525`。这约 0.5% 的差异不能解释为 LOBPCG 加速：全部后期尝试都失败后又执行了 exact SVD，而且只有一对依赖开发进程。该数值仅作为诊断计时保留。

独立复核先判 `REVISE`：原合同把上游源码定位器误写为实际执行身份、未绑定 B09 参考哈希、退役措辞过宽。版本化修订补充了实际 SciPy `1.17.0`、git revision `8c75ae7...`、加载源码 SHA-256 `2789d5...`，绑定已消费的 eta=0.1 参考 SHA-256 `b7ab2139...`，并把结论收窄为 `RETIRE_FROZEN_ZERO_EXTENDED_SCIPY_LOBPCG_COMPARATOR`。独立修订闭合为 `PASS`，未重跑或修改原结果。

## 资源与范围

候选侧 10 个有界命令，独立初审 11 个命令、闭合复核 4 个命令；已知仪器化 wall 下界 `15.8454s`，可测进程 CPU 下界 `14.5854s`，峰值 RSS `131368 KiB`。两个候选诊断命令及多数源码检查未完整计时，因此总量明确是下界。所有科学进程已结束，reservation 为零。

该结果只支持拒绝冻结的零扩展 SciPy LOBPCG 比较器。它不是新方法、未见确认、一般 warm/rank-adaptive LOBPCG 不可能性、native5000 结果、recourse 改进、原创性或论文 PASS。

## 下一步

机器第7步选择继续第2/4步：冻结已有 randomized block-Krylov 端点比较器，明确源码身份、随机种子、迭代与 matvec 预算，并沿用 exact endpoint objective 和整条策略轨迹审计。先做 bounded native512 校准，通过后才决定是否进入 native5000。
