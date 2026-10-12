# B11：候选碰撞闭合与代码门禁复核

日期：2026-10-10

## 本轮问题

B10 留下 C12/C13、C16、C20 三组尚未闭合的候选。B11 检查它们是否构成结构上独立的新方法，而不是已知优化器、证书或策略的重新命名。本轮没有授权方法代码或新性能实验。

## 数学结论

1. **C12/C13 当前不能计入已验证独立方法。** 固定二维旋转平面的能量可写成
   \(q(\theta)=m+\rho\cos(2\theta-\phi)\)。枚举阈值方程的全部根，只能得到该预选平面内的最小投影改变量。若把平面选择推广到固定搜索空间 \(S\)，约束“满足能量阈值且最大化与旧投影的重合”在 supported boundary point 可化为求 \(S^TGS+\mu S^TP_0S\) 的 top-k 特征子空间。该结论没有证明所有 constrained optimum 都被覆盖，也不等同于预选二维路径；它把候选压回 Hara–Yoshida Consistent PCA 的受限惩罚家族附近，但不足以宣称完全功能等价。
2. **C16 的核心求解器已知，完整包装碰撞未完全闭合。** “Ritz 向量—块残差扩展—重正交”的核心与未预条件 block-Davidson 高度重合；LOBPCG/Jacobi–Davidson 只是邻近家族，并非逐操作等价。证书审计与精确回退的完整组合尚未获得高置信文献覆盖，但当前也没有新算子或新保证，不能计入已验证候选。
3. **C20 的条件恒等式与既有 B07 证书形式相同，但实现身份需保留限定。** 若 FD 摘要满足 \(0\preceq G-B^TB\preceq\Delta I\) 且 \(\operatorname{tr}(G-B^TB)=\ell\Delta\)，则
   \[
   U=\operatorname{KyFan}_k(B^TB)+k\Delta,
   \qquad
   L=\operatorname{tr}G-U
    =\operatorname{tail}_k(B^TB)+(\ell-k)\Delta.
   \]
   因而 C20 的数学卡片没有新增证书内容；本轮没有重新读取并逐函数绑定 B07 的实际 width/convention，所以只判定条件恒等式 PASS、实现身份 PARTIAL。

## 有限检查

冻结脚本 `verify_b11_math.py`（最终 SHA256 `bd8f7db9be73737b378adc9c3b5893a2f6fbdc4d2ab1b518ddce6c676dd20e31`）的成功运行结果：

- 500/500 个随机二维 PSD 平面：最大边界方程误差 `3.55e-15`，与 40,001 点稠密网格的最小 recourse 差 `7.78e-05`，KKT 驻点残差 `1.11e-16`。
- 120 个满足 FD 精确包络与迹恒等式的独立元组：Ky–Fan 上界与 OPT 下界违例均为 `0`，最大代数恒等式误差 `4.26e-14`。
- 成功命令 wall `0.971016349 s`、CPU `0.970424765 s`、峰值 RSS `25,596 KiB`；结果 SHA256 `a202547bc988265583299cea57e6264429b973307587b1fd1d8d46ecc7a0788d`。

这只是有限代数诊断，不能替代理论证明、原始 FD 实现确认或新颖性证明。

## 失败与修复历史

原辅助脚本尝试在本轮再次运行 streaming FD。两次尝试均在“压缩后空行”的浮点判定处失败，分别耗时 `1.225115319 s` 与 `1.218226512 s`；无结果文件。按同类失败两次上限，未再修它，而改为直接检查本轮真正需要的包络与迹恒等式推论。失败回执及 stderr 全部保留。静态编译成功耗时 `0.107143139 s`。本轮共 4 次 attempt，总命令 wall `3.598604521 s`，结束时 reservation 为 `0`。

执行器是当前已安装的 Simple `.6` 命令/回执执行器，源快照 digest `2d2b3f006f7e444c97762224d87b71a6bb4dd5d08632861c86e1cb3fb5a25f66`；它不是历史 `.3` digest，也不代表部署了完整 SQLite/ACP RSI supervisor。研究决策仍遵循固定版本 autonomous-rsi 流程。

## 文献与源码碰撞

- Hara & Yoshida, *Consistent PCA with smooth perturbation*：最大化子空间重合并保持 PCA 质量的同一优化家族。
- Balzano et al., *Streaming PCA and Subspace Tracking: The Missing Data Case*：GROUSE 的秩一 Grassmann 正弦/余弦更新是已知结构。
- Alimisis, Saad & Vandereycken, *Riemannian optimization with exact line search*：特征子空间上的安全求根/精确线搜索已有直接先例。
- LOBPCG 与 Jacobi–Davidson：Ritz/残差扩展是成熟特征求解器结构。
- Woodruff & Zhou 作者代码在 Landmark 路径上刷新 randomized SVD；没有发现 C12 边界根作为作者原生更新。

## 门禁判断与下一步

B10 的 20 个草案经本轮审查后，没有任何一项达到“结构差异、证明边界和高置信碰撞审计均通过”的 verified-candidate 标准；因此不存在合法 Top-15，方法代码门禁继续为 **NO-GO**。独立复核将“碰撞完全闭合”判为 PARTIAL、将 NO-GO 判为 PASS：C12/C13 的 supported-point 推广、C16 的完整 certified wrapper、C20 与 B07 代码/约定的逐项身份仍留有限缺口。这些缺口不足以授权代码，也不能被表述为“全部 computation graph 严格等价”。这不是论文任务失败，也不是负结果的独立确认。

机器第 7 步选择回到研究第 2/3 步，但收紧候选定义：下一轮只接受同时给出“认证松弛—端点构造摊销成本—累计投影 recourse”可证伪联系的候选；单独求根器、特征求解器、证书、回退策略和参数策略不计入方法数。若该更强目标仍不能产生结构差异，应转向诚实的负结果/基准论文叙事，而不是继续扩充名字。

