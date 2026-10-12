# B14：Landmark-512 谱隙／角度诊断的负结果

## 结论

B14 在 B09 已保存的原生 Landmark 前 512 行、`d=2704,k=25` exact-query
状态上，前瞻冻结并检验了 top-k 内部谱隙、最坏主角、near-boundary hard
mass 和 block-power 工作代理。结果不支持“这些标量可稳定判断真实刷新”的假设：
没有任何前瞻候选特征在 `eta=0.01` 与 `eta=0.1` 两档同时达到 AUROC 0.75。

| 特征 | eta=0.01 AUROC | eta=0.1 AUROC | 两档通过 |
|---|---:|---:|---:|
| `rho=lambda_{k+1}/lambda_k` | 0.465 | 0.518 | 否 |
| 最坏主角 `sin^2(theta_max)` | 0.780 | 0.639 | 否 |
| near-boundary hard mass（V2） | 0.747 | 0.619 | 否 |
| block-power 工作代理（V2 定义域） | 0.479 | 0.455 | 否 |

严格唯一子空间的事后敏感性分析排除了每档 16 个零边界-gap 状态，仍不改变
结论：最有利的最坏主角 AUROC 为 0.763/0.570，hard mass 为
0.732/0.559。该敏感性不是原前瞻终点。

## 数学与语义核验

对 `G=A^T A`、精确 top-k 投影 `P` 和保存端点 `Q`，独立复核通过：

`(lambda_k-lambda_{k+1}) r(P,Q) <= loss(Q)-OPT <= (lambda_1-lambda_d) r(P,Q)`。

在 408 与 205 个真实 query 状态中，下界零容差违例。重新构造 273 个唯一
完整 SVD 端点后，保存 incoming loss 的最大绝对误差为
`1.539879335155092e-13`，query/update 掩码完全一致。

V1 独立复核为 REVISE：原 AUROC 过滤了有效的正无穷工作分数，一个
`lambda_k=0` 状态错误进入一步收敛分支，零 gap 的目标 top-k 子空间也并不唯一。
V2 保留 V1 原文件，修正无穷排序、将 16 个退化状态的工作代理标为未定义、
严格恢复预冻结 near-band 公式，并把未预声明的 hard fraction 降为探索性指标。
V1 全状态工作代理的透明修正为 0.512/0.532，仍为负。独立修订闭合为 PASS。

## 来源碰撞

普通/块幂法的 gap-dependent 工作关系不是新贡献；Musco--Musco block Krylov、
shift-and-invert 以及 SciPy LOBPCG 已提供更强或可 warm-start 的现成路线。
实际代码核查确认 SciPy LOBPCG 接受初始块 `X` 并用残差终止；mlpack block
Krylov 使用随机块、重复矩阵乘法、QR 与 Rayleigh--Ritz。因此仅把旧端点喂给
这些求解器只能作为强工程基线，不能算新方法。

## 执行与范围

候选与独立复核合计 8 个有记录命令，全部成功。可测／保守命令 wall 下界
为 42.598 秒（另有两个复核检查命令未计时并明确保留为未知），可测进程 CPU
下界 36.649 秒，峰值 RSS 356,540 KiB；8 CPU、8 GiB cgroup 内，数值线程 1，
无 GPU、容器或依赖安装，reservation=0。

这是同一公开开发前缀上的相关状态诊断，不是独立样本、因果证据、新方法、
native5000 结果、原创性判定或论文 PASS。

## 第7步决定

淘汰“用单一 geometry/gap/angle 标量推出刷新次数或 CPU”的路线。返回第2步：
把 warm-start LOBPCG/block-Krylov 作为有归因强基线，前瞻冻结与完整 SVD 相同
端点精度下的 matvec、CPU、RSS 和失败规则，先在 native512 真刷新端点做有限
校准；在强基线和证书后果明确前不运行 native5000，也不重新包装成新候选。
