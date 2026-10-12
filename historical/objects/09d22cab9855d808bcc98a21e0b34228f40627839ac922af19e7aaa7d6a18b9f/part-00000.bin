**2026 年论文：CPU / 8GiB 原生小规模复现记录**

核查日期：2026-10-11。目标是实际运行作者代码，确认指定实验在当前资源中能否完成。本报告不把小规模实验成功扩大为整篇论文、全数据集或全部随机种子的复现成功。

本轮处理 38 篇会议候选：原清单按新范围筛选后 34 篇，新增 ACL / EMNLP 候选 4 篇。Jev 的离线重算与本地 Laya 推理单列。这是已检索候选的逐篇执行审计，不声称穷尽 2026 年所有论文。

范围集中于 AI、机器学习、NLP 和视觉。按 [CCF 2026 目录，第57–58页](https://dengpingfan.github.io/papers/CCF-Recommend-2026.pdf)，人工智能 A 类包含 AAAI、NeurIPS、ACL、CVPR、ICCV、ICML、ICLR；EMNLP 与 ECCV 按用户要求额外保留。IJCAI 在新版目录为 B，本轮不进入主表。未用其他年份的 ICCV 论文充作 ICCV 2026。EMNLP 作者自报录用但官方论文集未核实的条目，在对应限制中单独标注。

本轮确实启动了 6 个 subagent。执行进程可在同一宿主 /proc 中交叉观察，归属同一 cgroup；memory.max=8,589,934,592 字节（8GiB），cpu.max=800000/100000（8核当量）。PID 命名空间隔离没有带来独立内存额度，不能汇总成 64GB。这描述的是当前执行容器，不代表 GPT 模型服务所用硬件。

原生计算、编译及安装使用共享串行锁；实验禁用可见 CUDA、限制 BLAS/OpenMP 线程，未调用付费 Jev、OpenAI 或其他远程模型 API。公开代码、数据和权重下载不算本地推理。

为给控制进程留余量，包装器通常设单个任务进程组 RSS 保护线5.5GiB，共享工作集保护线7.25GiB；容器硬上限仍为8GiB。保护线触发会停止任务，不能据此宣称方法本身需要超过8GiB。CPU核数或线程数的显式例外保留在实际命令中。

**读表口径：**“限定范围跑通”要求算法运行完成并检查实际输出；只成功安装、导入、编译或返回 exit=0 不构成通过。“受阻”表示代码、数据、许可证、依赖或平台条件没有满足，不等于内存超过8GiB；时间上限到达也不等于内存不足。

内存列取有效进程组 RSS 采样峰值与内核 child ru_maxrss 两者的较大值，单位 MiB，四舍五入到一位小数；100ms 采样可能漏掉极短的多进程合计峰值。最早 v1 包装器的进程组采样受 PID 命名空间影响，相关记录仅采用有效的内核 ru_maxrss。v2 修复进程定位，v3 将可回收 inactive_file 缓存从共享工作集保护阈值中剔除。大量下载文件的 active_file 缓存曾触发过保守保护；用 POSIX_FADV_DONTNEED 提示内核回收本轮下载工件的缓存后再试，没有修改文件内容或8GiB硬上限。96MiB 真实内存分配校验已通过。全容器缓存占用不被写成单篇论文的 RSS。

耗时是本次指定任务的墙钟时间；部分任务包含依赖安装、首次 JIT 编译或多个子任务，对应阶段见命令与逐篇说明。不同硬件、不同输入范围之间不直接比较速度。受阻或失败行的内存仅表示该次尝试的观测值，不能证明完整方法的内存需求。

结果：限定范围跑通 23 篇；受阻 12 篇；运行或结果核验未通过 2 篇；超时 1 篇。

| ID | 论文 / 会场 | 本次实际范围 | 状态 | 峰值 MiB | 本次耗时 s |
|---|---|---|---|---:|---:|
| 01 | Distributions as Actions: A Unified Framework for Diverse Action Spaces / ICLR 2026 | 作者CartPole-v1训练脚本；seed=1，20000步，保留12500步warmup及算法默认值。 | 限定范围跑通 | 330.1 | 36.412 |
| 02 | Consistent Low-Rank Approximation / ICLR 2026 | 作者Rice算法与数据，仅将n=3000缩为1000；d=7,k=1,c=[1.1,2,5,10,100]，5个c均完整执行。 | 限定范围跑通 | 189.2 | 12.060 |
| 03 | Fine-tuning Behavioral Cloning Policies with Preference-Based Reinforcement Learning / ICLR 2026 | 作者官方StarMDP debug配置：2 seeds、N_iterations=2（含初始化），BRIDGE与purely-online baseline；仅将seed调度改成串行。 | 限定范围跑通 | 419.7 | 92.590 |
| 04 | SpotIt: Evaluating Text-to-SQL Evaluation with Formal Verification / ICLR 2026 | 后续作者仓库保留的固定原版Vanilla verifier；BIRD question 1、ALPHA原预测、bound=2。 | 限定范围跑通 | 73.4 | 21.743 |
| 05 | Bilevel MCTS for Amortized O(1) Node Selection in Classical Planning / AAAI 2026 | 实际克隆原链接及IBM公开替代仓库，检查代码入口。 | 受阻 | — | — |
| 06 | Two Constraint Compilation Methods for Lifted Planning / AAAI 2026 | 作者 scripts.run 编译自带 blocksworld p1–p3，输出3组domain/problem PDDL。 | 限定范围跑通 | 107.3 | 2.421 |
| 10 | Extreme Value Monte Carlo Tree Search for Classical Planning / AAAI 2026 | 作者 Pyperplan 分支的 GUCT-Uniform，使用 hFF、seed=23959，求解仓库自带 airport p01 单实例。 | 限定范围跑通 | 112.1 | 2.709 |
| 18 | Managing Infinite Abstractions in Numeric Pattern Database Heuristics / AAAI 2026 | 原Zenodo版本的numeric_ipdb LLL配置，求解作者预翻译 counters-sym/problem_2.sas。 | 限定范围跑通 | 21.1 | 0.218 |
| 19 | Not Everything Is Permitted: Constrained Cartesian Abstractions for Optimal Classical Planning / AAAI 2026 | 精确论文代码与全AC3约束消歧配置，求解Autoscale21.11五块积木p01，包含PDDL翻译及h2预处理。 | 限定范围跑通 | 25.1 | 0.214 |
| 21 | Conformalized Decision Risk Assessment / ICLR 2026 | 原exp1_tradeoff notebook cells[1,2,5]完整首个Gaussian实验99 trials；ntr=ncal=100,K=100，参考MC K=10000。 | 限定范围跑通 | 399.0 | 19.598 |
| 22 | Stable coresets: Unleashing the power of uniform sampling / ICLR 2026 | 原作者Taxi实验函数；真实2024-01 Taxi全文件加载清洗后前10000行，coreset=[150,300]，3 repeats，seed=0。 | 限定范围跑通 | 1604.3 | 4.473 |
| 23 | Combinatorial Bandit Bayesian Optimization for Tensor Outputs / ICLR 2026 | 已实际检索/获取作者原生代码入口，未改写替代算法。 | 受阻 | — | — |
| 24 | A Direct Approach for Handling Contextual Bandits with Latent State Dynamics / ICML 2026 | 原始UCI信用卡数据；作者steps1–6及原生评分；seed1951、1000轮；LinUCB/BoxA/BoxB各1配置 | 限定范围跑通 | 374.3 | 35.621 |
| 25 | Near-Optimal Private Linear Regression via Iterative Hessian Mixing / ICML 2026 | 作者Fertility数据，原生90/10划分、9维；6个ε点，各5次Monte Carlo；IHM及4基线 | 限定范围跑通 | 205.7 | 3.557 |
| 26 | Simple Projection-Free Algorithm for Contextual Recommendation with Logarithmic Regret and Robustness / NeurIPS 2026 (accepted, to appear) | 检索论文、作者页面及公开GitHub仓库；未定位原生CoRectron实现 | 受阻 | — | — |
| 32 | TESO: Online Tracking of Essential Matrix by Stochastic Optimization / CVPR 2026 | 作者 CARLA-Drift 仿真数据序列 000 原始前10帧；原生 SIFT/FAISS/TESO 跟踪及原生 MAE。 | 限定范围跑通 | 322.3 | 5.017 |
| 33 | Linear Fundamental Matrix Estimation from 7 or 5 Points / CVPR 2026 | 作者 Fig.4 general 合成设置，两种噪声 σ=1，各10000次；原生5pt/7pt基线。 | 限定范围跑通 | 10.2 | 0.749 |
| 34 | Gravity-aware Partially Calibrated Absolute Pose Estimation from Affine- or Rotation-covariant Features / ECCV 2026 | 作者 README 原生无噪声单问题例，seed=1234，9种求解器；未改算法。 | 限定范围跑通 | 10.2 | 0.110 |
| 35 | Rolling Shutter Relative Pose Estimation Made Practical / ECCV 2026 | 空闲容器中限定7direct/5pt构建成功；两条既定原生命令实际启动，但均未产生第一条结果。 | 运行或结果核验未通过 | — | — |
| 36 | High-Throughput Event-Based Feature Detection and Tracking on an Embedded CPU / ECCV 2026 | 核读官方ECCV章节、作者项目页与完整作者PDF，核查作者公开代码仓库。 | 受阻 | — | — |
| 37 | MeshA*: Efficient Path Planning with Motion Primitives / AAAI 2026 | 作者Labyrinth单例：三种原生搜索均执行，weight=8，使用自带运动基元和mesh。 | 限定范围跑通 | 464.0 | 22.457 |
| 40 | Satisficing and Optimal Generalised Planning via Goal Regression / AAAI 2026 | MOOSE在全部20个Ferry训练实例上合成策略，再求解heldout p0_02。 | 限定范围跑通 | 59.6 | 10.977 |
| 41 | Scalable Bayesian Inference for Nonlinear Conservation Laws / ICML 2026 | 原始Burgers CLI两次、仅跳过绘图导入的兼容副本一次；N=8、5时间步；每次限300秒 | 超时 | 3738.0 | 901.536 |
| 42 | KASALv2: Fully Automatic 3D Rotational Symmetry Classification and Axis Localization / CVPR 2026 | 原生 headless CPU 对称性分析，作者 mesh obj_000007_ours.ply；workers=1、FPS采样512点。 | 限定范围跑通 | 584.1 | 21.548 |
| 43 | NanoGS: Training-Free Gaussian Splat Simplification / ECCV 2026 | 作者公开 drone PLY 的原生CPU NanoGS简化，ratio=.5、k=16、merge_cap=.5、opacity=.1、两项权重1。 | 限定范围跑通 | 325.6 | 13.214 |
| 44 | From Rashomon Theory to PRAXIS: Efficient Decision Tree Rashomon Sets / ICML 2026 | 作者API；完整COMPAS 4966×44；λ=0.02、ε=0.03、depth=5、lookahead=1；单核 | 限定范围跑通 | 205.3 | 3.459 |
| 45 | Fair Classification by Direct Intervention on Operating Characteristics / ICLR 2026 | 已实际检索/获取作者原生代码入口，未改写替代算法。 | 受阻 | — | — |
| 46 | FAST: Topology-Aware Frequency-Domain Distribution Matching for Coreset Selection / CVPR 2026 | 原CLI以及修正入口路径后直接调用原生pipeline，两次实际启动尝试。 | 受阻 | — | — |
| 49 | Breadth-First Search vs. Restarting Random Walks for Escaping Uninformed Heuristic Regions / AAAI 2026 | 实际下载并解包作者arXiv源工件，检查运行代码。 | 受阻 | — | — |
| 50 | Using Certifying Constraint Solvers for Generating Step-wise Explanations / AAAI 2026 | 尝试原生example.py的9×9不满足Sudoku证明生成及逐步解释。 | 受阻 | — | — |
| 51 | Right Branches Matter in Failure-based Variable Ordering Heuristics / AAAI 2026 | 克隆作者Java启发式文件并实际尝试javac编译。 | 受阻 | — | — |
| 59 | Learning-Augmented Moment Estimation on Time-Decay Models / ICLR 2026 | 原SS-SSA notebook cells[1,7,8,9,10,12,14,15]完整uniform例子，n=10,m=10000。 | 限定范围跑通 | 54.2 | 66.123 |
| 60 | Constraint Optimization of MicroPlate Designs / AAAI 2026 | 作者COMPD v1.0原始screening-8-8-1单板模型、默认策略、8个CP-SAT工作线程；16×24板，292种compound及8正8负controls。 | 限定范围跑通 | 508.2 | 55.070 |
| 61 | Probabilistic Safety Verification of Neural Policies via Predicate Abstraction / AAAI 2026 | 克隆作者PPAToolset并实际尝试公布的Docker入口。 | 受阻 | — | — |
| ACL01 | Prefix Parsing is Just Parsing / ACL 2026 main conference, Volume 2: Short Papers | 原生 benchmark_grammar_size.py 的 Earley 与 PrefixEarley 两条流水线，使用作者固定子模块 wsj500unk.grammar，核对论文表 2 的 WSJ500 行。 | 运行或结果核验未通过 | 158.9 | 5.431 |
| ACL02 | Parity-Aware Byte-Pair Encoding: Improving Cross-lingual Fairness in Tokenization / ACL 2026 main conference, Volume 1: Long Papers | 原生 Classical BPE 与 PA-BPE ratio 分支各训练 1000 次合并；FineWeb2 德语、法语各 80 文档训练、20 文档诊断编码；目标比例 1:1，单 worker。 | 限定范围跑通 | 112.8 | 9.545 |
| EMNLP01 | Every Time I Hire a Linguist, Inference Costs Go Down: On Linguistic Rules as Effective Prompt Compressors / EMNLP 2026 main according to author announcement; official Anthology/accepted-list verification pending | 拟运行作者演化得到的 spaCy 语言规则压缩器；论文报告 CPU 峰值 1.43GB，但没有找到作者可运行代码，未执行。 | 受阻 | — | — |
| EMNLP02 | FlashTrie: A GPU-Accelerated Constrained Beam Search for Generative Retrieval / EMNLP 2026 according to author repository; official main-volume verification pending | 审查作者发布的 CPU trie 分支与构建入口；原生项目强制 CUDA 编译，本机无 nvcc，未执行实验。 | 受阻 | — | — |

下列逐篇记录给出结果、限制和作者来源；完整命令、安装尝试、失败重试、原始 stdout/stderr、固定版本与各 worker 的详细清单见证据包。

**01. Distributions as Actions: A Unified Framework for Diverse Action Spaces（ICLR 2026）**

本次结果：最后10个episode训练回报均值=9.1; 最后qf1_loss=0.04086899012327194, loss记录至step=19900。 另一次默认500k尝试在300.093秒超时，峰值366.27MiB；末个日志step=434522，末10个episode训练回报均值=500.0，不视为完整500k成功或独立评估。

适用边界 / 阻塞原因：训练步数是默认500000的4%；未复现收敛曲线、全部seed或全部环境。主/Hybrid仓库没有bandit脚本。Python3.12/CPU torch2.5.1与作者旧依赖不同；tyro升级仅修CLI兼容。 额外完整500000步尝试未完成：timeout。

代码版本：`dd7d5ffb513eb15ff91c90fca5a4ff3a6d9883cf`。对应任务：`iclr01_daac_cartpole_20000`, `iclr01_daac_cartpole_20000_fixed`, `iclr01_daac_cartpole_full500k`。

来源：[来源 1](https://github.com/hejm37/da-ac)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/898c63fee61c06aa00745769c444e2ec-Paper-Conference.pdf)；[来源 3](https://github.com/hejm37/da-ac-hybrid)

**02. Consistent Low-Rank Approximation（ICLR 2026）**

本次结果：recourse=[50, 10, 5, 4, 3]; 最后近似误差比=[1.0001930090119704, 1.0009408729083373, 1.0040975953819244, 1.0060290440412274, 1.004317868906333]。

适用边界 / 阻塞原因：只复现Rice子实验，未扩展为所有数据/算法完整复现。首次300秒超时；另有仅n=1000的缩数据运行，明确区分。 原始n=3000完整配置在300秒及600秒上限内均未完成；本成功结果仅为缩数据版本。

代码版本：`d607c4f6467216c470d1e3b93989d44d5fcdec97`。对应任务：`iclr02_lra_rice_full`, `iclr02_lra_rice_n1000`, `iclr02_lra_rice_full600`。

来源：[来源 1](https://github.com/samsonzhou/consistent-LRA)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/b14d76c7266be21b338527cd25deac45-Paper-Conference.pdf)

**03. Fine-tuning Behavioral Cloning Policies with Preference-Based Reinforcement Learning（ICLR 2026）**

本次结果：原生平均累计regret：BRIDGE=0.552631，purely-online=23.047454；BC平均回报=42.811223，专家平均回报=44.357875。

适用边界 / 阻塞原因：是官方debug规模，未复现连续控制或训练专家。原多进程torch结果传输被本平台IPC socket限制；执行适配器串行调用同一作者函数，算法代码未改。原训练数值已保存，后续绘图因type1ec.sty缺失失败；单独核验saved metrics并调用作者绘图，禁用TeX。耗时/RSS包括该训练及最终后处理。

代码版本：`dc4d27f664bd69aa09f63f82669d3a191acc3ab7`。对应任务：`iclr03_bridge_debug`, `iclr03_bridge_debug_serial`, `iclr03_bridge_postprocess`, `iclr03_bridge_postprocess_fixed`。

来源：[来源 1](https://github.com/pfriedric/bridge)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/88bdfbf58591102f4b8855a22ac76437-Paper-Conference.pdf)

**04. SpotIt: Evaluating Text-to-SQL Evaluation with Formal Verification（ICLR 2026）**

本次结果：equivalent=False; verifier内部time_cost=0.6899460000000001秒。

适用边界 / 阻塞原因：单个已生成SQL对的验证，不包括生成预测、完整BIRD评测或人工判定counterexample是否真实。严格隔离固定Vanilla模块；不能把后续SpotIt+完整方法当作原论文复现。使用作者custom Z3绑定并补旧pkg_resources依赖，时间包括该依赖安装。

代码版本：`abee2baa26b2b50398c1807a46b2db126d2dda97;verieql=fb1bdaae8f3e4a544d08feffa44bc14270d99329;vanilla=71a3b5ced9553a040b049609d2250624e1a08d39`。对应任务：`iclr04_spotit_vanilla_q1`, `iclr04_spotit_native_vanilla`, `iclr04_spotit_pkg_resources`。

来源：[来源 1](https://github.com/ai-ar-research/SpotIt-plus)；[来源 2](https://www.cs.sfu.ca/~yuepeng/pubs/iclr26.pdf)；[来源 3](https://github.com/atremante26/VeriEQL/tree/71a3b5ced9553a040b049609d2250624e1a08d39)

**05. Bilevel MCTS for Amortized O(1) Node Selection in Classical Planning（AAAI 2026）**

本次结果：未执行核心实验：公开替代仓库没有实现。

适用边界 / 阻塞原因：旧链接克隆失败；IBM仓库仅README和LICENSE，无实现，未执行算法。

代码版本：`f5b9f4241f636e6b2e6f7d3716b5400addd558f3`。对应任务：未运行算法。

来源：[来源 1](https://github.com/guicho271828/downward-mcts)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/40933/44894)；[来源 3](https://github.com/IBM/downward-mcts-public)

**06. Two Constraint Compilation Methods for Lifted Planning（AAAI 2026）**

本次结果：成功编译3个实例，输出6个PDDL文件。

适用边界 / 阻塞原因：仅LiftedTCORE编译阶段；未运行LCC或下游LAMA，未复现整套比较。

代码版本：`aed8ec5676cd34e63c5523fbf20d9ebe8ece7426`。对应任务：`aaai_shared_install`, `aaai06_native_blocksworld`。

来源：[来源 1](https://github.com/Periklismant/LiftedTCORE)；[来源 2](https://github.com/LBonassi95/NumericTCORE)；[来源 3](https://github.com/Periklismant/aaai26-pddl3-benchmark)；[来源 4](https://ojs.aaai.org/index.php/AAAI/article/view/40952/44913)

**10. Extreme Value Monte Carlo Tree Search for Classical Planning（AAAI 2026）**

本次结果：求解成功：计划8步，展开8个状态，评估9次。

适用边界 / 阻塞原因：单例仅评估9次即提前找到解，未覆盖论文772问题或Fast Downward分支；仅修复此沙箱PID命名空间的RSS探针故障，算法未改。greedy为仅用h的选择准则，无独立CLI开关；外部300s硬上限。

代码版本：`64414bd787a537812595d8d59ad7d97380290c50`。对应任务：`aaai10_install`, `aaai10_native_uctuniform`, `aaai10_sympy_install`, `aaai10_native_uctuniform_retry`, `aaai10_native_uctuniform_pidfix`。

来源：[来源 1](https://github.com/guicho271828/pyperplan-mcts)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/40934/44895)；[来源 3](https://github.com/IBM/pyperplan-mcts-public)

**18. Managing Infinite Abstractions in Numeric Pattern Database Heuristics（AAAI 2026）**

本次结果：计划5步、cost=5；1个PDB、10001个PDB状态，展开6个搜索状态。

适用边界 / 阻塞原因：仅一个SAS实例，不含PDDL预处理；构建另耗186.558s、峰值1.383GiB。

代码版本：`99ec2ca273247eca05413d188d3c40b4914273cb`。对应任务：`aaai18_build`, `aaai18_native_counter2`。

来源：[来源 1](https://github.com/dgnad/numeric-fast-downward)；[来源 2](https://doi.org/10.5281/zenodo.17592540)；[来源 3](https://ojs.aaai.org/index.php/AAAI/article/download/40941/44902)

**19. Not Everything Is Permitted: Constrained Cartesian Abstractions for Optimal Classical Planning（AAAI 2026）**

本次结果：计划12步、cost=12；53个抽象状态，消歧状态计数41。

适用边界 / 阻塞原因：仅单实例；构建另耗223.119s、峰值1.309GiB。原生日志Peak memory读VmPeak虚拟内存，表中用外测RSS。

代码版本：`c4d2c76d4a28bd36c594f7c6318edc5c5f0d2398`。对应任务：`aaai19_build`, `aaai19_native_blocksworld`。

来源：[来源 1](https://zenodo.org/records/17515416)；[来源 2](https://github.com/Martin1887/scorpion/tree/cegar_disambiguation)；[来源 3](https://ojs.aaai.org/index.php/AAAI/article/view/40955/44916)

**21. Conformalized Decision Risk Assessment（ICLR 2026）**

本次结果：99 trials CREDO保守率=1.000000；NS=0.515152；Point=1.000000。

适用边界 / 阻塞原因：复现一个完整原生子实验，不包括其余参数扫描、misspecification、太阳能案例。pycddlib用CC=gcc、本地GMP头和PEP517在前次进程内构建成功；本次时间包含tqdm安装，不包含此前几何依赖设置。

代码版本：`19e884718599cd390564ddf93aff943a720f3e22`。对应任务：`iclr21_credo_gaussian`, `iclr21_credo_gaussian_retry`, `iclr21_credo_pep517`, `iclr21_credo_tqdm`。

来源：[来源 1](https://github.com/wbzhou2001/CREDO)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/11e0fdc1f9ec9303e5de60670e884e53-Paper-Conference.pdf)

**22. Stable coresets: Unleashing the power of uniform sampling（ICLR 2026）**

本次结果：size=[150,300]，uniform相对误差=[0.0006613007969131121, 0.002843222500788539]；two-step=[0.004330836011800831, 0.0013987165987615223]；one-step=[0.0019675365368628074, 0.0007152354332717177]。

适用边界 / 阻塞原因：明确缩数据、coreset网格和repeat数；并非全量论文对比。代码中的uniform与两种importance方法和误差定义保持原生。内存测量包含加载清洗全文件；依赖安装在前次进程内完成，成功耗时不含此前安装。

代码版本：`48f0233eb65269b8552eb163f275627e5447921d`。对应任务：`iclr22_stable_taxi_subset`, `iclr22_stable_taxi_subset_retry`, `iclr22_stable_taxi_fresh`, `iclr22_stable_taxi_tqdm`。

来源：[来源 1](https://github.com/amircarmel-lab/StableCoresets)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/408397eabe6bd3365730e9923975ed49-Paper-Conference.pdf)；[来源 3](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet)

**23. Combinatorial Bandit Bayesian Optimization for Tensor Outputs（ICLR 2026）**

本次结果：无原生执行结果

适用边界 / 阻塞原因：未找到可核实公开作者仓库；OpenReview网页验证墙，公共notes API及supplementary_material附件实际请求均HTTP403，未取得原生源码。

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://proceedings.iclr.cc/paper_files/paper/2026/file/4a06bfb11c00bd8a2a1cd7a522138f86-Paper-Conference.pdf)；[来源 2](https://arxiv.org/html/2602.00640v2)；[来源 3](https://openreview.net/forum?id=BgX4s1d2d0)

**24. A Direct Approach for Handling Contextual Bandits with Latent State Dynamics（ICML 2026）**

本次结果：终点belief-regret：LinUCB45.503705、BoxA48.429720、BoxB47.866844

适用边界 / 阻塞原因：原文50000轮、100种子和完整参数网格未跑；当前单种子短程不支持算法优越性；Python/NumPy/sklearn版本不同于README

代码版本：`f2736b2a2998ce62405eeb6190daa5238e01f362`。对应任务：`bandits_dependencies_01`, `bandits_native_small_01`。

来源：[来源 1](https://proceedings.mlr.press/v306/li26fk.html)；[来源 2](https://github.com/zhenli1989/bandits_latent_states)；[来源 3](https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip)

**25. Near-Optimal Private Linear Regression via Iterative Hessian Mixing（ICML 2026）**

本次结果：ε=10：IHM train MSE=0.085489、test MSE=0.063642；六点原生数组全部保存

适用边界 / 阻塞原因：论文500次及多数据集未跑；仅raw MSE；发布mask为90/10（论文表2也列90训练，正文写80/20）；缩小数据集列表改变随机数历程，不支持精确表值或总体优越性结论

代码版本：`37651364bdfa9814fa3220dd2512cdb94f6c213a`。对应任务：`hessian_fertility_native_01`, `hessian_tqdm_setup_01`, `hessian_fertility_native_02`。

来源：[来源 1](https://proceedings.mlr.press/v306/lev26a.html)；[来源 2](https://github.com/omrilev1/HessianMix)

**26. Simple Projection-Free Algorithm for Contextual Recommendation with Logarithmic Regret and Robustness（NeurIPS 2026 (accepted, to appear)）**

本次结果：无原生运行指标

适用边界 / 阻塞原因：已核对的相关仓库对应其他ONS/OGD/CP、M-convex和非平稳结构预测论文；未定位CoRectron原生代码，未用其他算法替代

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://arxiv.org/abs/2603.20826)；[来源 2](https://ssakaue.github.io/publication/)；[来源 3](https://ssakaue.github.io/publication/sakaue-2026-projection-free/)

**32. TESO: Online Tracking of Essential Matrix by Stochastic Optimization（CVPR 2026）**

本次结果：旋转 MAE xyz=[0.010070,0.010177,0.020975]°；平移=[0.00000305,0.017676,0.017241] mm；10×6 输出全部有限。

适用边界 / 阻塞原因：仅近初始标定的10帧，沿用作者名义标定初始化，GT最大漂移仅[.02,.03,.04]°；不代表155×1000帧总体表现，无GPU基线。只适配路径、循环边界和评分切片。

代码版本：`a309db1f5e5c15ac38e2cf8036f441787be33327`。对应任务：`vision32_teso_deps`, `vision32_teso_first10`。

来源：[来源 1](https://openaccess.thecvf.com/content/CVPR2026/html/Moravec_TESO_Online_Tracking_of_Essential_Matrix_by_Stochastic_Optimization_CVPR_2026_paper.html)；[来源 2](https://github.com/moravecj/teso)；[来源 3](https://cmp.felk.cvut.cz/teso/)

**33. Linear Fundamental Matrix Estimation from 7 or 5 Points（CVPR 2026）**

本次结果：independent 噪声 V-Umlaut mean R/t=36.5657°/23.9290°，5pt=14.0989°/9.0114°；dependent 设置 V-Umlaut=20.6682°/14.2807°。

适用边界 / 阻塞原因：只有两个合成点；原生协议使用GT虚拟中点及GT选解。dependent噪声只作用于V-Umlaut虚拟点，基线仍无噪声；该组不是同噪声胜负比较。随机seed未由CLI固定。

代码版本：`ce2175dd082a957d1bcdd5e5685b1bcb308c12da`。对应任务：`vision33_vumlaut_build`, `vision33_vumlaut_independent`, `vision33_vumlaut_dependent`。

来源：[来源 1](https://cvpr.thecvf.com/media/cvpr-2026/Slides/38619.pdf)；[来源 2](https://github.com/CIVA-Lab/v-umlaut)

**34. Gravity-aware Partially Calibrated Absolute Pose Estimation from Affine- or Rotation-covariant Features（ECCV 2026）**

本次结果：UP1PfAC 旋转误差3.33067e-16 rad、相对焦距误差3.39259e-15；UP2PfORI分别2.04613e-14 rad、7.83931e-14；9法均输出。

适用边界 / 阻塞原因：单例，不是论文5000次稳定性实验。原baseline UP2P循环用i代j的索引风险，未扩大nprob；编译仅链接所需原始PoseLib单元。短进程资源数含启动开销。

代码版本：`34f8fa9a2b2dcaacdbb7ffc784a80682228b288c`。对应任务：`vision34_gravity_build`, `vision34_gravity_example`。

来源：[来源 1](https://link.springer.com/chapter/10.1007/978-3-032-37211-6_19)；[来源 2](https://github.com/marcusvaltonen/eccv2026)

**35. Rolling Shutter Relative Pose Estimation Made Practical（ECCV 2026）**

本次结果：ac_rs_7direct和gs_5pt均0/31条结果，打印表头与方法名后SIGSEGV（exit -11，各0.104秒）；无有效误差数据。

适用边界 / 阻塞原因：崩溃原因未定位，不能归因内存不足或断定论文算法错误。工程补丁只删未选分支，没有补写算法。崩溃启动RSS/耗时单独保留，不作算法性能或≤8GiB成功证据；未继续修补或搜索参数。

代码版本：`d8340562be6a84a879e13ae61548f96cbdf807dd`。对应任务：`vision35_apt_index`, `vision35_apt_local_index`, `vision35_local_deb_extract`, `vision35_rs_7direct`, `vision35_rs_build_preflight`, `vision35_rs_gs5pt`, `vision35_rs_header_repair_build`, `vision35_rs_local_build`, `vision35_rs_scoped_build`, `vision35_rs_scoped_idle_build`。

来源：[来源 1](https://link.springer.com/chapter/10.1007/978-3-032-37196-6_16)；[来源 2](https://github.com/danini/rolling_shutter_made_practical)

**36. High-Throughput Event-Based Feature Detection and Tracking on an Embedded CPU（ECCV 2026）**

本次结果：未找到作者方法原生代码入口，无法启动方法实验；无实际性能或RAM数据。

适用边界 / 阻塞原因：作者公布CPU硬件为16GB/32GB，不能据此推断最低内存。仅代码可得性阻塞，不宣称算法不能在8GiB运行。

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://link.springer.com/chapter/10.1007/978-3-032-36969-7_26)；[来源 2](https://0thane.github.io/SPEEDTrack/)

**37. MeshA*: Efficient Path Planning with Motion Primitives（AAAI 2026）**

本次结果：三种搜索均成功；LazyLBA*/LBA*成本1501.56，MeshA*成本1585.57。

适用边界 / 阻塞原因：只测一个例子；MeshA*成本1585.57、两基线1501.56，不能宣称同质量加速；未跑25000+实例全套。

代码版本：`12574ff03d8d61ac153b4e4224eac2229a9577e1`。对应任务：`aaai37_build`, `aaai37_native_labyrinth`。

来源：[来源 1](https://github.com/PathPlanning/MeshAStar)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/41004/44965)

**40. Satisficing and Optimal Generalised Planning via Goal Regression（AAAI 2026）**

本次结果：处理20/20训练实例，学到5条规则；测试1/1成功，计划8步。

适用边界 / 阻塞原因：Apptainer缺失，薄启动器改用本地作者Scorpion构建，MOOSE算法未改；仅1个heldout任务，未做外部VAL验证。 本地Scorpion依赖构建峰值1.309GiB另计。

代码版本：`ce1e99bc12e9c839c5e8e870aac878fd5d31cf9e`。对应任务：`aaai40_python_deps`, `aaai40_native_planner_install`, `aaai40_native_ferry`。

来源：[来源 1](https://github.com/dillonzchen/moose)；[来源 2](https://github.com/dillonzchen/moose-dataset)；[来源 3](https://ojs.aaai.org/index.php/AAAI/article/download/40938/44899)

**41. Scalable Bayesian Inference for Nonlinear Conservation Laws（ICML 2026）**

本次结果：三次均在导入/预编译阶段超时，未得到PDE RMSE；累计入口尝试901.536秒

适用边界 / 阻塞原因：时间为三次入口尝试合计，RSS为三次最大值；仅测到准备阶段，未完成PDE原生实验，不能据此判断求解需超过8GiB；原始CLI超时和最小headless补丁全部保留

代码版本：`d711fbb68ec74755ef4029301472dfe8e23622de`。对应任务：`gpfvm_julia_setup_01`, `gpfvm_julia_setup_02`, `gpfvm_burgers_native_01`, `gpfvm_burgers_native_02`, `gpfvm_burgers_headless_native_03`。

来源：[来源 1](https://proceedings.mlr.press/v306/weiland26a.html)；[来源 2](https://github.com/timweiland/GPFiniteVolume.jl)

**42. KASALv2: Fully Automatic 3D Rotational Symmetry Classification and Axis Localization（CVPR 2026）**

本次结果：1/1模型成功；预测5重旋转对称（D(=1): n-fold Pyramidal Item），轴约[-0.01479,-0.01625,0.99976]；原生BOP JSON字段全部有限。

适用边界 / 阻塞原因：仅一个作者网格、FPS512；未提供独立类别/轴GT，不报告准确率。仅CPU对称性分析，未进行FoundationPose下游位姿评测。

代码版本：`5980894229e4209eba7769753fe4a79dc02233a5`。对应任务：`vision42_kasal_install`, `vision42_python310`, `vision42_kasal_cpu_deps`, `vision42_kasal_one_mesh`。

来源：[来源 1](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_KASALv2_Fully_Automatic_3D_Rotational_Symmetry_Classification_and_Axis_Localization_CVPR_2026_paper.html)；[来源 2](https://github.com/WangYuLin-SEU/KASAL)

**43. NanoGS: Training-Free Gaussian Splat Simplification（ECCV 2026）**

本次结果：336384→168192 splats（50%）；opacity筛至321218后合并153026对；输出2859264个浮点值全部有限，文件长度匹配。

适用边界 / 阻塞原因：作者demo模型，不是论文图像评测集；没有PSNR/SSIM/LPIPS或上游3DGS训练。仅下游原生简化范围完成。

代码版本：`cc64a752b5def8d17f9992216bfbb9e533f8364f`。对应任务：`vision43_nanogs_deps`, `vision43_nanogs_drone`。

来源：[来源 1](https://link.springer.com/chapter/10.1007/978-3-032-37095-2_29)；[来源 2](https://github.com/saliteta/NanoGS)；[来源 3](https://github.com/RongLiu-Leo/NanoGS/blob/5329d9901041b07ecb7ea31b554ce0ee417d0f21/examples/drone.ply)

**44. From Rashomon Theory to PRAXIS: Efficient Decision Tree Rashomon Sets（ICML 2026）**

本次结果：最小目标1992，与论文表16一致；28棵树；fit=0.123581秒

适用边界 / 阻塞原因：仅此数据/配置；无其他基线、召回率或跨数据验证；当前代码和依赖版本、主机不同于原论文，不能把单次计时当严格速度复现

代码版本：`ef6ce624cc40bcb00fcd39f4520364a3a05c8c80`。对应任务：`praxis_setup_venv_01`, `praxis_build_gcc_02`, `praxis_compas_native_01`。

来源：[来源 1](https://proceedings.mlr.press/v306/heile26a.html)；[来源 2](https://github.com/zakk-h/PRAXIS)

**45. Fair Classification by Direct Intervention on Operating Characteristics（ICLR 2026）**

本次结果：无原生执行结果

适用边界 / 阻塞原因：作者匿名仓库README实际GET返回HTTP403，OpenReview公共补充材料附件亦403；未取得原生代码。

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://anonymous.4open.science/r/Fair-Classification-via-Feasibility-Regions-38DE/README.md)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/f05a11e682bf9c57ab62f7cff08fbe5b-Paper-Conference.pdf)

**46. FAST: Topology-Aware Frequency-Domain Distribution Matching for Coreset Selection（CVPR 2026）**

本次结果：原入口缺 FAST.fsm；直接调用原 modules.pipeline.run 后在line41缺 dataset_training_manager。未进入数据/优化阶段。

适用边界 / 阻塞原因：另有export_distilled_dataset及visualization_stats缺失；未自行补写算法/数据管理器。导入失败内存不当作方法RAM。

代码版本：`6a218fcfdc93838634921399b0de6a36cdd29756`。对应任务：`vision46_fast_native`, `vision46_fast_pipeline_repair`。

来源：[来源 1](https://openaccess.thecvf.com/content/CVPR2026/html/Cui_FAST_Topology-Aware_Frequency-Domain_Distribution_Matching_for_Coreset_Selection_CVPR_2026_paper.html)；[来源 2](https://github.com/CAG-Research/FAST-Coreset-Selection)

**49. Breadth-First Search vs. Restarting Random Walks for Escaping Uninformed Heuristic Regions（AAAI 2026）**

本次结果：未执行核心实验：获取的论文源工件中没有可运行实现。

适用边界 / 阻塞原因：获取的工件只有LaTeX/图片等；未找到论文所述EHC/EHC-RRW可运行文件，未执行替代算法。

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://ojs.aaai.org/index.php/AAAI/article/view/41044/45005)；[来源 2](https://arxiv.org/src/2511.09549)

**50. Using Certifying Constraint Solvers for Generating Step-wise Explanations（AAAI 2026）**

本次结果：未生成解释序列：Default native entry fails because pumpkin_py is unavailable; the documented experimental pip-Pumpkin route fails at proof generation with TypeError: Model.satisfy() got an unexpected keyword argument 'prove'.

适用边界 / 阻塞原因：原生example.py默认入口缺pumpkin_py；文档experimental入口在CPMPy1.1.0/Pumpkin0.5.0上因prove关键字不兼容失败。原始Pumpkin commit d730b056需Rust源码构建，本轮未完成；没有生成证明或解释序列，初始化RSS不构成方法内存证据。

代码版本：`3374faf1842ed39bc2cc5edd269728ce5cb277d2`。对应任务：`aaai50_deps`, `aaai50_deps_fixed`, `aaai50_native_example`, `aaai50_native_experimental`。

来源：[来源 1](https://github.com/ML-KULeuven/Proof2Seq)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/38432/42394)

**51. Right Branches Matter in Failure-based Variable Ordering Heuristics（AAAI 2026）**

本次结果：编译入口启动失败，未执行CSP/COP求解。

适用边界 / 阻塞原因：javac不存在；仓库仅启发式Java文件与海报，未含作者构建工程、求解驱动或基准，未执行求解。

代码版本：`625a9586a47f19a951aa4123fb5aaf481de82c68`。对应任务：`aaai51_native_compile`。

来源：[来源 1](https://github.com/zy-nesime/right-branch-frba)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/38455/42417)

**59. Learning-Augmented Moment Estimation on Time-Decay Models（ICLR 2026）**

本次结果：t=0: SSA=901.396551, SS=1882.841404, 真L3=2156.237269；保留20个时间点。

适用边界 / 阻塞原因：只是作者仓库辅助uniform例子，不能确认论文主算法/cascaded低内存实验或CAIDA完整复现；t=0时SSA误差大于SS，不证明论文优势。

代码版本：`d2e49bb63f107ccd1f6af540cd97970d680937c9`。对应任务：`iclr59_ssa_native_uniform`。

来源：[来源 1](https://github.com/ndsoham/learning-augmented-fp-time-decay)；[来源 2](https://proceedings.iclr.cc/paper_files/paper/2026/file/1c64a54abd41035503c04119e06c28f9-Paper-Conference.pdf)

**60. Constraint Optimization of MicroPlate Designs（AAAI 2026）**

本次结果：单板生成1个最优解，objective=bound=-6006，输出308个内部孔位安排。

适用边界 / 阻塞原因：memory_test单线程240s无解返回UNKNOWN；单板用作者8线程设置。MiniZinc2.10.1/CP-SAT9.15与论文9.12不同；未做PLAID全比较。

代码版本：`271c717c6105b70f7a68c7c1bc73f355f1ff0405`。对应任务：`aaai60_minizinc_install`, `aaai60_native_memory_test`, `aaai60_native_screening`。

来源：[来源 1](https://github.com/astra-uu-se/COMPD)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/38438/42400)

**61. Probabilistic Safety Verification of Neural Policies via Predicate Abstraction（AAAI 2026）**

本次结果：容器入口启动失败，未执行神经策略验证。

适用边界 / 阻塞原因：docker命令不存在；完整依赖还包含PlaJA/Marabou/Z3/Boost/OpenBLAS及Gurobi许可，未检查许可状态，未执行策略验证。

代码版本：`7ae4cd688583cd6a0eea382c2e94d616b5cccfe3`。对应任务：`aaai61_native_start`。

来源：[来源 1](https://gitlab.cs.uni-saarland.de/vinzent/PPAToolset)；[来源 2](https://ojs.aaai.org/index.php/AAAI/article/view/40965/44926)；[来源 3](https://fai.cs.uni-saarland.de/vinzent/publications.html)；[来源 4](https://gitlab.cs.uni-saarland.de/vinzent/PPAToolset/-/blob/master/README.md)

**ACL01. Prefix Parsing is Just Parsing（ACL 2026 main conference, Volume 2: Short Papers）**

本次结果：作者程序正常完成、exit 0；表 2 Earley |G|=15981、|N|=1775 匹配；PrefixEarley |G|=43695 vs 论文 43701（少 6），|N|=5201 匹配；因此 1/2 流水线通过完整数值核验。另有 23 项功能测试通过，不算科学结果复现。

适用边界 / 阻塞原因：本次只检验表 2 的 WSJ500 行；最终原生程序 exit 0，但 PrefixEarley 的 |G|=43695，比论文 43701 少 6，其他对应列匹配，故未通过完整数值核验。差异已出现在 prefix_grammar 阶段；set 遍历、agenda 更新顺序及数值截断是静态审查发现的可能机制，尚未证实因果。此前四流水线尝试中三项匹配（含 PrefixEarley |G|=43701），CKY 前缀阶段 120s 超时，不能覆盖最终不一致。首轮选错输入的记录也保留。23 项功能测试不算科学结果复现。未覆盖 WSJ5000 与速度图；|G| 是语法规模，不是规则条数。

代码版本：`d5f5e366de9682bb23df89fe175de499fa541e2b`。对应任务：`nlp_dependencies`, `nlp_arsenal_build`, `nlp_setup_prefix_complete`, `nlp_prefix_gcc_native`, `nlp_prefix_paper_wsj500`, `nlp_prefix_earley_table2`。

来源：[来源 1](https://aclanthology.org/2026.acl-short.25/)；[来源 2](https://github.com/genlm/prefix-acl-26)；[来源 3](https://github.com/ClementeP/earleyx-acl-26-fork/blob/1171b93106d704638323d528278bfc8db3ceb23c/grammars/wsj500unk.grammar)

**ACL02. Parity-Aware Byte-Pair Encoding: Improving Cross-lingual Fairness in Tokenization（ACL 2026 main conference, Volume 1: Long Papers）**

本次结果：classical: 1000 合并，德/法诊断 token 数 47370/17973；parity_ratio: 1000 合并，德/法诊断 token 数 45861/18513

适用边界 / 阻塞原因：仅分词器训练的小规模原生分支；不是论文 30/60 语言、128k 词表实验，未复现 FLORES+ 公平性指标或下游大语言模型训练。FLORES+ 官方数据受访问条款限制，未绕过；采用作者公开的无开发集 ratio 分支。编码诊断用与作者一致的 tokenizers 词表构造，未调用需要 Transformers 的包装层。

代码版本：`c7395d469a653f3e48e80984e37593256ff8f365`。对应任务：`nlp_dependencies`, `nlp_parity_native`。

来源：[来源 1](https://aclanthology.org/2026.acl-long.342/)；[来源 2](https://github.com/swiss-ai/parity-aware-bpe)；[来源 3](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2)

**EMNLP01. Every Time I Hire a Linguist, Inference Costs Go Down: On Linguistic Rules as Effective Prompt Compressors（EMNLP 2026 main according to author announcement; official Anthology/accepted-list verification pending）**

本次结果：未实测；1.43GB 是论文表 23 的压缩阶段报告值。

适用边界 / 阻塞原因：作者公告称 EMNLP 2026 主会录用，官方论文条目尚无法核验。没有作者原生代码，未以通用 spaCy 或自行重写方法冒充复现；离线 LLM 搜索及下游问答不计入 CPU 范围。

代码版本：`—`。对应任务：未运行算法。

来源：[来源 1](https://arxiv.org/abs/2607.25335)；[来源 2](https://www.linkedin.com/posts/emmanuele-chersoni-phd-2497a1140_every-time-i-hire-a-linguist-inference-costs-activity-7497926044029501440-495c)；[来源 3](https://2026.emnlp.org/program/main_papers/)

**EMNLP02. FlashTrie: A GPU-Accelerated Constrained Beam Search for Generative Retrieval（EMNLP 2026 according to author repository; official main-volume verification pending）**

本次结果：未实测；作者所报 CPU 4GB 是索引大小，非进程峰值。

适用边界 / 阻塞原因：作者仓库标注 EMNLP 2026，官方主会条目未确认。CMake 强制 CXX CUDA，核心文件含 CUDA 头与编译依赖；MARISA_MANAGED_ALLOC=0 不解除该依赖。主算法为 GPU 算法，未用上游 MARISA 代替。

代码版本：`dfc940ddbd57cb874ef16f49e37cac943dc4f009`。对应任务：未运行算法。

来源：[来源 1](https://arxiv.org/abs/2607.10044)；[来源 2](https://github.com/Dakshitha-BA/flash-trie)；[来源 3](https://2026.emnlp.org/program/main_papers/)

**Jev 补充核查与实际测试**

TypeSafe [官方文档](https://docs.typesafe.ai/introduction) 提供托管的类型化决策 API；本轮未找到可下载的原版 Jev 权重。输出不是自由文本，不代表预测一定正确，也不代表模型可在8GiB CPU本地执行。Laya、JevLite / Open-Jev 是不同实现，不能与原版互换。

| 实际测试 | 结果 | 峰值 MiB | 耗时 s | 限制 |
|---|---|---:|---:|---|
| Fast Models, Slow Evidence — 原生缓存统计重算 | 限定范围跑通；主指标一致：工具选择Laya84.0%/Jev99.5%；路由48.5%/50.0%；RAG60.469%/60.990%；选项翻转30.3%/1.8%。仅3处ECE末位舍入差1e-5。 | 201.9 | 10.101 | 这是对缓存回答的统计重算，不是本地Jev推理，也未独立再生成作者的Jev/Laya全量回答。 |
| Laya 421M — 20条原生工具选择新推理 | 限定范围跑通；20/20有效输出，16/20正确（80.0%）；单次中位数5773.6ms；成功原生前向21次（含warmup），网络连接尝试0次。 | 2861.1 | 112.595 | 小规模资源/功能测试，不是论文全量复现；Laya是独立于TypeSafe Jev的模型。torch2.5.1+cpu/transformers4.57.6不同于论文环境；使用laya0.3.21的reviewed模型SHA55cf4c4e，未训练/调参。原生SDK将choice:11+的越界温度0.10058截为0.5，并警告受影响confidence未校准；保留原始输出。 |

在本次 Laya 0.3.21 原生实现中，choice 的 confidence 是 `1 − H(p) / log(K)`（归一化熵的补数）。证据表另列最高标签概率；这两个量都不能自动解释为答案正确率，也不能与帖子为 Jev 定义的 q 混用。

- [KITE](https://arxiv.org/html/2609.27535v1) 的百万 agent / 20 步 / 0.90 秒是表构建后的查表与随机执行，不包含实时 Jev 推理。新状态表的测量需要920.7秒；论文报告宿主48GB、执行峰值685MB。不能把这两种计时混为一谈。
- [Jev-Mobile](https://arxiv.org/abs/2609.30186) 的79%成功率对应强逐步VLM基线84%；节省73.4%模型费用限定于成功轨迹，并依赖视觉模型及托管决策服务。
- [JEV-Star](https://arxiv.org/abs/2609.27331) 的3.71美元平均费用包括3.56美元GPT-6费用；对手是最强的不作弊内置Lv7 AI。原系统不属于纯本地CPU实验。
- [Open-Jev / CallScreenBench](https://arxiv.org/html/2609.23959v1) 的AUROC .974是三种子集成，在41个留出合成场景、577个逐轮判断上测得；64.5ms为RTX 3090上的单模型测试。配方选择曾接触测试集，不能将零误报外推到真实来电总体。原文承诺公开工件不等于本轮已经取得相应权重。
- [JEV-as-a-Judge v4](https://arxiv.org/html/2609.26550v4) 已更新：1610个留出偏好对上，冻结级联准确率93.4%，GPT-6为92.5%，报告费用比例41.4%（保守口径44.0%）。该集合83%来自RewardBench；它不是任意任务上的通用收益保证。
- [Rubric Judges v2](https://arxiv.org/abs/2609.29769) 同时测整体与逐条rubric协议，费用差为16–325倍，时间差28–350倍；原帖的范围对应旧协议。此文同时指出高置信错误相关，回退模型的错误互补性会限制级联收益。
- [Jev-Mem](https://github.com/libingzheren/Jev-Mem) 后续支持本地Laya控制器，但作者明确其论文数字用的是Jev，Laya没有完成同协议评测，回答与裁判的System-Two仍另需模型。
- [Decision Hijacking](https://arxiv.org/abs/2609.28613) 的1.8%到3.5%来自510个测试情形，分别是9次和18次成功；自适应攻击有每例24次优化查询，并用5次重新采样验证。该结果的范围是论文的攻击协议，不能推导成任意部署的攻击概率。
- [Jev in the Wild](https://arxiv.org/abs/2609.30216) 的2170个项目是截至2026-09-22的生态样本。文章所说的“21篇”没有完整书目和统一统计截点，本报告不把它认作21篇已接受的顶会论文。已核对的主要条目及后续评测目前以arXiv证据为主。

本轮共核对 18 条相关论文来源，含后续评测；这不是与帖子原始21篇书目的逐项对应，也不计入上方已核查会议候选。“一周21篇、1865个新项目”缺少可复核的完整清单及统一统计口径，本轮未独立确认这两个总数。

| 相关论文 | 本轮核对 / 执行范围 |
|---|---|
| [Jev-Mobile: Jev as an Executor for Mobile GUI Agents](https://arxiv.org/abs/2609.30186) | 原系统需要托管 Jev、视觉模型及 Android 环境，未做本地全流程复现。 |
| [JEV-Star: Fast, Low-Cost StarCraft II Control with Language-Model Planning](https://arxiv.org/abs/2609.27331) | 原系统需要托管 Jev / GPT-6 及游戏环境，未实跑。 |
| [KITE: Scaling Jev Population Experiments with Sparse Flagship Calibration](https://arxiv.org/html/2609.27535v1) | 查表引擎与模型调用分开；公开工件不足以重建原始状态表，未实跑。 |
| [Open-Jev Judgments on CallScreenBench: Calibrated One-Pass Scam Screening with a Small Language Model](https://arxiv.org/abs/2609.23959) | 未找到论文专用适配器；论文速度来自 GPU，未做 CPU 推理。 |
| [Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions](https://arxiv.org/abs/2609.28613) | 攻击率依赖托管服务与限定协议，本轮未调用服务。 |
| [Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents](https://arxiv.org/abs/2609.23986) | 本地 Laya 控制器与论文 Jev 系统有区别，未重做 LoCoMo 指标。 |
| [JEV-as-a-Judge: Accept When Confident, Escalate When Unsure](https://arxiv.org/abs/2609.26550) | 核对 v4 数据；原版托管裁判及升级裁判未本地复现。 |
| [Type-Safe Decision Frameworks for Agentic 5G Control](https://arxiv.org/html/2609.33689v1) | 论文用 GPU / 托管服务及 5G 环境，未做原配置复现。 |
| [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/abs/2609.37647) | 公开缓存可供离线统计，本轮没有重算其 37 数据集。 |
| [Fast Models, Slow Evidence: A Paired and Self-Audited Evaluation of System-1 Decision Models for LLM Agent Harnesses](https://arxiv.org/abs/2610.02267) | 本轮执行公开缓存重算；另执行 Laya 原生 CPU 小样本，结果见上表。 |
| [Jev in the Wild](https://arxiv.org/abs/2609.30216) | 文献核对，未运行生态统计代码；原文确实统计了截至2026-09-22的2170个公开GitHub项目；这是生态样本数量，不是2170套有效实验，也不能推出本地CPU资源需求。 |
| [JEV vs. LLMs as Rubric Judges](https://arxiv.org/abs/2609.29769) | 文献核对，未调用托管API；帖子29–325倍费用、30–220倍时间来自旧版逐条rubric协议。v2同时比较整体与逐条协议，范围变为16–325倍费用、28–350倍时间；置信度级联需要错误互补，不能只凭q高便推广到新任务。 |
| [NumericJev](https://arxiv.org/abs/2609.28587) | 文献核对，未做原生推理；它是用多路决策树递归缩小数值区间的解码算法，不是独立本地小模型；100值网格可两轮10分支选择，但底层LLM调用资源仍须计入。 |
| [REFLEX with Jev](https://arxiv.org/abs/2609.26532) | 文献核对，未调用托管API；100任务实验报告95%成功、强模型调用减少72.7%；依赖Jev加LLM回退，外部BFCL等评测中相对廉价生成式级联的优势有限。不能换算成全流程8GB CPU。 |
| [Can Jev Judge Radiology Reports?](https://arxiv.org/abs/2609.27607) | 仅核实条目，未复现；核实到同名arXiv条目；本轮未实跑，不将医学评测准确率或CPU可行性列为已确认。 |
| [Fast Intent-Driven Service Orchestration with Jev for 6G Edge Networks](https://arxiv.org/abs/2609.23136) | 仅核实条目，未复现；核实到同名arXiv条目；本轮未实跑，不将边缘编排等同于Jev本地CPU推理。 |
| [Calibrated Decisions at Scale: Converting Police Crash Narratives into Probabilistic Crash Variables with a System One Model (Jev)](https://arxiv.org/abs/2609.24052) | 文献核对，未运行原始数据编码或托管模型；核实德州车祸叙述编码论文：筛选499500条、编码195857条，2416个盲审人工判断；Jev相对人工标签F1为0.908。此处核对摘要，不把这些规模或准确率当作8GB本地CPU运行证据。 |
| [Calibrated Decision Models for Autonomous Penetration-Testing Harnesses: JEV and Laya as System One Decision Layers for LLM-Driven Pentest Agents](https://arxiv.org/abs/2609.28940) | 文献核对，未运行渗透测试或托管模型；原文是13个漏洞的单一目标上有/无Jev各一次探索性运行，作者明确不足以建立统计显著性；Laya讨论和Rave训练方案也不能算8GB本地系统的已验证性能。 |

原清单中因本次会议范围排除的条目如下。这里只保留出处与分类，不把旧文献证据冒充本轮实测。

| 原 ID | 论文 | 会议 |
|---|---|---|
| 07 | Transforming and Encoding FTS for SAT Solving: What Helps, What Hurts | IJCAI 2026 |
| 08 | Are White Knights Worth the Trouble? Reconciling POCL and Partial-Order Plans for Plan Optimization | IJCAI 2026 |
| 09 | Variable-Oriented Adaptive Singleton Consistency | IJCAI 2026 |
| 11 | Operator-Counting Heuristics for Domain-Independent Dynamic Programming | ICAPS 2026 |
| 12 | Beyond Pruning: Leveraging Dominance Relations for Heuristic Propagation | ICAPS 2026 |
| 13 | Finding a Dominating State in a Haystack: Efficient Data Structures for Dominance Pruning | ICAPS 2026 |
| 14 | Planner Museum: Evaluating Classical Planners Over Time | ICAPS 2026 |
| 15 | Complete and Optimal Robust Planning Against Nature | ICAPS 2026 |
| 16 | When Both Grounding and Not Grounding Are Bad – a Partially Grounded Encoding of Planning into SAT | ICAPS 2026 |
| 17 | Planning with Minimal Disruption | ICAPS 2026 |
| 20 | Monotonic Variants of Saturated Cost Partitioning | ICAPS 2026 |
| 27 | General Weighted Averaging in Stochastic Gradient Descent: CLT and Adaptive Optimality | AISTATS 2026 |
| 28 | Adaptive Coverage Policies in Conformal Prediction | AISTATS 2026 |
| 29 | Mask-Conditional Conformal Prediction: Valid Uncertainty For All Missing Data Mechanisms | AISTATS 2026 |
| 30 | Online Bootstrap Inference for the Trend of Nonstationary Time Series | UAI 2026 |
| 31 | Don’t Test What You Can Deduce: Causal Discovery with Logical Inference | UAI 2026 |
| 38 | Extending Weighted Heuristic Search to Bi-Objective Search Problems | IJCAI 2026 |
| 39 | From Gridworlds to Warehouses: Adapting Lightweight One-shot Multi-Agent Pathfinding for AGVs | IJCAI 2026 |
| 47 | Computing Perfect Bayesian Equilibria, with Application to Empirical Game-Theoretic Analysis | AAMAS 2026 |
| 48 | Multi-Agent Cooperative Transportation: Optimal and Efficient Task Allocation and Path Finding | AAMAS 2026 |
| 52 | On-Demand Mutex Constraints for Numeric Planning as SMT | ICAPS 2026 |
| 53 | A Constraint Formulation for Domain Repair with Ground or Lifted Test Plans | ICAPS 2026 |
| 54 | Cartesian Abstraction Refinement for Simple Numeric Planning | ICAPS 2026 |
| 55 | Subgoaling Relaxation-based Heuristics for Numeric Planning with Infinite Actions | ICAPS 2026 |
| 56 | Incremental LTLf Synthesis | ICAPS 2026 |
| 57 | Planning as Goal Recognition: Deriving Heuristics from Intention Models | ICAPS 2026 |
| 58 | Policy Comparison Oracles for Action Policy Testing | ICAPS 2026 |

证据包不包含模型权重、完整数据集、已安装环境或作者论文全文。重跑需按记录中的仓库URL、commit、依赖与公开数据来源重新准备环境；命令中的工作区绝对路径需要映射到本机。原始失败日志保留用于审计，不能把失败的前置安装次数当作失败论文数量。
