# 2026 CPU / 8GiB：仅列实际跑通的实验

记录日期：2026-10-11。由既有逐任务执行记录筛选，本次整理没有重新运行实验。

**23篇会议论文至少有一个明确范围的原作者代码运行完成，并产出数值或任务输出；这不是23篇完整论文复现。** 所有运行均在同一个8GiB硬内存上限的CPU环境中完成；subagent共享资源。表中是已完成范围的进程峰值RSS，编译、安装和其他阶段须按各条说明另计。

进入此清单不代表方法已收敛、超过基线，或全文结论已获验证。尤其 Distributions as Actions 只完成短程训练；Learning-Augmented Moment Estimation 只完成作者辅助例子。

| Topic | 实际跑通条目数 |
|---|---:|
| 规划、搜索与约束求解 | 7 |
| 视觉几何与3D | 5 |
| 强化学习与Bandit | 3 |
| 低秩、coreset与流式统计 | 3 |
| 统计学习与可信决策 | 3 |
| NLP分词 | 1 |
| SQL形式化验证 | 1 |

## 规划、搜索与约束求解

### Two Constraint Compilation Methods for Lifted Planning

会议：AAAI 2026。原报告编号：06。

**实际跑通范围：** 作者 scripts.run 编译自带 blocksworld p1–p3，输出3组domain/problem PDDL。

**输出：** 成功编译3个实例，输出6个PDDL文件。

**实测资源：** 峰值RSS 107.34 MiB；墙钟时间 2.421 秒。

**边界：** 仅LiftedTCORE编译阶段；未运行LCC或下游LAMA，未复现整套比较。

论文/代码来源：
- https://github.com/Periklismant/LiftedTCORE
- https://github.com/LBonassi95/NumericTCORE
- https://github.com/Periklismant/aaai26-pddl3-benchmark
- https://ojs.aaai.org/index.php/AAAI/article/view/40952/44913

固定代码版本：`aed8ec5676cd34e63c5523fbf20d9ebe8ece7426`。

原始任务记录：`aaai_shared_install`, `aaai06_native_blocksworld`。

### Extreme Value Monte Carlo Tree Search for Classical Planning

会议：AAAI 2026。原报告编号：10。

**实际跑通范围：** 作者 Pyperplan 分支的 GUCT-Uniform，使用 hFF、seed=23959，求解仓库自带 airport p01 单实例。

**输出：** 求解成功：计划8步，展开8个状态，评估9次。

**实测资源：** 峰值RSS 112.10 MiB；墙钟时间 2.709 秒。

**边界：** 单例仅评估9次即提前找到解，未覆盖论文772问题或Fast Downward分支；仅修复此沙箱PID命名空间的RSS探针故障，算法未改。greedy为仅用h的选择准则，无独立CLI开关；外部300s硬上限。

论文/代码来源：
- https://github.com/guicho271828/pyperplan-mcts
- https://ojs.aaai.org/index.php/AAAI/article/view/40934/44895
- https://github.com/IBM/pyperplan-mcts-public

固定代码版本：`64414bd787a537812595d8d59ad7d97380290c50`。

原始任务记录：`aaai10_install`, `aaai10_native_uctuniform`, `aaai10_sympy_install`, `aaai10_native_uctuniform_retry`, `aaai10_native_uctuniform_pidfix`。

### Managing Infinite Abstractions in Numeric Pattern Database Heuristics

会议：AAAI 2026。原报告编号：18。

**实际跑通范围：** 原Zenodo版本的numeric_ipdb LLL配置，求解作者预翻译 counters-sym/problem_2.sas。

**输出：** 计划5步、cost=5；1个PDB、10001个PDB状态，展开6个搜索状态。

**实测资源：** 峰值RSS 21.14 MiB；墙钟时间 0.218 秒。

**边界：** 仅一个SAS实例，不含PDDL预处理；构建另耗186.558s、峰值1.383GiB。

论文/代码来源：
- https://github.com/dgnad/numeric-fast-downward
- https://doi.org/10.5281/zenodo.17592540
- https://ojs.aaai.org/index.php/AAAI/article/download/40941/44902

固定代码版本：`99ec2ca273247eca05413d188d3c40b4914273cb`。

原始任务记录：`aaai18_build`, `aaai18_native_counter2`。

### Not Everything Is Permitted: Constrained Cartesian Abstractions for Optimal Classical Planning

会议：AAAI 2026。原报告编号：19。

**实际跑通范围：** 精确论文代码与全AC3约束消歧配置，求解Autoscale21.11五块积木p01，包含PDDL翻译及h2预处理。

**输出：** 计划12步、cost=12；53个抽象状态，消歧状态计数41。

**实测资源：** 峰值RSS 25.12 MiB；墙钟时间 0.214 秒。

**边界：** 仅单实例；构建另耗223.119s、峰值1.309GiB。原生日志Peak memory读VmPeak虚拟内存，表中用外测RSS。

论文/代码来源：
- https://zenodo.org/records/17515416
- https://github.com/Martin1887/scorpion/tree/cegar_disambiguation
- https://ojs.aaai.org/index.php/AAAI/article/view/40955/44916

固定代码版本：`c4d2c76d4a28bd36c594f7c6318edc5c5f0d2398`。

原始任务记录：`aaai19_build`, `aaai19_native_blocksworld`。

### MeshA*: Efficient Path Planning with Motion Primitives

会议：AAAI 2026。原报告编号：37。

**实际跑通范围：** 作者Labyrinth单例：三种原生搜索均执行，weight=8，使用自带运动基元和mesh。

**输出：** 三种搜索均成功；LazyLBA*/LBA*成本1501.56，MeshA*成本1585.57。

**实测资源：** 峰值RSS 464.01 MiB；墙钟时间 22.457 秒。

**边界：** 只测一个例子；MeshA*成本1585.57、两基线1501.56，不能宣称同质量加速；未跑25000+实例全套。

论文/代码来源：
- https://github.com/PathPlanning/MeshAStar
- https://ojs.aaai.org/index.php/AAAI/article/view/41004/44965

固定代码版本：`12574ff03d8d61ac153b4e4224eac2229a9577e1`。

原始任务记录：`aaai37_build`, `aaai37_native_labyrinth`。

### Satisficing and Optimal Generalised Planning via Goal Regression

会议：AAAI 2026。原报告编号：40。

**实际跑通范围：** MOOSE在全部20个Ferry训练实例上合成策略，再求解heldout p0_02。

**输出：** 处理20/20训练实例，学到5条规则；测试1/1成功，计划8步。

**实测资源：** 峰值RSS 59.61 MiB；墙钟时间 10.977 秒。

**边界：** Apptainer缺失，薄启动器改用本地作者Scorpion构建，MOOSE算法未改；仅1个heldout任务，未做外部VAL验证。 本地Scorpion依赖构建峰值1.309GiB另计。

论文/代码来源：
- https://github.com/dillonzchen/moose
- https://github.com/dillonzchen/moose-dataset
- https://ojs.aaai.org/index.php/AAAI/article/download/40938/44899

固定代码版本：`ce1e99bc12e9c839c5e8e870aac878fd5d31cf9e`。

原始任务记录：`aaai40_python_deps`, `aaai40_native_planner_install`, `aaai40_native_ferry`。

### Constraint Optimization of MicroPlate Designs

会议：AAAI 2026。原报告编号：60。

**实际跑通范围：** 作者COMPD v1.0原始screening-8-8-1单板模型、默认策略、8个CP-SAT工作线程；16×24板，292种compound及8正8负controls。

**输出：** 单板生成1个最优解，objective=bound=-6006，输出308个内部孔位安排。

**实测资源：** 峰值RSS 508.22 MiB；墙钟时间 55.070 秒。

**边界：** memory_test单线程240s无解返回UNKNOWN；单板用作者8线程设置。MiniZinc2.10.1/CP-SAT9.15与论文9.12不同；未做PLAID全比较。

论文/代码来源：
- https://github.com/astra-uu-se/COMPD
- https://ojs.aaai.org/index.php/AAAI/article/view/38438/42400

固定代码版本：`271c717c6105b70f7a68c7c1bc73f355f1ff0405`。

原始任务记录：`aaai60_minizinc_install`, `aaai60_native_memory_test`, `aaai60_native_screening`。


## 视觉几何与3D

### TESO: Online Tracking of Essential Matrix by Stochastic Optimization

会议：CVPR 2026。原报告编号：32。

**实际跑通范围：** 作者 CARLA-Drift 仿真数据序列 000 原始前10帧；原生 SIFT/FAISS/TESO 跟踪及原生 MAE。

**输出：** 旋转 MAE xyz=[0.010070,0.010177,0.020975]°；平移=[0.00000305,0.017676,0.017241] mm；10×6 输出全部有限。

**实测资源：** 峰值RSS 322.27 MiB；墙钟时间 5.017 秒。

**边界：** 仅近初始标定的10帧，沿用作者名义标定初始化，GT最大漂移仅[.02,.03,.04]°；不代表155×1000帧总体表现，无GPU基线。只适配路径、循环边界和评分切片。

论文/代码来源：
- https://openaccess.thecvf.com/content/CVPR2026/html/Moravec_TESO_Online_Tracking_of_Essential_Matrix_by_Stochastic_Optimization_CVPR_2026_paper.html
- https://github.com/moravecj/teso
- https://cmp.felk.cvut.cz/teso/

固定代码版本：`a309db1f5e5c15ac38e2cf8036f441787be33327`。

原始任务记录：`vision32_teso_deps`, `vision32_teso_first10`。

### Linear Fundamental Matrix Estimation from 7 or 5 Points

会议：CVPR 2026。原报告编号：33。

**实际跑通范围：** 作者 Fig.4 general 合成设置，两种噪声 σ=1，各10000次；原生5pt/7pt基线。

**输出：** independent 噪声 V-Umlaut mean R/t=36.5657°/23.9290°，5pt=14.0989°/9.0114°；dependent 设置 V-Umlaut=20.6682°/14.2807°。

**实测资源：** 峰值RSS 10.25 MiB；墙钟时间 0.749 秒。

**边界：** 只有两个合成点；原生协议使用GT虚拟中点及GT选解。dependent噪声只作用于V-Umlaut虚拟点，基线仍无噪声；该组不是同噪声胜负比较。随机seed未由CLI固定。

论文/代码来源：
- https://cvpr.thecvf.com/media/cvpr-2026/Slides/38619.pdf
- https://github.com/CIVA-Lab/v-umlaut

固定代码版本：`ce2175dd082a957d1bcdd5e5685b1bcb308c12da`。

原始任务记录：`vision33_vumlaut_build`, `vision33_vumlaut_independent`, `vision33_vumlaut_dependent`。

### Gravity-aware Partially Calibrated Absolute Pose Estimation from Affine- or Rotation-covariant Features

会议：ECCV 2026。原报告编号：34。

**实际跑通范围：** 作者 README 原生无噪声单问题例，seed=1234，9种求解器；未改算法。

**输出：** UP1PfAC 旋转误差3.33067e-16 rad、相对焦距误差3.39259e-15；UP2PfORI分别2.04613e-14 rad、7.83931e-14；9法均输出。

**实测资源：** 峰值RSS 10.25 MiB；墙钟时间 0.110 秒。

**边界：** 单例，不是论文5000次稳定性实验。原baseline UP2P循环用i代j的索引风险，未扩大nprob；编译仅链接所需原始PoseLib单元。短进程资源数含启动开销。

论文/代码来源：
- https://link.springer.com/chapter/10.1007/978-3-032-37211-6_19
- https://github.com/marcusvaltonen/eccv2026

固定代码版本：`34f8fa9a2b2dcaacdbb7ffc784a80682228b288c`。

原始任务记录：`vision34_gravity_build`, `vision34_gravity_example`。

### KASALv2: Fully Automatic 3D Rotational Symmetry Classification and Axis Localization

会议：CVPR 2026。原报告编号：42。

**实际跑通范围：** 原生 headless CPU 对称性分析，作者 mesh obj_000007_ours.ply；workers=1、FPS采样512点。

**输出：** 1/1模型成功；预测5重旋转对称（D(=1): n-fold Pyramidal Item），轴约[-0.01479,-0.01625,0.99976]；原生BOP JSON字段全部有限。

**实测资源：** 峰值RSS 584.07 MiB；墙钟时间 21.548 秒。

**边界：** 仅一个作者网格、FPS512；未提供独立类别/轴GT，不报告准确率。仅CPU对称性分析，未进行FoundationPose下游位姿评测。

论文/代码来源：
- https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_KASALv2_Fully_Automatic_3D_Rotational_Symmetry_Classification_and_Axis_Localization_CVPR_2026_paper.html
- https://github.com/WangYuLin-SEU/KASAL

固定代码版本：`5980894229e4209eba7769753fe4a79dc02233a5`。

原始任务记录：`vision42_kasal_install`, `vision42_python310`, `vision42_kasal_cpu_deps`, `vision42_kasal_one_mesh`。

### NanoGS: Training-Free Gaussian Splat Simplification

会议：ECCV 2026。原报告编号：43。

**实际跑通范围：** 作者公开 drone PLY 的原生CPU NanoGS简化，ratio=.5、k=16、merge_cap=.5、opacity=.1、两项权重1。

**输出：** 336384→168192 splats（50%）；opacity筛至321218后合并153026对；输出2859264个浮点值全部有限，文件长度匹配。

**实测资源：** 峰值RSS 325.57 MiB；墙钟时间 13.214 秒。

**边界：** 作者demo模型，不是论文图像评测集；没有PSNR/SSIM/LPIPS或上游3DGS训练。仅下游原生简化范围完成。

论文/代码来源：
- https://link.springer.com/chapter/10.1007/978-3-032-37095-2_29
- https://github.com/saliteta/NanoGS
- https://github.com/RongLiu-Leo/NanoGS/blob/5329d9901041b07ecb7ea31b554ce0ee417d0f21/examples/drone.ply

固定代码版本：`cc64a752b5def8d17f9992216bfbb9e533f8364f`。

原始任务记录：`vision43_nanogs_deps`, `vision43_nanogs_drone`。


## 强化学习与Bandit

### Distributions as Actions: A Unified Framework for Diverse Action Spaces

会议：ICLR 2026。原报告编号：01。

**实际跑通范围：** 作者CartPole-v1训练脚本；seed=1，20000步，保留12500步warmup及算法默认值。

**输出：** 最后10个episode训练回报均值=9.1; 最后qf1_loss=0.04086899012327194, loss记录至step=19900。 另一次默认500k尝试在300.093秒超时，峰值366.27MiB；末个日志step=434522，末10个episode训练回报均值=500.0，不视为完整500k成功或独立评估。

**实测资源：** 峰值RSS 330.13 MiB；墙钟时间 36.412 秒。

**边界：** 训练步数是默认500000的4%；未复现收敛曲线、全部seed或全部环境。主/Hybrid仓库没有bandit脚本。Python3.12/CPU torch2.5.1与作者旧依赖不同；tyro升级仅修CLI兼容。 额外完整500000步尝试未完成：timeout。

论文/代码来源：
- https://github.com/hejm37/da-ac
- https://proceedings.iclr.cc/paper_files/paper/2026/file/898c63fee61c06aa00745769c444e2ec-Paper-Conference.pdf
- https://github.com/hejm37/da-ac-hybrid

固定代码版本：`dd7d5ffb513eb15ff91c90fca5a4ff3a6d9883cf`。

原始任务记录：`iclr01_daac_cartpole_20000`, `iclr01_daac_cartpole_20000_fixed`, `iclr01_daac_cartpole_full500k`。

### Fine-tuning Behavioral Cloning Policies with Preference-Based Reinforcement Learning

会议：ICLR 2026。原报告编号：03。

**实际跑通范围：** 作者官方StarMDP debug配置：2 seeds、N_iterations=2（含初始化），BRIDGE与purely-online baseline；仅将seed调度改成串行。

**输出：** 原生平均累计regret：BRIDGE=0.552631，purely-online=23.047454；BC平均回报=42.811223，专家平均回报=44.357875。

**实测资源：** 峰值RSS 419.68 MiB；墙钟时间 92.590 秒。

**边界：** 是官方debug规模，未复现连续控制或训练专家。原多进程torch结果传输被本平台IPC socket限制；执行适配器串行调用同一作者函数，算法代码未改。原训练数值已保存，后续绘图因type1ec.sty缺失失败；单独核验saved metrics并调用作者绘图，禁用TeX。耗时/RSS包括该训练及最终后处理。

论文/代码来源：
- https://github.com/pfriedric/bridge
- https://proceedings.iclr.cc/paper_files/paper/2026/file/88bdfbf58591102f4b8855a22ac76437-Paper-Conference.pdf

固定代码版本：`dc4d27f664bd69aa09f63f82669d3a191acc3ab7`。

原始任务记录：`iclr03_bridge_debug`, `iclr03_bridge_debug_serial`, `iclr03_bridge_postprocess`, `iclr03_bridge_postprocess_fixed`。

### A Direct Approach for Handling Contextual Bandits with Latent State Dynamics

会议：ICML 2026。原报告编号：24。

**实际跑通范围：** 原始UCI信用卡数据；作者steps1–6及原生评分；seed1951、1000轮；LinUCB/BoxA/BoxB各1配置

**输出：** 终点belief-regret：LinUCB45.503705、BoxA48.429720、BoxB47.866844

**实测资源：** 峰值RSS 374.31 MiB；墙钟时间 35.621 秒。

**边界：** 原文50000轮、100种子和完整参数网格未跑；当前单种子短程不支持算法优越性；Python/NumPy/sklearn版本不同于README

论文/代码来源：
- https://proceedings.mlr.press/v306/li26fk.html
- https://github.com/zhenli1989/bandits_latent_states
- https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip

固定代码版本：`f2736b2a2998ce62405eeb6190daa5238e01f362`。

原始任务记录：`bandits_dependencies_01`, `bandits_native_small_01`。


## 低秩、coreset与流式统计

### Consistent Low-Rank Approximation

会议：ICLR 2026。原报告编号：02。

**实际跑通范围：** 作者Rice算法与数据，仅将n=3000缩为1000；d=7,k=1,c=[1.1,2,5,10,100]，5个c均完整执行。

**输出：** recourse=[50, 10, 5, 4, 3]; 最后近似误差比=[1.0001930090119704, 1.0009408729083373, 1.0040975953819244, 1.0060290440412274, 1.004317868906333]。

**实测资源：** 峰值RSS 189.18 MiB；墙钟时间 12.060 秒。

**边界：** 只复现Rice子实验，未扩展为所有数据/算法完整复现。首次300秒超时；另有仅n=1000的缩数据运行，明确区分。 原始n=3000完整配置在300秒及600秒上限内均未完成；本成功结果仅为缩数据版本。

论文/代码来源：
- https://github.com/samsonzhou/consistent-LRA
- https://proceedings.iclr.cc/paper_files/paper/2026/file/b14d76c7266be21b338527cd25deac45-Paper-Conference.pdf

固定代码版本：`d607c4f6467216c470d1e3b93989d44d5fcdec97`。

原始任务记录：`iclr02_lra_rice_full`, `iclr02_lra_rice_n1000`, `iclr02_lra_rice_full600`。

### Stable coresets: Unleashing the power of uniform sampling

会议：ICLR 2026。原报告编号：22。

**实际跑通范围：** 原作者Taxi实验函数；真实2024-01 Taxi全文件加载清洗后前10000行，coreset=[150,300]，3 repeats，seed=0。

**输出：** size=[150,300]，uniform相对误差=[0.0006613007969131121, 0.002843222500788539]；two-step=[0.004330836011800831, 0.0013987165987615223]；one-step=[0.0019675365368628074, 0.0007152354332717177]。

**实测资源：** 峰值RSS 1604.27 MiB；墙钟时间 4.473 秒。

**边界：** 明确缩数据、coreset网格和repeat数；并非全量论文对比。代码中的uniform与两种importance方法和误差定义保持原生。内存测量包含加载清洗全文件；依赖安装在前次进程内完成，成功耗时不含此前安装。

论文/代码来源：
- https://github.com/amircarmel-lab/StableCoresets
- https://proceedings.iclr.cc/paper_files/paper/2026/file/408397eabe6bd3365730e9923975ed49-Paper-Conference.pdf
- https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet

固定代码版本：`48f0233eb65269b8552eb163f275627e5447921d`。

原始任务记录：`iclr22_stable_taxi_subset`, `iclr22_stable_taxi_subset_retry`, `iclr22_stable_taxi_fresh`, `iclr22_stable_taxi_tqdm`。

### Learning-Augmented Moment Estimation on Time-Decay Models

会议：ICLR 2026。原报告编号：59。

**实际跑通范围：** 原SS-SSA notebook cells[1,7,8,9,10,12,14,15]完整uniform例子，n=10,m=10000。

**输出：** t=0: SSA=901.396551, SS=1882.841404, 真L3=2156.237269；保留20个时间点。

**实测资源：** 峰值RSS 54.22 MiB；墙钟时间 66.123 秒。

**边界：** 只是作者仓库辅助uniform例子，不能确认论文主算法/cascaded低内存实验或CAIDA完整复现；t=0时SSA误差大于SS，不证明论文优势。

论文/代码来源：
- https://github.com/ndsoham/learning-augmented-fp-time-decay
- https://proceedings.iclr.cc/paper_files/paper/2026/file/1c64a54abd41035503c04119e06c28f9-Paper-Conference.pdf

固定代码版本：`d2e49bb63f107ccd1f6af540cd97970d680937c9`。

原始任务记录：`iclr59_ssa_native_uniform`。


## 统计学习与可信决策

### Conformalized Decision Risk Assessment

会议：ICLR 2026。原报告编号：21。

**实际跑通范围：** 原exp1_tradeoff notebook cells[1,2,5]完整首个Gaussian实验99 trials；ntr=ncal=100,K=100，参考MC K=10000。

**输出：** 99 trials CREDO保守率=1.000000；NS=0.515152；Point=1.000000。

**实测资源：** 峰值RSS 398.99 MiB；墙钟时间 19.598 秒。

**边界：** 复现一个完整原生子实验，不包括其余参数扫描、misspecification、太阳能案例。pycddlib用CC=gcc、本地GMP头和PEP517在前次进程内构建成功；本次时间包含tqdm安装，不包含此前几何依赖设置。

论文/代码来源：
- https://github.com/wbzhou2001/CREDO
- https://proceedings.iclr.cc/paper_files/paper/2026/file/11e0fdc1f9ec9303e5de60670e884e53-Paper-Conference.pdf

固定代码版本：`19e884718599cd390564ddf93aff943a720f3e22`。

原始任务记录：`iclr21_credo_gaussian`, `iclr21_credo_gaussian_retry`, `iclr21_credo_pep517`, `iclr21_credo_tqdm`。

### Near-Optimal Private Linear Regression via Iterative Hessian Mixing

会议：ICML 2026。原报告编号：25。

**实际跑通范围：** 作者Fertility数据，原生90/10划分、9维；6个ε点，各5次Monte Carlo；IHM及4基线

**输出：** ε=10：IHM train MSE=0.085489、test MSE=0.063642；六点原生数组全部保存

**实测资源：** 峰值RSS 205.70 MiB；墙钟时间 3.557 秒。

**边界：** 论文500次及多数据集未跑；仅raw MSE；发布mask为90/10（论文表2也列90训练，正文写80/20）；缩小数据集列表改变随机数历程，不支持精确表值或总体优越性结论

论文/代码来源：
- https://proceedings.mlr.press/v306/lev26a.html
- https://github.com/omrilev1/HessianMix

固定代码版本：`37651364bdfa9814fa3220dd2512cdb94f6c213a`。

原始任务记录：`hessian_fertility_native_01`, `hessian_tqdm_setup_01`, `hessian_fertility_native_02`。

### From Rashomon Theory to PRAXIS: Efficient Decision Tree Rashomon Sets

会议：ICML 2026。原报告编号：44。

**实际跑通范围：** 作者API；完整COMPAS 4966×44；λ=0.02、ε=0.03、depth=5、lookahead=1；单核

**输出：** 最小目标1992，与论文表16一致；28棵树；fit=0.123581秒

**实测资源：** 峰值RSS 205.26 MiB；墙钟时间 3.459 秒。

**边界：** 仅此数据/配置；无其他基线、召回率或跨数据验证；当前代码和依赖版本、主机不同于原论文，不能把单次计时当严格速度复现

论文/代码来源：
- https://proceedings.mlr.press/v306/heile26a.html
- https://github.com/zakk-h/PRAXIS

固定代码版本：`ef6ce624cc40bcb00fcd39f4520364a3a05c8c80`。

原始任务记录：`praxis_setup_venv_01`, `praxis_build_gcc_02`, `praxis_compas_native_01`。


## NLP分词

### Parity-Aware Byte-Pair Encoding: Improving Cross-lingual Fairness in Tokenization

会议：ACL 2026 main conference, Volume 1: Long Papers。原报告编号：ACL02。

**实际跑通范围：** 原生 Classical BPE 与 PA-BPE ratio 分支各训练 1000 次合并；FineWeb2 德语、法语各 80 文档训练、20 文档诊断编码；目标比例 1:1，单 worker。

**输出：** classical: 1000 合并，德/法诊断 token 数 47370/17973；parity_ratio: 1000 合并，德/法诊断 token 数 45861/18513

**实测资源：** 峰值RSS 112.84 MiB；墙钟时间 9.545 秒。

**边界：** 仅分词器训练的小规模原生分支；不是论文 30/60 语言、128k 词表实验，未复现 FLORES+ 公平性指标或下游大语言模型训练。FLORES+ 官方数据受访问条款限制，未绕过；采用作者公开的无开发集 ratio 分支。编码诊断用与作者一致的 tokenizers 词表构造，未调用需要 Transformers 的包装层。

论文/代码来源：
- https://aclanthology.org/2026.acl-long.342/
- https://github.com/swiss-ai/parity-aware-bpe
- https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

固定代码版本：`c7395d469a653f3e48e80984e37593256ff8f365`。

原始任务记录：`nlp_dependencies`, `nlp_parity_native`。


## SQL形式化验证

### SpotIt: Evaluating Text-to-SQL Evaluation with Formal Verification

会议：ICLR 2026。原报告编号：04。

**实际跑通范围：** 后续作者仓库保留的固定原版Vanilla verifier；BIRD question 1、ALPHA原预测、bound=2。

**输出：** equivalent=False; verifier内部time_cost=0.6899460000000001秒。

**实测资源：** 峰值RSS 73.40 MiB；墙钟时间 21.743 秒。

**边界：** 单个已生成SQL对的验证，不包括生成预测、完整BIRD评测或人工判定counterexample是否真实。严格隔离固定Vanilla模块；不能把后续SpotIt+完整方法当作原论文复现。使用作者custom Z3绑定并补旧pkg_resources依赖，时间包括该依赖安装。

论文/代码来源：
- https://github.com/ai-ar-research/SpotIt-plus
- https://www.cs.sfu.ca/~yuepeng/pubs/iclr26.pdf
- https://github.com/atremante26/VeriEQL/tree/71a3b5ced9553a040b049609d2250624e1a08d39

固定代码版本：`abee2baa26b2b50398c1807a46b2db126d2dda97;verieql=fb1bdaae8f3e4a544d08feffa44bc14270d99329;vanilla=71a3b5ced9553a040b049609d2250624e1a08d39`。

原始任务记录：`iclr04_spotit_vanilla_q1`, `iclr04_spotit_native_vanilla`, `iclr04_spotit_pkg_resources`。

## 单列：已跑通的本地模型推理

这一项不加入上述23篇会议论文计数，也不称为本地原版Jev。

**Laya 421M — 20条原生工具选择新推理**

作者原生run_laya.py + laya0.3.21，CPU/float32/单线程，20个预先固定样本；2/5/10/20/50候选各4例。网络连接被阻断；保留逐样本gold、预测、完整概率。

20/20有效输出，16/20正确（80.0%）；单次中位数5773.6ms；成功原生前向21次（含warmup），网络连接尝试0次。

峰值RSS 2.794 GiB；墙钟时间 112.595 秒。

小规模资源/功能测试，不是论文全量复现；Laya是独立于TypeSafe Jev的模型。torch2.5.1+cpu/transformers4.57.6不同于论文环境；使用laya0.3.21的reviewed模型SHA55cf4c4e，未训练/调参。原生SDK将choice:11+的越界温度0.10058截为0.5，并警告受影响confidence未校准；保留原始输出。
