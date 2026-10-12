# 2026年CPU／8GiB论文严格复核清单

核查日期：2026-10-11（UTC）。本版替换前版43篇清单并保留原编号。

本轮实际测量的是当前会话的代码执行环境：cgroup `memory.max=8589934592`，即8GiB（约8.59GB）；`cpu.max=800000 100000`，即8个CPU核当量配额；可见逻辑CPU与affinity为9，但不能据此宣称有9核算力配额。没有可见NVIDIA设备或nvidia-smi，未发现可用GPU。宿主/proc/meminfo不应代替容器限额。该结果不代表所有GPT会话的配置，更不是GPT模型本身的硬件需求。

**本轮没有运行任何论文实验。** 以下是正式论文、附录、作者代码和工件的资源证据审查。主张“资源条件支持指定实验”与“已在本机完整复现”必须区分；后者本轮均未确认。

默认优先选择单任务2–4GiB、串行运行的实验。8GB/8GiB任务额度不等于整台8GiB环境有足够余量；运行库、解释器、数据加载、子进程及其他常驻任务都需要计入。原协议包含超时/OOM结果时，应保留该结果，不能把“限额内评估”改写成“所有实例都能成功求解”。

## 如何理解本版分级

- A：论文主实验协议有明确CPU和≤8GB（或远低于8GiB）的用量、限额或整机配置。不是代码完整、全数据预处理或本机成功的保证；具体限制以记录为准。
- P：仅明确的数据集、参数、阶段或分支符合；整篇及未注明的上游不纳入。
- G：原文为8GiB。与当前硬上限相同，但没有完整宿主开销余量；不再仅因GB/GiB单位差别排除。
- B：CPU或完整峰值内存、实现对应性仍缺证据，不计严格确认。
- C：完整原比较或上游明确有GPU/更高资源等条件，不能按整篇CPU/8GiB推荐。

ICLR、ICML、NeurIPS、AAAI、IJCAI、CVPR、ECCV等与AAMAS/ICAPS分开理解：后两者是多智能体、规划与调度领域会议。清单不把workshop、未录用稿、期刊混称为这些会议主会论文，也不声称穷尽全部2026论文。

## 最值得开始的具体实验

1. **PRAXIS（ICML，44）／COMPAS表1**：给定二值CSV，4966×44；λ=.02、ε=.03、depth5；作者方法+全部3基线峰值均<4GB，包含导入和加载。比仅给主机RAM的论文更适合先测。
2. **CT-TAPF（AAMAS，48）**：公开地图、场景和结果；CPU、每worker4GiB，设`--num-cores 1`。没有神经训练或API上游。
3. **DA-AC（ICLR，01）**：全部训练CPU，单次<256MB/<2GB；仓库及基线可查，但Bandit脚本和环境版本要对齐；控制任务可需要7–9小时/run。
4. **Domain Repair（ICAPS，53）**：单核3.5GB；作者资源库含benchmark、测试计划、二进制及本地复现命令。
5. **On-Demand Mutex（ICAPS，52）**：单核2GB预算明确；公开实现入口尚需成功读取。
6. **FTS→SAT（IJCAI，07）**：1.75GB最有余量；artifact实际文件仍未读取成功。

FAST（46）虽有CPU/4GB实验，但公开代码有路径与辅助模块缺口，暂不当作可直接启动的首选。BRIDGE（03）从零专家训练涉及MPS；VOASC（09）只确认求解阶段，均不扩展为完整纯CPU保证。

## 原10篇的复核变化

| 论文 | 本版结论 |
| --- | --- |
| Distributions as Actions | 保留CPU/低RAM训练证据；代码公开，尚未跑通。 |
| Consistent Low-Rank Approximation | 保留8GB整机证据；严格按论文截取规模，加载阶段不可忽略。 |
| BRIDGE | 仅连续控制主实验；专家训练用过MPS，默认Slurm申请124GB须改并行。 |
| SpotIt | 仅SQL验证；原预测输入部分不公开，生成阶段不在预算内。 |
| Bilevel MCTS | 论文含grounding的8GB预算成立；实现完整性未确认。 |
| Two Constraint Compilation Methods | 论文全部实验8GB成立，benchmark已读；实现读取待补。 |
| Extreme Value MCTS | 仍只确认Fast Downward分支，不能覆盖Pyperplan全比较。 |
| Transforming and Encoding FTS | 1.75GB证据强；归档实际文件待核。 |
| White Knights | 4GB核心+8GB初始生成；原始482.5MB工件已找到，尚未解包运行。 |
| VOASC | 由A改为P；离线flatten内存未知，当前应串行求解。 |

## 新增条目索引

以下数字沿用论文原始单位，括号及范围限制不可省略。B为待核，不计“已确认适合”。

| 编号 | 会议 | 论文 | 资源证据 | 范围/等级 |
| --- | --- | --- | --- | --- |
| 44 | ICML 2026 | [From Rashomon Theory to PRAXIS: Efficient Decision Tree Rashomon Sets](https://proceedings.mlr.press/v306/heile26a.html) | COMPAS：单核；PRAXIS峰值RSS130.47MB，TreeFARMS3742.00MB，SORTeD163.50MB，RESPLIT159.61MB。 | P；限定4966样本、44二值特征，λ=0.02、ε=0.03、depth=5；RSS包含包导入、数据加载和集合计算。直接使用作者预二值化CSV；重新二值化独立峰值未报。整篇存在>8GiB实验及最高200GB基线，不能推广。 |
| 45 | ICLR 2026 | [Fair Classification by Direct Intervention on Operating Characteristics](https://proceedings.iclr.cc/paper_files/paper/2026/file/f05a11e682bf9c57ab62f7cff08fbe5b-Paper-Conference.pdf) | COMPAS每run最多10 CPU核、1GB RAM；Lawschool/BiasBios各2核8GB；ACSIncome1核32GB。 | P；只推荐COMPAS子实验，资源段覆盖作者方法和基线；清洗后5278条，普通表格处理和小MLP。当前8核配额需要降低并行，尚未实测。 |
| 46 | CVPR 2026 | [FAST: Topology-Aware Frequency-Domain Distribution Matching for Coreset Selection](https://openaccess.thecvf.com/content/CVPR2026/html/Cui_FAST_Topology-Aware_Frequency-Domain_Distribution_Matching_for_Coreset_Selection_CVPR_2026_paper.html) | FAST-EDGE：RK3588 CPU，NPU关闭、整机4GB。ImageNet逐类选择Table3称Peak RAM约782MB；摘要称1.7GB但未给完整统计边界。 | P；最明确是CIFAR-10、10%保留率，文中效率成本包括采样和early-stopping训练。不能覆盖整篇基线、全部数据集和7B LLM微调；部分ResNet特征比较使用GPU。782MB模块表不等于含加载器及下游训练的全进程RSS。 |
| 47 | AAMAS 2026 | [Computing Perfect Bayesian Equilibria, with Application to Empirical Game-Theoretic Analysis](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/WQXT1004.pdf) | PrivateGenGoof4/5每次完整TE-PSRO分别2GB/3GB，单CPU核。 | P；该段包含DQN最佳响应训练，不只是最终求均衡；小型TensorFlow全连接网络从头训练。仅覆盖PrivateGenGoof4/5，不推广到§5.3全部Bargain实验。 |
| 48 | AAMAS 2026 | [Multi-Agent Cooperative Transportation: Optimal and Efficient Task Allocation and Path Finding](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/WZSB2882.pdf) | Xeon Cooper Lake CPU；每实例500秒、论文4GB；源码执行4×1024³字节即4GiB RLIMIT_AS。 | A；作者方法、变体和基线；8×8和16×16网格，按原协议逐步扩大实例。当前应设--num-cores 1，避免默认多个4GiB worker并行。限额内超时/失败仍是原评测的一部分。 |
| 49 | AAAI 2026 | [Breadth-First Search vs. Restarting Random Walks for Escaping Uninformed Heuristic Regions](https://ojs.aaai.org/index.php/AAAI/article/view/41044/45005) | 8核Xeon Gold6226R CPU；每problem3.5GB、10分钟、5次运行。 | A；PDDL到SAS+转换也在3.5GB限制下；原论文排除了翻译超限实例，应保持这一原始测试集定义。论文称被测试搜索方法未发生OOM。8核是作者机器描述，不是单run必须8核。 |
| 50 | AAAI 2026 | [Using Certifying Constraint Solvers for Generating Step-wise Explanations](https://ojs.aaai.org/index.php/AAAI/article/view/38432/42394) | 单核Xeon Silver4514Y，8GB RAM。 | A；Python3.11、CPMPy、Pumpkin、Exact与Gurobi12.0.1；100 Sudoku、100 jobshop、102建模样例。CPU预算明确；8GB为边界配置，Gurobi许可另须具备。 |
| 51 | AAAI 2026 | [Right Branches Matter in Failure-based Variable Ordering Heuristics](https://ojs.aaai.org/index.php/AAAI/article/view/38455/42417) | 每次1 CPU核、8GB；作者集群并行96个任务。 | P；JDK23+Choco，103 CSP和186 COP实例；离线flatten资源未给，故仅确认求解阶段。当前应串行。 |
| 52 | ICAPS 2026 | [On-Demand Mutex Constraints for Numeric Planning as SMT](https://ojs.aaai.org/index.php/ICAPS/article/download/42846/50406/46947) | EPYC7763，单核，每任务2GB、1小时。 | A；Unified Planning+Z3；24域417个实例，比较ENHSP/Patty。论文明确保留解析失败、超时和内存超限统计，不能承诺所有实例都求解成功。 |
| 53 | ICAPS 2026 | [A Constraint Formulation for Domain Repair with Ground or Lifted Test Plans](https://ojs.aaai.org/index.php/ICAPS/article/download/42810/50370/46911) | 全部实验单CPU核，Intel E5-2695，3.5GB RAM。 | A；ground和lifted修复及基线；4655个ground实例、1323个lifted实例。ground评测60秒；依照作者原始实例过滤与变量语义。 |
| 54 | ICAPS 2026 | [Cartesian Abstraction Refinement for Simple Numeric Planning](https://ojs.aaai.org/index.php/ICAPS/article/download/42857/50417/46958) | 每run3.5GB、30分钟；CEGAR最多精化15分钟。 | B；RAM明确，Numeric Fast Downward实现支持CPU判断，但原文未写CPU型号/核数；严格标准下仍缺显式CPU硬件或工件配置核验。 |
| 55 | ICAPS 2026 | [Subgoaling Relaxation-based Heuristics for Numeric Planning with Infinite Actions](https://ojs.aaai.org/index.php/ICAPS/article/download/42809/50369/46910) | i9-12900KF CPU；每run8GB、30分钟。 | A；ENHSP中的DPEX启发式与NextFLAP；7域连续/离散版本，固定种子。接近当前内存上限，尚无进程峰值余量证明。 |
| 56 | ICAPS 2026 | [Incremental LTLf Synthesis](https://ojs.aaai.org/index.php/ICAPS/article/download/42814/50374/46915) | 全部实验3.6GHz CPU笔记本，8GB RAM，单实例最多3600秒。 | A；ISABEL-DP与ISABEL-FP比较；四套基准。论文明确TIREWORLD大实例触及8GB并OOM，预算内评测不等于全部实例可完成。 |
| 57 | ICAPS 2026 | [Planning as Goal Recognition: Deriving Heuristics from Intention Models](https://ojs.aaai.org/index.php/ICAPS/article/download/42832/50392/46933) | AMD EPYC7763单核；全部实验8GB、1800秒。 | A；C++ LAPKT、Downward Lab；使用Fast Downward grounding，含公理时回退Tarski。实验限额明确，但接近当前8GiB上限。 |
| 58 | ICAPS 2026 | [Policy Comparison Oracles for Action Policy Testing](https://ojs.aaai.org/index.php/ICAPS/article/download/42859/50419/46960) | Intel E5-2660 CPU；每task8GiB、2小时。 | P；仅测试阶段；使用先前工作已训练好的ASNet策略。上游策略训练资源不在8GiB证据内。并且8GiB正好是本会话硬上限，没有常驻开销余量。 |
| 59 | ICLR 2026 | [Learning-Augmented Moment Estimation on Time-Decay Models](https://proceedings.iclr.cc/paper_files/paper/2026/file/1c64a54abd41035503c04119e06c28f9-Paper-Conference.pdf) | 合成cascaded实验SSA68.86/112.32MB，SS74.63/117.27MB，CountSketch65.96MB；作者整机M2/16GB。 | B；未确认这些数值是完整进程峰值或oracle总和；全篇CAIDA另用ChatGPT/Gemini和LSTM。不能称纯本地CPU全篇。 |
| 60 | AAAI 2026 | [Constraint Optimization of MicroPlate Designs](https://ojs.aaai.org/index.php/AAAI/article/view/38438/42400) | 8核Apple M3、16GB主机；特定memory_test.dzn实例原文写COMPD用“3 Gb”，5分钟内证明最优。 | P；只涵盖指定COMPD实例，不把原文Gb静默改写为精确GB/RSS；PLAID基线同例用“75 Gb”，整套比较不符合8GiB预算。 |
| 61 | AAAI 2026 | [Probabilistic Safety Verification of Neural Policies via Predicate Abstraction](https://ojs.aaai.org/index.php/AAAI/article/view/40965/44926) | AMD EPYC9654 CPU；每次12小时、4GB内存上限。 | P；仅使用已有DQN策略进行验证，C++、Marabou和Z3；从头训练DQN未获4GB证明。单run最长12小时，不能把低RAM理解为短时复现。 |

本版共保存61条研究记录（前版43条＋新增18条）：A 21条、P 12条、G 3条、B 20条、C 5条。这不是已成功复现论文的数量。新增中2条B只作待核保留，其余也必须遵守指定范围和代码可用性限制。


## A：主实验有CPU与内存预算证据


### 01. Distributions as Actions: A Unified Framework for Diverse Action Spaces

**会议与分级：** ICLR 2026；A。

**研究内容：** 强化学习：统一离散、连续、混合动作空间。

**硬件证据：** Bandit：每次单 CPU 核、<256MB；其余任务：每次单核、<2GB。 定位：p.27，Appendix D.9。

**适用范围与限制：** 原文覆盖全部训练；种子/配置应串行或受限并行。Bandit 2000步多数<10秒；MuJoCo 100万步约7小时，LR-AC约9小时。

**数据／环境：** Bandit、Gym、MuJoCo、DMC、MinAtar、PAMDP。

**作者代码／实验入口：** [代码／数据](https://github.com/hejm37/da-ac)。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/898c63fee61c06aa00745769c444e2ec-Paper-Conference.pdf)。

**本轮严格复核：** 主仓库和[hybrid仓库](https://github.com/hejm37/da-ac-hybrid)已打开；主训练脚本在CUDA不可用时回退CPU，W&B默认关闭。包含多种基线，不依赖外部API。Bandit原始脚本尚未逐一定位；仓库Hopper-v4与论文v3应对齐。以上不等于已安装或运行成功。


### 02. Consistent Low-Rank Approximation

**会议与分级：** ICLR 2026；A。

**研究内容：** 在线低秩近似与输出稳定性。

**硬件证据：** 全部实验：Ryzen 7 5700U，8核，8GB RAM。 定位：p.9，§4；附录G。

**适用范围与限制：** 匹配论文原实验规模；Landmark使用前5000行，不能扩大解释为完整71952行逐前缀精确SVD都很便宜。

**数据／环境：** SuiteSparse Landmark、UCI Skin等论文实验。

**作者代码／实验入口：** [代码／数据](https://github.com/samsonzhou/consistent-LRA)。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/b14d76c7266be21b338527cd25deac45-Paper-Conference.pdf)。

**本轮严格复核：** 作者仓库包含Landmark、Skin、Rice数据和脚本。Landmark脚本先读入并稠密化完整矩阵再截前5000行，不能用截取后数组大小推导全进程峰值。Skin仅前3000行。论文8GB整机证据保留，仍需实际RSS测量。


### 05. Bilevel MCTS for Amortized O(1) Node Selection in Classical Planning

**会议与分级：** AAAI 2026；A。

**研究内容：** Nεbula：双层MCTS与树折叠。

**硬件证据：** Xeon 6258R；全部实验默认5分钟、8GB，包含PDDL grounding。 定位：p.2，实验约定。

**适用范围与限制：** 原文实验额度明确；部分困难实例会耗尽额度，这是评估结果之一。论文给了代码地址，但本轮未确认其可构建状态。

**数据／环境：** IPC2018、IPC2023，随机方法5 seeds。

**作者代码／实验入口：** [代码／数据](https://github.com/guicho271828/downward-mcts)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/view/40933/44894)。

**本轮严格复核：** 论文写代码将发布；指定downward-mcts仓库本轮工具无法读取。保留CPU/8GB/含grounding的论文预算结论，代码完整性未确认。工具读取失败不等于仓库不存在。


### 06. Two Constraint Compilation Methods for Lifted Planning

**会议与分级：** AAAI 2026；A。

**研究内容：** LiftedTCORE/LCC：规划约束编译。

**硬件证据：** 全部实验：Xeon Gold6140M，1800秒、8GB。 定位：p.6，§6。

**适用范围与限制：** 包括编译后LAMA求解；适合按实例串行复现。

**数据／环境：** 7域、280个PDDL3问题；作者benchmark公开。

**作者代码／实验入口：** [代码／数据](https://github.com/Periklismant/LiftedTCORE) ; [代码／数据](https://github.com/LBonassi95/NumericTCORE) ; [代码／数据](https://github.com/Periklismant/aaai26-pddl3-benchmark)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/view/40952/44913)。

**本轮严格复核：** [benchmark仓库](https://github.com/Periklismant/aaai26-pddl3-benchmark)已打开，包含7域ground/nonground PDDL；LiftedTCORE/LCC实现仓库本轮读取失败，未验证编译和完整依赖。


### 07. Transforming and Encoding FTS for SAT Solving: What Helps, What Hurts

**会议与分级：** IJCAI 2026；A。

**研究内容：** 事实分解状态系统的SAT编码与规划。

**硬件证据：** AMD EPYC9654；每次1.75GB，1800秒。 定位：p.8，§6；p.10存档引用。

**适用范围与限制：** 论文算法与比较实验有统一预算；内存余量较好。存档DOI由论文确认，本轮未下载构建。

**数据／环境：** IPC 2026个实例、FTS 431个实例。

**作者代码／实验入口：** [代码／数据](https://doi.org/10.5281/zenodo.20444380)。

**原文与会议来源：** [论文／来源](https://www.ijcai.org/proceedings/2026/0249.pdf)。

**本轮严格复核：** 正式论文CPU/1.75GB/1800秒证据保留；[归档DOI](https://doi.org/10.5281/zenodo.20444380)的实际文件本轮未成功读取，不能声称已完成数据和代码下载核验。


### 08. Are White Knights Worth the Trouble? Reconciling POCL and Partial-Order Plans for Plan Optimization

**会议与分级：** IJCAI 2026；A。

**研究内容：** 用MaxSAT优化偏序计划。

**硬件证据：** i5-1240P；初始计划生成限8GB；核心编码+求解限4GB，各30分钟。 定位：p.5，§4。

**适用范围与限制：** 宿主32GB但任务额度明确；分阶段/实例串行。核心优化适合8GB整机优先验证。

**数据／环境：** IPC计划；SCORPION MAIDU生成、PySAT RC2优化。

**作者代码／实验入口：** [代码／数据](https://github.com/HarrisonOates/popgen) ; [代码／数据](https://zenodo.org/records/19950104)。

**原文与会议来源：** [论文／来源](https://www.ijcai.org/proceedings/2026/0688.pdf)。

**本轮严格复核：** [原始Zenodo工件](https://zenodo.org/records/19950104)已成功打开：482.5MB code.zip，说明包含Popgen快照、domains、scripts和data。尚未下载解包，未确认所有初始计划是否打包。核心4GB含编码与求解；从零流程仍包含8GB初始计划生成。


### 11. Operator-Counting Heuristics for Domain-Independent Dynamic Programming

**会议与分级：** ICAPS 2026；A。

**研究内容：** 用算子计数/线性约束强化通用动态规划。

**硬件证据：** AMD EPYC7742单核，内存限3.5GB。 定位：p.8，实验；p.10存档。

**适用范围与限制：** 搜索30分钟；算子计数预处理最多2小时，低内存不等于整套耗时短。

**数据／环境：** 论文OR组合优化基准。

**作者代码／实验入口：** [代码／数据](https://doi.org/10.5281/zenodo.19114180)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42839/50399/46940)。


### 12. Beyond Pruning: Leveraging Dominance Relations for Heuristic Propagation

**会议与分级：** ICAPS 2026；A。

**研究内容：** 把支配关系用于启发式传播。

**硬件证据：** AMD EPYC7551；每次4GB、30分钟。 定位：p.8，实验。

**适用范围与限制：** 主实验原文明确CPU与额度。

**数据／环境：** IPC1998–2023，排除论文指定不支持的任务类型。

**作者代码／实验入口：** [代码／数据](https://doi.org/10.5281/zenodo.19133258)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42833/50393/46934)。


### 13. Finding a Dominating State in a Haystack: Efficient Data Structures for Dominance Pruning

**会议与分级：** ICAPS 2026；A。

**研究内容：** 高效支配查询的数据结构。

**硬件证据：** AMD EPYC7551；每run 4GB、30分钟。 定位：p.6，§6实验设置。

**适用范围与限制：** 硬件充分；正式PDF的Zenodo引用显示缺失占位，具体代码存档仍待定位。

**数据／环境：** IPC1998–2023。

**作者代码／实验入口：** 论文声称Zenodo发布，但具体记录未确认。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42834/50394/46935)。


### 14. Planner Museum: Evaluating Classical Planners Over Time

**会议与分级：** ICAPS 2026；A。

**研究内容：** 统一复现和比较历代规划器。

**硬件证据：** Xeon Gold6130，4GiB约4.29GB，30分钟。 定位：p.4，Results。

**适用范围与限制：** 资源限额符合≤8GB；全套横跨大量规划器/实例，总运行量较大。

**数据／环境：** 42个IPC/Autoscale域；历代规划器。

**作者代码／实验入口：** [代码／数据](https://github.com/mrlab-ai/planner-museum/tree/icaps-2026) ; [代码／数据](https://doi.org/10.5281/zenodo.17861051)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42852/50412/46953)。


### 15. Complete and Optimal Robust Planning Against Nature

**会议与分级：** ICAPS 2026；A。

**研究内容：** 针对外部变化的完备最优鲁棒规划。

**硬件证据：** Ryzen9 7950X CPU；4GB、1800秒。 定位：p.8，实验与代码脚注。

**适用范围与限制：** LAMA子问题与COMP/ECOMP实验有明确CPU预算。

**数据／环境：** 5个鲁棒规划域，包括AUV和Service Robot。

**作者代码／实验入口：** [代码／数据](https://github.com/lchrpa/Robust-Plans-ICAPS-26)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42812/50372/46913)。


### 16. When Both Grounding and Not Grounding Are Bad – a Partially Grounded Encoding of Planning into SAT

**会议与分级：** ICAPS 2026；A。

**研究内容：** 部分实例化的SAT规划编码。

**硬件证据：** AMD EPYC9654；8GB、1800秒。 定位：p.7，Experimental Evaluation。

**适用范围与限制：** 按原始规划基准逐实例运行。

**数据／环境：** 标准lifted planning benchmark；VAL验证。

**作者代码／实验入口：** [代码／数据](https://github.com/galvusdamor/PGSAT) ; [代码／数据](https://github.com/abcorrea/htg-domains)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42815/50375/46916)。


### 17. Planning with Minimal Disruption

**会议与分级：** ICAPS 2026；A。

**研究内容：** 兼顾行动成本和执行扰动的规划。

**硬件证据：** Xeon E5-2666 v3；8GB、1800秒。 定位：p.5，实验设置。

**适用范围与限制：** Fast Downward+A*/LM-Cut；算法代码未找到明确独立发布地址。

**数据／环境：** IPC规划域，作者采用downward-benchmarks。

**作者代码／实验入口：** 基准 [代码／数据](https://github.com/aibasel/downward-benchmarks) ；算法代码未确认。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42831/50391/46932)。


### 48. Multi-Agent Cooperative Transportation: Optimal and Efficient Task Allocation and Path Finding

**会议与分级：** AAMAS 2026；A。

**研究内容：** 协作搬运的任务分配与多智能体寻路（CT-TCBS）

**硬件证据：** Xeon Cooper Lake CPU；每实例500秒、论文4GB；源码执行4×1024³字节即4GiB RLIMIT_AS。 定位：物理p7/印刷p2956，§5；multiprocessing_runner.py。

**适用范围与限制：** 作者方法、变体和基线；8×8和16×16网格，按原协议逐步扩大实例。当前应设--num-cores 1，避免默认多个4GiB worker并行。限额内超时/失败仍是原评测的一部分。

**代码与可用性：** [作者入口](https://github.com/BlankNing/CTAPF_CT_TCBS)。通过公开API/raw读取代码，地图/场景、camera-ready CSV和生成器已确认；NumPy/SciPy，无训练或GPU/API上游。未执行实验。

**原文与会议来源：** [来源1](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/WZSB2882.pdf)。


### 49. Breadth-First Search vs. Restarting Random Walks for Escaping Uninformed Heuristic Regions

**会议与分级：** AAAI 2026；A。

**研究内容：** 广度优先与重启随机游走逃离启发式平台

**硬件证据：** 8核Xeon Gold6226R CPU；每problem3.5GB、10分钟、5次运行。 定位：p7/印刷37149，§5实验；p8结果。

**适用范围与限制：** PDDL到SAS+转换也在3.5GB限制下；原论文排除了翻译超限实例，应保持这一原始测试集定义。论文称被测试搜索方法未发生OOM。8核是作者机器描述，不是单run必须8核。

**代码与可用性：** 主文未给直接Github链接，技术报告与实验工件入口仍需补核；不能宣称代码已齐。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/AAAI/article/view/41044/45005)。


### 50. Using Certifying Constraint Solvers for Generating Step-wise Explanations

**会议与分级：** AAAI 2026；A。

**研究内容：** 由可认证约束求解器生成逐步解释

**硬件证据：** 单核Xeon Silver4514Y，8GB RAM。 定位：p6/印刷14197，Experimental setup。

**适用范围与限制：** Python3.11、CPMPy、Pumpkin、Exact与Gurobi12.0.1；100 Sudoku、100 jobshop、102建模样例。CPU预算明确；8GB为边界配置，Gurobi许可另须具备。

**代码与可用性：** [作者入口](https://github.com/ML-KULeuven/Proof2Seq)。作者仓库已成功读取；没有GPU/LLM依赖。尚未安装运行，不能保证当前环境具备Gurobi许可。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/AAAI/article/view/38432/42394)。


### 52. On-Demand Mutex Constraints for Numeric Planning as SMT

**会议与分级：** ICAPS 2026；A。

**研究内容：** 按需求生成互斥约束以加速数值规划SMT编码

**硬件证据：** EPYC7763，单核，每任务2GB、1小时。 定位：p3，Experimental Results。

**适用范围与限制：** Unified Planning+Z3；24域417个实例，比较ENHSP/Patty。论文明确保留解析失败、超时和内存超限统计，不能承诺所有实例都求解成功。

**代码与可用性：** [作者入口](https://github.com/udg-lai/ICAPS26-Mutex-On-Demand-SMT)。论文给出实现仓库，工具本轮未成功读取；硬件证据已确认，代码完整性尚未确认。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42846/50406/46947)。


### 53. A Constraint Formulation for Domain Repair with Ground or Lifted Test Plans

**会议与分级：** ICAPS 2026；A。

**研究内容：** 用约束规划修复规划领域模型

**硬件证据：** 全部实验单CPU核，Intel E5-2695，3.5GB RAM。 定位：p7，Experiments。

**适用范围与限制：** ground和lifted修复及基线；4655个ground实例、1323个lifted实例。ground评测60秒；依照作者原始实例过滤与变量语义。

**代码与可用性：** [作者入口](https://github.com/plaans/resources-icaps-26-domrep)。已打开作者资源库，含benchmark、ground/lifted测试计划、Aries子模块与预构建二进制、本地/Slurm复现实验命令和结果摘要。未运行。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42810/50370/46911)。


### 55. Subgoaling Relaxation-based Heuristics for Numeric Planning with Infinite Actions

**会议与分级：** ICAPS 2026；A。

**研究内容：** 无限动作空间数值规划的子目标松弛启发式

**硬件证据：** i9-12900KF CPU；每run8GB、30分钟。 定位：p7 Experiments。

**适用范围与限制：** ENHSP中的DPEX启发式与NextFLAP；7域连续/离散版本，固定种子。接近当前内存上限，尚无进程峰值余量证明。

**代码与可用性：** [作者入口](https://github.com/hstairs/jpddlplus/tree/enhsp25-dpex)。论文给作者分支和数据入口；本轮工具未成功读取对应分支，未跑实验。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42809/50369/46910)。


### 56. Incremental LTLf Synthesis

**会议与分级：** ICAPS 2026；A。

**研究内容：** 增量有限轨迹线性时序逻辑综合

**硬件证据：** 全部实验3.6GHz CPU笔记本，8GB RAM，单实例最多3600秒。 定位：p6 §7；p8对OOM的讨论。

**适用范围与限制：** ISABEL-DP与ISABEL-FP比较；四套基准。论文明确TIREWORLD大实例触及8GB并OOM，预算内评测不等于全部实例可完成。

**代码与可用性：** [作者入口](https://github.com/GianmarcoDIAG/ISabel/)。作者给公开实现入口；本轮工具未成功读取。LYDIA、MONA、SYFT/CUDD工具链需安装核验。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42814/50374/46915)。


### 57. Planning as Goal Recognition: Deriving Heuristics from Intention Models

**会议与分级：** ICAPS 2026；A。

**研究内容：** 将目标识别模型转化为搜索启发式

**硬件证据：** AMD EPYC7763单核；全部实验8GB、1800秒。 定位：p7 Experimental Results。

**适用范围与限制：** C++ LAPKT、Downward Lab；使用Fast Downward grounding，含公理时回退Tarski。实验限额明确，但接近当前8GiB上限。

**代码与可用性：** 已核正式原文，尚未定位到完整复现仓库，未验证编译。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42832/50392/46933)。


## P：只确认指定子实验或阶段


### 03. Fine-tuning Behavioral Cloning Policies with Preference-Based Reinforcement Learning

**会议与分级：** ICLR 2026；P。

**研究内容：** BRIDGE：离线模仿与在线偏好强化学习。

**硬件证据：** 连续控制：每seed单CPU核，<2GB RAM。 定位：p.14，Appendix A。

**适用范围与限制：** 仅连续控制分支有<2GB依据；离散分支使用32GB M1 Max。连续控制200次迭代最长约8小时；原文20seed并行不能直接照搬到8GB整机。

**数据／环境：** 离散MDP与连续控制环境，具体采用论文Appendix A协议。

**作者代码／实验入口：** [代码／数据](https://github.com/pfriedric/bridge)。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/88bdfbf58591102f4b8855a22ac76437-Paper-Conference.pdf)。

**本轮严格复核：** [官方README](https://github.com/pfriedric/bridge)明确专家训练使用mps和cpu；MPS涉及Apple GPU。首次连续控制运行还要预计算候选策略embedding。Reacher/PPO和Ant/TD3专家训练没有独立低内存证明。[默认SLURM脚本](https://github.com/pfriedric/bridge/blob/main/run_continuous_slurm.sh)请求20CPU/124GB，不能直接在当前环境照跑。<2GB仅保留为连续主实验每seed证据。


### 04. SpotIt: Evaluating Text-to-SQL Evaluation with Formal Verification

**会议与分级：** ICLR 2026；P。

**研究内容：** 用形式化验证重新评估Text-to-SQL。

**硬件证据：** 每次验证器调用：1物理CPU核，8GB内存，600秒。 定位：p.7，§5。

**适用范围与限制：** CPU范围是对已生成SQL进行验证；不包括重新调用/训练LLM生成全部预测。原版代码与全部预测公开性仍需进一步确认。

**数据／环境：** BIRD-dev 1533问题；另有Spider2 SQLite子集。

**作者代码／实验入口：** 原版独立仓库未确认；勿把后续SpotIt+直接当作原版复现。

**原文与会议来源：** [论文／来源](https://www.cs.sfu.ca/~yuepeng/pubs/iclr26.pdf)。

**本轮严格复核：** 10种方法的SQL预测由作者向开发者索取，部分方法及预测未公开。8GB只覆盖验证；生成涉及GPT-4o/大模型。[SpotIt+](https://github.com/ai-ar-research/SpotIt-plus)是后续项目，不能代替原版完整复现。


### 09. Variable-Oriented Adaptive Singleton Consistency

**会议与分级：** IJCAI 2026；P。

**研究内容：** VOASC：约束满足中的自适应传播。

**硬件证据：** 每run：1 CPU核、8GB RAM。 定位：p.5，§5 Environment。

**适用范围与限制：** 原服务器512GB/96路并行；可改为串行。主要求解器实验满足单任务额度，预先MiniZinc flattening内存未单列。

**数据／环境：** MiniZinc CSP/COP、Choco、JDK21。

**作者代码／实验入口：** [代码／数据](https://github.com/tiger510520/VOASC)。

**原文与会议来源：** [论文／来源](https://www.ijcai.org/proceedings/2026/0266.pdf)。

**本轮严格复核：** 严格复核由A调整为P：1核/8GB证明覆盖求解run；原始MiniZinc预flatten的峰值未给。作者还排除1小时内不能完成flatten的大实例。仓库已打开，含inst/lib/src/org与MainSolve.class；当前须串行，不能照搬96任务并发。


### 10. Extreme Value Monte Carlo Tree Search for Classical Planning

**会议与分级：** AAAI 2026；P。

**研究内容：** 极值分布驱动的MCTS bandit。

**硬件证据：** Fast Downward/IPC2018分支：Xeon6258R、5分钟、8GB。 定位：p.6–7，Fast Downward实验。

**适用范围与限制：** 另一Pyperplan分支未独立给出相同内存限额；不能把整篇标成完全8GB已证实。

**数据／环境：** IPC2018；Pyperplan另一组为24域772问题。

**作者代码／实验入口：** [代码／数据](https://github.com/guicho271828/pyperplan-mcts)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/view/40934/44895)。

**本轮严格复核：** 仅确认Fast Downward/IPC2018分支；Pyperplan的772问题比较使用10000节点预算，不能外推同一RAM条件。指定pyperplan-mcts仓库本轮读取失败。


### 44. From Rashomon Theory to PRAXIS: Efficient Decision Tree Rashomon Sets

**会议与分级：** ICML 2026；P。

**研究内容：** 近最优稀疏决策树集合（Rashomon sets）

**硬件证据：** COMPAS：单核；PRAXIS峰值RSS130.47MB，TreeFARMS3742.00MB，SORTeD163.50MB，RESPLIT159.61MB。 定位：正式PDF p8 Table1、p63 Machines Used。

**适用范围与限制：** 限定4966样本、44二值特征，λ=0.02、ε=0.03、depth=5；RSS包含包导入、数据加载和集合计算。直接使用作者预二值化CSV；重新二值化独立峰值未报。整篇存在>8GiB实验及最高200GB基线，不能推广。

**代码与可用性：** [作者入口](https://github.com/zakk-h/PRAXIS)。作者实现与示例公开；praxis分支examples/compas_binarized.csv实读尺寸与论文一致；没有运行实验或确认全表一键脚本。

**补充子实验：** 缓存消融（p57 Table7，λ=.003、ε=.03、depth5）：Bank-217 开3.05GB/关0.28GB；Covertype-45 2.42/2.41GB；Credit-225 4.24/0.23GB；Diabetes-121 .76/.68GB；Wine-64 .75/.52GB；Churn仅关缓存5.59GB，开8.60GB。这些数值不证明外部基线也符合。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v306/heile26a.html) · [来源2](https://raw.githubusercontent.com/mlresearch/v306/main/assets/heile26a/heile26a.pdf) · [来源3](https://arxiv.org/pdf/2606.00202)。


### 45. Fair Classification by Direct Intervention on Operating Characteristics

**会议与分级：** ICLR 2026；P。

**研究内容：** 公平分类与ROC操作点约束优化

**硬件证据：** COMPAS每run最多10 CPU核、1GB RAM；Lawschool/BiasBios各2核8GB；ACSIncome1核32GB。 定位：p38 Appendix A.6.2。

**适用范围与限制：** 只推荐COMPAS子实验，资源段覆盖作者方法和基线；清洗后5278条，普通表格处理和小MLP。当前8核配额需要降低并行，尚未实测。

**代码与可用性：** [作者入口](https://anonymous.4open.science/r/Fair-Classification-via-Feasibility-Regions-38DE/README.md)。论文匿名代码入口本轮HTTP403，不能视为已拿到可复现代码。LPP使用CVXPY+Gurobi，文中给SCS fallback，替换求解器需验证。

**原文与会议来源：** [来源1](https://proceedings.iclr.cc/paper_files/paper/2026/file/f05a11e682bf9c57ab62f7cff08fbe5b-Paper-Conference.pdf)。


### 46. FAST: Topology-Aware Frequency-Domain Distribution Matching for Coreset Selection

**会议与分级：** CVPR 2026；P。

**研究内容：** 无DNN的频域分布匹配与coreset选择

**硬件证据：** FAST-EDGE：RK3588 CPU，NPU关闭、整机4GB。ImageNet逐类选择Table3称Peak RAM约782MB；摘要称1.7GB但未给完整统计边界。 定位：p6 §4.1；p7 Table2/§4.2；p12 Appendix A。

**适用范围与限制：** 最明确是CIFAR-10、10%保留率，文中效率成本包括采样和early-stopping训练。不能覆盖整篇基线、全部数据集和7B LLM微调；部分ResNet特征比较使用GPU。782MB模块表不等于含加载器及下游训练的全进程RSS。

**代码与可用性：** [作者入口](https://github.com/CAG-Research/FAST-Coreset-Selection)。README要求额外dataset_training_manager等辅助模块，入口目录与公开树存在不一致；Issue1报告复现材料缺漏（第三方反馈）。默认视觉输入为pixels，无需预训练网络。没有完成安装或运行。

**原文与会议来源：** [来源1](https://openaccess.thecvf.com/content/CVPR2026/html/Cui_FAST_Topology-Aware_Frequency-Domain_Distribution_Matching_for_Coreset_Selection_CVPR_2026_paper.html) · [来源2](https://arxiv.org/html/2511.19476v3) · [来源3](https://github.com/CAG-Research/FAST-Coreset-Selection/issues/1)。


### 47. Computing Perfect Bayesian Equilibria, with Application to Empirical Game-Theoretic Analysis

**会议与分级：** AAMAS 2026；P。

**研究内容：** PBE-CFR与不完全信息博弈的经验博弈分析

**硬件证据：** PrivateGenGoof4/5每次完整TE-PSRO分别2GB/3GB，单CPU核。 定位：物理p7，印刷p1835，§5.2。

**适用范围与限制：** 该段包含DQN最佳响应训练，不只是最终求均衡；小型TensorFlow全连接网络从头训练。仅覆盖PrivateGenGoof4/5，不推广到§5.3全部Bargain实验。

**代码与可用性：** [作者入口](https://github.com/ckonicki-umich/AAMAS26/)。参数生成器、仿真器、PBE-CFR与DQN公开；无预训练/API依赖。参数JSON读取路径有目录不一致、依赖版本未固定，需要整理后运行。

**原文与会议来源：** [来源1](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/WQXT1004.pdf)。


### 51. Right Branches Matter in Failure-based Variable Ordering Heuristics

**会议与分级：** AAAI 2026；P。

**研究内容：** CSP/COP的失败驱动变量选择启发式

**硬件证据：** 每次1 CPU核、8GB；作者集群并行96个任务。 定位：p4/印刷14400，Environment/Benchmark。

**适用范围与限制：** JDK23+Choco，103 CSP和186 COP实例；离线flatten资源未给，故仅确认求解阶段。当前应串行。

**代码与可用性：** [作者入口](https://github.com/zy-nesime/right-branch-frba)。论文给仓库入口，但本轮网页工具读取失败；不据此断言仓库不存在。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/AAAI/article/view/38455/42417)。


### 58. Policy Comparison Oracles for Action Policy Testing

**会议与分级：** ICAPS 2026；P。

**研究内容：** 通过多策略比较发现动作策略错误

**硬件证据：** Intel E5-2660 CPU；每task8GiB、2小时。 定位：p3–4 Experimental Setup。

**适用范围与限制：** 仅测试阶段；使用先前工作已训练好的ASNet策略。上游策略训练资源不在8GiB证据内。并且8GiB正好是本会话硬上限，没有常驻开销余量。

**代码与可用性：** 论文引用既有策略/实现；本轮未核完整预训练策略获取链。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42859/50419/46960)。


### 60. Constraint Optimization of MicroPlate Designs

**会议与分级：** AAAI 2026；P。

**研究内容：** 实验微孔板设计的约束优化（COMPD）

**硬件证据：** 8核Apple M3、16GB主机；特定memory_test.dzn实例原文写COMPD用“3 Gb”，5分钟内证明最优。 定位：p6/印刷14248。

**适用范围与限制：** 只涵盖指定COMPD实例，不把原文Gb静默改写为精确GB/RSS；PLAID基线同例用“75 Gb”，整套比较不符合8GiB预算。

**代码与可用性：** [作者入口](https://github.com/astra-uu-se/COMPD)。作者仓库已打开，含evaluation_aaai26和MiniZinc模型，README要求v1.0；深层memory_test.dzn文件未实读。无神经训练/GPU/API。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/AAAI/article/view/38438/42400)。


### 61. Probabilistic Safety Verification of Neural Policies via Predicate Abstraction

**会议与分级：** AAAI 2026；P。

**研究内容：** 神经策略的概率安全验证与谓词抽象

**硬件证据：** AMD EPYC9654 CPU；每次12小时、4GB内存上限。 定位：p6/印刷36443。

**适用范围与限制：** 仅使用已有DQN策略进行验证，C++、Marabou和Z3；从头训练DQN未获4GB证明。单run最长12小时，不能把低RAM理解为短时复现。

**代码与可用性：** [作者入口](https://gitlab.cs.uni-saarland.de/vinzent/PPAToolset)。作者主页链接工具；README搜索索引列出JANI模型、谓词和.nnet/.pt预训练策略、aaai26 Docker及命令。尚未逐文件下载；需要有效Gurobi许可及容器执行条件。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/AAAI/article/view/40965/44926) · [来源2](https://fai.cs.uni-saarland.de/vinzent/publications.html) · [来源3](https://gitlab.cs.uni-saarland.de/vinzent/PPAToolset/-/blob/master/README.md)。


## G：8GiB边界配置


### 18. Managing Infinite Abstractions in Numeric Pattern Database Heuristics

**会议与分级：** AAAI 2026；G。

**研究内容：** 数值规划的模式数据库启发式。

**硬件证据：** Xeon Gold6130；8GiB、30分钟。 定位：p.6，Experimental Evaluation。

**适用范围与限制：** 8GiB≈8.59GB，严格十进制8GB不能直接计入。

**数据／环境：** IPC2023 numeric及文献数值规划基准。

**作者代码／实验入口：** [代码／数据](https://github.com/dgnad/numeric-fast-downward) ; [代码／数据](https://doi.org/10.5281/zenodo.17592540)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/download/40941/44902)。

**按当前实测环境更新：** 本会话上限是8GiB，单位本身不再构成超限；但任务使用整个8GiB额度时，没有给其他常驻进程留下余量。本项保留为边界候选，不表示本机已经复现。


### 19. Not Everything Is Permitted: Constrained Cartesian Abstractions for Optimal Classical Planning

**会议与分级：** AAAI 2026；G。

**研究内容：** 约束化Cartesian abstraction/CEGAR。

**硬件证据：** 每run 8GiB、30分钟；未列CPU型号。 定位：p.5，实验。

**适用范围与限制：** Fast Downward/Scorpion推断为CPU求解流程；严格8GB及设备信息仍需核实。

**数据／环境：** Autoscale21.11，30个域。

**作者代码／实验入口：** [代码／数据](https://zenodo.org/records/17515416) ; [代码／数据](https://github.com/Martin1887/scorpion/tree/cegar_disambiguation)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/view/40955/44916)。

**按当前实测环境更新：** 本会话上限是8GiB，单位本身不再构成超限；但任务使用整个8GiB额度时，没有给其他常驻进程留下余量。本项保留为边界候选，不表示本机已经复现。


### 20. Monotonic Variants of Saturated Cost Partitioning

**会议与分级：** ICAPS 2026；G。

**研究内容：** 饱和代价划分启发式的单调变体。

**硬件证据：** 所有run 8GiB、30分钟；处理器未披露。 定位：p.3，实验。

**适用范围与限制：** CPU规划实现可行性与严格8GB峰值仍需测；不要把8GiB写成8GB。

**数据／环境：** IPC1998–2023，无条件效果任务。

**作者代码／实验入口：** 具体作者代码地址本轮未确认。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/ICAPS/article/download/42856/50416/46957)。

**按当前实测环境更新：** 本会话上限是8GiB，单位本身不再构成超限；但任务使用整个8GiB额度时，没有给其他常驻进程留下余量。本项保留为边界候选，不表示本机已经复现。


## B：证据不足，不能计为严格符合


### 21. Conformalized Decision Risk Assessment

**会议与分级：** ICLR 2026；B。

**研究内容：** CREDO：保形风险评估与逆优化。

**硬件证据：** 13代i7，16核16GB；GPU未使用。 定位：p.20，Appendix E.1。

**适用范围与限制：** CPU明确，≤8GB未证实；每个包含多次trial的实验少于30分钟。

**数据／环境：** 2组合成数据、太阳能安装案例。

**作者代码／实验入口：** [代码／数据](https://github.com/wbzhou2001/CREDO)。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/11e0fdc1f9ec9303e5de60670e884e53-Paper-Conference.pdf)。


### 22. Stable coresets: Unleashing the power of uniform sampling

**会议与分级：** ICLR 2026；B。

**研究内容：** 核心集、L1中位数与排序聚合。

**硬件证据：** Apple M1、16GB，Python。 定位：p.8，§6。

**适用范围与限制：** 未提供峰值；也未单独写GPU不用。大数据/稠密化可能增加内存，不能直接保证全量8GB。

**数据／环境：** NYC Taxi、Twitter、单细胞、MyAnimeList。

**作者代码／实验入口：** [代码／数据](https://github.com/amircarmel-lab/StableCoresets)。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/408397eabe6bd3365730e9923975ed49-Paper-Conference.pdf)。


### 23. Combinatorial Bandit Bayesian Optimization for Tensor Outputs

**会议与分级：** ICLR 2026；B。

**研究内容：** 张量输出GP与组合bandit优化。

**硬件证据：** i9-7900X，32GB RAM。 定位：p.23，Appendix K.1。

**适用范围与限制：** CPU实验有据；8GB峰值和作者公开代码未确认。

**数据／环境：** 合成案例、CHEM、MAT、PRINT、REEN。

**作者代码／实验入口：** 未找到可核实公开仓库。

**原文与会议来源：** [论文／来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/4a06bfb11c00bd8a2a1cd7a522138f86-Paper-Conference.pdf)。


### 24. A Direct Approach for Handling Contextual Bandits with Latent State Dynamics

**会议与分级：** ICML 2026；B。

**研究内容：** 隐马尔可夫状态驱动的contextual bandit。

**硬件证据：** 8核16线程32GB，明确无GPU。 定位：PDF p.46硬件、p.55运行时间。

**适用范围与限制：** 全部仿真CPU；每个参数配置100次运行约15分钟；内存未实测。

**数据／环境：** UCI信用卡数据改造的营销模拟：2隐状态、20观测、3动作。

**作者代码／实验入口：** [代码／数据](https://github.com/zhenli1989/bandits_latent_states)。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v306/li26fk.html) · [来源2](https://arxiv.org/pdf/2604.08149)。


### 25. Near-Optimal Private Linear Regression via Iterative Hessian Mixing

**会议与分级：** ICML 2026；B。

**研究内容：** 差分隐私线性回归、Hessian混合。

**硬件证据：** 论文未披露硬件/RAM；作者源码为NumPy/SciPy/sklearn CPU计算。 定位：源码主脚本与utils；PDF p.32数据表。

**适用范围与限制：** CPU判断来自源码，不是作者硬件声明；先测小数据，不保证Buzz/Slice全量。

**数据／环境：** Communities、Pol、Slump、Fertility、Parkinsons、Protein、Servo、Pendulum等。

**作者代码／实验入口：** [代码／数据](https://github.com/omrilev1/HessianMix)。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v306/lev26a.html) · [来源2](https://arxiv.org/pdf/2601.07545)。


### 26. Simple Projection-Free Algorithm for Contextual Recommendation with Logarithmic Regret and Robustness

**会议与分级：** NeurIPS 2026（已录用，待出版）；B。

**研究内容：** CoRectron：免投影在线推荐与对数regret。

**硬件证据：** M4 MacBook Air，10核32GB；Python/NumPy；BLAS线程固定1。 定位：PDF p.18 Appendix H、p.21。

**适用范围与限制：** 原文小规模CPU数值实验，但内存峰值未报；代码未找到。录用已由官方列表及作者确认。

**数据／环境：** 合成m-out-of-n；线性/RBF；10 seeds。

**作者代码／实验入口：** 未找到公开代码。

**原文与会议来源：** [来源1](https://arxiv.org/pdf/2603.20826) · [来源2](https://ssakaue.github.io/publication/) · [来源3](https://neurips.cc/Downloads/2026)。


### 27. General Weighted Averaging in Stochastic Gradient Descent: CLT and Adaptive Optimality

**会议与分级：** AISTATS 2026；B。

**研究内容：** SGD平均、渐近正态性与自适应最优性。

**硬件证据：** MacBook Air M1，8GB LPDDR4，R4.1.1。 定位：正式稿p.37 Appendix D。

**适用范围与限制：** 原文把M1 4性能+4能效核标为GPU，设备表述有歧义；尚未取得可核代码，所以不算严格CPU-only确认。

**数据／环境：** d=5线性/逻辑回归，n=100000；均值估计。

**作者代码／实验入口：** checklist称补充有代码，公开仓库未定位。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v300/wei26b.html) · [来源2](https://www.stat.uchicago.edu/~wbwu/papers/534_General_Weighted_Averaging%20(1).pdf)。

**本轮严格复核：** 本轮仍未取得可核实的R源码，保留B；M1/8GB与GPU字段矛盾不能凭猜测消除。


### 28. Adaptive Coverage Policies in Conformal Prediction

**会议与分级：** AISTATS 2026；B。

**研究内容：** 学习自适应覆盖率策略。

**硬件证据：** i7-13700H CPU；RAM未报。 定位：Appendix D，正式PDF p.16。

**适用范围与限制：** 回归数秒、CIFAR分类数分钟；分类使用冻结预测器/预计算scores，不能忽略其生成成本。

**数据／环境：** 合成回归、CIFAR-10。

**作者代码／实验入口：** [代码／数据](https://github.com/GauthierE/adaptive-coverage-policies)。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v300/gauthier26a.html) · [来源2](https://arxiv.org/html/2510.04318v2)。


### 29. Mask-Conditional Conformal Prediction: Valid Uncertainty For All Missing Data Mechanisms

**会议与分级：** AISTATS 2026；B。

**研究内容：** 缺失数据机制下的保形预测。

**硬件证据：** Xeon Gold6252 CPU，RAM未报。 定位：正式PDF p.26 Appendix E.1。

**适用范围与限制：** 计算时间不能忽略：表中synthetic约21320秒、Concrete约4766秒；先单设置测资源。

**数据／环境：** Synthetic、Concrete等；插补、QRF和boosting。

**作者代码／实验入口：** [代码／数据](https://github.com/jrfan/Mask-Conditional-Conformal-Prediction)。

**原文与会议来源：** [论文／来源](https://proceedings.mlr.press/v300/fan26a.html)。


### 30. Online Bootstrap Inference for the Trend of Nonstationary Time Series

**会议与分级：** UAI 2026；B。

**研究内容：** 非平稳时间序列的在线bootstrap。

**硬件证据：** 作者全部实验使用8核M1 Pro MacBook；RAM未报。 定位：作者README Runtime；正文§6。

**适用范围与限制：** 可限制n_jobs；不能照搬默认全部核并行。

**数据／环境：** 150条长度3500序列、200 bootstrap；附录还有更大设置。

**作者代码／实验入口：** [代码／数据](https://github.com/Tobias-Brock/olbootstrapping)。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v337/nagler26a.html) · [来源2](https://arxiv.org/html/2602.23911v1)。


### 31. Don’t Test What You Can Deduce: Causal Discovery with Logical Inference

**会议与分级：** UAI 2026；B。

**研究内容：** DF-PC：先推理再做条件独立检验。

**硬件证据：** Xeon Gold6342，48核；RAM未报；有CPU-only Slurm配置。 定位：正式PDF p.16 Appendix C.1；README。

**适用范围与限制：** 先10/20/30变量实验；发布代码只含skeleton，不含CPDAG orientation；降低24 workers默认并发。

**数据／环境：** 线性SEM、离散BN；1000–10000样本。

**作者代码／实验入口：** [代码／数据](https://github.com/snu-causality-lab/DF-PC)。

**原文与会议来源：** [论文／来源](https://proceedings.mlr.press/v337/kim26a.html)。


### 33. Linear Fundamental Matrix Estimation from 7 or 5 Points

**会议与分级：** CVPR 2026；B。

**研究内容：** V-Umlaut：基础矩阵最小求解器。

**硬件证据：** C++17/CMake/Eigen代码，未取得CPU型号或RAM声明。 定位：作者README Synthetic Experiments。

**适用范围与限制：** 优先§4 Figure4合成实验；真实数据fork/绘图脚本仍写soon，不能承诺完整复现。

**数据／环境：** 合成噪声实验，作者给10000次试验命令。

**作者代码／实验入口：** [代码／数据](https://github.com/CIVA-Lab/v-umlaut)。

**原文与会议来源：** [来源1](https://openaccess.thecvf.com/content/CVPR2026/html/Kucukpinar_Linear_Fundamental_Matrix_Estimation_from_7_or_5_Points_CVPR_2026_paper.html) · [来源2](https://v-umlaut.github.io/)。


### 34. Gravity-aware Partially Calibrated Absolute Pose Estimation from Affine- or Rotation-covariant Features

**会议与分级：** ECCV 2026；B。

**研究内容：** 重力先验下的位姿与焦距求解。

**硬件证据：** i5-1145G7@2.60GHz笔记本，C++；RAM未报。 定位：§4.1 Execution time。

**适用范围与限制：** 合成/几何核心有CPU依据；真实数据深度特征支路不计CPU全流程。

**数据／环境：** 合成数据、Cambridge Landmarks、Aachen Day-Night v1.1。

**作者代码／实验入口：** [代码／数据](https://github.com/marcusvaltonen/eccv2026)。

**原文与会议来源：** [来源1](https://link.springer.com/chapter/10.1007/978-3-032-37211-6_19) · [来源2](https://arxiv.org/html/2608.20056v1)。


### 35. Rolling Shutter Relative Pose Estimation Made Practical

**会议与分级：** ECCV 2026；B。

**研究内容：** 滚动快门相对位姿与运动估计。

**硬件证据：** 作者合成example明确纯C++/CPU；RAM未报。 定位：作者README Example(i)/(ii)。

**适用范围与限制：** 仅合成/缓存对应后的几何实验；真实数据RoMa提取要求CUDA。

**数据／环境：** 合成扫描、TUM Rolling-Shutter、EuRoC MAV。

**作者代码／实验入口：** [代码／数据](https://github.com/danini/rolling_shutter_made_practical)。

**原文与会议来源：** [来源1](https://link.springer.com/chapter/10.1007/978-3-032-37196-6_16) · [来源2](https://arxiv.org/html/2606.26863v1)。


### 36. High-Throughput Event-Based Feature Detection and Tracking on an Embedded CPU

**会议与分级：** ECCV 2026；B。

**研究内容：** SPEEDTrack：事件流检测与跟踪。

**硬件证据：** 作者方法仅用Jetson 8核CPU，但主存16GB；桌面benchmark32GB。 定位：p.11，§5。

**适用范围与限制：** 不能把8核当8GB；未发现公开源码入口，实测低于8GB未确认。

**数据／环境：** ATIS Corner、Event Camera、EDS。

**作者代码／实验入口：** [代码／数据](https://0thane.github.io/SPEEDTrack/) （项目；未定位源码）。

**原文与会议来源：** [论文／来源](https://0thane.github.io/assets/paper.pdf)。


### 37. MeshA*: Efficient Path Planning with Motion Primitives

**会议与分级：** AAAI 2026；B。

**研究内容：** 含运动基元的路径搜索。

**硬件证据：** 全部实验 AMD EPYC7742，C++；RAM未报。 定位：p.6，实验。

**适用范围与限制：** CPU已确认，需要进程峰值测量。

**数据／环境：** MovingAI四张地图，25000+实例。

**作者代码／实验入口：** [代码／数据](https://github.com/PathPlanning/MeshAStar)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/view/41004/44965)。


### 38. Extending Weighted Heuristic Search to Bi-Objective Search Problems

**会议与分级：** IJCAI 2026；B。

**研究内容：** WBOA*ε：双目标近似Pareto搜索。

**硬件证据：** i5-12400，32GB，C++。 定位：p.5，实验。

**适用范围与限制：** 低于8GB未经证明。

**数据／环境：** DIMACS路网、MovingAI地图。

**作者代码／实验入口：** [代码／数据](https://github.com/hansjkl/WBOAE)。

**原文与会议来源：** [论文／来源](https://www.ijcai.org/proceedings/2026/0700.pdf)。


### 39. From Gridworlds to Warehouses: Adapting Lightweight One-shot Multi-Agent Pathfinding for AGVs

**会议与分级：** IJCAI 2026；B。

**研究内容：** 仓储AGV多智能体路径规划。

**硬件证据：** M3 Pro笔记本18GB，C++。 定位：p.5，实验。

**适用范围与限制：** 未报告≤8GB峰值；与仓储/物流场景较相关，但不把主题相关性当资源证明。

**数据／环境：** 12个MAPF地图，含转向/加减速。

**作者代码／实验入口：** [代码／数据](https://github.com/hirokiNagai-39/mawpf)。

**原文与会议来源：** [论文／来源](https://www.ijcai.org/proceedings/2026/0035.pdf)。


### 54. Cartesian Abstraction Refinement for Simple Numeric Planning

**会议与分级：** ICAPS 2026；B。

**研究内容：** 简单数值规划的CEGAR抽象启发式

**硬件证据：** 每run3.5GB、30分钟；CEGAR最多精化15分钟。 定位：p4 Experiments。

**适用范围与限制：** RAM明确，Numeric Fast Downward实现支持CPU判断，但原文未写CPU型号/核数；严格标准下仍缺显式CPU硬件或工件配置核验。

**代码与可用性：** [作者入口](https://doi.org/10.5281/zenodo.18999076)。论文提供代码、benchmark、data DOI，归档本轮工具无法读取。仅列待补证据，不纳入最严格推荐数量。

**原文与会议来源：** [来源1](https://ojs.aaai.org/index.php/ICAPS/article/download/42857/50417/46958)。


### 59. Learning-Augmented Moment Estimation on Time-Decay Models

**会议与分级：** ICLR 2026；B。

**研究内容：** 借助heavy-hitter oracle改进时间衰减数据流矩估计

**硬件证据：** 合成cascaded实验SSA68.86/112.32MB，SS74.63/117.27MB，CountSketch65.96MB；作者整机M2/16GB。 定位：p26 C.4.1；主机p9；oracle p23 C.1。

**适用范围与限制：** 未确认这些数值是完整进程峰值或oracle总和；全篇CAIDA另用ChatGPT/Gemini和LSTM。不能称纯本地CPU全篇。

**代码与可用性：** [作者入口](https://github.com/ndsoham/learning-augmented-fp-time-decay)。作者基础NumPy/Python notebook公开；静态查不到对应cascaded实验/内存测量脚本，CPU-only也未在该段明示。留作待核，不计严格新增。

**原文与会议来源：** [来源1](https://proceedings.iclr.cc/paper_files/paper/2026/file/1c64a54abd41035503c04119e06c28f9-Paper-Conference.pdf)。


## C：完整原协议有其他资源条件


### 32. TESO: Online Tracking of Essential Matrix by Stochastic Optimization

**会议与分级：** CVPR 2026；C。

**研究内容：** 无需训练的双目相机标定漂移跟踪。

**硬件证据：** Ryzen5 9600X CPU；1024×512、最多1000点/帧，全流程86.01ms/帧。 定位：Appendix A.3。

**适用范围与限制：** 没有总RAM峰值；38个优化参数不等于总内存。视觉方向优先做8GB实测的候选。

**数据／环境：** CARLA-Drift、KITTI、MAN TruckScenes。

**作者代码／实验入口：** [代码／数据](https://github.com/moravecj/teso)。

**原文与会议来源：** [来源1](https://openaccess.thecvf.com/content/CVPR2026/html/Moravec_TESO_Online_Tracking_of_Essential_Matrix_by_Stochastic_Optimization_CVPR_2026_paper.html) · [来源2](https://arxiv.org/html/2604.19420v1)。

**本轮严格复核：** 严格复核由B调整为C：86.01ms只对应在线SIFT/几何跟踪路径；完整benchmark的KO用SuperGlue，VOF/DC用RAFT，比较匹配器涉及GPU。38状态参数不能替代总RAM证据。[原文](https://arxiv.org/html/2604.19420v1)。


### 40. Satisficing and Optimal Generalised Planning via Goal Regression

**会议与分级：** AAAI 2026；C。

**研究内容：** MOOSE：用目标回归合成通用规划规则。

**硬件证据：** MOOSE合成实测<1GB，表内平均52–187MB；规划阶段8GB。 定位：p.7–8，实验/表2。

**适用范围与限制：** 合成比较整体允许32GB/12小时，SLEARN基线未证8GB；CPU型号也未注明。适合方法核心，非全套基线认证。

**数据／环境：** 8个经典域、4个数值域。

**作者代码／实验入口：** [代码／数据](https://github.com/dillonzchen/moose) ; [代码／数据](https://github.com/dillonzchen/moose-dataset)。

**原文与会议来源：** [论文／来源](https://ojs.aaai.org/index.php/AAAI/article/download/40938/44899)。


### 41. Scalable Bayesian Inference for Nonlinear Conservation Laws

**会议与分级：** ICML 2026；C。

**研究内容：** GP有限体积法的贝叶斯PDE求解。

**硬件证据：** GP方法在M1 Max 32GB；PINN基线用RTX2080Ti。 定位：p.14 Appendix B；README。

**适用范围与限制：** 核心CPU可测，完整原基线组合不属于CPU-only已证实；多数图秒至分钟，校准/扩展性数小时。

**数据／环境：** Burgers、Poisson、浅水方程等。

**作者代码／实验入口：** [代码／数据](https://github.com/timweiland/GPFiniteVolume.jl)。

**原文与会议来源：** [来源1](https://proceedings.mlr.press/v306/weiland26a.html) · [来源2](https://arxiv.org/pdf/2605.31127)。


### 42. KASALv2: Fully Automatic 3D Rotational Symmetry Classification and Axis Localization

**会议与分级：** CVPR 2026；C。

**研究内容：** 3D旋转对称分类与轴定位。

**硬件证据：** i5-13400F/RTX3050、32GB；作者提供CPU模式。 定位：§4.1.1；CPU安装说明。

**适用范围与限制：** 几何核心可CPU；整篇含FoundationPose重新训练，不算完整CPU复现。

**数据／环境：** DSRSTO、GSO、BOP。

**作者代码／实验入口：** [代码／数据](https://github.com/WangYuLin-SEU/KASAL)。

**原文与会议来源：** [来源1](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_KASALv2_Fully_Automatic_3D_Rotational_Symmetry_Classification_and_Axis_Localization_CVPR_2026_paper.html) · [来源2](https://arxiv.org/html/2610.09534v1)。


### 43. NanoGS: Training-Free Gaussian Splat Simplification

**会议与分级：** ECCV 2026；C。

**研究内容：** 已有3DGS资产的高斯简化。

**硬件证据：** 项目声称CPU简化；可访问v1实验/渲染使用RTX4090。 定位：§4 Implementation Details；项目页。

**适用范围与限制：** 未给≤8GB峰值；输入3DGS训练和渲染评价不属于CPU简化阶段。

**数据／环境：** NeRF Synthetic、Mip-NeRF360、Tanks and Temples等。

**作者代码／实验入口：** [代码／数据](https://github.com/saliteta/NanoGS)。

**原文与会议来源：** [来源1](https://saliteta.github.io/NanoGS/) · [来源2](https://arxiv.org/html/2603.16103v1)。


## 本轮明确排除的典型误命中

- [Improved Algorithms for Clustering with Noisy Distance Oracles（AISTATS）](https://proceedings.mlr.press/v300/pradhan26a.html)：早期M2/8GB，主要重实验1.5TB/64核约10天；不可只摘8GB。
- [Learning Heuristic Functions for HTN Planning（AAAI）](https://ojs.aaai.org/index.php/AAAI/article/view/40945/44906)：测试8GB，训练峰值64.7GB。
- [Efficient and Reliable Hitting-Set Computations for the Implicit Hitting Set Approach（AAAI）](https://ojs.aaai.org/index.php/AAAI/article/view/38439/42401)：单任务14GB。
- [Certified Branch-and-Bound MaxSAT Solving（AAAI）](https://ojs.aaai.org/index.php/AAAI/article/view/38449/42411)：求解32GB、证明检查64GB。
- [Towards Cardinality-Aware Local Search for SAT with Cardinality Constraints（IJCAI）](https://www.ijcai.org/proceedings/2026/0251.pdf)：每次30GB。
- [Weight-Aware Branch-and-Bound for Weighted Maximum Satisfiability（IJCAI）](https://www.ijcai.org/proceedings/2026/0270.pdf)：单核31GB。
- [Scalable Algorithms for Approximate DNF Model Counting（IJCAI）](https://www.ijcai.org/proceedings/2026/0244.pdf)：只说a few GB，1TB主机；没有严格≤8GiB峰值/限额证据。
- ICAPS的GPMS虽报告启发式平均<2.5GB，但其他模型平均8/12GB、实际上限144GB；平均值不能替代峰值。Optimal Clifford Synthesis的Symk部分5GB，但另有80GB比较，仅能局部探索，未放入严格推荐。

## 覆盖范围与下一步验证的边界

本轮有新增明确证据的会议包括ICML、ICLR、CVPR、AAAI、AAMAS、ICAPS；NeurIPS、ECCV、AISTATS、UAI、COLT没有新增达到相同标准的整篇CPU/8GiB确认项。没有发现不代表不存在。AAMAS对151篇组合/规划/博弈方向论文做了硬件段筛查；ICML对56篇相关论文做了硬件段筛查；候选仍以原文逐项审核为准。

真正执行时应固定论文数据与参数、顺序运行seed/实例，记录整个进程树的峰值RSS及cgroup总量；分别记录预处理、主方法和强基线。当前环境硬上限8GiB，优先保留明显余量。算法计数表、模型参数量、文件大小、平均内存、显存和服务器总RAM均不能冒充完整实验峰值。需要许可证、容器、未公开输入或缺失模块的条目，不能写成已具备一键复现条件。
