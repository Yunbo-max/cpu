# 全新选题：稀疏训练与累计缓冲的隐式局部正则

日期：2026-10-23（Europe/London）。最新状态：CPU PyTorch已安装；已执行固定Megatron版本提取的原函数，74个排列及去偏对照通过；补充HT精确方差定理与873个排列核验。完整CUDA模型训练尚未运行。最新原创性结论已下调，见下文“最新原创性复审”章节；前轮记录保留供追溯。

## 最新原创性复审：2026-10-23

**结论下调：当前不支持“新的 MoE 去偏负载均衡方法”这一主张。** 代数和 CPU 原函数核验仍有效，但不能替代原创性和训练收益证据。本节覆盖此前较乐观的选题判断，历史记录保留。

本轮共执行 11 个定向检索查询（两种搜索引擎），并阅读关键原文、算法和附录。这是有边界的近邻审查，不是完整系统综述；没有可信的纯搜索计时，不能换算成已检索多少小时。

### 关键遗漏及修正

[φ-Balancing for Mixture-of-Experts Training](https://arxiv.org/html/2605.15403v1)，2026-05-14，当前核验为预印本。§3.1 明确提出小批次插件估计与总体均衡目标的偏差，以凸对偶、镜像下降和 EMA 追踪负载。附录 Algorithm 2 明确停止梯度，且 EMA 更新包含当前批次；Algorithm 3 还给出选择频率 EMA。因而“发现小批次偏差”“用历史频率去偏”“停止梯度的累计统计”均不能作为我们的独立创新。此前漏检此文是实质性缺口。

两者并非已经证明完全等价：该文主目标是总体平均路由概率的凸势；我们的恒等式针对固定参数、固定等大小微批次、均匀随机排列下的有限批次硬频率—概率梯度乘积。不得将该文的 EMA 概括为有限步严格无偏，也不得仅凭目标不同就宣称我们的算法新颖。

[Demons in the Detail](https://aclanthology.org/2025.acl-long.249/)，ACL 2025，已明确微批次均衡妨碍专门化以及全局批次均衡方案。此前对其顺序累计近似的核查仍保留；不能把已承认的近似描述为作者声称精确却被推翻。

[Unbiased Gradient Estimation with Balanced Assignments for Mixtures of Experts](https://arxiv.org/abs/2109.11817)，NeurIPS 2021 workshop，已研究容量约束下分配/跳过样本的无偏修正。其采样目标与我们的辅助损失不同，但排除了“首次研究硬件约束诱发的 MoE 梯度偏差”这种宽泛主张。

[PrefixFlow](https://arxiv.org/html/2606.01143v1) 附录 B 用逻辑 token 重数保持辅助损失语义；其中 prefix 指共享提示词，而非我们的时间累计前缀，不能混为同一问题。[EQB/LEI 作者说明](https://aleph-alpha.com/en/blog/balancing-experts-at-two-scales/) 已区分全局与局部均衡，宽泛的“两尺度控制”同样不是空白。

### 剩余可检验主张

在既定假设下，E[g_prefix]=(1-lambda_G)g_global+lambda_G*g_local，lambda_G=(H_G-1)/(G-1)。本轮已读材料中没有定位到这一特定有限排列系数推导；这是有限覆盖内的检索结果，不是首创证明。HT 配对修正、反序配对和不完全 U 统计的基本思想已有统计学先例，不能以重新推导取代方法创新论证。

保留定位：**累计前缀实现的梯度语义与可复现性审计**。撤回定位：已成立的新型去偏 MoE 优化方法。74 个 CPU 排列核验支持实现与公式一致，不支持困惑度、吞吐或泛化提升。

继续投入的必要对照为：原始累计前缀、精确全局均衡、按理论系数显式混合局部/全局、φ-Balancing（概率及频率版本）、合理的 loss-free 基线。需区分固定参数的单步梯度等价与真实多步训练结果，统一批次、token、计算与调参预算。若改进仅能由显式混合系数复现，应报告机制解释；若没有实用差异，不升级为新方法论文。

---

## 1. 重启范围与真实进展

本次按用户要求重新选题。旧 A（缓存漂移）、B（实验选择后验）、C（校准聚合）全部排除，不作为本轮候选。旧记录和费用历史保留。本轮继续使用 Autopilot Compact 0.10.0-compact.1，branching 模式。三个叶子分别检索科学导数、生成约束、稀疏优化；每叶至多 5 个查询和 6 次原文打开，不递归派生。三个叶子均已返回。没有远程训练、付费作业、定时任务或后台常驻研究。

本文件同时保留不成立的方向，避免下轮再次包装。当前仅保留一个有具体证据的研究诊断：**稀疏模型的使用率加权究竟改变了什么，以及其效果能否在实际更新尺度一致时保留。** 这是待审计的研究问题，不是已被证明原创、可发表的新优化器。

## 2. 三个方向的筛选

| 分支 | 本轮检查 | 数学对象 | 决定及原因 |
|---|---|---|---|
| D1 科学模型导数 | 力预测准确，曲率/稳定性仍错误 | Hessian 谱、最小特征值符号 | 淘汰宽泛新方法主张；PFT/HINT 已直接训练曲率。低频模态留下线索，未满足原创性标准 |
| D2 生成模型约束 | 严格可行并不意味着目标分布正确 | 投影推前分布、条件分布、coarea | 淘汰宽泛新方法主张；SAL、条件 guidance、调度和测度修正有直接先例 |
| D3 稀疏训练 | 系数均值守恒是否意味着更新尺度守恒 | 分块更新范数、系数—范数协方差 | 保留可验证的机制审计；原文有明确推断，数学反例成立，实际重要性未知 |

三个方向按机制区分，不是同一方法的不同应用。排序是探索性优先级，不是正式独立选题接受。

## 3. D3 原文依据与限制

主要对象：[Excitation: Momentum For Experts](https://arxiv.org/html/2602.21798v1)，v1，2026-02-25。复核 §3 Eq.(1)–(10)、§4.1 控制组、§4.5 模型规模、§4.6 batch-size 与学习率结果。其操作是在已有优化器产生的参数更新之后，用 batch 专家使用率计算乘子进行缩放。它使用平均乘子为 1 的 ZS 形式，并以此支持更新尺度保持及机制归因。

这是一处一般性机制解释，而不是具名定理。论文已有 Global-Exp、Random-Boost 和学习率扫描，不能声称作者完全没有控制。我们的具体问题是这些控制是否精确匹配了实际参数更新范数。论文报告的精度收益不因下述代数反例而自动失效。作者主页可检索到论文，但本轮未找到并核对其确切实验代码提交。

当前强相关新工作：[ExpertMuon-Compass](https://arxiv.org/pdf/2610.04140)，2026-10-02。复核 §1–3 的方向对齐缩放及附录 A Algorithm 1；它已经比较利用率缩放和梯度—更新对齐，并提供常数缩放等消融。因此不能把“按专家分配步长”或“依据对齐调步长”作为本轮原创。

[Megatron Core 官方文档](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/features/moe.html) 的 Router and Load Balancing 明确区分 micro-batch、sequence 和 global-batch balancing。将全局统计作为简单修复有很强先例，不是新概念。Exact Quantile Balancing and Load-Error Injection（2609.28053）搜索中出现，但正文两种地址均访问失败，等价性尚待核查。

## 4. 已完成推导：系数均值不守恒更新能量

设不同专家参数互不重叠，基础更新为 delta_e，a_e=||delta_e||_2，乘子为 phi_e>=0，E_e 为专家均匀平均。若 E_e phi_e=1，则

    E_e ||phi_e delta_e|| - E_e ||delta_e|| = Cov_e(phi_e,a_e).

因此平均分块范数保持需要额外的零协方差条件。整个参数向量的平方范数满足

    ||delta_mod||² = sum_e phi_e² a_e².

仅有乘子均值为 1 不足以固定该量，即便所有基础块范数相同。两专家 phi=(1.5,0.5)、a=(2,1) 时，基础平方范数 5，加权后 9.25，打乱乘子后 3.25。Random-Boost 保持乘子集合，却不保持和真实更新大小的配对。

最小因果对照是已知的范数匹配：

    c = sqrt(sum_e a_e² / sum_e phi_e² a_e²),
    delta_control,e = c phi_e delta_e.

对定向和打乱两组都应用同样匹配。分母为零且基础非零时回退基础更新并记录，不静默除零。此控制保持全局欧氏范数，不保持函数变化、KL 或 Hessian 二次型。它不是新方法贡献。

局部二阶变化为 grad L · delta + 0.5 delta^T H delta + remainder。即使范数相同，梯度对齐和曲率暴露仍会不同；因此不能预设范数匹配必定消除原方法收益。

## 5. 从该节点派生的新诊断：微批次如何进入期望更新

父节点：利用率和更新来自同一批样本，不能把两者当独立量。子问题：在参数、路由和每样本贡献固定时，先分批加权再累积，与先累积再加权，是否表示相同的算法？这是实现语义诊断，不是已观察到的原作者代码缺陷。

限定条件：固定参数位置；K 个专家；top-1；每样本路由不受其他样本影响；iid 样本；SGD 无 momentum；gamma=1；乘子停止梯度；无 clipping、额外正则项或 batch-dependent layer。对一个专家令 I_i 为选中指示，p=Pr(I_i=1)，v_i 为选中后的梯度，mu=E[v_i|I_i=1]，n=sum_i I_i，g=(1/B)sum_i I_i v_i。ZS 乘子为 K n/B。

展开同索引和异索引项：

    E[(K n/B)g]
    = K/B² sum_ij E[I_i I_j v_j]
    = K[p²+p(1-p)/B] mu
    = K[p+(1-p)/B] E[g].

这是条件恒等式。它说明不同 B 会改变专家块之间的相对缩放，而不只是统一学习率。它**不意味着一般性改变最优点**：对互不共享参数的专家及无其他损失项情况，正的块预条件不改变各块零梯度位置。对 Adam、训练中变化的 router、序列相关 tokens、共享参数、top-k、capacity/drop、额外辅助损失均需单独分析。

同一组 4 个样本，路由 (0,0,0,1)，各选中梯度均为 1，只有一次最终参数更新：

| 加权时统计窗口 | 两个专家的加权梯度 |
|---|---|
| 全部 4 个样本一起 | (9/8,1/8) |
| 切成 (0,0) 和 (0,1)，局部加权再等权累积 | (5/4,1/4) |
| 单样本局部加权再累积 | (3/2,1/2) |

这些向量不共线，单一全局学习率不能相互转换。该例的路由、样本和参数位置均不变，排除了多次 SGD 更新的顺序效应。

最简单的精确修复：先累计整个 optimizer step 的 count_e、样本总数和基础梯度，再执行一次基础优化器，再用一次全局 phi_e 调制。若 routes、逐样本梯度及基础 optimizer step 完全一致，则分块方式不改变更新（除浮点累加误差）。分布式情况下需要正确的通信组和 count reduction；这有额外成本，不能当作免费。若原实现本来这样做，此缺陷不存在，立即取消该代码缺陷假设。

另一个仅用于估计器分析的对照是 B>1 时 K(n-1)/(B-1)g，其期望是 Kp²mu。这是标准 leave-one-out/U-statistic 消除对角项的思路，不主张原创或更优。它会抑制单次访问，可能增大方差；也不等于整个有限样本 batch 的经验频率更新。

## 6. 实际完成的验证

运行了 Python 标准库 Fraction 精确枚举：B=1..8，p in {1/10,1/2,9/10} 共 24 组，逐项遍历全部二进制路由，验证上述期望式及 B>1 的 leave-one-out 恒等式。三个固定 partition 的分数结果也通过断言。退出码 0。

这只是有限代数诊断，不是训练实验、公开 benchmark 结果或原代码复现。另一个分支工作者做了内部数学查错，指出预条件不自动改变驻点的限制；其完整记录附后。内部查错不是独立 Work 批准。

## 7. 具体下一阶段设计（草案，未冻结、未执行）

先做机制审计，再决定是否值得整段训练。不靠“加一个模块”填补原创性空缺。

| ID | 要回答的问题 | 对比/控制 | 观测量与判定 | 状态 |
|---|---|---|---|---|
| M0 | 代数是否正确 | 有理数精确枚举；固定路由 partition | 恒等式逐项成立；不使用统计显著性 | 已完成 |
| C0 | 原方法实际在哪个窗口计算 phi | 精确代码提交、调用顺序、DDP/accumulation 配置 | 若全局 count 后一次调制，取消 microbatch 实现指控 | 未完成，原代码提交未知 |
| D0 | 真实更新有多大尺度变化 | 同一 checkpoint、batch、optimizer state；base/ZS/shuffle/norm-matched | global norm ratio、Cov(phi,a)、方向余弦、一步损失变化 | 未运行 |
| D1 | 是否存在纯 partition 效应 | 固定全批次128样本，micro=1/8/32/128；单次更新；关闭 batch-coupled 操作 | base 与 global-count 应一致；局部调制差异须超过浮点对照 | 未运行 |
| D2 | 改善是否仍来自定向分配 | 调好 LR 的 base、ZS、norm-matched ZS、norm-matched shuffle | 验证误差、步长、算力；只剩尺度收益则改写机制 | 未运行 |
| D3 | 从神经元稀疏到分块专家是否成立 | 同样干预用于 block MoE，必要时 Adam 单独分析 | 不能把 MLP 现象直接外推到 LLM | 未运行 |

原文可定位的起点：CIFAR-10 top-k MLP，4层、宽128、90%稀疏；block MoE ViT，64 experts、4层、宽128、top2。前者“expert”是神经元，不能混称标准分块 MoE。数据划分、确切 k 的取整、初始化、数据增强、train length、代码 revision、依赖和 baseline reproduction 还需核对。

建议诊断配置（本轮新拟，不冒充原文）：32个固定 batch、3个初始化种子；train只用于诊断；划出独立validation调参，test封存；D0/D1 优先 FP64 或 FP32 确定性路径，先记录 floating-control baseline，再定义差异阈值。3 seeds 只作探索，确认样本数由 pilot 方差与最小有意义效应确定，不预称显著。后续多对比需声明主对比并做家族控制；不能选择最有利 batch 作为结果。

低成本初始预算建议：D0/D1 单CPU最多10分钟或单GPU最多15分钟；运行前必须测内存并固定硬件/精度。此处是拟议限制，不是已批准硬件或测得用时。完整训练预算尚不能诚实给出，须先有原代码、epoch成本和审查。没有启动任何 GPU 作业。

需要的实现接口：collect_counts(routes,mask)、accumulate_gradient、compute_base_delta_once、modulate_delta、measure_update。count 应排除 padding、明确 top-k 总分母、在对应 replica group 汇总；optimizer state 每个逻辑 step 只更新一次；weight decay 是否随 phi 缩放须单列；AMP overflow 时 count、梯度、step 状态须同步重置。不要用每个 microbatch 调一次 Adam 的错误对照去“证明”调制问题。

## 8. 是否值得正式立题

当前判断：D3 是最值得先检查的低成本研究诊断，但**尚不够正式选为新方法论文**。两个基本修复都很简单，且与已有尺度控制/全局统计有直接联系。其价值必须来自真实训练中的影响及更一般、可验证的原则，而不是代数反例本身。

淘汰条件：原实现已经全局累积；真实 norm confounding 很小；精确范数匹配后机制解释仍完整；简单全局统计修复全部问题且没有新的代价/泛化问题；或者检索到完全等价的已有研究。任一命中都应保留负结果并重新进入发现，而不硬凑新优化器。

## 9. 全流程状态与审查交接

| 阶段 | 实际状态 |
|---|---|
| 重新选题、分支搜索、已有工作排除 | 完成这一轮三个叶子的探索 |
| 原文机制核查、推导、有限数值诊断 | D3已完成上述限定部分 |
| 原创性确立、正式选题冻结 | 未完成 |
| 原生代码/数据定位与完整实验协议 | 未完成，明确缺口见 C0 |
| 独立 Work 选题/设计审查 | 未发生 |
| 正式实现、代码审查、模型实验、结果审查 | 未发生 |

可直接交给独立审查会话的任务：阅读本文件和文中原文；首先判断 D3 是否只够作复现审计而非论文选题；核对 Eq.6 的机制归因以及微批次子问题是否对应真实代码；检查有限样本条件、共享参数、Adam与routing的边界；判断最简单修复是否已消除新方法必要性；对三个分支给出 accept/revise/reject，并引用具体证据。禁止把没有找到代码解释为代码存在缺陷。未获得回复前不能记录批准。

Compact 的独立审查要求来自 references/counterexample-review.md：Use a separate real conversation reserved for review。当前内部 agents 不满足这个独立会话要求。该文件可用于实质审查，但尚无研究项目 GitHub commit、冻结 subject 或审查回执；不能捏造这些元数据。

## 10. 成本与可复现记录

本轮新发现阶段：三个叶子共15查询、18次打开（含失败）；整合者12查询、13次打开（含失败），合计27查询、31次打开。另有find操作，详见叶子日志及当前对话。内部代数检查一次；Python有限诊断先浮点探索一次，再Fraction精确枚举一次，均无训练。工具总耗时不是CPU计费用时，provider tokens/费用无回执，记为未知。

旧轮成本不清零：旧文件记录26查询、36次打开；之后恢复旧题的原文核查另有调用，不能把这份新轮27/31当作会话累计总成本。本次仅独立记录用户明确要求的重新选题这一轮。

整合者检索原词：
1. machine learning interatomic potentials Hessian phonons force accuracy failure 2025 2026
2. diffusion constrained sampling projection distribution bias 2025 2026
3. mixture experts optimizer momentum inactive expert sparse Adam 2025 2026
4. "Excitation" "2602.21798" optimizer
5. "mixture of experts" "update" "frequency" optimizer learning rate
6. "mixture of experts" "utilization" "batch size" "optimizer"
7. "Excitation" "gradient accumulation"
8. "expert" "utilization" "leave-one-out" gradient
9. "mixture of experts" "batch size" "learning rate" frequency squared
10. "Excitation" "Shaier" github
11. "mixture of experts" "microbatch" "optimizer" utilization
12. "utilization" "gradient" "U-statistic" experts

下附完整叶子、内部数学查错以及可重跑诊断程序/输出。它们是来源和探索记录，不代表独立批准。


---

## 附件 fresh_derivatives.md

# Fresh discovery leaf D — scientific surrogates and derivative reliability

Date: 2026-10-23. Status: REJECT generic proposal; PARK narrow spectral-decision lead. Discovery only. No implementation, experiments, independent review, formal verification, or novelty certification.

## Decision

Do not select “accurate energy/forces but wrong Hessian; add Hessian supervision” as a new project. Explicit curvature supervision, scalable HVP losses, and even transition-state validation already exist. A narrow remaining question concerns whether averaged curvature error conceals wrong curvature signs near soft modes, but both its mathematical explanation and obvious repair are classical. Further investment requires a demonstrably unaddressed practical failure; the present evidence does not establish one.

This is a fresh inquiry, not a continuation of previous A/B/C. No previous project costs or evidence were erased. The parent owns integration and persistence.

## Primary evidence inspected

1. **PFT: Phonon Fine-tuning for Machine Learned Interatomic Potentials**, Koker et al., ICML 2026. Official proceedings result: https://proceedings.mlr.press/v306/koker26a.html ; inspected arXiv v1 https://arxiv.org/html/2601.07742v1 §§2.1–3.3, Eq. (1)–(9). Its conservative energy model is differentiated to obtain forces; Eq. (8) adds curvature supervision to energy/force/stress losses. Eq. (9) samples a Hessian column and applies elementwise absolute error. This already addresses missing curvature and scalable supervision. Do not conflate its MAE objective with HINT’s squared Frobenius objective. Proceedings metadata verifies acceptance; the final proceedings PDF was not opened, so version differences remain unverified.

2. **Hessian-informed machine learning interatomic potential towards bridging theory and experiments**, Yin et al., arXiv:2603.25373v1. https://arxiv.org/html/2603.25373v1 . Inspected introduction and Methods, especially Eq. (1)–(4), lines 120–154. HINT combines low-fidelity pretraining, configuration sampling and a growing Hessian-loss weight. Its random-vector loss estimates squared curvature error; Rademacher probes and five vectors per batch are reported. Native evaluation includes ReactBench’s 960 reactions, growing-string initialization, RS-I-RFO and IRC endpoint validation. Thus “curvature helps transition-state search” is also occupied.

3. **Hessian-Informed Conformation Augmentation for Potential Energy Surface Curvature in Machine Learning Interatomic Potentials**, Kwak and Jo, arXiv:2609.05233v3 (12 October). https://arxiv.org/html/2609.05233v3 . Inspected abstract/introduction only (not detailed equations). Hessian-derived Taylor labels for perturbed geometries offer another existing repair; isotropic and normal-mode displacement schemes are named. Treat the exact weighting and implementation as uninspected leads, not ruled-out equivalents.

4. **Targeted fine-tuning of machine-learning interatomic potentials for phonons and phase transitions**, Grandel et al., npj Computational Materials, published 7 October 2026. https://www.nature.com/articles/s41524-026-02338-w . Search result from publisher reports differences in instability/phase-transition correctness despite similar harmonic accuracy, and compares L2-TSP and transfer/multihead/LoRA alternatives. Full article open failed with publisher redirect. This is a strong collision lead, not full-text inspection evidence.

Other search-only leads: Projected Hessian Learning arXiv:2603.04523; HIP direct Hessian prediction; 2021 Sobolev-trained surrogates for optimization; 2025 Systematic softening in universal MLIPs. None is claimed fully audited.

## Concrete mechanism and exact witness

Object: a conservative local quadratic energy on the physical subspace after removing translational/rotational zero modes. Let dimension d >= 2 and 0 < epsilon < 1/3. Reference energy E(q)=q^T H q/2 has

H = diag(epsilon,1,...,1).

Two model Hessians are

H_A = diag(-epsilon,1,...,1),
H_B = diag(epsilon,1+3 epsilon,1,...,1).

Their squared Frobenius errors satisfy

||H_A-H||_F^2 = 4 epsilon^2 < 9 epsilon^2 = ||H_B-H||_F^2.

Model A has lower average curvature error but predicts an unstable direction; model B remains positive definite. Their elementwise absolute errors are likewise 2 epsilon versus 3 epsilon. Thus the order reversal applies to both inspected error families, without equating the families.

Along the first mode q=t e_1,

E_A(q)-E(q) = -epsilon t^2,
F_A(q)-F(q) = 2 epsilon t e_1.

On a fixed radius, both energy and force error vanish as epsilon tends to zero, while the sign is wrong at every positive epsilon. Both models derive forces from scalar energies, so enforcing conservativity does not repair the example. No imaginary frequency is caused by a non-conservative force field here.

For HINT-style Rademacher z with E[zz^T]=I, the exact identity is

E[||(H_hat-H)z||_2^2]/d = ||H_hat-H||_F^2/d.

An unbiased stochastic loss faithfully estimates the chosen average error; unbiasedness does not make that error a certificate for a sign decision. The single soft-mode defect contributes 4 epsilon^2/d to this objective. This is a property of the objective, not proof of a failed training trajectory or a claim that using more probes makes the model worse.

## Scope and strongest simple explanation

The witness is classical spectral sensitivity, not new mathematics. Weyl’s perturbation bound gives

lambda_min(H_hat) >= lambda_min(H) - ||H_hat-H||_2.

If a valid operator-norm bound delta is available, lambda_min(H_hat)>delta certifies positive definiteness of H on the projected physical subspace. Near a true transition, the spectral margin tends to zero; fixed absolute accuracy cannot uniformly certify the sign. Exact or sufficiently accurate Hessian supervision solves the example. There is no impossibility theorem against PFT or HINT, and no contradiction of their empirical average improvements.

The easiest candidate repair is evaluation/sampling concentrated near soft modes plus reference-calculation fallback for uncertain signs. Spectral weighting, trust-region eigenvalue checks and uncertainty certification are well-known mathematical tools. Their combination is not automatically a contribution. Direct spectral loss must also confront zero modes and near-degenerate eigenspaces; an eigenvector-by-eigenvector target may introduce arbitrary basis dependence. No new loss is recommended until these antecedents and the latest October paper are inspected.

## Discriminating native probe (proposed, not run)

Potential assets, subject to repository/data access and exact version checks:

- PFT’s Nequix MP/MDR phonon setting for dynamical stability.
- HINT’s AlphaNet/HORM/ReactBench setting for transition-state inertia and native IRC success.

At fixed reference geometries and identical labels, compare standard energy/force training with existing PFT or projected-Hessian training. Stratify only by held-out reference spectral margin after removing known rigid-body modes. Report operator-norm error, inertia/sign accuracy and native downstream outcomes alongside average Hessian error. Freeze strata before treatment results. Perturbation-based synthetic witnesses are diagnostics, not substitutes for native data.

Falsifier: ordinary existing curvature supervision already achieves reliable native decisions at matched data and compute, or remaining disagreements lie entirely within reference numerical uncertainty. A simple DFT fallback/eigenvalue-error threshold that matches a proposed module also rejects the module’s necessity.

Empirical question that survives only as a lead: does limited-budget curvature supervision systematically leave practically consequential sign errors in soft subspaces even when average curvature metrics improve, and can a cheaper existing repair already remove them? This is not yet established as an original gap.

## Exact search and access accounting

Five individual queries, no further queries:

1. system2: machine learning interatomic potentials Hessian phonon errors force accuracy smoothness 2025 2026
2. system2: learned surrogate inverse design gradient error Sobolev training optimization reliable derivatives
3. system1 recency=730: "phonon" "fine-tuning" "soft modes" Hessian loss
4. system1 recency=730: "Hessian-informed" "HINT" interatomic potential
5. system1 recency=730: machine learning interatomic potential Hessian eigenvalue weighted loss soft modes instability

Six opens (including repeats and failure): PFT HTML introduction; Grandel publisher page (failed); HINT HTML introduction; PFT lines 100 onward; HINT lines 130 onward; ModeAug v3 HTML introduction. No find calls, no code executions, no native jobs, no paid model runs initiated. Provider token and monetary costs unknown without receipts. Primary evidence retrieved via web; no local benchmark evidence.

## Handoff

Rank below a branch with an actual novel mechanism. Preserve this negative result and the concrete spectral witness. Do not rescue it by renaming it, claiming a new field, or asserting that modern MLIPs lack Hessian supervision. Parent may retain the soft-mode lead for future targeted source inspection, but should not freeze it as a selected method on this record.


---

## 附件 fresh_constraints.md

# Fresh discovery leaf: constrained generative sampling

Date: 2026-10-23. Leaf owner: /root/generative_constraints. Parent: fresh-topic reset, not continuation of previous A/B/C. Stage: bounded literature/mechanism discovery; no model experiments or independent approval.

## Decision

**REJECT the broad topic as a new-method recommendation in this round.** The appealing claim “hard feasibility can worsen distributional correctness” is real but already central to current literature. Projection bias, disconnected/nonconvex exploration, correction timing, endpoint conditioning and coarea corrections all have directly relevant prior work. A narrow diagnostic survives, but not an evidence-supported original algorithm.

Do not spend training compute on a renamed projection/scheduling method. No new scientific candidate is promoted and no full experiment design is frozen. This negative result is a completed discovery outcome, not evidence that all constrained generation is solved.

## Grounding and inspected sources

1. **Split Augmented Langevin (SAL)**, Blanke et al., arXiv:2505.18017v1, 23 May 2025. https://arxiv.org/html/2505.18017v1 . Inspected introduction, §2 target definition via find, nonconvex-exploration passages and Appendix A.2 via find, §5.3 via find. §2 Eq. (2.2) targets exp(-f(x)) times an indicator. The paper explicitly identifies hard-projection trapping and biased exploration under nonconvex constraints; its proposed family uses variable splitting/primal-dual sampling. Appendix A.2 already illustrates deficient exploration on an energy constraint. Its native applications include energy-constrained fields, data assimilation, and acceleration-controlled trajectories with obstacles. **Not inspected:** full convergence proof or exact SAL update chain. Thus do not claim a theorem refutation or equivalent detailed implementation.

2. **Enforcing Constraints in Generative Sampling via Adaptive Correction Scheduling**, Trupin & Xue, arXiv:2605.11214v1, 11 May 2026. https://arxiv.org/html/2605.11214v1 . Inspected §1–3.3 equations and Appendix G.6/I.3 via find. The actual operation is x_next = projection(Phi(x)) when a schedule fires, otherwise Phi(x); the scheduler uses s_t = d(Phi(x_t), M). Evaluation follows deviation from the stepwise reference, including accumulated defect, rather than proving that reference is the desired conditional distribution. Appendix I.3 explicitly acknowledges poor alignment between defect and downstream distortion. Therefore sensitivity-weighted correction cannot be presented as exposing an unacknowledged universal guarantee. Projection-call savings also do not establish equal wall-clock savings.

3. **Conditional Diffusion Guidance under Hard Constraint: A Stochastic Analysis Approach**, Guo, Tang & Xu, 5 February 2026, arXiv:2602.05533. https://www.columbia.edu/~wt2319/Diffusion_guidance.pdf . Inspected pp. 1–3 including h(t,y)=P(Y_T in S | Y_t=y) and drift b+g² grad log h. This directly addresses terminal conditional generation with a pretrained diffusion. A generic proposal to learn future constraint probability and guide by its log-gradient collides with this work and classical Doob transforms. **Not inspected:** full assumptions, nonasymptotic proofs and experiments. Do not assert exact hard feasibility for an arbitrary learned approximate h or zero-probability equality event based on the displayed ideal construction.

4. **Metropolis Sampling for Constrained Diffusion Models**, Fishman et al., NeurIPS 2023. https://proceedings.neurips.cc/paper_files/paper/2023/hash/c47bfcc8e2eccdc540fad1e25f13aa4d-Abstract-Conference.html . Search-result primary abstract only: a Metropolis noising process discretizes reflected Brownian motion and covers nonconvex domains. This is a collision lead, not full inspection.

5. **Constrained Synthesis with Projected Diffusion Models**, Christopher et al., NeurIPS 2024. https://papers.nips.cc/paper_files/paper/2024/hash/a28af221f2f70be183afc16797a56b91-Abstract-Conference.html . Official code surfaced: https://github.com/RAISELab-atUVA/Projected-Diffusion . Search-result primary abstract only; code not inspected. It establishes that projected diffusion itself is not new.

6. **Neural SHAKE: geometric constraints in neural differential equations**, Journal of Cheminformatics 2025, DOI 10.1186/s13321-025-01053-w. https://pmc.ncbi.nlm.nih.gov/articles/PMC12323260/ . Primary search result exposes explicit coarea/Fixman treatment and full-rank constraint-map formula. This is a direct collision lead for any generic Jacobian correction proposal; full derivation not read under this leaf's open limit. A 2026 title “The Right Measure for Physics-Constrained Generation: A Co-Area Correction for Posterior-Consistent PDE Inverse Problems” also surfaced on ResearchGate; it remains an unverified lead, not accepted evidence.

7. **Constrained Diffusion for Protein Design with Hard Structural Constraints**, ICLR 2026 primary PDF URL https://proceedings.iclr.cc/paper_files/paper/2026/file/c991f77d9faa6de92bc6945c191d66e6-Paper-Conference.pdf . Both PMC and PDF access failed (CAPTCHA and size limit). Search snippets acknowledge early projection bias and cite SAL. Do not describe this as full-paper inspection or choose an exact checkpoint from it.

## Mathematics: three distinctions that eliminate weak novelty claims

### A. Projection is not conditioning (exact elementary witness)

Let X be standard Gaussian and C=[0,infinity). The Euclidean projection is Z=max(X,0). Its distribution is

    Law(Z) = 1/2 delta_0 + phi(z) 1{z>0} dz.

The conditional target is instead

    Law(X | X>=0) = 2 phi(z) 1{z>0} dz.

Both outputs are perfectly feasible. Their mass at {0} differs by 1/2, so their total variation distance is at least 1/2 (in fact exactly 1/2). This is a proof about terminal clipping, not all projected Langevin/diffusion procedures and not an empirical model result. Rejection sampling exactly solves this example with two proposals per accepted draw on average. Learned h-guidance is already a general relevant repair. No new method follows.

### B. A zero-set does not uniquely specify a conditional target (conditional coarea identity)

Let p be a smooth ambient density, g:R^d -> R^m smooth and full rank on M={g=0}, with regularity/integrability sufficient for a thin-tube conditional limit. Conditioning on ||g(X)||<=epsilon as epsilon tends to zero gives surface density proportional to

    p(x) / J_g(x),   J_g(x)=sqrt(det(Dg(x) Dg(x)^T)).

Replacing a scalar constraint g by g_tilde=a(x)g(x), with positive smooth a, leaves M unchanged but on M changes J to a J. The limiting distribution changes by 1/a. Thus “same feasible set” is not enough to establish the same probabilistic inference problem. Euclidean-distance tubes, residual tubes, and a prescribed surface-density target are different choices. This is standard coarea reasoning and already represented in current constrained-generation work; not claimed original.

An evaluation must specify which target is correct before accusing a sampler of bias. In scientific design where only feasible high-quality candidates matter, matching a conditional probability law may not even be the objective. This limits the practical scope of the whole proposed topic.

### C. Largest geometric defect need not deserve the projection budget (exact constructed witness)

State x=(u,v); feasible set M={v=0}; projection P(u,v)=(u,0). Start (0,0), and allow exactly one optional correction after either the first or second update, plus common terminal projection. Define

    Phi_1(u,v) = (u,10),
    Phi_2(u,v) = (u,1),
    Phi_3(u,v) = (u+K v,0),   K>0.

The first defect is 10 and second is 1. Correcting after Phi_1 has zero terminal value because Phi_2 discards that normal coordinate; the endpoint is (K,0). Correcting after Phi_2 produces (0,0), matching stepwise correction. Every final sample is feasible. A rule that spends its sole correction on the larger defect can therefore be arbitrarily worse in endpoint distance as K grows.

This targets endpoint fidelity, not cumulative defect: the former must not be silently substituted for the latter. The scheduler paper itself lists defect/value misalignment as a limitation, so this is a scope witness and a diagnostic, not a refutation of an unconditional theorem.

For smooth dynamics and small omitted correction delta_t, the first-order terminal effect is approximately

    delta x_T = D Phi_{T-1} ... D Phi_{t+1} delta_t,

with intervening projection Jacobians where applicable. A terminal scalar loss changes approximately by its gradient paired with that transported perturbation. Adjoint/error-propagation methods already motivate this expression. Estimating it adds backward/rollout cost, and no bounded collision search established a new algorithmic distinction.

## Smallest justified action and falsifier

No new module. If revisited, first audit whether a native task requires a conditional probability law or merely feasible useful designs. For a distributional task, evaluate exact low-dimensional examples under the actual intended law, comparing terminal projection, stepwise projection, rejection, SAL where applicable, and h-guidance. For a scheduling task, compare endpoint/sample-distribution error at matched total compute, not only defect sums or correction counts. Strong simple control: random/periodic schedules and one-step sensitivity with its overhead charged.

Reject a new method claim if an existing correct conditional sampler or simple correction schedule matches it at fair compute. Park practical testing if no native target distribution/reference can be specified without invented labels. These analytic witnesses can be implemented later as unit diagnostics but are not substitutes for a scientific benchmark.

## Model/data readiness

- PDM official repository is a grounded starting point, but exact commit, weights, dataset version and native evaluator have not been inspected; NOT execution-ready.
- SAL §5.1 energy-constrained bimodal fields and §5.3 controlled trajectories are grounded published setups, but exact released assets are not verified; NOT execution-ready.
- Protein constrained generation is not an approved candidate because the full primary paper and checkpoint were inaccessible in this leaf.
- No new checkpoint or dataset is invented, and no expensive experiment is requested.

## Retrieval and cost log

Five individual queries:
1. diffusion models hard constraints projection sampling manifold scientific design distribution bias
2. constrained diffusion sampling disconnected manifold projection topology Fixman
3. diffusion hard constraints disconnected components probability weights projected diffusion 2025 2026 (system1, recency 730)
4. "Blanke" "diffusion" "constraints" 2025 (system1)
5. "diffusion" "constraint" "coarea" "Fixman"

Six open attempts:
1. adaptive-scheduling arXiv HTML
2. protein PMC (CAPTCHA)
3. SAL HTML
4. adaptive-scheduling HTML at line 125
5. ICLR protein PDF (size failure)
6. conditional-guidance author PDF

Five finds: SAL Algorithm 1; SAL Constrained target distribution; SAL non-convex; guidance Assumption 1 (no match); scheduler projection cost.

No model experiment, paid native job or benchmark run. Provider tokens and charges unknown; not inferred from byte lengths. This leaf's search/opener allowance is exhausted. Formal independent comparison/design review remains absent.


---

## 附件 fresh_sparse.md

# Fresh leaf S — Sparse optimization: distinguish update allocation from update size

Date: 2026-10-23. Discovery only; no model training, no native experiment, no independent review. New topic, separate from old A/B/C. Root owns persistence.

## Decision

**Retain a narrow reproducibility/mechanism audit, not yet a novel method or selected paper topic.** Reject the generic proposal to invent an expert-activation clock: sparse moment masking is established, and Adam itself explicitly analyzes rare-gradient step amplification. An inspected recent paper gives a sharper concrete target: its average multiplier normalization does not establish its claimed preservation of update magnitude. The resulting norm-matched experiment is valuable, but its scientific consequence is unknown and elementary normalization is not a novel optimizer.

## Grounded target

Excitation: Momentum For Experts, Sagi Shaier, arXiv:2602.21798v1 (25 February 2026), https://arxiv.org/html/2602.21798v1 . Inspected §2, §3.1 Eq.1–5, §3.2 Eq.6–10, §4.1 controls, §4.2–4.5 excerpts. No official acceptance confirmed. No official implementation inspected or located; the equation specification is the implementation locator for this discovery leaf.

The paper partitions parameters into expert blocks, measures batch utilization u_k, computes a base optimizer step delta_k, then scales it by Phi_k. Its zero-sum option uses Phi_k = u_k^gamma / mean_j(u_j^gamma). Therefore mean(Phi)=1. The paper treats this as preserving average update magnitude and uses it in a causal argument that gains are driven by allocation rather than global update scale. Its random-shuffle control preserves the multiset of Phi but not its association with update magnitudes. These are the exact claims being audited; the paper's empirical improvements are not disproved by this observation.

## Exact mathematical witness

Let a_k = ||delta_k||_2 and let E denote the uniform average over K expert blocks. Since Phi_k >= 0,

    E[||Phi_k delta_k||] - E[||delta_k||]
      = E[Phi a] - E[a]
      = Cov(Phi,a),  when E[Phi]=1.

Thus average block update norm is preserved iff this covariance is zero. No such condition follows from normalizing the multipliers. Because expert blocks are disjoint, global squared Euclidean update norm is

    ||delta_exc||_2^2 = sum_k Phi_k^2 a_k^2,

which is not fixed by mean(Phi)=1 even when all a_k are equal.

Finite witness: two experts, u=(3/4,1/4), gamma=1, Phi=(3/2,1/2), a=(2,1). The base average block norm is 1.5; after scaling it is 1.75. Base squared global norm is 5; scaled squared norm is 9.25. If the multipliers are swapped, squared norm is 3.25. Consequently the targeted-vs-shuffled comparison also changes global update norm in this witness.

This is an algebraic counterexample to a general preservation assertion, not an empirical counterexample to the reported learning curves. The witness uses feasible utilization frequencies and nonnegative block norms but does not assert they occur at a particular trained checkpoint.

## Smallest diagnostic repair (known normalization, not claimed novel)

To isolate allocation while preserving global Euclidean step norm, use

    c = sqrt(sum_k a_k^2 / sum_k Phi_k^2 a_k^2),
    delta_control,k = c Phi_k delta_k.

Use c=1 if both norms are zero; if only the denominator is zero, fall back to the base update and record the event. The same normalization must be applied after shuffling. If testing average block norm instead, use c = sum(a)/sum(Phi a). These are different controls and should not be conflated.

This scalar does not change the direction of the modulated full update; it removes its change in global norm. It does not preserve functional KL, Hessian energy, or descent alignment. A norm match is a necessary causal control here, not proof that all optimization confounds are eliminated.

For a twice differentiable objective, local change has expansion

    L(theta+d)-L(theta) = grad(L)^T d + (1/2)d^T H d + O(||d||^3).

At matched ||d||, allocation may still improve gradient alignment or alter curvature exposure. That is the useful remaining question: does utilization supply beneficial *directional allocation*, after step magnitude and LR tuning are controlled? If yes, the original mechanism may survive despite the false preservation rationale. If no, there is a concrete causal reinterpretation rather than a new optimizer.

### Conditional harmful boundary, not novel theory

For fixed routing/utilization and a quadratic local model L(theta)=1/2 sum_k lambda_k theta_k^2 with lambda_k>0, base SGD is stable iff 0<eta lambda_k<2 for every block. Excitation gives theta'_k=(1-eta Phi_k lambda_k)theta_k, requiring 0<eta Phi_k lambda_k<2. With Phi=(1.5,0.5), lambda=(1,1), eta=1.5, the base contraction factor is -0.5 in both coordinates; the first modulated factor is -1.25 and diverges. Mean(Phi)=1 has not preserved the stability boundary. This is standard diagonally preconditioned gradient descent analysis, not an originality claim and not evidence that the paper's chosen learning rate diverges. The observable prediction is that curvature-weighted amplification, not utilization alone, determines the dangerous step-size region. A global LR reduction already repairs this toy case. Norm matching removes one confound but does not ensure a curvature bound.

## Closest established alternatives and collision status

1. Adam, Kingma and Ba, ICLR 2015, arXiv:1412.6980v9, https://arxiv.org/pdf/1412.6980 . Inspected Algorithm 1, §2 rare-gradient stepsize discussion, §3/§5 sparsity and bias-correction excerpts. The paper already treats sparse gradients; it is incorrect to propose that rare activation effects are newly discovered. Its algorithm specifies moment decay, bias corrections, and updates, providing an exact comparator.
2. PyTorch SparseAdam official docs, https://docs.pytorch.org/docs/main/generated/torch.optim.SparseAdam.html . Inspected masked-update explanation lines 304–321: moment and parameter updates are restricted to materialized sparse-gradient entries. This is a strong antecedent to conditional moment clocks, though the native tensor constraints mean it is not automatically a drop-in MoE optimizer.
3. Excitation itself is a direct collision for generic utilization-dependent step scaling. Do not propose such scaling as our novelty.
4. Global step normalization and clipping are elementary existing techniques. No exhaustive search on norm-matched MoE optimizer comparisons was performed after the concrete issue emerged; novelty of a systematic study remains unresolved.

The alternative clock idea is parked, not quietly replaced: with a scalar gradient previously zero for T-1 steps, Adam's first nonzero update approaches eta*(1-beta1)/sqrt(1-beta2) as T grows (epsilon negligible), rather than eta at a fresh local clock. This is already discussed by Adam, so it cannot be sold as a new counterexample.

## Concrete diagnostic design, not approved execution

Source-grounded model/data: Excitation §4.1 uses a 4-layer width-128 top-k MLP at 90% activation sparsity on CIFAR-10, CIFAR-100 and SVHN; §4.5 includes a 17M parameter MoE-ViT with 64 experts, L=4, d=128, top-k=2. These are reported configurations, not inspected dataset files/checkpoints or a reproducible commit. Start with the published micro-MoE only for reconstruction, then require a real block-MoE replication before generalizing to LLMs.

Proposed stage 0, no full training: at identical saved states and identical minibatches, record u_k, a_k, Phi_k, covariance, base/scaled/shuffled global norm ratios, and one-step objective change for Adam and SGD. All arms start from the same parameters and optimizer states. Do not update the base optimizer twice when extracting delta; either clone state or compute candidate deltas non-mutatingly. Define treatment of decoupled weight decay consistently; measuring the entire AdamW delta versus only its gradient component changes the intervention.

Proposed stage 1: base optimizer with matched LR tuning; published Excitation-ZS; norm-matched ZS; norm-matched shuffled-ZS. Record validation loss/accuracy, training loss, routing utilization, base and applied norms, covariance, optimization steps, examples, and wall time. Use paired seeds and a fresh confirmation split. Exact dataset hashes, implementation commit, hyperparameter grid and resource limits remain to be fixed by the owner before execution.

Falsifiers: if actual covariances/norm ratios are negligible in the native configuration, the issue has little empirical force. If norm-matched ZS consistently retains the gains over tuned base and norm-matched shuffle, directional allocation remains supported. If tuning/matching removes the difference, reinterpret the benefit as partly global-scale mediation. If discrepancies arise only in an unfaithful reconstruction, do not attribute them to the original method.

## Scope, costs and next action

This leaf does not warrant a promise of a top-tier paper. It warrants an inexpensive mechanism diagnostic once actual code and protocol are available, or parking in favor of a stronger topic. A rigorous negative result is useful but may be an audit note, not a standalone major contribution. No need to invent a new loss or method.

Search use: 5 individual queries (2 system2 + 3 system1), 6 open attempts (including one redirect-only result and a repeated paper section), 6 find operations. No model experiments. Provider tokens/fees unknown; no bill received. Queries:

1. mixture experts Adam optimizer rarely activated experts optimizer time step sparse gradients
2. mixture of experts optimizer inactive experts momentum updates Adam conditional computation
3. "mixture" "experts" "Adam" "frequency" (system1, recency 730)
4. "sparse" "Adam" "bias correction" "inactive"
5. "mixture of experts" "optimizer" "clock"

Open attempts: Excitation HTML; SparseAdam docs; stable zero_grad docs (redirect-only); Adam PDF; Excitation line 97; versioned zero_grad docs (main body not returned in opened excerpt). Do not count the latter as verified None-versus-zero semantics; no relevant text was retrieved by find. Finds: Excitation Algorithm, modulat, github; SparseAdam mask; zero_grad skip; Adam sparse.

Useful browser refs for owner to reopen before citation: turn15view0 (Excitation Eq.6 and controls), turn13view4 (SparseAdam), turn16view2 (Adam rare-gradient result). URLs above are authoritative locators.


---

## 附件 fresh_algebra_audit.md

# Internal algebra audit: microbatch-dependent frequency modulation

2026-10-23. Requested by integration owner. This is an internal mathematical check, not independent Work selection/design approval, formal verification, a novelty audit, or a native experiment. No searches or experiments performed.

## Verdict

The stated expectation and leave-one-out correction are algebraically correct under explicit token-independence and fixed-parameter assumptions. The strongest accurate interpretation is **microbatch-dependent expected expert-block preconditioning**, not automatically a changed optimum or a worse learner. A global-count implementation gives exact partition invariance only when routes and individual gradients are unchanged and the update is performed once after accumulation.

## Setup and assumptions

Fix model parameters theta and expert e. For token i, I_i is its top-1 routing indicator and V_i is its hypothetical gradient contribution to expert e's parameter block. Define W_i=I_i V_i. Assume:

- Token pairs (I_i,V_i) are iid across i; p=P(I_i=1), mu=E[V_i | I_i=1]. Finite first moments suffice for the expectation identities.
- Gradient V_i may depend on the same token that determines routing; independence between I_i and V_i is NOT required.
- Other tokens' routes do not change V_i. Thus batch capacity/drop effects, cross-token operations, batch-normalization, and token-coupled losses can invalidate this simplification. Autoregressive tokens from a shared sequence are generally not iid without an explicit approximation or different sampling unit.
- All microbatches use the same theta, with no optimizer update between them. The count modulation is treated as an applied, stop-gradient coefficient rather than differentiated as a parameter-dependent objective.
- K is fixed, n=sum_i I_i, g=B^-1 sum_i W_i, and Phi=K n/B. This is the gamma=1 case. Nonlinear exponents require different moments.

## Direct expectation

Expand n sum_i W_i into same-token and cross-token terms:

E[n sum_i W_i]
 = sum_i E[I_i V_i] + sum_{j != i} E[I_j I_i V_i]
 = B p mu + B(B-1) p^2 mu.

Therefore

E[Phi g]
 = K/B^2 [B p+B(B-1)p^2]mu
 = K[p^2+p(1-p)/B]mu.

The O(1/B) term comes from using the same token both to estimate frequency and to contribute its gradient. It is not caused by bias in the standalone estimator n/B of p.

For two microbatch sizes with equal token-weighted accumulation and the same fixed parameters,

E[G_(B1)]-E[G_(B2)]
 = K p(1-p)(1/B1-1/B2)mu.

With a fixed total count N of iid tokens, averaging N/B equal-sized, independently modulated microbatch gradients preserves the B-dependent expectation. A single global-count modulation instead has the formula with N in place of B. It still has a finite-N covariance term; it does not equal K p^2 mu exactly.

## Leave-one-out identity

For B>1 define G_LOO=K (n-1)/(B-1) g. When n=0, g is exactly zero, so the product is zero; numerically using max(n-1,0) is equivalent in exact arithmetic because the zero-count contribution vanishes.

(n-1) sum_i I_i V_i = sum_{j != i} I_j I_i V_i.

Thus E[G_LOO]=K p^2 mu. This is a vector-valued order-two U-statistic construction, not automatically a novel algorithm. A separate independent frequency-estimation sample would also remove the same-sample covariance under analogous independence.

Singleton counts n=1 are suppressed exactly. For small Bp, informative updates become rare, so unbiasedness does not establish lower variance, faster learning, or improved accuracy. At B=1 this estimator is undefined; no continuous implementation convention makes the unbiased pair estimator available from a single observation without more information.

For the illustrative constant V_i=mu case, the scalar coefficient is K n(n-1)/(B(B-1)), with n binomial(B,p). Its exact variance follows from

E[(n(n-1))^2] = (B)_4 p^4 + 4(B)_3 p^3 + 2(B)_2 p^2,

where (B)_r is a falling factorial, zero when r>B. Divide by [B(B-1)]^2 and subtract p^4, then multiply by K^2. This explicitly shows why unbiasedness alone is insufficient. This identity is analytical, not a reported numerical check.

## What is and is not partition invariant

For a fixed collection of N tokens with fixed routes and contributions, global count n_global and gradient g_global=N^-1 sum_i W_i give

G_global=K(n_global/N)g_global.

This quantity is exactly invariant to partitioning that collection into microbatches, provided accumulation uses token-count weights (important for unequal final microbatches), and one optimizer operation is applied only afterward. Per-microbatch modulation does not generally have this deterministic invariance.

Distinguish this from a random partition of a fixed finite collection. Conditional on a token routed to e and the global count n_global, its expected peer frequency in a uniformly random microbatch is (n_global-1)/(N-1). Consequently, the microbatch LOO estimator, averaged over random partitions, targets

K (n_global-1)/(N-1) g_global,

not K(n_global/N)g_global. Its iid unconditional target K p^2 mu and the exact finite-collection global empirical-frequency target are different. Do not claim LOO recreates the global-count gradient on each batch or each partition.

## Stationary points and optimizer interpretation

Since E[g]=p mu,

E[Phi g] = K[p+(1-p)/B] E[g].

For p>0 this is a positive scalar multiplication of that expert block's expected gradient. If each expert has disjoint parameters, routing is fixed for the comparison, there are no additional unscaled gradient terms, and the underlying expected block gradients are those of one objective, their common zero set is unchanged. The expected field is block preconditioned; it need not itself be the Euclidean gradient of a scalar objective.

Even when p varies with theta, the pointwise identity alone can preserve the zero set for disjoint blocks under the same assumptions. However, it does NOT imply identical trajectories, implicit bias, stochastic stationary distributions, or convergence rates. If expert-dependent contributions are summed into shared parameters, changing relative weights can change cancellation and stationary points. Unscaled auxiliary losses or weight decay can also move equilibria. Router-gradient treatment needs its own derivation rather than inheriting the expert-block result.

For Adam, clipping, momentum operations applied between microbatches, or finite learning-rate updates, the expected raw gradient is insufficient to derive the expected parameter update. The nonlinearity of optimizer states must be inspected. If the actual implementation has no same-sample frequency multiplication, this witness does not apply.

## Suggested claim wording

“At a fixed parameter state, same-microbatch frequency modulation introduces a finite-batch covariance term in the expected expert gradient. Consequently its effective expert-block scaling changes with microbatch size even when the total tokens per optimizer step are held fixed. Global-count modulation is exactly partition invariant for fixed token routes and contributions. A leave-one-out correction removes the covariance in the iid model but introduces sparse-update and variance tradeoffs.”

Avoid: “Smaller microbatches optimize a different loss,” “LOO restores the correct optimum,” “this proves a training failure,” or “the correction is novel.” Those require additional analysis/evidence and are not established here.


## 可重跑的有限代数诊断

```python
"""Exploratory exact-arithmetic check; no model training or benchmark claims."""
from fractions import Fraction as F
from itertools import product
import json

def modulation(routes, values, groups, k=2):
    out=[F(0) for _ in range(k)]
    n=len(routes)
    for group in groups:
        b=len(group)
        for e in range(k):
            count=sum(routes[i]==e for i in group)
            grad=sum((values[i] for i in group if routes[i]==e),F(0))/b
            out[e]+=F(b,n)*F(k*count,b)*grad
    return out

routes=[0,0,0,1]; values=[F(1)]*4
partitions={'full':[[0,1,2,3]],'pairs':[[0,1],[2,3]],'singletons':[[0],[1],[2],[3]]}
updates={name:modulation(routes,values,groups) for name,groups in partitions.items()}
assert updates['full']==[F(9,8),F(1,8)]
assert updates['pairs']==[F(5,4),F(1,4)]
assert updates['singletons']==[F(3,2),F(1,2)]
assert updates['pairs'][0]/updates['full'][0]!=updates['pairs'][1]/updates['full'][1]
checked=0
for b in range(1,9):
    for p in [F(1,10),F(1,2),F(9,10)]:
        exact=F(0); loo=F(0)
        for bits in product([0,1],repeat=b):
            n=sum(bits); prob=p**n*(1-p)**(b-n)
            exact+=prob*2*F(n,b)**2
            if b>1: loo+=prob*2*F(n*(n-1),b*(b-1))
        assert exact==2*(p*p+p*(1-p)/b)
        if b>1: assert loo==2*p*p
        checked+=1
print(json.dumps({'status':'pass','exact_expectation_cases':checked,
    'updates':{k:[str(x) for x in v] for k,v in updates.items()},
    'interpretation':'Finite algebra validation only; not Excitation code reproduction.'},indent=2))

```

## 实际诊断输出

```json
{
  "status": "pass",
  "exact_expectation_cases": 24,
  "updates": {
    "full": [
      "9/8",
      "1/8"
    ],
    "pairs": [
      "5/4",
      "1/4"
    ],
    "singletons": [
      "3/2",
      "1/2"
    ]
  },
  "interpretation": "Finite algebra validation only; not Excitation code reproduction."
}

```


---

# 继续执行：累计缓冲负载均衡的隐式局部正则

2026-10-23。此节更新前一轮“仅保留更新尺度诊断”的判断。当前优先跟进 D3 的新子节点 D3-P：梯度累积中的 prefix 频数估计。Excitation 更新尺度问题保留为独立待验证诊断，不与 D3-P 合并成同一贡献。

## 新证据与范围修正

[ACL 2025 Demons in the Detail](https://aclanthology.org/2025.acl-long.249.pdf) 已研究全局负载均衡，并明确将顺序缓冲称为近似。这里不反驳其精确性定理，也不把“扩大均衡统计窗口”称为新方法。[Megatron #7213](https://github.com/NVIDIA/Megatron-LM/issues/7213) 已报告不等有效 token 数的分母错误；该修复明确保留 prefix 近似。根代理已通过 GitHub 读取 issue 全文，不能再把该分母错误申报为新发现。

根代理读取并保存了固定版本的实际路由代码：commit `72d23540d0358ae24a41ff289d1461b094a770fa`，`megatron/core/transformer/moe/router.py`，Git blob `8cb8936a785d4d02ed6e240a61912d3aa2b29cbf`；配套 `moe_utils.py` blob `739283ee8b72cce835f94d6109e76169edfa0112`。机制路径：`routing` → `compute_routing_scores_for_aux_loss` → `_apply_global_aux_loss` → `switch_load_balancing_loss_func` → `attach_and_log_load_balancing_loss`。读取了频数累计、当前批概率、loss 分母和附加损失缩放代码。没有执行完整原生 CUDA router，尚未审完分布式梯度 finalize 和 activation recomputation 全链。

这里的新问题是：**实现选择的累积长度，是否无意中改变了全局／局部均衡的混合比例；这一比例能否与硬件分批方式解耦？** 这是范围明确的候选研究问题，尚不构成方法原创性结论。

## 已证明的有限排列恒等式

固定参数、G 个等大微批次，f_i 是停止梯度的专家频数，J_i 是该批平均路由概率对参数的 Jacobian。微批次及其随机性绑定记录，均匀随机排列，梯度最后统一平均。令 g_local 为逐批频数与本批 Jacobian 的平均配对，g_global 为全局平均频数与全局平均 Jacobian 的配对。prefix 使用截至当前批次的累计平均频数，则

    E_perm[g_prefix] = (1-lambda_G) g_global + lambda_G g_local,
    lambda_G = (H_G-1)/(G-1), H_G = sum_{j=1}^G 1/j, G>1.

G=1 时直接使用三者相同，避免除零。G=2 时 lambda=1/2，G=4 为13/36，G=6 为29/100。通过同索引／异索引项展开证明，三个内部分析独立一致；另用 Fraction 穷举 G=1..7 共5,913个排列精确验证。完整证明附后。内部分析不冒充独立 Work 审查。

含义：随机顺序本身不能消除期望局部均衡分量；它不意味着一定损害模型性能。已有论文有主动加入局部均衡的效率动机。恒等式针对辅助梯度，不针对 Adam 期望更新或完整训练轨迹。

## 可解析的可实现路由反例

两专家，logits=(theta*x,0)，两个单样本微批次 x=(1,-1)，theta=log(4)，top-1，无随机性。全局频数为(1/2,1/2)。计入专家数2后，全局辅助损失恒为1，梯度0；micro 损失1.6，梯度0.32；prefix 两种顺序平均损失1.3，梯度0.16。非负随机配对估计平均梯度0。

进一步检查 x=(1,2,-1,-3) 和 (1,1,2,-1,-2,-3)，分别枚举24及360个不重复排列；均通过理论均值检查和有限差分梯度检查。固定顺序可有差异，不能把期望等式说成逐排列等式。此检查是 NumPy 可解析路由，不是原生 Megatron 复现或语言模型实验。

## 去偏控制与负面结果

随机配对估计属于已有统计思想：[Clémençon 等，JMLR 2016](https://jmlr.org/papers/v17/15-012.html) 研究 incomplete U-statistics 及 SGD 应用。以下是检验机制的控制，不宣称新统计原理。

1. 非负历史均值：第t批系数 a_t=f_t/G + 1[t>1] sum_{s<t}f_s/(t-1)，最终对 a_t·J_t 按1/G平均。对角部分精确，异索引部分均匀排列下无偏；状态O(E)。
2. 代数相减：(g_prefix-lambda*g_local)/(1-lambda)。无偏但可能放大方差、产生负系数。
3. 随机先后配对 HT 控制：a_t=(f_t+2 sum_{s<t}f_s)/G。每个不同索引配对仅在先后顺序匹配时出现，概率1/2；乘2校正后无偏。各次排列不等于全局值。该控制同样是经典抽样估计思路。
4. 真全局参考：先获得全部频数，再计算各批相应反向；实际需要保留计算图、重算前向或存储足够的 Jacobian 信息。不能把它的内存和重算成本当作零。

对64个预设seed(0..63)的解析softmax路由器，G=4,E=3,input_dim=2，随机正态输入和权重，枚举每组全部24种排列，共1,536个排列。没有训练、验证集选择或性能基准。均方误差相对于该固定数据和参数的真全局辅助梯度，单位为本fixture的参数坐标尺度。

| 估计 | 平均偏差平方 | 平均方差 | 平均MSE | MSE优于prefix／差于prefix |
|---|---:|---:|---:|---:|
| prefix |0.0263160|0.0358313|0.0621474|基准|
| 非负历史均值 |约0|0.0417164|0.0417164|50／14|
| 代数相减 |约0|0.0877834|0.0877834|14／48（另2组数值相等）|
| 先后配对HT |约0|0.0258519|0.0258519|58／6|

所有偏差—方差分解和均值断言通过。**无偏并不保证更低MSE；这里也没有保证任何无偏控制提高真实任务性能。** 未用该64组来声称方法胜出。若后续选择其中一个估计，必须在新的独立条件和原生训练中确认，不能重复把这些探索数据当确认集。

## 原生实验表与明确反证条件

以下尚未运行，不以 toy 数值代替：

| 行 | 目的 | 固定因素与对照 | 通过／反证标准 | 状态 |
|---|---|---|---|---|
| P0 | 解析推导与排列均值 | G1..7精确枚举；softmax梯度有限差分 | Fraction相等；浮点恒等式误差<1e-12 | 完成 |
| P1 | 原生辅助梯度语义 | 固定提交，单GPU，FP32，等token，禁fusion/jitter，top1；G2/4；固定输入/参数 | 所有排列均值对公式的误差不超过参考浮点累计误差；不匹配则先修映射 | 未运行 |
| P2 | 分母与prefix分离 | #7213修复作为现成对照；先等token再padding/不等token；每窗口reset | 不等token需重推加权式；不能把分母误差计为新机制 | 未运行 |
| P3 | 定向局部正则对照 | exact global、prefix、显式lambda混合、三种无偏控制、零辅助项；相同数据/更新/辅助系数 | 验证一步梯度；比较偏差、方差、clip比例和实际步长 | 未运行 |
| P4 | 现实效果 | 原生小型MoE benchmark；随机域混合与分域批；G2/4/16；固定总batch；同预算调学习率和辅助系数 | 最强已知修复或显式混合匹配结果则降级为机制论文／负结果；不许只比弱prefix | 未运行 |
| P5 | 留出确认 | P4选定协议后冻结；新seed和未参与选择的数据；报告全部失败 | 没有独立效果或代价过高则拒绝新方法主张 | 未运行 |

P1只需先验证代码语义，不训练LLM。P4前必须确定数据许可、确切小模型配置、基准原生scorer、训练与调参成本；目前这些未确定，因此不填写虚假的完整训练预算。P1建议上限15 GPU分钟，失败即记录；未提交任何作业。正式独立评审状态未完成，但这不妨碍本轮已进行的原文核查和探索性数学分析。

## 实际环境与证据状态

本次检测当前Python及primary runtime均没有torch；没有nvidia-smi或/dev/nvidia0、/dev/nvidiactl。没有已确认的远程执行目标。原生GPU模型检查未启动，不能称之为已完成全流程。已完成的是持续的原文/代码定位、数学证明、候选修复推导和反例/方差审计。

下一执行节点为P1，输入已明确为固定commit、辅助路由函数链和可解析fixture。继续工作的记录不依赖再次询问“是否继续”；也没有创建无人值守后台任务或假称本轮结束后自动训练。


## 附录：prefix完整数学审计

# Internal mathematical audit: cumulative-prefix router balancing

Date: 2026-10-23. Scope: independent internal algebra check for the integration owner, not a formal independent Work gate. Exact finite rational enumeration below is mathematical verification, not a model experiment or a novelty audit. No searches or recursive delegation.

## Verdict

The proposed permutation identity is correct for G>1:

E_perm[A] = lambda_G D + (1-lambda_G) T,
lambda_G = (H_G-1)/(G-1), H_G=sum_(j=1)^G 1/j.

It also holds componentwise for fixed Jacobian-valued q_i, hence for the stop-gradient router gradient under the assumptions below. It is not an identity for every ordering. For G=1, A=D=T exactly and the displayed lambda formula is undefined; choose any lambda by convention, preferably handle G=1 directly.

## Definitions and exact proof

Let f_i and q_i be fixed vectors in R^K, for i=1,...,G. Neither probability normalization nor iid sampling of the microbatches is needed for this finite-set combinatorial identity. Equal microbatch sizes justify using unweighted means as the implementation’s token averages. Let pi be a uniformly random permutation, independent of these fixed records, and

A(pi)=1/G sum_(j=1)^G [ (1/j) sum_(k=1)^j f_pi(k) ] dot q_pi(j).

D=(1/G)sum_i f_i dot q_i,
T=((1/G)sum_i f_i) dot ((1/G)sum_i q_i).

Introduce the average distinct-index cross pairing

C=1/[G(G-1)] sum_(i != l) f_i dot q_l.

For a fixed position j, the term with k=j has expectation D. Each of its j-1 earlier-position pairings has expectation C, since any ordered pair of distinct indices is equally likely. Thus

E[A] = (1/G) sum_j [D/j + (j-1)C/j]
     = (H_G/G)D + (1-H_G/G)C.

Expanding the product of means gives G^2 T = G D + G(G-1)C, so C=(G T-D)/(G-1). Substitution yields

coefficient(D) = H_G/G -(G-H_G)/[G(G-1)]
               = (H_G-1)/(G-1),
coefficient(T) = (G-H_G)/(G-1) = 1-lambda_G.

This proves the identity. For G>1, 0<lambda_G<1. Its asymptotic order is log(G)/G. The blend approaches the global product of means, but finite-G prefix averaging is not an unbiased estimator of that global product alone.

## Fixed-order counterexample compatible with top-1 routes

Use two experts, two equal microbatches, with constant router probabilities within each microbatch:

f_1=(1,0), q_1=(9/10,1/10);
f_2=(0,1), q_2=(2/5,3/5).

The f vectors agree with deterministic top-1 routing from their respective q vectors. Then

D=3/4; T=1/2; lambda_2=1/2.

For order (1,2), A=(9/10+1/2)/2=7/10.
For order (2,1), A=(3/5+1/2)/2=11/20.

Neither equals the permutation mean 5/8, while their mean is exactly 5/8=(D+T)/2. Thus a fixed curriculum, packing rule or correlated order cannot be replaced with the permutation-mean formula without justification. This also gives a concrete example in which the same token collection and identical routes have different prefix loss values under ordering.

## Gradient identity and its interpretation

At a fixed parameter state theta_0, let each f_i be a detached routing-frequency vector and q_i(theta) a differentiable router-probability vector. Set J_i=partial q_i/partial theta at theta_0. For the applied stop-gradient computation,

g_A(pi)=1/G sum_j [ (1/j)sum_(k<=j) f_pi(k) ]^T J_pi(j).

The proof uses only bilinearity, so replacing q_i by J_i gives

E_perm[g_A] = lambda_G g_D +(1-lambda_G)g_T,

g_D=(1/G)sum_i f_i^T J_i,
g_T=((1/G)sum_i f_i)^T ((1/G)sum_i J_i).

All averages and transposes are interpreted componentwise in parameter space. A constant expert-count multiplier or balance coefficient can multiply the whole identity.

This is an identity for the gradient actually applied under detachment, not a justification to differentiate through hard routing. If f(theta) is recomputed at each update, the resulting field need not be the gradient of one globally fixed scalar surrogate. If instead ordinary differentiation through smooth f were intended, the scalar permutation identity still differentiates when regularity permits, but the additional df/dtheta terms must appear on BOTH sides. Do not silently mix these two notions of derivative.

The identity describes gradients before clipping or adaptive optimization. It does not establish equality of expected Adam steps, training trajectories, stationary solutions or final model quality. A finite expectation over permutations poses no analytic interchange problem, but nonuniform, parameter-dependent permutation weights add their own derivative terms if those weights are differentiated.

## Required implementation conditions

1. Parameters remain fixed throughout the G accumulated microbatches, with a single optimizer update afterward. Per-microbatch updates invalidate the fixed-record argument.
2. Each microbatch's routes, probability vectors and Jacobians must be unchanged when moved to another position. The same token collection alone is insufficient if attention contexts, packing, capacity drops or other batch-coupled operations change.
3. For exact conditional reasoning with dropout, fix each microbatch's randomness to that microbatch across permutations, rather than fixing only a global RNG seed whose draws move between examples. Alternatively, prove suitable exchangeability and average over fresh randomness; this weaker argument should be labeled separately.
4. Prefix count means must actually equal j^-1 sum_(k<=j) f_pi(k). Unequal token counts, masked/padded-token denominator differences, expert capacity corrections and distributed all-reduce groups can change this formula. Re-derive the weighted case from the actual implementation.
5. The order distribution must be uniform over the fixed microbatch records for the given lambda. Random shuffling of individual tokens can change the microbatch records themselves and is not the same conditioning experiment. Fixed/native orders still have valid A values but no automatic permutation-mean equality.
6. Final accumulation uses the stated 1/G mean; extra distributed averaging, loss scaling and gradient accumulation divisors must be accounted for once.

## Exact rational enumeration receipt

A Python fractions.Fraction script exhaustively enumerated all permutations for G=1,...,7 using two-dimensional rational vectors. It asserted exact equality, with no floating-point tolerance. It also evaluated the two valid-routing fixed-order examples above. Exit code 0; tool-reported wall time 0.298458 seconds. This verifies finitely many examples and the implementation of the algebra; the proof above establishes the general identity.

Results:

| G | Permutations | Exact mean A | lambda used | Equality |
|---|---:|---|---|---|
| 1 | 1 | 8/11 | 1 (convention) | true |
| 2 | 2 | 177/308 | 1/2 | true |
| 3 | 6 | 1354/2079 | 5/12 | true |
| 4 | 24 | 59/99 | 13/36 | true |
| 5 | 120 | 2257/4125 | 77/240 | true |
| 6 | 720 | 3152/5775 | 29/100 | true |
| 7 | 5040 | 7979/15092 | 223/840 | true |

The enumeration generated f_i=((3i+1) mod 7)/7 and its complement, and q_i=((5i+2) mod 11)/11 and its complement, using i=0,...,G-1. These generic identity checks need not correspond to top-1 routing; the separate counterexample does. The exact permutation-sum algorithm was:

```python
from fractions import Fraction as F
from itertools import permutations
from math import factorial

def dot(a,b):
    return sum((x*y for x,y in zip(a,b)), F(0))

def mean(xs):
    return [sum((x[k] for x in xs), F(0))/len(xs)
            for k in range(len(xs[0]))]

for G in range(1,8):
    fs=[[F((i*3+1)%7,7), 1-F((i*3+1)%7,7)] for i in range(G)]
    qs=[[F((i*5+2)%11,11), 1-F((i*5+2)%11,11)] for i in range(G)]
    D=sum((dot(f,q) for f,q in zip(fs,qs)), F(0))/G
    T=dot(mean(fs), mean(qs))
    actual=F(0)
    for perm in permutations(range(G)):
        pref=[F(0),F(0)]
        acc=F(0)
        for j,i in enumerate(perm,1):
            pref=[x+y for x,y in zip(pref,fs[i])]
            acc+=dot([x/j for x in pref], qs[i])
        actual+=acc/G
    actual/=factorial(G)
    lam=(F(1) if G==1 else
         (sum((F(1,j) for j in range(1,G+1)), F(0))-1)/(G-1))
    assert actual==lam*D+(1-lam)*T
```

## Recommended claim

“For a fixed collection of equal-sized microbatches at fixed parameters, uniformly permuting a cumulative-prefix frequency estimator yields an expected detached balancing gradient equal to a known convex blend of microbatch-local and global balancing gradients. The blend weight depends on the accumulation length through a harmonic number. Fixed orders can differ, and the identity requires stable per-microbatch routes and Jacobians.”

Novelty, prevalence in actual implementations and performance consequences remain untested by this audit.


### fresh_prefix_router_witness.py

SHA256: bd2e736290ca8e0a2a69a640c5f50f6cbe09ddb096a36b91367e1ef899d52b8e

```python
"""Exploratory analytic witness, not training or native Megatron reproduction."""
import itertools,json,math
import numpy as np

def calc(xs, theta, mode):
    p=1/(1+np.exp(-theta*np.array(xs,dtype=float)))
    q=np.column_stack([p,1-p])
    f=np.column_stack([p>.5,p<.5]).astype(float) # fixed away from ties
    d=np.column_stack([np.array(xs)*p*(1-p),-np.array(xs)*p*(1-p)])
    G=len(xs)
    if mode=='global': w=np.tile(f.mean(0),(G,1))
    elif mode=='micro': w=f
    elif mode=='prefix': w=np.cumsum(f,axis=0)/np.arange(1,G+1)[:,None]
    elif mode=='pairwise':
        w=f/G
        for j in range(1,G): w[j]+=f[:j].mean(0)
    else: raise ValueError(mode)
    return float(2*np.sum(w*q)/G),float(2*np.sum(w*d)/G)

out={'scope':'analytic top-1 binary router only; no trained model; hard counts detached', 'cases':[]}
for xs in [(1,-1),(1,2,-1,-3),(1,1,2,-1,-2,-3)]:
    G=len(xs);theta=math.log(4)
    orders=list(set(itertools.permutations(xs)))
    pref=np.array([calc(x,theta,'prefix') for x in orders])
    pair=np.array([calc(x,theta,'pairwise') for x in orders])
    glob=np.array(calc(xs,theta,'global'));micro=np.array(calc(xs,theta,'micro'))
    lam=(sum(1/j for j in range(1,G+1))-1)/(G-1)
    predicted=(1-lam)*glob+lam*micro
    assert np.max(np.abs(pref.mean(0)-predicted))<1e-12
    assert np.max(np.abs(pair.mean(0)-glob))<1e-12
    for mode in ['global','micro','prefix','pairwise']:
        h=1e-5
        fd=(calc(xs,theta+h,mode)[0]-calc(xs,theta-h,mode)[0])/(2*h)
        assert abs(fd-calc(xs,theta,mode)[1])<1e-9
    out['cases'].append({'xs':xs,'permutations':len(orders),'lambda':lam,
       'global_loss_gradient':glob.tolist(),'micro_loss_gradient':micro.tolist(),
       'prefix_mean_loss_gradient':pref.mean(0).tolist(),
       'prefix_gradient_range':[float(pref[:,1].min()),float(pref[:,1].max())],
       'pairwise_mean_loss_gradient':pair.mean(0).tolist(),
       'prefix_gradient_variance':float(pref[:,1].var()),
       'pairwise_gradient_variance':float(pair[:,1].var())})
print(json.dumps(out,indent=2))

```


### fresh_prefix_router_witness.json

SHA256: 9e0ddfa950a8370d455cfa406efcead89a9f91199a5dea37cca06e963936b120

```json
{
  "scope": "analytic top-1 binary router only; no trained model; hard counts detached",
  "cases": [
    {
      "xs": [
        1,
        -1
      ],
      "permutations": 2,
      "lambda": 0.5,
      "global_loss_gradient": [
        1.0,
        0.0
      ],
      "micro_loss_gradient": [
        1.6,
        0.32
      ],
      "prefix_mean_loss_gradient": [
        1.3000000000000003,
        0.16
      ],
      "prefix_gradient_range": [
        0.15999999999999998,
        0.16000000000000003
      ],
      "pairwise_mean_loss_gradient": [
        1.0,
        0.0
      ],
      "prefix_gradient_variance": 7.703719777548943e-34,
      "pairwise_gradient_variance": 7.703719777548943e-34
    },
    {
      "xs": [
        1,
        2,
        -1,
        -3
      ],
      "permutations": 24,
      "lambda": 0.36111111111111116,
      "global_loss_gradient": [
        1.0,
        0.0
      ],
      "micro_loss_gradient": [
        1.76289592760181,
        0.23808521529043225
      ],
      "prefix_mean_loss_gradient": [
        1.275490196078431,
        0.0859752166326561
      ],
      "prefix_gradient_range": [
        0.041176334090893586,
        0.12778935730226654
      ],
      "pairwise_mean_loss_gradient": [
        0.9999999999999997,
        -4.336808689942018e-18
      ],
      "prefix_gradient_variance": 0.0005276367388842755,
      "pairwise_gradient_variance": 0.0014434322084018187
    },
    {
      "xs": [
        1,
        1,
        2,
        -1,
        -2,
        -3
      ],
      "permutations": 360,
      "lambda": 0.29000000000000004,
      "global_loss_gradient": [
        1.0,
        0.0
      ],
      "micro_loss_gradient": [
        1.755656108597285,
        0.24896569139316013
      ],
      "prefix_mean_loss_gradient": [
        1.2191402714932131,
        0.07220005050401648
      ],
      "prefix_gradient_range": [
        0.03483266563383678,
        0.12861980712925614
      ],
      "pairwise_mean_loss_gradient": [
        1.0000000000000004,
        -2.4093381610788987e-18
      ],
      "prefix_gradient_variance": 0.00039200375996577134,
      "pairwise_gradient_variance": 0.001031999024856781
    }
  ]
}

```


### fresh_prefix_estimator_audit.py

SHA256: 65ad9efa82b663a88be8384d1880c491b83650a5af05a7a94a210e9f10945144

```python
"""Finite-permutation estimator audit; no model training/native-framework execution."""
import itertools,json
import numpy as np
G,K,d=4,3,2
perms=list(itertools.permutations(range(G)))
rows=[]
for seed in range(64):
    rng=np.random.default_rng(seed)
    x=rng.normal(size=(G,d)); W=rng.normal(size=(K,d))
    z=x@W.T;z-=z.max(1,keepdims=True)
    p=np.exp(z);p/=p.sum(1,keepdims=True)
    f=np.eye(K)[p.argmax(1)]
    def grad(coef):
        dz=p*(coef-(coef*p).sum(1,keepdims=True))
        return K/G*dz.T@x
    glob=grad(np.tile(f.mean(0),(G,1)));micro=grad(f)
    lam=(sum(1/j for j in range(1,G+1))-1)/(G-1)
    results={name:[] for name in ['prefix','positive','subtract','pair_ht']}
    for perm in perms:
        pre=np.zeros_like(f);positive=np.zeros_like(f);ht=np.zeros_like(f)
        past=np.zeros(K)
        for j,i in enumerate(perm):
            pre[i]=(past+f[i])/(j+1)
            positive[i]=f[i]/G+(past/j if j else 0)
            ht[i]=(f[i]+2*past)/G
            past+=f[i]
        gp=grad(pre)
        results['prefix'].append(gp)
        results['positive'].append(grad(positive))
        results['subtract'].append((gp-lam*micro)/(1-lam))
        results['pair_ht'].append(grad(ht))
    stats={}
    for name, vals in results.items():
        vals=np.stack(vals);mean=vals.mean(0)
        bias=float(np.sum((mean-glob)**2));var=float(np.mean(np.sum((vals-mean)**2,axis=(1,2))))
        mse=float(np.mean(np.sum((vals-glob)**2,axis=(1,2))))
        assert abs(mse-bias-var)<1e-12
        if name!='prefix': assert bias<1e-25
        else: assert np.max(abs(mean-((1-lam)*glob+lam*micro)))<1e-12
        stats[name]={'bias_squared':bias,'variance':var,'mse':mse}
    rows.append({'seed':seed,'expert_counts':f.sum(0).tolist(),'stats':stats})
summary={}
for name in ['prefix','positive','subtract','pair_ht']:
    summary[name]={m:float(np.mean([r['stats'][name][m] for r in rows])) for m in ['bias_squared','variance','mse']}
    summary[name]['mse_better_than_prefix']=sum(r['stats'][name]['mse']<r['stats']['prefix']['mse']-1e-14 for r in rows)
    summary[name]['mse_worse_than_prefix']=sum(r['stats'][name]['mse']>r['stats']['prefix']['mse']+1e-14 for r in rows)
out={'scope':'64 seeded random analytic softmax fixtures, G4 K3 d2, all24 permutations; descriptive no benchmark inference', 'summary':summary,'rows':rows}
print(json.dumps(out,indent=2))

```


### fresh_prefix_estimator_audit.json

SHA256: 5014defccab89375d246dfcfb700e01f09f46d3e80c9e57f03af46d41f4d7043

```json
{
  "scope": "64 seeded random analytic softmax fixtures, G4 K3 d2, all24 permutations; descriptive no benchmark inference",
  "summary": {
    "prefix": {
      "bias_squared": 0.02631603352195731,
      "variance": 0.03583132601241598,
      "mse": 0.06214735953437329,
      "mse_better_than_prefix": 0,
      "mse_worse_than_prefix": 0
    },
    "positive": {
      "bias_squared": 7.704990424953222e-33,
      "variance": 0.04171640422409496,
      "mse": 0.04171640422409496,
      "mse_better_than_prefix": 50,
      "mse_worse_than_prefix": 14
    },
    "subtract": {
      "bias_squared": 6.118342450771114e-33,
      "variance": 0.08778336202663728,
      "mse": 0.08778336202663728,
      "mse_better_than_prefix": 14,
      "mse_worse_than_prefix": 48
    },
    "pair_ht": {
      "bias_squared": 4.258194444473402e-33,
      "variance": 0.025851874053425417,
      "mse": 0.02585187405342542,
      "mse_better_than_prefix": 58,
      "mse_worse_than_prefix": 6
    }
  },
  "rows": [
    {
      "seed": 0,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.02058554559820972,
          "variance": 0.02104645663134078,
          "mse": 0.0416320022295505
        },
        "positive": {
          "bias_squared": 4.4010508494786444e-34,
          "variance": 0.021333892447607753,
          "mse": 0.021333892447607753
        },
        "subtract": {
          "bias_squared": 1.2669007915422286e-33,
          "variance": 0.05156182947867232,
          "mse": 0.05156182947867233
        },
        "pair_ht": {
          "bias_squared": 3.0769740127124198e-34,
          "variance": 0.009032938463055532,
          "mse": 0.00903293846305553
        }
      }
    },
    {
      "seed": 1,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.036981323101296454,
          "variance": 0.03275099484823432,
          "mse": 0.06973231794953078
        },
        "positive": {
          "bias_squared": 7.019111867630043e-34,
          "variance": 0.030320984052634864,
          "mse": 0.030320984052634867
        },
        "subtract": {
          "bias_squared": 2.8445082498938042e-33,
          "variance": 0.08023684182100509,
          "mse": 0.08023684182100509
        },
        "pair_ht": {
          "bias_squared": 1.2413220344683356e-34,
          "variance": 0.018494104989838542,
          "mse": 0.018494104989838542
        }
      }
    },
    {
      "seed": 2,
      "expert_counts": [
        0.0,
        1.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.0186650458590865,
          "variance": 0.022808630898696242,
          "mse": 0.04147367675778273
        },
        "positive": {
          "bias_squared": 3.5746342398124205e-33,
          "variance": 0.06562526481674046,
          "mse": 0.06562526481674046
        },
        "subtract": {
          "bias_squared": 9.496113563682767e-34,
          "variance": 0.0558789898765791,
          "mse": 0.0558789898765791
        },
        "pair_ht": {
          "bias_squared": 1.9559852778226478e-32,
          "variance": 0.06160810290138654,
          "mse": 0.061608102901386554
        }
      }
    },
    {
      "seed": 3,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.10299340987727976,
          "variance": 0.16924463000188553,
          "mse": 0.2722380398791653
        },
        "positive": {
          "bias_squared": 2.903941244271379e-33,
          "variance": 0.16943710550087132,
          "mse": 0.16943710550087132
        },
        "subtract": {
          "bias_squared": 2.575931300617928e-33,
          "variance": 0.4146333468477197,
          "mse": 0.4146333468477197
        },
        "pair_ht": {
          "bias_squared": 6.226170398339361e-33,
          "variance": 0.07785122174922363,
          "mse": 0.07785122174922361
        }
      }
    },
    {
      "seed": 4,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.021496575177131296,
          "variance": 0.016620016509635935,
          "mse": 0.038116591686767225
        },
        "positive": {
          "bias_squared": 7.95767357710059e-33,
          "variance": 0.008964621345292747,
          "mse": 0.008964621345292747
        },
        "subtract": {
          "bias_squared": 8.207818774955573e-33,
          "variance": 0.040717469558578794,
          "mse": 0.04071746955857879
        },
        "pair_ht": {
          "bias_squared": 7.950150413255328e-33,
          "variance": 0.0022032502548582212,
          "mse": 0.0022032502548582217
        }
      }
    },
    {
      "seed": 5,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.02753542051069493,
          "variance": 0.014772196410995834,
          "mse": 0.042307616921690765
        },
        "positive": {
          "bias_squared": 3.629926555339224e-35,
          "variance": 0.009585979696205076,
          "mse": 0.009585979696205076
        },
        "subtract": {
          "bias_squared": 4.122693787203927e-34,
          "variance": 0.036190484969093765,
          "mse": 0.036190484969093765
        },
        "pair_ht": {
          "bias_squared": 1.8074401138243493e-34,
          "variance": 0.007544032756741273,
          "mse": 0.007544032756741274
        }
      }
    },
    {
      "seed": 6,
      "expert_counts": [
        3.0,
        0.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.05220110455640399,
          "variance": 0.04956889226454442,
          "mse": 0.10176999682094841
        },
        "positive": {
          "bias_squared": 3.235562306570556e-32,
          "variance": 0.08374704122809147,
          "mse": 0.08374704122809147
        },
        "subtract": {
          "bias_squared": 4.092601131822876e-33,
          "variance": 0.12143910089763625,
          "mse": 0.12143910089763625
        },
        "pair_ht": {
          "bias_squared": 3.851859888774472e-33,
          "variance": 0.020448838632716276,
          "mse": 0.020448838632716276
        }
      }
    },
    {
      "seed": 7,
      "expert_counts": [
        0.0,
        2.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.029049723494189793,
          "variance": 0.00906171194720914,
          "mse": 0.03811143544139894
        },
        "positive": {
          "bias_squared": 4.363435030252331e-34,
          "variance": 0.008646677594630144,
          "mse": 0.008646677594630144
        },
        "subtract": {
          "bias_squared": 2.5548664418511926e-33,
          "variance": 0.022200337776149427,
          "mse": 0.022200337776149427
        },
        "pair_ht": {
          "bias_squared": 1.399308475218851e-33,
          "variance": 0.004402875439056247,
          "mse": 0.004402875439056247
        }
      }
    },
    {
      "seed": 8,
      "expert_counts": [
        0.0,
        3.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.022736813815350934,
          "variance": 0.09904068058104554,
          "mse": 0.12177749439639647
        },
        "positive": {
          "bias_squared": 4.1214900809886847e-32,
          "variance": 0.11888232525547764,
          "mse": 0.11888232525547764
        },
        "subtract": {
          "bias_squared": 2.311115933264683e-32,
          "variance": 0.2426403063006333,
          "mse": 0.2426403063006333
        },
        "pair_ht": {
          "bias_squared": 9.62964972193618e-34,
          "variance": 0.05237318826039792,
          "mse": 0.05237318826039791
        }
      }
    },
    {
      "seed": 9,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.015286538279419299,
          "variance": 0.016996591271176874,
          "mse": 0.032283129550596174
        },
        "positive": {
          "bias_squared": 2.1215322043640645e-33,
          "variance": 0.009073059764493255,
          "mse": 0.009073059764493255
        },
        "subtract": {
          "bias_squared": 4.724546894824938e-34,
          "variance": 0.04164004213127643,
          "mse": 0.04164004213127643
        },
        "pair_ht": {
          "bias_squared": 9.870390964984584e-34,
          "variance": 0.004882116826422912,
          "mse": 0.004882116826422912
        }
      }
    },
    {
      "seed": 10,
      "expert_counts": [
        1.0,
        3.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.01858318639638768,
          "variance": 0.009765690180107997,
          "mse": 0.028348876576495662
        },
        "positive": {
          "bias_squared": 2.949080227342955e-33,
          "variance": 0.01701302827143092,
          "mse": 0.01701302827143092
        },
        "subtract": {
          "bias_squared": 8.498165879608678e-33,
          "variance": 0.02392501790816629,
          "mse": 0.02392501790816629
        },
        "pair_ht": {
          "bias_squared": 2.1787082495880606e-33,
          "variance": 0.013991848273486861,
          "mse": 0.013991848273486861
        }
      }
    },
    {
      "seed": 11,
      "expert_counts": [
        1.0,
        3.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.011230127280530706,
          "variance": 0.016049501630060223,
          "mse": 0.027279628910590926
        },
        "positive": {
          "bias_squared": 5.9824198897528514e-33,
          "variance": 0.051528067314202765,
          "mse": 0.051528067314202765
        },
        "subtract": {
          "bias_squared": 4.0564899453656155e-33,
          "variance": 0.039319762027519946,
          "mse": 0.039319762027519946
        },
        "pair_ht": {
          "bias_squared": 1.396299209680746e-33,
          "variance": 0.04003206310624533,
          "mse": 0.04003206310624533
        }
      }
    },
    {
      "seed": 12,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.07886888654153047,
          "variance": 0.06558929819897862,
          "mse": 0.14445818474050906
        },
        "positive": {
          "bias_squared": 9.03531977816043e-34,
          "variance": 0.04461520161474954,
          "mse": 0.04461520161474954
        },
        "subtract": {
          "bias_squared": 6.469356669637476e-33,
          "variance": 0.16068758122093818,
          "mse": 0.16068758122093818
        },
        "pair_ht": {
          "bias_squared": 1.2542994921014137e-33,
          "variance": 0.03623341106704015,
          "mse": 0.03623341106704015
        }
      }
    },
    {
      "seed": 13,
      "expert_counts": [
        0.0,
        4.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 6.41575412723998e-33,
          "variance": 6.41575412723998e-33,
          "mse": 0.0
        },
        "positive": {
          "bias_squared": 7.427168274597089e-32,
          "variance": 0.018822381751296552,
          "mse": 0.018822381751296552
        },
        "subtract": {
          "bias_squared": 6.379642940782719e-33,
          "variance": 3.334266216220402e-33,
          "mse": 3.0935249731719976e-33
        },
        "pair_ht": {
          "bias_squared": 1.5864847916889855e-32,
          "variance": 0.03137063625216092,
          "mse": 0.03137063625216092
        }
      }
    },
    {
      "seed": 14,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.008733343180850808,
          "variance": 0.024129087078255233,
          "mse": 0.03286243025910605
        },
        "positive": {
          "bias_squared": 2.2909745722473124e-33,
          "variance": 0.012674768039368728,
          "mse": 0.012674768039368728
        },
        "subtract": {
          "bias_squared": 3.178602846180699e-34,
          "variance": 0.05911398270967635,
          "mse": 0.05911398270967635
        },
        "pair_ht": {
          "bias_squared": 6.378223531354101e-33,
          "variance": 0.009081372851511366,
          "mse": 0.009081372851511366
        }
      }
    },
    {
      "seed": 15,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.03677771886352974,
          "variance": 0.028585466424527323,
          "mse": 0.06536318528805705
        },
        "positive": {
          "bias_squared": 8.42030113381021e-34,
          "variance": 0.025989762485498197,
          "mse": 0.025989762485498197
        },
        "subtract": {
          "bias_squared": 5.420439550511732e-33,
          "variance": 0.07003169090016524,
          "mse": 0.07003169090016526
        },
        "pair_ht": {
          "bias_squared": 1.7453740121009325e-34,
          "variance": 0.015020412599577268,
          "mse": 0.015020412599577268
        }
      }
    },
    {
      "seed": 16,
      "expert_counts": [
        0.0,
        2.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.030771157416725908,
          "variance": 0.043785261855701,
          "mse": 0.07455641927242691
        },
        "positive": {
          "bias_squared": 1.7935222607106134e-33,
          "variance": 0.051973736096791956,
          "mse": 0.051973736096791956
        },
        "subtract": {
          "bias_squared": 1.7935222607106134e-33,
          "variance": 0.10726975305290831,
          "mse": 0.10726975305290831
        },
        "pair_ht": {
          "bias_squared": 6.367605878630299e-33,
          "variance": 0.02881761695524786,
          "mse": 0.02881761695524786
        }
      }
    },
    {
      "seed": 17,
      "expert_counts": [
        2.0,
        2.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.01552268958107979,
          "variance": 0.06983981960497321,
          "mse": 0.085362509186053
        },
        "positive": {
          "bias_squared": 1.8898187579299752e-33,
          "variance": 0.0798273814820361,
          "mse": 0.0798273814820361
        },
        "subtract": {
          "bias_squared": 1.552781017662209e-33,
          "variance": 0.17110095691501948,
          "mse": 0.17110095691501948
        },
        "pair_ht": {
          "bias_squared": 1.339725017564371e-32,
          "variance": 0.04286567505941361,
          "mse": 0.04286567505941361
        }
      }
    },
    {
      "seed": 18,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.00843907979089242,
          "variance": 0.007352191055687769,
          "mse": 0.015791270846580188
        },
        "positive": {
          "bias_squared": 2.371301244026784e-33,
          "variance": 0.008376206518841836,
          "mse": 0.008376206518841836
        },
        "subtract": {
          "bias_squared": 1.023150282955719e-33,
          "variance": 0.018012173172346598,
          "mse": 0.018012173172346598
        },
        "pair_ht": {
          "bias_squared": 1.2157432773944426e-33,
          "variance": 0.004971118383307184,
          "mse": 0.004971118383307184
        }
      }
    },
    {
      "seed": 19,
      "expert_counts": [
        0.0,
        1.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.019221112573357166,
          "variance": 0.00910395113236207,
          "mse": 0.028325063705719213
        },
        "positive": {
          "bias_squared": 4.8629731095777705e-33,
          "variance": 0.010924384646134563,
          "mse": 0.010924384646134563
        },
        "subtract": {
          "bias_squared": 6.018531076210112e-33,
          "variance": 0.022303819787412565,
          "mse": 0.022303819787412565
        },
        "pair_ht": {
          "bias_squared": 1.5888922041194696e-33,
          "variance": 0.004110038368223336,
          "mse": 0.004110038368223336
        }
      }
    },
    {
      "seed": 20,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.037272813526835806,
          "variance": 0.029000792907850282,
          "mse": 0.06627360643468609
        },
        "positive": {
          "bias_squared": 1.4865771758238977e-33,
          "variance": 0.02126527429836229,
          "mse": 0.02126527429836229
        },
        "subtract": {
          "bias_squared": 4.312277516104545e-33,
          "variance": 0.07104920152849521,
          "mse": 0.07104920152849521
        },
        "pair_ht": {
          "bias_squared": 6.680569494593224e-34,
          "variance": 0.012754299179557227,
          "mse": 0.012754299179557229
        }
      }
    },
    {
      "seed": 21,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.04238169809949876,
          "variance": 0.04334080676331228,
          "mse": 0.08572250486281104
        },
        "positive": {
          "bias_squared": 4.068527007518036e-33,
          "variance": 0.048479996373272,
          "mse": 0.048479996373272
        },
        "subtract": {
          "bias_squared": 1.6298182154376983e-32,
          "variance": 0.1061808800855439,
          "mse": 0.1061808800855439
        },
        "pair_ht": {
          "bias_squared": 2.046300565911438e-33,
          "variance": 0.022989082802891248,
          "mse": 0.022989082802891248
        }
      }
    },
    {
      "seed": 22,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.02639415813187629,
          "variance": 0.04618310624170199,
          "mse": 0.0725772643735783
        },
        "positive": {
          "bias_squared": 2.4555606790937257e-33,
          "variance": 0.06227867650580724,
          "mse": 0.06227867650580724
        },
        "subtract": {
          "bias_squared": 1.829633447167874e-33,
          "variance": 0.11314424515925481,
          "mse": 0.11314424515925481
        },
        "pair_ht": {
          "bias_squared": 1.1675950287847617e-33,
          "variance": 0.031632536754746164,
          "mse": 0.031632536754746164
        }
      }
    },
    {
      "seed": 23,
      "expert_counts": [
        2.0,
        2.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.023115857096293446,
          "variance": 0.014309571477143864,
          "mse": 0.037425428573437315
        },
        "positive": {
          "bias_squared": 1.9231087579452624e-33,
          "variance": 0.015394756178509666,
          "mse": 0.015394756178509666
        },
        "subtract": {
          "bias_squared": 9.064660117156955e-33,
          "variance": 0.0350570976075207,
          "mse": 0.0350570976075207
        },
        "pair_ht": {
          "bias_squared": 1.1151209609640548e-33,
          "variance": 0.00827020702702198,
          "mse": 0.00827020702702198
        }
      }
    },
    {
      "seed": 24,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.040510972947938574,
          "variance": 0.033282918035060734,
          "mse": 0.07379389098299932
        },
        "positive": {
          "bias_squared": 1.2917272322315953e-33,
          "variance": 0.041270970303935596,
          "mse": 0.041270970303935596
        },
        "subtract": {
          "bias_squared": 4.49057649923727e-33,
          "variance": 0.08154000335243612,
          "mse": 0.08154000335243612
        },
        "pair_ht": {
          "bias_squared": 4.81482486096809e-34,
          "variance": 0.01763692522941326,
          "mse": 0.01763692522941326
        }
      }
    },
    {
      "seed": 25,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.029190564039035357,
          "variance": 0.03219754495140992,
          "mse": 0.06138810899044527
        },
        "positive": {
          "bias_squared": 8.413835914880687e-34,
          "variance": 0.018929196682020002,
          "mse": 0.018929196682020002
        },
        "subtract": {
          "bias_squared": 6.293702548794101e-33,
          "variance": 0.07888094188473962,
          "mse": 0.07888094188473961
        },
        "pair_ht": {
          "bias_squared": 2.9739066680323216e-33,
          "variance": 0.016748783668341306,
          "mse": 0.016748783668341302
        }
      }
    },
    {
      "seed": 26,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.08703458118545108,
          "variance": 0.1343981859619023,
          "mse": 0.22143276714735338
        },
        "positive": {
          "bias_squared": 1.3601880232234853e-33,
          "variance": 0.07953324402390723,
          "mse": 0.07953324402390723
        },
        "subtract": {
          "bias_squared": 6.41575412723998e-33,
          "variance": 0.32926285256450927,
          "mse": 0.32926285256450927
        },
        "pair_ht": {
          "bias_squared": 2.6963019221421302e-33,
          "variance": 0.07342057664815634,
          "mse": 0.07342057664815634
        }
      }
    },
    {
      "seed": 27,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.038029192437885925,
          "variance": 0.09184532303782961,
          "mse": 0.12987451547571555
        },
        "positive": {
          "bias_squared": 4.1514698889120563e-33,
          "variance": 0.07610481244596616,
          "mse": 0.07610481244596617
        },
        "subtract": {
          "bias_squared": 1.0583586897515482e-32,
          "variance": 0.22501236041025938,
          "mse": 0.2250123604102594
        },
        "pair_ht": {
          "bias_squared": 1.5234406786656846e-33,
          "variance": 0.05157669980621696,
          "mse": 0.05157669980621695
        }
      }
    },
    {
      "seed": 28,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.04113051290304297,
          "variance": 0.028382569228268595,
          "mse": 0.06951308213131156
        },
        "positive": {
          "bias_squared": 1.4564845204428471e-33,
          "variance": 0.02628016192884498,
          "mse": 0.02628016192884498
        },
        "subtract": {
          "bias_squared": 4.887047233882611e-33,
          "variance": 0.06953461194676012,
          "mse": 0.06953461194676012
        },
        "pair_ht": {
          "bias_squared": 4.574083617919685e-34,
          "variance": 0.014044127542608168,
          "mse": 0.014044127542608165
        }
      }
    },
    {
      "seed": 29,
      "expert_counts": [
        1.0,
        0.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.0018036391328827288,
          "variance": 0.0009368079220090057,
          "mse": 0.002740447054891735
        },
        "positive": {
          "bias_squared": 1.233798870623073e-34,
          "variance": 0.002780812608781881,
          "mse": 0.00278081260878188
        },
        "subtract": {
          "bias_squared": 4.724546894824938e-34,
          "variance": 0.002295090863749852,
          "mse": 0.002295090863749852
        },
        "pair_ht": {
          "bias_squared": 4.363435030252331e-34,
          "variance": 0.00235846603784829,
          "mse": 0.002358466037848289
        }
      }
    },
    {
      "seed": 30,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.03659217347820375,
          "variance": 0.056315049580759835,
          "mse": 0.09290722305896361
        },
        "positive": {
          "bias_squared": 1.6562997521730228e-32,
          "variance": 0.11762621315765635,
          "mse": 0.11762621315765635
        },
        "subtract": {
          "bias_squared": 1.723707300226576e-32,
          "variance": 0.1379665486893474,
          "mse": 0.13796654868934738
        },
        "pair_ht": {
          "bias_squared": 7.559275031719901e-33,
          "variance": 0.07032508398231962,
          "mse": 0.07032508398231962
        }
      }
    },
    {
      "seed": 31,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.01607013851988204,
          "variance": 0.018960825383915917,
          "mse": 0.03503096390379796
        },
        "positive": {
          "bias_squared": 2.6199418091127144e-34,
          "variance": 0.013849617064339579,
          "mse": 0.013849617064339579
        },
        "subtract": {
          "bias_squared": 1.6236868369038093e-33,
          "variance": 0.04645223005208891,
          "mse": 0.04645223005208891
        },
        "pair_ht": {
          "bias_squared": 5.478744070312518e-34,
          "variance": 0.008130821090961656,
          "mse": 0.008130821090961655
        }
      }
    },
    {
      "seed": 32,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.005665276602097844,
          "variance": 0.01483589364955358,
          "mse": 0.020501170251651425
        },
        "positive": {
          "bias_squared": 9.319695371511358e-33,
          "variance": 0.01235642677782469,
          "mse": 0.012356426777824692
        },
        "subtract": {
          "bias_squared": 2.9046935606559053e-33,
          "variance": 0.03634653718302731,
          "mse": 0.03634653718302731
        },
        "pair_ht": {
          "bias_squared": 4.900777007900215e-33,
          "variance": 0.007984999535702312,
          "mse": 0.00798499953570231
        }
      }
    },
    {
      "seed": 33,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.008413354176275232,
          "variance": 0.011066102247550183,
          "mse": 0.01947945642382541
        },
        "positive": {
          "bias_squared": 4.997261584215709e-34,
          "variance": 0.011066038253640153,
          "mse": 0.011066038253640156
        },
        "subtract": {
          "bias_squared": 1.5764907387182944e-33,
          "variance": 0.02711090456110593,
          "mse": 0.02711090456110593
        },
        "pair_ht": {
          "bias_squared": 9.396901840473366e-34,
          "variance": 0.006411926122322856,
          "mse": 0.006411926122322855
        }
      }
    },
    {
      "seed": 34,
      "expert_counts": [
        0.0,
        3.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.0152872816205828,
          "variance": 0.02103086090472256,
          "mse": 0.03631814252530537
        },
        "positive": {
          "bias_squared": 3.286117967610721e-33,
          "variance": 0.035134341534512364,
          "mse": 0.035134341534512364
        },
        "subtract": {
          "bias_squared": 3.430562713439764e-33,
          "variance": 0.051523621422533916,
          "mse": 0.051523621422533916
        },
        "pair_ht": {
          "bias_squared": 8.937518648172016e-34,
          "variance": 0.027419429431892545,
          "mse": 0.027419429431892545
        }
      }
    },
    {
      "seed": 35,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.01758685840625545,
          "variance": 0.0410419563333398,
          "mse": 0.05862881473959523
        },
        "positive": {
          "bias_squared": 7.402793223738438e-34,
          "variance": 0.024312857557524603,
          "mse": 0.024312857557524603
        },
        "subtract": {
          "bias_squared": 2.6857694927587625e-33,
          "variance": 0.10054891381476065,
          "mse": 0.10054891381476065
        },
        "pair_ht": {
          "bias_squared": 1.6626192098030435e-34,
          "variance": 0.01546161956662274,
          "mse": 0.01546161956662274
        }
      }
    },
    {
      "seed": 36,
      "expert_counts": [
        0.0,
        2.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.020911775506159483,
          "variance": 0.006349750336581754,
          "mse": 0.027261525842741233
        },
        "positive": {
          "bias_squared": 1.2518544638517033e-33,
          "variance": 0.009571706518293551,
          "mse": 0.009571706518293551
        },
        "subtract": {
          "bias_squared": 6.704643618898065e-33,
          "variance": 0.015556288159187059,
          "mse": 0.015556288159187059
        },
        "pair_ht": {
          "bias_squared": 1.4956049724382128e-33,
          "variance": 0.0058979804771765775,
          "mse": 0.005897980477176579
        }
      }
    },
    {
      "seed": 37,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.01000988860867702,
          "variance": 0.02648566442379502,
          "mse": 0.03649555303247204
        },
        "positive": {
          "bias_squared": 4.702964818543841e-33,
          "variance": 0.014101487260578886,
          "mse": 0.014101487260578882
        },
        "subtract": {
          "bias_squared": 9.233605103993011e-33,
          "variance": 0.0648873744673693,
          "mse": 0.0648873744673693
        },
        "pair_ht": {
          "bias_squared": 7.840576707343428e-34,
          "variance": 0.010384583084578307,
          "mse": 0.010384583084578307
        }
      }
    },
    {
      "seed": 38,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.02540819026084542,
          "variance": 0.06591334315919066,
          "mse": 0.09132153342003609
        },
        "positive": {
          "bias_squared": 1.9891997523258947e-32,
          "variance": 0.09986767486186769,
          "mse": 0.09986767486186769
        },
        "subtract": {
          "bias_squared": 1.801045424555876e-32,
          "variance": 0.16148146074538963,
          "mse": 0.16148146074538963
        },
        "pair_ht": {
          "bias_squared": 5.212047911997957e-33,
          "variance": 0.057463273590006976,
          "mse": 0.05746327359000699
        }
      }
    },
    {
      "seed": 39,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.018434653526047885,
          "variance": 0.03023630487811239,
          "mse": 0.04867095840416027
        },
        "positive": {
          "bias_squared": 5.53528534858707e-34,
          "variance": 0.042770132866282756,
          "mse": 0.042770132866282756
        },
        "subtract": {
          "bias_squared": 8.754717521675642e-33,
          "variance": 0.07407608907756835,
          "mse": 0.07407608907756835
        },
        "pair_ht": {
          "bias_squared": 3.174963221796966e-33,
          "variance": 0.02387799674898099,
          "mse": 0.02387799674898099
        }
      }
    },
    {
      "seed": 40,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.026225488051475544,
          "variance": 0.04897145295261557,
          "mse": 0.07519694100409112
        },
        "positive": {
          "bias_squared": 2.8172932046835666e-32,
          "variance": 0.055591091080834605,
          "mse": 0.05559109108083462
        },
        "subtract": {
          "bias_squared": 5.807882488542758e-34,
          "variance": 0.11997543105215462,
          "mse": 0.11997543105215462
        },
        "pair_ht": {
          "bias_squared": 1.9770874585350218e-33,
          "variance": 0.04837552235972336,
          "mse": 0.04837552235972336
        }
      }
    },
    {
      "seed": 41,
      "expert_counts": [
        2.0,
        2.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.010946067992338753,
          "variance": 0.05442227938936837,
          "mse": 0.06536834738170712
        },
        "positive": {
          "bias_squared": 9.208352546601471e-34,
          "variance": 0.0681962035914762,
          "mse": 0.0681962035914762
        },
        "subtract": {
          "bias_squared": 5.1766890419252226e-33,
          "variance": 0.13332944062121252,
          "mse": 0.13332944062121252
        },
        "pair_ht": {
          "bias_squared": 1.9199114133110257e-33,
          "variance": 0.03925923895199241,
          "mse": 0.03925923895199242
        }
      }
    },
    {
      "seed": 42,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.013148899077220411,
          "variance": 0.010428159184899704,
          "mse": 0.023577058262120115
        },
        "positive": {
          "bias_squared": 1.0383658818327627e-32,
          "variance": 0.013251562999595387,
          "mse": 0.013251562999595387
        },
        "subtract": {
          "bias_squared": 5.123274578623858e-34,
          "variance": 0.025548004354688115,
          "mse": 0.025548004354688115
        },
        "pair_ht": {
          "bias_squared": 8.65333113391722e-33,
          "variance": 0.007726489998255588,
          "mse": 0.007726489998255588
        }
      }
    },
    {
      "seed": 43,
      "expert_counts": [
        3.0,
        0.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.015467007478826771,
          "variance": 0.015147642778496012,
          "mse": 0.030614650257322778
        },
        "positive": {
          "bias_squared": 8.696777405123612e-34,
          "variance": 0.025209159531754854,
          "mse": 0.025209159531754857
        },
        "subtract": {
          "bias_squared": 2.1787082495880606e-33,
          "variance": 0.03711029308304505,
          "mse": 0.03711029308304505
        },
        "pair_ht": {
          "bias_squared": 6.2592723192585165e-34,
          "variance": 0.017134509530833484,
          "mse": 0.017134509530833484
        }
      }
    },
    {
      "seed": 44,
      "expert_counts": [
        1.0,
        3.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.036855741127410635,
          "variance": 0.018240064500901283,
          "mse": 0.0550958056283119
        },
        "positive": {
          "bias_squared": 4.333342374871281e-34,
          "variance": 0.04786435003876536,
          "mse": 0.04786435003876536
        },
        "subtract": {
          "bias_squared": 1.1940765655200862e-32,
          "variance": 0.04468643401355022,
          "mse": 0.04468643401355022
        },
        "pair_ht": {
          "bias_squared": 5.200010849845537e-33,
          "variance": 0.021283901427023206,
          "mse": 0.021283901427023206
        }
      }
    },
    {
      "seed": 45,
      "expert_counts": [
        3.0,
        0.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.017314251940964503,
          "variance": 0.0028943433465319995,
          "mse": 0.020208595287496522
        },
        "positive": {
          "bias_squared": 3.484729493125655e-33,
          "variance": 0.014308660263059339,
          "mse": 0.01430866026305934
        },
        "subtract": {
          "bias_squared": 1.1495394355561314e-33,
          "variance": 0.0070908676315793425,
          "mse": 0.007090867631579342
        },
        "pair_ht": {
          "bias_squared": 2.8287096058187527e-34,
          "variance": 0.008970979362037118,
          "mse": 0.008970979362037118
        }
      }
    },
    {
      "seed": 46,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.027299359721663446,
          "variance": 0.013805244015785359,
          "mse": 0.041104603737448814
        },
        "positive": {
          "bias_squared": 1.781485198558193e-33,
          "variance": 0.013588649784637696,
          "mse": 0.013588649784637695
        },
        "subtract": {
          "bias_squared": 6.2592723192585165e-34,
          "variance": 0.03382154299519438,
          "mse": 0.03382154299519438
        },
        "pair_ht": {
          "bias_squared": 4.333342374871281e-34,
          "variance": 0.0068261045394007805,
          "mse": 0.0068261045394007805
        }
      }
    },
    {
      "seed": 47,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.004284921705363054,
          "variance": 0.0418944121465005,
          "mse": 0.04617933385186355
        },
        "positive": {
          "bias_squared": 6.355568816477878e-33,
          "variance": 0.048975124975246344,
          "mse": 0.048975124975246344
        },
        "subtract": {
          "bias_squared": 6.355568816477878e-33,
          "variance": 0.1026373499846213,
          "mse": 0.1026373499846213
        },
        "pair_ht": {
          "bias_squared": 4.8148248609680896e-33,
          "variance": 0.026374947812666652,
          "mse": 0.026374947812666652
        }
      }
    },
    {
      "seed": 48,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.06165111592798625,
          "variance": 0.029336075429333825,
          "mse": 0.0909871913573201
        },
        "positive": {
          "bias_squared": 3.0167887019503187e-34,
          "variance": 0.0242703933961352,
          "mse": 0.024270393396135195
        },
        "subtract": {
          "bias_squared": 4.405564747785802e-33,
          "variance": 0.0718706120159105,
          "mse": 0.0718706120159105
        },
        "pair_ht": {
          "bias_squared": 5.446770623970151e-34,
          "variance": 0.009877089396536932,
          "mse": 0.009877089396536932
        }
      }
    },
    {
      "seed": 49,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.0017672017193323913,
          "variance": 0.001935819026728608,
          "mse": 0.003703020746061001
        },
        "positive": {
          "bias_squared": 3.673184747449484e-34,
          "variance": 0.0010953547341159828,
          "mse": 0.0010953547341159828
        },
        "subtract": {
          "bias_squared": 1.3222430655789419e-33,
          "variance": 0.004742573645822828,
          "mse": 0.004742573645822828
        },
        "pair_ht": {
          "bias_squared": 2.219756512318775e-33,
          "variance": 0.0003508818394975192,
          "mse": 0.0003508818394975192
        }
      }
    },
    {
      "seed": 50,
      "expert_counts": [
        4.0,
        0.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 2.253338034933066e-32,
          "variance": 2.253338034933066e-32,
          "mse": 0.0
        },
        "positive": {
          "bias_squared": 3.42815530100928e-32,
          "variance": 0.03796084504439284,
          "mse": 0.03796084504439282
        },
        "subtract": {
          "bias_squared": 4.237045877651919e-33,
          "variance": 3.274080905458301e-33,
          "mse": 9.62964972193618e-34
        },
        "pair_ht": {
          "bias_squared": 4.044452883213195e-33,
          "variance": 0.06326807507398806,
          "mse": 0.06326807507398806
        }
      }
    },
    {
      "seed": 51,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.008212766373047012,
          "variance": 0.010548139497018572,
          "mse": 0.01876090587006559
        },
        "positive": {
          "bias_squared": 1.0239025993402453e-33,
          "variance": 0.0048322111112986494,
          "mse": 0.0048322111112986494
        },
        "subtract": {
          "bias_squared": 1.0775051417377416e-33,
          "variance": 0.0258419447790852,
          "mse": 0.0258419447790852
        },
        "pair_ht": {
          "bias_squared": 1.601681582656416e-33,
          "variance": 0.0011354417110084967,
          "mse": 0.0011354417110084967
        }
      }
    },
    {
      "seed": 52,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.015380541968262117,
          "variance": 0.012888550208766716,
          "mse": 0.02826909217702883
        },
        "positive": {
          "bias_squared": 6.394689268473244e-35,
          "variance": 0.010928228990667685,
          "mse": 0.010928228990667685
        },
        "subtract": {
          "bias_squared": 9.00522712277938e-34,
          "variance": 0.03157572981202583,
          "mse": 0.03157572981202583
        },
        "pair_ht": {
          "bias_squared": 9.930576275746685e-35,
          "variance": 0.007703426970183038,
          "mse": 0.007703426970183037
        }
      }
    },
    {
      "seed": 53,
      "expert_counts": [
        2.0,
        1.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.032769352961747794,
          "variance": 0.03754908395623215,
          "mse": 0.07031843691797995
        },
        "positive": {
          "bias_squared": 1.2638915260041235e-34,
          "variance": 0.04306168811971384,
          "mse": 0.04306168811971384
        },
        "subtract": {
          "bias_squared": 3.442599775592184e-33,
          "variance": 0.09199170663001299,
          "mse": 0.09199170663001299
        },
        "pair_ht": {
          "bias_squared": 9.059770060657534e-34,
          "variance": 0.019268965120340802,
          "mse": 0.019268965120340806
        }
      }
    },
    {
      "seed": 54,
      "expert_counts": [
        1.0,
        0.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.017898731006917155,
          "variance": 0.038507292543039286,
          "mse": 0.05640602354995645
        },
        "positive": {
          "bias_squared": 4.2851941262616e-33,
          "variance": 0.057420735801423185,
          "mse": 0.05742073580142318
        },
        "subtract": {
          "bias_squared": 9.67779797054586e-33,
          "variance": 0.09433922709977112,
          "mse": 0.09433922709977112
        },
        "pair_ht": {
          "bias_squared": 1.5888922041194696e-33,
          "variance": 0.029815606124091423,
          "mse": 0.029815606124091426
        }
      }
    },
    {
      "seed": 55,
      "expert_counts": [
        1.0,
        0.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.015623913095438141,
          "variance": 0.018713540206851023,
          "mse": 0.034337453302289156
        },
        "positive": {
          "bias_squared": 8.044619310632749e-32,
          "variance": 0.05422116636208887,
          "mse": 0.05422116636208887
        },
        "subtract": {
          "bias_squared": 6.523796164012758e-32,
          "variance": 0.045846404741169994,
          "mse": 0.04584640474117
        },
        "pair_ht": {
          "bias_squared": 5.107522954322839e-32,
          "variance": 0.04469295136922871,
          "mse": 0.04469295136922871
        }
      }
    },
    {
      "seed": 56,
      "expert_counts": [
        3.0,
        1.0,
        0.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.020496721698900648,
          "variance": 0.10330730417525691,
          "mse": 0.12380402587415762
        },
        "positive": {
          "bias_squared": 1.444447458290427e-32,
          "variance": 0.1354297953673008,
          "mse": 0.1354297953673008
        },
        "subtract": {
          "bias_squared": 6.018531076210112e-33,
          "variance": 0.2530931308338998,
          "mse": 0.2530931308338998
        },
        "pair_ht": {
          "bias_squared": 6.897236613336788e-33,
          "variance": 0.06566207437255178,
          "mse": 0.06566207437255178
        }
      }
    },
    {
      "seed": 57,
      "expert_counts": [
        0.0,
        1.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.013798401622606177,
          "variance": 0.01347297637876553,
          "mse": 0.02727137800137171
        },
        "positive": {
          "bias_squared": 7.15076723492214e-33,
          "variance": 0.03332810278744317,
          "mse": 0.03332810278744317
        },
        "subtract": {
          "bias_squared": 6.970211302635836e-33,
          "variance": 0.0330075186897545,
          "mse": 0.0330075186897545
        },
        "pair_ht": {
          "bias_squared": 8.583929947444672e-34,
          "variance": 0.03348865435881616,
          "mse": 0.03348865435881616
        }
      }
    },
    {
      "seed": 58,
      "expert_counts": [
        0.0,
        1.0,
        3.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.027187885082394607,
          "variance": 0.011770551155746876,
          "mse": 0.03895843623814147
        },
        "positive": {
          "bias_squared": 5.055566104016494e-33,
          "variance": 0.04132603597433504,
          "mse": 0.04132603597433503
        },
        "subtract": {
          "bias_squared": 1.7333369499485123e-33,
          "variance": 0.028836737803115225,
          "mse": 0.028836737803115225
        },
        "pair_ht": {
          "bias_squared": 7.318533788671496e-33,
          "variance": 0.024487758382286836,
          "mse": 0.024487758382286836
        }
      }
    },
    {
      "seed": 59,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.08164013826785455,
          "variance": 0.044589167071794035,
          "mse": 0.12622930533964857
        },
        "positive": {
          "bias_squared": 1.989124520687442e-33,
          "variance": 0.03331930247141532,
          "mse": 0.03331930247141532
        },
        "subtract": {
          "bias_squared": 7.623221924404633e-33,
          "variance": 0.10923924484885648,
          "mse": 0.10923924484885648
        },
        "pair_ht": {
          "bias_squared": 4.935195482492292e-33,
          "variance": 0.021889630040243423,
          "mse": 0.021889630040243423
        }
      }
    },
    {
      "seed": 60,
      "expert_counts": [
        2.0,
        0.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.0587689398928139,
          "variance": 0.04025509699436965,
          "mse": 0.09902403688718353
        },
        "positive": {
          "bias_squared": 2.2268564981977415e-33,
          "variance": 0.07847663951348681,
          "mse": 0.07847663951348681
        },
        "subtract": {
          "bias_squared": 3.4185256512873436e-33,
          "variance": 0.09862118280662208,
          "mse": 0.09862118280662206
        },
        "pair_ht": {
          "bias_squared": 4.790750736663249e-33,
          "variance": 0.049039737590453734,
          "mse": 0.049039737590453734
        }
      }
    },
    {
      "seed": 61,
      "expert_counts": [
        1.0,
        1.0,
        2.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.024854089657611492,
          "variance": 0.06666367534509224,
          "mse": 0.09151776500270371
        },
        "positive": {
          "bias_squared": 1.748571356735169e-33,
          "variance": 0.04673867832194095,
          "mse": 0.04673867832194095
        },
        "subtract": {
          "bias_squared": 3.148444069242415e-34,
          "variance": 0.16331970368098211,
          "mse": 0.16331970368098211
        },
        "pair_ht": {
          "bias_squared": 6.1765175169606275e-34,
          "variance": 0.02308752885936149,
          "mse": 0.02308752885936149
        }
      }
    },
    {
      "seed": 62,
      "expert_counts": [
        1.0,
        2.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.029559659491182628,
          "variance": 0.17501409891923744,
          "mse": 0.20457375841042005
        },
        "positive": {
          "bias_squared": 4.2851941262616e-33,
          "variance": 0.1434484215924954,
          "mse": 0.14344842159249543
        },
        "subtract": {
          "bias_squared": 1.4059288594026822e-32,
          "variance": 0.4287680003768086,
          "mse": 0.4287680003768086
        },
        "pair_ht": {
          "bias_squared": 1.0640762942739478e-32,
          "variance": 0.10146991907287284,
          "mse": 0.10146991907287284
        }
      }
    },
    {
      "seed": 63,
      "expert_counts": [
        3.0,
        0.0,
        1.0
      ],
      "stats": {
        "prefix": {
          "bias_squared": 0.00615256744419461,
          "variance": 0.0106254496218627,
          "mse": 0.016778017066057308
        },
        "positive": {
          "bias_squared": 1.6790573228049423e-32,
          "variance": 0.016671201364130608,
          "mse": 0.016671201364130608
        },
        "subtract": {
          "bias_squared": 7.786768453434538e-33,
          "variance": 0.026031347277758146,
          "mse": 0.026031347277758146
        },
        "pair_ht": {
          "bias_squared": 1.9872061139069e-32,
          "variance": 0.013206223638556537,
          "mse": 0.013206223638556537
        }
      }
    }
  ]
}

```


本次子分析成本：sparse followup 4查询、6打开/点击、8find；prior-art followup 4查询、6打开/点击、2find；数学审计无网络。主分析另有检索和代码读取，旧账保留；无供应商费用凭证，不估造价格或token消耗。


---

# 再次继续执行：CPU原函数反向传播与精确方差边界

## 执行环境已解除的阻塞

上一阶段把没有torch作为停止点是不充分的。本阶段已安装CPU版 `torch==2.14.1+cpu`（Python3.12.14）；没有修改原有研究结果。安装成功后实际执行了固定Megatron代码的CPU辅助损失与自动求导路径。CUDA硬件仍不可用，但CPU验证不再被依赖缺失阻塞。

## 原函数检查的准确范围

从commit `72d23540d0358ae24a41ff289d1461b094a770fa` 的两份源码用AST原样提取并执行：`compute_routing_scores_for_aux_loss`、`switch_load_balancing_loss_func`、`MoEAuxLossAutoScaler`、`_apply_global_aux_loss`、`attach_and_log_load_balancing_loss`、`reset_global_aux_loss_tracker`。原文件整体Git blob哈希已与GitHub读取结果核对，并在测试中断言。

归约替身为单rank恒等映射，日志替身只记录loss；路由参数、频数缓冲在CPU建立。没有运行完整TopKRouter构造、CUDA gating、专家网络、分布式通信或训练pipeline。已读取同一提交的schedules.py（blob 0c4fbf9b92c6cb3386aa99f3f07195ef3b7763e2）与finalize_model_grads.py（blob b29d4f3a96fd6e23f455588f395aca3e3106a78c）。非per-token模式手动设置aux backward scale=1/G；per-token模式设置为1，末尾除总token数G*n，与该单rank等大小条件下源码次序对应。没有执行生产pipeline本身，通信与重算仍未验证。源码也显示finalize阶段调用reset，测试尚未执行完整生命周期。

4个固定fixture：二专家解析例子的2种排列，以及3个三专家随机fixture各24种排列，共74种。独立参考直接构造torch softmax与频数配对，不复用原损失helper。已验证：

- 原函数与独立参考最大梯度绝对误差约2.05e-8。
- prefix排列均值与谐波恒等式最大绝对误差约1.30e-8。
- 重置缓冲后重复计算逐bit一致；这只检验reset直接调用的作用，不证明生产生命周期调用正确。
- per-token最终缩放最大差约3.73e-8。
- loss误差断言<3e-7；源文件Git blob哈希断言通过。
- 三个非对称fixture的梯度坐标排列极差分别约0.1566、0.1516、0.1275。对称二专家例子只展示残留局部项，不展示真实顺序差异。

非负历史均值和HT控制也接入同一原loss helper及自定义backward。两者排列均值与真全局梯度均在浮点容差内一致；HT正逆序配对的最大绝对误差约1.68e-8。

首次运行因日志替身未接受`reduce_group`关键字参数而失败，随后仅修复替身签名。初次源码保存末尾多一个换行，在全文件哈希校验时发现并移除；提取函数主体未变。最终结果来自修正后执行。没有隐藏首次失败，也不将其计为Megatron缺陷。

## 更进一步：方差可以精确解释

定义C_ij=f_i J_j，T=G^-2 sum_ij C_ij，A_ij=C_ij-C_ji，b_i=sum_{j!=i}A_ij。HT顺序估计为

    ghat(pi)=G^-2 [sum_i C_ii+2 sum_{i precedes j} C_ij].

均匀随机顺序、固定记录下，有精确方差：

    E||ghat-T||² = (sum_i||b_i||²+sum_{i<j}||A_ij||²)/(3G^4).

它把额外方差直接对应到不同微批次之间的非对称配对；无偏不等于低方差。零方差要求所有A_ij=0。原专家数和辅助损失系数如果另乘在ghat上，方差需乘其平方。

更强的逐排列恒等式为

    [ghat(pi)+ghat(reverse(pi))]/2 = T.

这里不需要随机顺序，但必须固定参数、路由、Jacobian和逐微批次随机性。若反序跑第二遍改变了dropout或中间更新参数，结论不能直接用。它也不是免费精确算法：需要第二遍反向/重算或等价的信息存储。对部署来说它首先是强校验对照，尚不是可宣称更快的新训练方法。

内部数学分析已证明上述式子，并用Fraction穷举G1..6共873个排列验证均值、方差及每个反序配对。完整推导附后。用户授权继续研究；内部参与者的核验仍不冒充另外真实Work会话的正式接受。

## 本阶段结论与下一节点

P0数学检查继续扩展；P1的“提取原函数CPU语义子检查”已完成。P1完整CUDA路由、P2原生mask/不等token、P3生产pipeline对照、P4模型任务效果、P5留出确认仍未运行。不能把74排列检查写成74次模型训练或宣称准确率提升。

当前研究已从“怀疑实现有偏”推进到：固定代码中的偏差被实际自动求导复现；其期望局部项被量化；随机配对的方差和精确反序消去有证明。原创性与真实训练收益仍待确认。下一步优先检查原生pipeline的loss缩放/缓冲生命周期，再做有GPU的完整路由验证；不需要再重复搜索同一个宽泛idea或重新计算已通过的恒等式。


## 附录：fresh_ht_variance_audit.md

# Internal mathematical audit: prefix Horvitz–Thompson variance

Date: 2026-10-23. Scope: bounded internal algebra verification requested by the integration owner. No literature search, novelty claim, model-performance claim, native model experiment, recursive delegation, or formal independent Work gate. Exact rational enumeration is mathematical diagnostic evidence.

## Verdict

Both requested statements are correct for fixed contributions and a uniform permutation:

E ||g_hat-T||^2 = [sum_i ||b_i||^2 + sum_(i<j) ||A_ij||^2]/(3 G^4),

and, for every individual permutation pi,

[g_hat(pi)+g_hat(reverse(pi))]/2 = T.

The variance formula holds for G>=1; at G=1 all antisymmetric sums are empty and both sides are zero. G=0 is undefined.

## Definitions and shapes

Let C_ij=f_i J_j be a fixed vector in R^d. For example, f_i can be a detached K-dimensional row vector and J_j a K-by-d router Jacobian. The result uses only the values C_ij, so it does not require their particular factorization, iid data, or probability normalization.

Define

T=G^-2 sum_(i,j) C_ij,
g_hat(pi)=G^-2 [sum_i C_ii+2 sum_(i precedes j in pi) C_ij],
A_ij=C_ij-C_ji, A_ji=-A_ij, A_ii=0,
b_i=sum_(j != i) A_ij.

For i<j write s_ij(pi)=+1 if i precedes j, and -1 otherwise. Extend it by s_ji=-s_ij. The product s_ij A_ij is invariant to reversing the labeling of the edge.

## Exact error representation and unbiasedness

For an unordered pair {i,j}, the full target includes C_ij+C_ji. The estimate includes either 2 C_ij or 2 C_ji. Their difference is therefore s_ij A_ij. Diagonal terms cancel exactly, giving

g_hat-T=G^-2 sum_(i<j) s_ij A_ij.

Under a uniform permutation E[s_ij]=0, hence E[g_hat]=T. This is the Horvitz–Thompson inclusion correction for directed off-diagonal contributions with inclusion probability 1/2. The edge-inclusion events are dependent, and their dependence is essential for the variance formula.

## Permutation sign moments

1. E[s_ij^2]=1.
2. If edges {i,j} and {k,l} are disjoint, E[s_ij s_kl]=0. The two relative orders are uniformly distributed; swapping the positions of i and j flips the first sign without changing the second.
3. For distinct i,j,k, orient both edges outward from their common vertex i. Then E[s_ij s_ik]=1/3. Among the six relative orders of these three indices, i is first or last with total probability 2/3, giving sign product +1; i is in the middle with probability 1/3, giving sign product -1.

The third identity must be used with the corresponding orientation of A. In an increasing-index convention, a chain-shaped pairing can have sign covariance -1/3; pretending every shared-edge covariance is +1/3 without reorienting A is an error.

## Vector mean squared error proof

Set S=sum_(i<j)||A_ij||^2. Let

U=sum_i sum_(j<k; j,k != i) <A_ij,A_ik>,

where each term uses edges oriented outward from the common vertex i. Each pair of distinct edges sharing one vertex occurs exactly once in U. Expanding the squared error and applying the sign moments gives

G^4 E||g_hat-T||^2 = S+(2/3)U.

On the other hand,

sum_i ||b_i||^2
 = sum_i sum_(j != i)||A_ij||^2 + 2U
 = 2S+2U.

Eliminating U yields

S+(2/3)U = [S+sum_i||b_i||^2]/3,

which proves the requested expression.

A stronger matrix version also follows by replacing inner products with symmetrized outer products:

Cov(g_hat)=[sum_i b_i b_i^T+sum_(i<j)A_ij A_ij^T]/(3G^4).

The stated MSE is its trace. In particular, zero permutation variance requires every A_ij=0; cancellation of the b_i alone is insufficient in the general C_ij setting. This criterion concerns the estimator at fixed records, not properties of a trained model.

## Exact forward/reverse cancellation

Reversing a permutation flips every pairwise order: s_ij(reverse(pi))=-s_ij(pi). Therefore the reverse error is exactly the negative forward error:

g_hat(reverse(pi))-T=-(g_hat(pi)-T).

Averaging gives T identically, without needing to randomize pi or average over additional permutations. Equivalently, the two passes include both orientations of every off-diagonal pair once after averaging, while preserving the diagonal contribution.

This exact identity does not imply a free computational gain: an implementation must obtain the relevant gradients for both orders or otherwise reproduce their algebraic sum. Runtime, graph retention, repeated forwards, memory, and random-number coupling require separate implementation accounting.

## Implementation and gradient assumptions

- Hold parameters fixed throughout the estimator and any paired reverse pass; update only after the intended accumulation. Sequential optimizer updates alter J_j and invalidate the fixed-record cancellation.
- Preserve f_i and J_i for each microbatch under reordering. Capacity-dependent routing, batch-dependent operations, sequence repacking or changed attention context can break this condition.
- With dropout, exact cancellation requires the same per-microbatch random realization across both passes, or cached contributions. The same global seed alone need not associate the same masks with a microbatch after reversing order.
- Treat f_i as detached if this is the intended applied gradient. The audit concerns the resulting vectors f_i J_j and does not add gradients through routing frequencies.
- Uniform permutations are required for the displayed unbiasedness/variance law. Exact forward/reverse averaging is valid for ANY initial order, provided its fixed records are preserved.
- Equal microbatch means and the 1/G^2 normalization must match the real implementation. Token-count weighting, masked denominators and distributed reduction require a weighted derivation if they differ.
- These are raw-gradient identities. Nonlinear clipping or adaptive updates performed separately on the forward and reverse estimates generally do not preserve their cancellation at the parameter-update level. Average the raw vectors first to use the exact identity.

## Exact rational enumeration

A Python Fraction calculation enumerated all permutations for G=1,...,6 (873 permutations total). For each order it checked exact forward/reverse cancellation, then checked unbiasedness and the proposed vector MSE formula. No tolerance or floating-point arithmetic was used. Exit code 0; tool-reported wall time 0.181795978 seconds.

| G | Permutations | Exact vector MSE | Formula | Unbiased | Every reverse pair exact |
|---|---:|---|---|---|---|
| 1 | 1 | 0 | true | true | true |
| 2 | 2 | 365369645/41699273616 | true | true | true |
| 3 | 6 | 3252475295/562940193816 | true | true | true |
| 4 | 24 | 25133517/3206403200 | true | true | true |
| 5 | 120 | 265175083/57829983750 | true | true | true |
| 6 | 720 | 464743165/140735048454 | true | true | true |

This finite diagnostic checks representative inputs and the arithmetic implementation. The argument above proves the general fixed-record result.

Reproduction code:

```python
from fractions import Fraction as F
from itertools import permutations

def plus(a,b): return tuple(x+y for x,y in zip(a,b))
def minus(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(c,a): return tuple(c*x for x in a)
def norm2(a): return sum((x*x for x in a),F(0))
def product(f,J):
    return tuple(sum((f[k]*J[k][r] for k in range(2)),F(0))
                 for r in range(2))

for G in range(1,7):
    fs=[(F(i+1,G+1),F(G-i,G+1)) for i in range(G)]
    Js=[((F((3*i+2)%7,7),F((5*i+1)%11,11)),
         (F((2*i+3)%13,13),F((4*i+1)%17,17))) for i in range(G)]
    pairs=[[product(fs[i],Js[j]) for j in range(G)] for i in range(G)]
    zero=(F(0),F(0))
    T=scale(F(1,G*G),tuple(
        sum((pairs[i][j][r] for i in range(G) for j in range(G)),F(0))
        for r in range(2)))
    A=[[minus(pairs[i][j],pairs[j][i]) for j in range(G)]
       for i in range(G)]
    bs=[tuple(sum((A[i][j][r] for j in range(G)),F(0))
              for r in range(2)) for i in range(G)]
    rhs=(sum((norm2(b) for b in bs),F(0))+
         sum((norm2(A[i][j]) for i in range(G)
              for j in range(i+1,G)),F(0)))/(3*G**4)
    def est(perm):
        z=zero
        for pos,j in enumerate(perm):
            z=plus(z,pairs[j][j])
            for i in perm[:pos]: z=plus(z,scale(F(2),pairs[i][j]))
        return scale(F(1,G*G),z)
    mse=F(0); avg=zero; count=0
    for perm in permutations(range(G)):
        h=est(perm); hr=est(perm[::-1])
        assert scale(F(1,2),plus(h,hr))==T
        avg=plus(avg,h)
        mse+=norm2(minus(h,T)); count+=1
    mse/=count; avg=scale(F(1,count),avg)
    assert avg==T and mse==rhs
```

## Claim boundary

Established: exact fixed-record expectation, covariance/MSE, and deterministic antithetic order cancellation.

Not established: originality, applicability to a particular codebase, improved model learning, computational advantage, distributed-system correctness, or a formal review gate.


## 附录：fresh_native_cpu_review.md

# Informal review of extracted Megatron CPU audit

Date: 2026-10-23. Reviewer: sparse-training leaf worker. This is an implementation/math check by a participating worker, **not independent Work acceptance**, design approval, actual-code gate approval, or full native-model validation. I did not modify the audited script or evidence files.

## Verdict

No blocking defect found for the stated narrow claim: the unchanged non-fused, top-1 softmax loss/helper bodies, run on CPU with equal-size microbatches and single-rank stubs, reproduce the prefix auxiliary gradient and its permutation-average mixture identity. The script correctly handles the unusual custom auxiliary backward by setting the scaler directly rather than relying on scaling a dummy main loss.

It must not be described as a completed Megatron distributed training reproduction, a Qwen benchmark result, an audit of current main, or proof of practical damage. The source pin is historical `72d23540d0358ae24a41ff289d1461b094a770fa`.

## Actual review actions and receipt

Read the entire `fresh_native_cpu_audit.py`; inspected relevant original source sections in `evidence/megatron_router_72d2354.py` and `evidence/megatron_moe_utils_72d2354.py`. Executed once with `python fresh_native_cpu_audit.py`; exit code 0. Runtime: torch 2.14.1+cpu, Python 3.12.14. Tool process wall time 2.503 s; script's measured inner audit time 0.803 s. Four fixtures, 74 permutations total (2 + 3*24); each permutation runs ordinary, per-token-scaled, and reset/repeated variants.

Observed maxima across reported fixtures:

- Native extracted versus independently written prefix gradient: 2.0489096641540527e-8.
- Mean native versus harmonic-mixture identity: 1.30385160446167e-8.
- Per-token equivalent final scaling difference: 3.725290298461914e-8.
- Logged loss difference: 1.1920928955078125e-7.
- All reset/repeat comparisons exact in this run.

This review rerun is additional verification work; do not merge its time with an earlier run or count it as an independent seed/model experiment.

## Correct aspects

1. AST extraction compiles original function/class statement nodes without body rewriting. Names and exact extracted-source hashes are emitted. Technically this is five functions/methods plus one class, rather than six functions. Missing module initialization is replaced deliberately by supplied globals and SimpleNamespace state.
2. `_apply_global_aux_loss` includes the historical count accumulation, ga_steps update, and current-score loss; these are the mechanism under examination.
3. Native route counts are discrete and non-differentiable, matching the independent detached-frequency reference. Immediate backward after each forward avoids an accidental buffer-mutation/autograd lifetime divergence from normal sequential accumulation.
4. `MoEAuxLossAutoScaler.backward` injects its configured auxiliary gradient regardless of zero main upstream gradient. Consequently `(out.sum()*0).backward()` legitimately isolates auxiliary gradients here. This is not a vanishing-loss false negative.
5. Setting the scaler to 1/G explicitly makes the ordinary auxiliary gradient equal the average of G microbatch contributions. The reference separately constructs the corresponding scalar objective; it does not call the extracted loss function.
6. For equal-size n and single rank, the per-token arm multiplies the aux loss by n internally, sets scaler 1/G, then divides the resulting gradient by n. This has the same final factor as multiplying by n, setting scaler 1, and finalizing by 1/(Gn). Hence the reported final gradient equivalence is valid for these fixtures.

## Scope restrictions and possible misleading conclusions

### Binary fixture is not an order-sensitivity witness

The binary fixture uses opposite input signs and a symmetric score derivative. Both permutations yield the same nonzero gradient; its exact-global gradient is zero. It is a clean witness of **systematic micro-batch contamination even after permutation averaging**, but not of variation between the two orders. Do not show its gradient as an order-dependence demonstration. The random fixtures may show order variation, but the script currently does not emit a max/rms permutation-spread metric or explicitly assert it is nonzero.

### Per-token scaling tests a final algebraic equivalence, not pipeline integration

The scaler value and final n division are hand-set. `finalize_model_grads`, pipeline schedules, gradient scaling, optimizer step, data-parallel normalization and token count aggregation are not executed. The comment correctly calls this explicit replacement. Because all batches have equal size, this test cannot address uneven valid tokens, padding, packed sequences, or issue #7213. Also it does not establish exact scaling under TP/CP/DP group overlaps or multiple pipeline stages.

### Reset is directly invoked, not scheduled

The repeated-router check verifies `reset_global_aux_loss_tracker()` clears these two buffers and restores repeated behavior. It does not verify that production code calls reset at the right lifecycle boundary, after activation recomputation, on skipped optimizer updates, or on failures. Do not present it as production reset-scheduling coverage.

### Dtype and top-k boundaries

All fixture tensors are float32 and CPU. The source softmax explicitly casts to float32; the independent reference does not specify a dtype but agrees because inputs are float32. Extending to float64 or mixed precision would require reference semantics to match that cast. The audit does not cover BF16/FP16, loss scaling/overflow, fused TE kernels, stochastic jitter, top-k>1, sigmoid routing, capacity/token dropping, or expert outputs.

Native `torch.topk` and reference `argmax` can disagree on tied scores; present fixtures appear to avoid ties. The fixture contract should remain “no score ties,” or tie handling should be aligned before adding adversarial tests. This is not an observed failure in the run.

### Receipt strength

The script records extracted segment hashes but does not itself verify complete downloaded files against a trusted remote artifact. Provenance must come from the owner's download receipt/source pin. It reports `loss_max_abs_error` without asserting a tolerance on that metric; gradient equality is asserted. Calling the loss comparison a passing automated assertion would overstate the script, though observed values are small. With coefficient fixed at 1, the audit does not check configuration-driven coefficient retrieval/disabled-loss branches.

## Minimal useful follow-up, if needed

No broad testing sweep is necessary to support the already scoped identity. Before using the audit to support a separate order-dependence claim, add/record a permutation-spread statistic or an asymmetric two-batch fixture. Before claiming production training behavior, inspect and execute the actual pipeline scaling/reset path on a pinned full setup; the present CPU extraction is deliberately narrower. A GPU training run is not needed merely to validate this finite gradient identity.

Suggested precise description: “We executed unchanged AST-extracted non-fused Megatron routing-loss components from a fixed commit in a single-rank CPU harness, with explicit auxiliary-loss scaling. Across 74 permutations, their gradients matched an independent prefix reference and the derived permutation-average identity to float32 tolerance.”

## Scientific interpretation

The CPU audit supports the algebra-to-implementation connection. It does not settle novelty, native effect size, training convergence, specialization harm, or advantage of any correction. The original paper openly calls its buffer approximate. A deviation from the exact global objective therefore establishes an approximation property, not by itself an implementation bug or refutation of reported performance.

## Final revision addendum — supersedes the receipt/spread omissions above

Reviewed the added source-blob assertions, loss assertion, permutation spread, and two coefficient-control arms. The final audited script SHA256 is `eb8604d9314a9378380255980d702bd37a890fe5383d61740fa7eef0c4f816f2`. This addendum applies to that exact file, not to later edits.

Source SHA256 values:

- Router: `fae1518fcc97e85c972a7699a898ddcf7920d717185e7a7efaa505562f69f882`.
- MoE utilities: `0ca558ad82bd8a03f70b2e3f04c4cf0435c5394031aa4fb210fe3c7572c731c7`.

The new Git blob hash calculation correctly includes the `blob <byte-length>\0` prefix and asserts the entire original byte sequence. The assertions passed for router blob `8cb8936a785d4d02ed6e240a61912d3aa2b29cbf` and utility blob `739283ee8b72cce835f94d6109e76169edfa0112`. Root reports matching GitHub API blob receipts; this reviewer verified local assertions, not an independent remote refetch. The former complete-file-hash gap is closed conditional on those remote receipts. The new `maxloss < 3e-7` assertion also closes the formerly descriptive-only loss check.

Executed the revised script once successfully: exit 0, torch 2.14.1+cpu, Python 3.12.14, outer wall time 2.916 s, inner time 0.952 s. This is a separate final-revision rerun; do not combine timing with the earlier revision. Across the same 74 permutations, maximum prefix/reference gradient error was 2.0489096641540527e-8; maximum logged-loss error 1.1920928955078125e-7; maximum per-token equivalence error 3.725290298461914e-8; all direct reset/repeat checks remained exact.

The new prefix coordinate-range maxima are 1.4901161193847656e-8 for binary, and 0.1566033512353897, 0.15156501531600952, 0.12750288844108582 for the three asymmetric fixtures. Thus the latter provide concrete order-dependence witnesses. The binary result remains roundoff-level order variation and must remain a systematic-bias witness rather than an order-spread witness.

### Added controls: mathematically consistent, bounded claim

For current microbatch frequency f and accumulated previous frequencies P at zero-based position j, the new code supplies effective coefficients `a = f/G + P/j` (with the previous term zero at j=0) or `a = (f+2P)/G`. Passing `a*n` into the unchanged native loss helper yields the intended weighted linear score objective; these are effective counts, not actual observed token counts or necessarily normalized frequency vectors. Detached top-1 routing makes the coefficient treatment consistent with the existing derivation.

Under frozen parameters, equal microbatch sizes, no stochastic forward changes, and uniform random permutations, both controls have the exact-global gradient in expectation. For the first control, the diagonal coefficient is 1/G before the outer 1/G, and the expectation of the previous-average term assigns 1/G to every off-diagonal item. For the second, each ordered pair appears with probability one half and receives weight 2/G. Pairing an ordering with its reversal therefore recovers all ordered cross terms exactly, with the correct diagonal weight. These facts justify the added mean/reverse-pair comparisons.

Observed maximum errors across fixtures: positive-control mean versus global 1.30385160446167e-8; pair-HT mean versus global 1.30385160446167e-8; pair-HT forward/reverse average versus global 1.6763806343078613e-8. All corresponding assertions passed.

Crucial scope: the controls use newly written coefficient logic and unchanged native score/loss/custom-backward helpers. They do **not** execute an unchanged production `_apply_global_aux_loss` correction, and reverse pairing is two executions, not an exact causal single-pass solution. This verifies coefficient algebra through the original helper/autograd path, not estimator novelty, variance benefit, training improvement, or a production implementation. All earlier dtype, single-rank, equal-size, manual-scaling, reset-lifecycle and no-full-model limits remain.

No new blocking defect found in the added segments. The original setup/stub failure receipt should remain in root's chronological report; a successful corrected run must not erase it. This reviewer did not independently inspect that first failed receipt and makes no claim about its exact failure text.

### Final stable scaling revision

The last small revision changes the per-token arm to set auxiliary scaler 1 and divide the resulting gradient by G*n, matching root's inspected scheduler/finalizer sequence more directly. I inspected this changed block and reran the stable script: exit 0; outer process time 2.729 s, inner 0.897 s. Maximum per-token equivalence error remains 3.725290298461914e-8. All other assertions passed. The final script SHA256 verified before and after that run is **`ff3fa89cef4b27f0ee7001b7c9c2ca71447e681b6ce243f23daa5102d78dce6a`**, superseding the script hash in the preceding addendum; both source hashes remain unchanged.

The old review description of scaler 1/G followed by division by n describes the earlier script only. The final code uses scaler 1 then division by G*n, while ordinary mode uses scaler 1/G. The finalizer and scheduler themselves still do not execute in the harness. I have not separately fetched their source in this review. Reset remains manually invoked at the beginning of each harness run; production end-of-step reset timing is not validated here. This final revision preserves the narrow no-blocker verdict and does not expand evidence to full pipeline integration.


## 附录：fresh_native_cpu_audit.py

```python
"""Execute unchanged AST-extracted Megatron functions on CPU, single-rank stubs.
Not a full TopKRouter/CUDA/distributed model test.
"""
import ast,hashlib,itertools,json,math,platform,time,types
from pathlib import Path
import torch

torch.set_num_threads(1)
ROOT=Path(__file__).parent
SOURCE_BLOBS={'evidence/megatron_router_72d2354.py':'8cb8936a785d4d02ed6e240a61912d3aa2b29cbf',
              'evidence/megatron_moe_utils_72d2354.py':'739283ee8b72cce835f94d6109e76169edfa0112'}
for name,expected in SOURCE_BLOBS.items():
    raw=(ROOT/name).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==expected
ns={'torch':torch,'HAVE_TE':False,'fused_moe_aux_loss':None,
    'fused_compute_score_for_moe_aux_loss':None,
    'reduce_from_tensor_model_parallel_region':lambda x,group:x}
logs=[]
ns['save_to_aux_losses_tracker']=lambda name,loss,*args,**kwargs:logs.append(float(loss.detach()))
extracted=[]
def extract(path,names,cls=None):
    raw=path.read_text();tree=ast.parse(raw)
    nodes=tree.body if cls is None else next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls).body
    for name in names:
        node=next(n for n in nodes if getattr(n,'name',None)==name)
        src=ast.get_source_segment(raw,node)
        extracted.append({'source':str(path.relative_to(ROOT)),'name':name,'start':node.lineno,'end':node.end_lineno,'sha256':hashlib.sha256(src.encode()).hexdigest()})
        # AST compilation retains exact source statements; no function body rewriting.
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
extract(ROOT/'evidence/megatron_moe_utils_72d2354.py',[
    'switch_load_balancing_loss_func','compute_routing_scores_for_aux_loss','MoEAuxLossAutoScaler'])
extract(ROOT/'evidence/megatron_router_72d2354.py',[
    '_apply_global_aux_loss','attach_and_log_load_balancing_loss','reset_global_aux_loss_tracker'],cls='TopKRouter')
class Group:
    def size(self):return 1

def make_router(K,token_scale=False):
    r=types.SimpleNamespace(topk=1,tp_dp_cp_group=Group(),
        global_tokens_per_expert=torch.zeros(K),ga_steps=torch.tensor(0.),
        config=types.SimpleNamespace(num_moe_experts=K,moe_router_fusion=False,num_layers=1,mtp_num_layers=None),
        layer_number=1,calculate_per_token_loss=token_scale,get_aux_loss_coeff=lambda x:1.)
    for name in ['_apply_global_aux_loss','attach_and_log_load_balancing_loss','reset_global_aux_loss_tracker']:
        setattr(r,name,types.MethodType(ns[name],r))
    return r

def native_gradient(W0,batches,order,token_scale=False,router=None):
    G=len(batches);W=W0.clone().requires_grad_();r=router or make_router(W.shape[0],token_scale)
    r.reset_global_aux_loss_tracker();assert r.ga_steps.item()==0 and r.global_tokens_per_expert.sum()==0
    logs.clear()
    # This replaces pipeline loss scaling explicitly. The native custom backward
    # does not obtain its aux scale from multiplying the dummy main loss by 1/G.
    ns['MoEAuxLossAutoScaler'].set_loss_scale(torch.tensor(1. if token_scale else 1./G))
    for i in order:
        logits=batches[i]@W.T
        routes,scores=ns['compute_routing_scores_for_aux_loss'](logits,1,'softmax',False)
        out=r._apply_global_aux_loss(scores,scores,routes)
        (out.sum()*0).backward()
    grad=W.grad.clone()
    if token_scale:
        # Source schedule uses scale 1; finalize divides total global token count.
        # Single rank and equal-sized batches only; finalize itself is not executed.
        grad/=G*len(batches[0])
    return grad,logs.copy(),r

def independent(W0,batches,order,mode):
    W=W0.clone().requires_grad_();G=len(batches);K=W.shape[0]
    ps=[torch.softmax(x@W.T,dim=-1) for x in batches]
    fs=[torch.nn.functional.one_hot(p.argmax(-1),K).float().mean(0).detach() for p in ps]
    qs=[p.mean(0) for p in ps]
    coeff=torch.zeros(K);terms=[]
    for j,i in enumerate(order):
        coeff+=fs[i]
        a=coeff/(j+1) if mode=='prefix' else (fs[i] if mode=='micro' else torch.stack(fs).mean(0))
        terms.append(K*(a*qs[i]).sum()/G)
    loss=sum(terms)
    return torch.autograd.grad(loss,W)[0],float(loss.detach())

def native_control(W0,batches,order,mode):
    """New estimator coefficients passed through unchanged native helper/backward."""
    W=W0.clone().requires_grad_();G=len(batches);K=W.shape[0]
    r=make_router(K);past=torch.zeros(K)
    ns['MoEAuxLossAutoScaler'].set_loss_scale(torch.tensor(1./G))
    for j,i in enumerate(order):
        routes,scores=ns['compute_routing_scores_for_aux_loss'](batches[i]@W.T,1,'softmax',False)
        n=len(batches[i]);f=routes.float().mean(0)
        if mode=='positive':a=f/G+(past/j if j else 0)
        elif mode=='pair_ht':a=(f+2*past)/G
        else:raise ValueError(mode)
        loss=ns['switch_load_balancing_loss_func'](scores,a*n,n,1,K,1.,False)
        out=r.attach_and_log_load_balancing_loss(scores,1.,loss,'control',r.tp_dp_cp_group)
        (out.sum()*0).backward()
        past+=f
    return W.grad.clone()

start=time.time();receipts=[]
cases=[('binary',torch.tensor([[math.log(4.)],[0.]]),[torch.tensor([[1.]]),torch.tensor([[-1.]])])]
for seed in [101,102,103]:
    gen=torch.Generator().manual_seed(seed)
    cases.append(('three_expert_'+str(seed),torch.randn(3,2,generator=gen),[torch.randn(3,2,generator=gen) for _ in range(4)]))
for name,W,batches in cases:
    G=len(batches);orders=list(itertools.permutations(range(G)))
    grads=[];maxerr=0.;maxloss=0.;tokenerr=0.
    controls={m:[] for m in ['positive','pair_ht']}
    for order in orders:
        got,losses,r=native_gradient(W,batches,order)
        ref,loss=independent(W,batches,order,'prefix')
        err=float((got-ref).abs().max());maxerr=max(maxerr,err)
        maxloss=max(maxloss,abs(sum(losses)/G-loss))
        torch.testing.assert_close(got,ref,atol=2e-7,rtol=2e-5)
        scaled,_,_=native_gradient(W,batches,order,True)
        tokenerr=max(tokenerr,float((got-scaled).abs().max()))
        torch.testing.assert_close(scaled,got,atol=2e-7,rtol=2e-5)
        again,_,_=native_gradient(W,batches,order,router=r)
        torch.testing.assert_close(again,got,atol=0,rtol=0)
        grads.append(got)
        for mode in controls:controls[mode].append(native_control(W,batches,order,mode))
    gg,_=independent(W,batches,orders[0],'global');gm,_=independent(W,batches,orders[0],'micro')
    lam=(sum(1/j for j in range(1,G+1))-1)/(G-1)
    mean=torch.stack(grads).mean(0);pred=(1-lam)*gg+lam*gm
    torch.testing.assert_close(mean,pred,atol=2e-7,rtol=2e-5)
    assert maxloss<3e-7
    for mode,values in controls.items():
        torch.testing.assert_close(torch.stack(values).mean(0),gg,atol=2e-7,rtol=2e-5)
    reverse_error=0.
    for idx,order in enumerate(orders):
        rev=orders.index(tuple(reversed(order)))
        paired=(controls['pair_ht'][idx]+controls['pair_ht'][rev])/2
        reverse_error=max(reverse_error,float((paired-gg).abs().max()))
        torch.testing.assert_close(paired,gg,atol=2e-7,rtol=2e-5)
    receipts.append({'name':name,'G':G,'permutations':len(orders),'lambda':lam,
      'native_vs_reference_max_abs_gradient_error':maxerr,'loss_max_abs_error':maxloss,
      'per_token_scaling_max_abs_error':tokenerr,'mean_vs_identity_max_abs_error':float((mean-pred).abs().max()),
      'prefix_coordinate_range_max':float((torch.stack(grads).max(0).values-torch.stack(grads).min(0).values).max()),
      'ht_reverse_pair_max_abs_error':reverse_error,
      'control_mean_max_abs_error':{m:float((torch.stack(v).mean(0)-gg).abs().max()) for m,v in controls.items()},
      'global_gradient':gg.tolist(),'native_mean_gradient':mean.tolist(),'reset_repeat_exact':True})
print(json.dumps({'scope':'unchanged extracted CPU functions with identity single-rank reduction and stub logging; manual pipeline scaling; no full CUDA router',
  'torch':torch.__version__,'python':platform.python_version(),'elapsed_seconds':time.time()-start,
  'source_commit':'72d23540d0358ae24a41ff289d1461b094a770fa','verified_source_blobs':SOURCE_BLOBS,'extracted':extracted,'receipts':receipts},indent=2))

```


## 附录：fresh_native_cpu_audit.json

```json
{
  "scope": "unchanged extracted CPU functions with identity single-rank reduction and stub logging; manual pipeline scaling; no full CUDA router",
  "torch": "2.14.1+cpu",
  "python": "3.12.14",
  "elapsed_seconds": 0.95060133934021,
  "source_commit": "72d23540d0358ae24a41ff289d1461b094a770fa",
  "verified_source_blobs": {
    "evidence/megatron_router_72d2354.py": "8cb8936a785d4d02ed6e240a61912d3aa2b29cbf",
    "evidence/megatron_moe_utils_72d2354.py": "739283ee8b72cce835f94d6109e76169edfa0112"
  },
  "extracted": [
    {
      "source": "evidence/megatron_moe_utils_72d2354.py",
      "name": "switch_load_balancing_loss_func",
      "start": 35,
      "end": 112,
      "sha256": "fb4f02f3e91d2312eb7511affacac6bfce90ac55c7136743fa4629d788cb2eb7"
    },
    {
      "source": "evidence/megatron_moe_utils_72d2354.py",
      "name": "compute_routing_scores_for_aux_loss",
      "start": 599,
      "end": 629,
      "sha256": "abc03956ff66aa5ca01080d47595fb4323edc916484afd38a58c8de9002a24ab"
    },
    {
      "source": "evidence/megatron_moe_utils_72d2354.py",
      "name": "MoEAuxLossAutoScaler",
      "start": 166,
      "end": 216,
      "sha256": "bab45e4f8cbdfa91329cc008ba10a60b62b31f2c9113badb0b326ede1fa5c286"
    },
    {
      "source": "evidence/megatron_router_72d2354.py",
      "name": "_apply_global_aux_loss",
      "start": 327,
      "end": 363,
      "sha256": "6b935eef5ba93c50361e1d1008da54abafb541ab90e43f18e2534fe39670a326"
    },
    {
      "source": "evidence/megatron_router_72d2354.py",
      "name": "attach_and_log_load_balancing_loss",
      "start": 365,
      "end": 399,
      "sha256": "134b28b4339a0c04e4b8cb058634e48644500c44bd839134fb11c6074563f296"
    },
    {
      "source": "evidence/megatron_router_72d2354.py",
      "name": "reset_global_aux_loss_tracker",
      "start": 523,
      "end": 527,
      "sha256": "f70be4b508095d8a5fc08af3e45b2b6aa61c33c23d6ad6d7a14774bf0791aa13"
    }
  ],
  "receipts": [
    {
      "name": "binary",
      "G": 2,
      "permutations": 2,
      "lambda": 0.5,
      "native_vs_reference_max_abs_gradient_error": 0.0,
      "loss_max_abs_error": 5.960464477539063e-08,
      "per_token_scaling_max_abs_error": 0.0,
      "mean_vs_identity_max_abs_error": 0.0,
      "prefix_coordinate_range_max": 1.4901161193847656e-08,
      "ht_reverse_pair_max_abs_error": 7.450580596923828e-09,
      "control_mean_max_abs_error": {
        "positive": 7.450580596923828e-09,
        "pair_ht": 7.450580596923828e-09
      },
      "global_gradient": [
        [
          0.0
        ],
        [
          0.0
        ]
      ],
      "native_mean_gradient": [
        [
          0.1599999964237213
        ],
        [
          -0.1599999964237213
        ]
      ],
      "reset_repeat_exact": true
    },
    {
      "name": "three_expert_101",
      "G": 4,
      "permutations": 24,
      "lambda": 0.36111111111111116,
      "native_vs_reference_max_abs_gradient_error": 1.4901161193847656e-08,
      "loss_max_abs_error": 1.1920928955078125e-07,
      "per_token_scaling_max_abs_error": 1.862645149230957e-08,
      "mean_vs_identity_max_abs_error": 1.30385160446167e-08,
      "prefix_coordinate_range_max": 0.1566033512353897,
      "ht_reverse_pair_max_abs_error": 1.6763806343078613e-08,
      "control_mean_max_abs_error": {
        "positive": 1.30385160446167e-08,
        "pair_ht": 1.30385160446167e-08
      },
      "global_gradient": [
        [
          -0.00426925253123045,
          0.02183239907026291
        ],
        [
          0.04953873157501221,
          -0.02005215361714363
        ],
        [
          -0.045269474387168884,
          -0.0017802356742322445
        ]
      ],
      "native_mean_gradient": [
        [
          0.0013063786318525672,
          0.022806702181696892
        ],
        [
          0.07786190509796143,
          -0.045067813247442245
        ],
        [
          -0.07916828989982605,
          0.022261135280132294
        ]
      ],
      "reset_repeat_exact": true
    },
    {
      "name": "three_expert_102",
      "G": 4,
      "permutations": 24,
      "lambda": 0.36111111111111116,
      "native_vs_reference_max_abs_gradient_error": 2.0489096641540527e-08,
      "loss_max_abs_error": 1.1920928955078125e-07,
      "per_token_scaling_max_abs_error": 3.725290298461914e-08,
      "mean_vs_identity_max_abs_error": 3.725290298461914e-09,
      "prefix_coordinate_range_max": 0.15156501531600952,
      "ht_reverse_pair_max_abs_error": 1.4901161193847656e-08,
      "control_mean_max_abs_error": {
        "positive": 3.725290298461914e-09,
        "pair_ht": 7.450580596923828e-09
      },
      "global_gradient": [
        [
          -0.054536111652851105,
          -0.039973802864551544
        ],
        [
          0.023056622594594955,
          -0.021738704293966293
        ],
        [
          0.031479477882385254,
          0.06171249970793724
        ]
      ],
      "native_mean_gradient": [
        [
          -0.055227845907211304,
          -0.05547335371375084
        ],
        [
          0.008759557269513607,
          -0.03754992410540581
        ],
        [
          0.04646826907992363,
          0.09302326291799545
        ]
      ],
      "reset_repeat_exact": true
    },
    {
      "name": "three_expert_103",
      "G": 4,
      "permutations": 24,
      "lambda": 0.36111111111111116,
      "native_vs_reference_max_abs_gradient_error": 1.1175870895385742e-08,
      "loss_max_abs_error": 1.1920928955078125e-07,
      "per_token_scaling_max_abs_error": 2.60770320892334e-08,
      "mean_vs_identity_max_abs_error": 3.725290298461914e-09,
      "prefix_coordinate_range_max": 0.12750288844108582,
      "ht_reverse_pair_max_abs_error": 1.4901161193847656e-08,
      "control_mean_max_abs_error": {
        "positive": 7.450580596923828e-09,
        "pair_ht": 7.450580596923828e-09
      },
      "global_gradient": [
        [
          -0.07486002147197723,
          0.020324692130088806
        ],
        [
          0.07642433047294617,
          -0.0038209203630685806
        ],
        [
          -0.0015643208753317595,
          -0.01650378294289112
        ]
      ],
      "native_mean_gradient": [
        [
          -0.05557026341557503,
          -0.0013103311648592353
        ],
        [
          0.06804850697517395,
          0.01699904166162014
        ],
        [
          -0.012478248216211796,
          -0.015688730403780937
        ]
      ],
      "reset_repeat_exact": true
    }
  ]
}

```
