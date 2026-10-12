# B13：冻结幂迭代模型后的几何—工作量边界

## 本轮结论

B12 说明在不限制实现时，`(Delta,D,k,r)` 不能决定 CPU 成本。本轮把问题
收紧到一个完全明确的模型：只保留上一步单位向量 `q`，一次 `Gq` 计一个
工作单位，采用普通 warm-start power iteration，并输出显式秩一投影。

在该模型内得到并独立复核了两项结果：

1. 若再给定相对谱比 `rho=lambda_2/lambda_1`，则投影误差满足精确谱分解，
   并有

   ```
   E_m <= rho^(2m) r / ((1-r)+rho^(2m)r).
   ```

   对 `0<lambda_2<lambda_1` 可直接解出达到误差 `epsilon` 的充分 matvec
   次数；`lambda_2=0` 时单列为恰好一次 matvec。

2. 即使固定完整 B12 元组，也仍可令工作量发散。构造
   `G_gamma=diag(1,0,1-gamma)`，并相应选择 warm start，使
   `(Delta,D,k,r)=(delta,1,1,r_0)` 对所有 `gamma` 完全相同；但当
   `gamma -> 0+` 时达到固定投影容差所需 matvec 数趋于无穷。

因此，全局谱直径和端点移动量不足以充当端点构造成本代理。后续工作量
定理至少需要内部 eigengap，或更精确地记录 retained state 在近顶特征空间
中的质量分布。

## 独立复核与修订

初次独立复核结论为 `REVISE / code gate NO-GO`。复核确认固定元组反例和
发散论证正确，但发现原式遗漏 `lambda_2=0`：若把对数分母形式直接延拓，
会错误得到零次迭代，而实际在 `epsilon<r` 时最少需要一次 matvec。

已完成精确修订：

- 对数工作量公式限定为 `0<lambda_2<lambda_1`；
- 单列 `lambda_2=0 => m_min=1`；
- 新增四个零次/一次边界诊断。

同一独立复核任务对修订后精确字节给出 `PASS for revision closure`。该 PASS
只关闭数学修订，不授予新颖性、代码门禁、通用求解器下界、5000 行实验或
论文 PASS。

## 有限诊断

- 随机 PSD 谱与 warm start：6000 例；
- 公式与直接投影最大绝对差：`6.562675750054758e-16`；
- 上界最大浮点超出：`2.220446049250313e-16`；
- 等号构造最大误差：`8.881784197001252e-16`；
- `lambda_2=0` 分段边界：4/4 通过；
- 固定 `(Delta,D,k,r)=(0.2,1,1,0.6)`：`gamma` 从 `0.1` 降到
  `0.0002` 时，最小工作量从 `15` 增至 `7361`，且 `gamma*m` 稳定在约
  `1.47`，与 `Theta(1/gamma)` 一致。

这些只是 float64 有限代数诊断，不是一般定理证明、native benchmark、
独立实验重复或统计样本。

## 运行与资源

本轮共 5 次有界命令尝试：4 成功、1 失败。失败来自宿主没有
`/usr/bin/time`，随后改用 shell `time -p`；没有重复科学失败。保守命令
wall 合计 `0.770031817` 秒，可测科学进程 CPU 下界 `0.434892353` 秒，
峰值 RSS `23904 KiB`。实测 cgroup 为 8 CPU 配额、8 GiB 内存，数值线程
均固定为 1；最终无 reservation 或常驻科学进程。

## 文献边界

Wang–Zhang–Zhang 已分析 warm-start power/Lanczos 的 gap-dependent 与
gap-independent界；Musco–Musco 给出 gap-independent block Krylov 近似；
Garber 等展示 shift-and-invert 的不同 gap、稀疏性和稳定秩依赖。在线 PCA、
Oja 和增量 PCA 又对应不同的 regret/统计估计目标。因此：

- 本轮精确幂迭代式是经典控制，不是新贡献；
- 固定元组反例只作为本项目的决策边界；
- 尚未完成覆盖充分的 closest-work/新颖性审计。

## Step 7 决策

保持 `NO-GO_NEW_METHOD`，不运行 Landmark-5000。下一轮回到 Steps 2/3：
从已保存的 native512 查询状态中检查 top-k 内部谱隙和近顶 hard-angle mass
是否实际可测且具有判别力；同时核对 warm-start block power/Lanczos 的原始
定理与实现。只有得到不等同于已有求解器分析、并能联系一致性证书和真实
刷新次数的命题，才重新进入候选筛选；否则退役“由 recourse 预测构造成本”
这一路线。
