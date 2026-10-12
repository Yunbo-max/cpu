# 12 篇论文的 CPU 实测复现记录

生成时间：2026-10-09T00:03:17.766915+00:00

**已获得 11 篇的选定实验 / 示例结果。每个结果来自本次新执行的作者方法。本文没有把选定分支、缩短实验或单次运行称为整篇论文的完整复现。**

实际主机配额为 8 核 CPU、8 GiB 内存。科学运行一般限制 BLAS/OpenMP 为 1 线程；公平聚类的 Rust 核心使用 2 线程。未使用 GPU、外部付费算力、Docker 或 LLM API。CPU 是 AMD EPYC 9V74 共享主机，不能直接把这些时间外推到其他 CPU 笔记本。

## 实际执行范围与资源

耗时包含 Python 导入与该次实验，不含代码下载、数据下载、依赖安装和 C++ 编译。峰值为 Linux 内核 getrusage 的最大单进程常驻内存，已与科学程序自己的记录交叉验证；这些科学任务为单 Python 进程加线程。它不包括全环境文件缓存，也不是多进程 RSS 之和。

| 会议 | 论文 | 本次执行范围 | 耗时 | 峰值 RSS | 未覆盖部分 |
|---|---|---|---:|---:|---|
| ICLR 2026 | Consistent Low-Rank Approximation | Rice：3000 个前缀步骤，d=7、k=1，全部 5 个 c | 483.24 s | 419.80 MiB | Skin、Landmark、合成数据及全部基线未跑 |
| ICLR 2026 | Distribution-informed Online Conformal Prediction | AMZN：3 个预计算预测器 × 8 方法 × 4 学习率，共 96 配置 | 197.49 s | 885.46 MiB | 预测器训练与其余数据集未跑 |
| ICLR 2026 | On the Impact of the Utility in Semivalue-based Data Valuation | 乳腺癌：训练 100 / 测试 50；TP、Gamma、3 种 semivalue；1 次原生收敛运行 | 111.87 s | 482.81 MiB | 作者配置 5 次，本次 1 次；其余数据集未跑 |
| ICLR 2026 | Bandits with Single-Peaked Preferences and Limited Resources | MvM：100 用户、20 臂、1000 轮、1 次；逐轮验证预算 | 14.45 s | 36.11 MiB | 轮数由 100000 缩短到 1000；多实例、多重复、未知顺序分支未跑 |
| ICML 2026 | Online Conformal Prediction via Universal Portfolio Algorithms | AMZN、GOOGL、elec2 共 27 配置；UP、KT、SFOGD、DtACI | 270.28 s（3 数据集） | 210.26 MiB | 预计算预测器；另外 4 配置文件及预测器训练未跑 |
| ICML 2024 | Online conformal prediction with decaying step sizes | 完整 elec2 notebook：45312 个观测，22656 验证 + 22656 评估 | 4.64 s | 666.15 MiB | ImageNet 与其他数据分支未跑 |
| ICML 2022 | Fair and Fast k-Center Clustering for Data Summarization | CountQuery：10000 点、k=7；作者完整隐私下界扫描 | 1.82 s | 42.39 MiB | Adult、Diabetes、Electric 与其他参数网格未跑 |
| ICML 2020 | Boosting Frank-Wolfe by Chasing Gradients | 原生稀疏信号恢复：m=200、n=500；AFW、BCG、DICG、BoostFW | 75.87 s | 251.77 MiB | 其余任务未跑；各算法原生停止规则不同 |
| CVPR 2026 | DualReg: Dual-Space Filtering and Reinforcement for Rigid Registration | 数据访问阻塞：官方法线增强对应关系链接返回 Site Unavailable | 未运行 | — | 未运行，不计入通过数；还需 PCL 及原始点云数据 |
| CVPR 2025 | Dense Match Summarization for Faster Two-view Estimation | MegaDepth DKM 前 32 对 × 10 原生种子 × 3 方法 = 960 次 | 73.96 s | 234.58 MiB | 1500 对全量、RoMa、ScanNet 和深度匹配提取未跑 |
| CVPR 2025 | Practical Solutions to the Relative Pose of Three Calibrated Cameras | Aachen 前 32 三元组 × --rc 6 方法 = 192 次 | 28.40 s | 484.53 MiB | 全量场景、完整迭代网格和特征提取未跑 |
| CVPR 2020 | MAGSAC++, a Fast, Reliable and Accurate Robust Estimator | 完整原生 graf 单应矩阵示例；SIFT 在 CPU 提取；3 估计器 | 2.12 s | 229.01 MiB | 完整论文基准及其他几何问题未跑 |

## 关键结果与解释

### 低秩表示

保持 `consistent-lra-rice.py` 不变，含原生 full_matrices=True 的 SVD 和最优前缀参照。最后一个前缀实际包含 2999 行，因为作者循环为 t=0..2999、切片 0:t。时间包含全部 SVD 参照计算，不能当作单次在线更新的延迟。

| c | 原生 recourse | 全部 3000 前缀的平均误差比 | 最大误差比 |
|---:|---:|---:|---:|
| 1.1 | 60 | 1.000120 | 1.011361 |
| 2 | 11 | 1.001415 | 1.362311 |
| 5 | 6 | 1.005166 | 2.160212 |
| 10 | 5 | 1.011487 | 2.164946 |
| 100 | 3 | 1.045602 | 2.164946 |

误差比分母和接近零的处理沿用作者代码；全部前缀的最大值均满足本次 c 阈值。

### 在线保形预测

分布感知 COP 与 UP 使用作者发布的预测缓存。所有校准器与比较方法本次重新执行；没有将作者预存的校准实验结果作为本次结果。预测模型的训练与推理成本另计，不能据此声称整个预测管线可在这些资源内重训。评分沿用 burnin+1 和作者的覆盖定义。

| UP 数据集 | 评估点数 | 目标覆盖率 | UP 实测覆盖率 | 平均有限区间长度 |
|---|---:|---:|---:|---:|
| AMZN | 2919 | 95% | 94.7585% | 88.449419 |
| GOOGL | 2919 | 95% | 94.7585% | 93.535175 |
| ELEC2 | 1699 | 95% | 95.1148% | 0.157193 |

递减步长 OCP 的 elec2 评估覆盖率为 89.9938%，目标 90%。原 notebook 计算的时间条件覆盖标准差为 0.040031；固定步长为 0.139731。这是该 notebook 的指标，不能换成不同滑窗覆盖指标。

COP 的 96 配置和 UP 的 27 配置全部保留在 metrics.json，不仅保留表现最好的学习率。部分基线产生无穷区间或覆盖不足，属于此次真实输出。`mean_interval_length_finite` 仅统计有限区间；其无穷区间比例单独报告，不能直接当作总体平均宽度进行优劣比较。

### 视觉几何

DMS 使用作者的 KMeans 4D/128 簇、ClusterCorrespondence、三种原生估计器和原生连续 AUC 评分。32 对为 HDF5 顺序的前 32 对，全部来自开头同一场景，不能代表整个 MegaDepth 1500 对。

| DMS 方法 | AUC@5 | AUC@10 | AUC@20 | 平均估计时间 |
|---|---:|---:|---:|---:|
| dense_baseline | 79.86% | 89.91% | 94.96% | 190.822 ms |
| ours_CCC | 79.30% | 89.82% | 94.91% | 6.554 ms |
| ours_CCA | 77.52% | 88.81% | 94.40% | 7.006 ms |

CCC 的估计阶段约快 29.11 倍；每对聚类及摘要平均另需 147.542 ms。简单合计聚类+CCC 为 154.096 ms，对比稠密估计 190.822 ms，仅约 1.24 倍，不能把估计阶段加速称为端到端加速。

三视图保持作者 `eval.py --rc --first 32 --num_workers 1` 的求解与评分，加载公开 Aachen SuperPoint/LightGlue 三元组及 K/R/T 真值。AUC 采用作者整数角度阈值召回平均，与 DMS 的连续积分 AUC 口径不同。

| 三视图方法 | 样本数 | 原生 AUC@10 | 中位姿态误差 | 平均估计时间 |
|---|---:|---:|---:|---:|
| 4p3v(A) | 32 | 7.81% | 60.083° | 16.962 ms |
| 4p3v(A) + R | 32 | 5.31% | 57.037° | 29.177 ms |
| 4p3v(M) | 32 | 63.12% | 3.473° | 45.711 ms |
| 4p3v(M) + R | 32 | 58.75% | 3.468° | 75.573 ms |
| 4p3v(M-D) | 32 | 65.94% | 3.329° | 131.694 ms |
| 4p3v(M-D) + R | 32 | 57.50% | 4.314° | 170.438 ms |

非有限误差按失败计为 180°，没有删除失败样本；计数见 metrics.json。公开 HDF5 的 K/R/T 以斜杠分组存储，作者读取器期望反斜杠平面键；本次仅无损重排叶节点名，每文件 6697 个数值数组逐一验证完全相同，记录见 hdf5_adapter.json。

MAGSAC++ 在 graf 配对上新提取了 845 个 SIFT 比率测试匹配，平均真值角点误差 4.132 px；OpenCV RANSAC 为 4.120 px。此单例没有表现出更小的角点误差，不能据此宣称算法全面胜出。作者显示阈值下的内点数也不等于估计质量。

### 其余原生分支

公平聚类运行了 31 个隐私下界配置，逐项独立核对中心数、每类代表数、最小簇大小和最大欧氏距离；全部通过。Rust 返回半径为 float32，采用 2e-6 相对 / 2e-7 绝对容差验证，没有更改算法。

| 数据估值方法 | TP/Gamma 排序的 Spearman ρ（单次） |
|---|---:|
| shapley | 0.980666 |
| (4,1)-beta_shapley | 0.982394 |
| banzhaf | 0.926313 |

估值训练模型、正则化、划分、收敛控制保持原生配置；仅将 5 次估值重复缩为 1 次，不提供跨重复置信区间。

| BoostFW 比较方法 | 最终目标值 | 原生记录的 CPU 时间 |
|---|---:|---:|
| afwls | 0.000934293792 | 50.015 s |
| bcg | 7.11010504e-05 | 7.187 s |
| dicg | 0.000442640218 | 8.134 s |
| boostfwls | 9.07143466e-05 | 1.157 s |

所有最终向量满足非负和 l1 单纯形约束。算法使用作者各自停止规则，因此不能用不同最终精度下的时间直接宣称统一加速倍数。

Bandit 原生 MvM 的 1000 轮累计 regret 为 11978.280509，预算为 10；原生生成器的单峰性质及全部匹配预算均验证通过。UCB 中的 log(T) 因缩短 T 而变化，因此这是明确标记的短视界运行，不能视为原 100000 轮曲线的前缀。原生小型 DP/穷举检查日志另外保留，但其中生成器输出并非全部单峰，故不将这些小检查单独计为科学复现。

## 兼容适配和失败记录

保留初始失败、后续重跑与补充测量。最终通过数只看具有 exit_code=0、metrics.json 和可信内核 RSS 的科学运行；构建成功、依赖安装与资源测量校准不计入论文数。

- NumPy 2：恢复 np.infty 别名；BoostFW notebook 对字符串 step 比较增加 isinstance 守卫，避免数组与字符串比较产生异常，数值算法未改。
- COP/UP：仅移除不使用的 Darts 训练导入、修复作者绝对数据路径、将结果输出到新目录。保留原缓存加载早返回及校准代码，适配 diff 在每个运行目录。
- C++：Python Development 改为 Development.Module，适应本环境没有 libpython 共享开发库；DMS 显式查找 glog。作者 DMS 缺少 pybind11 gitlink，采用官方 v2.13.6。
- 三视图：GCC 13 / Eigen 3.4 / AVX512 的 array-bounds 和 stringop-overread 警告保持输出，降低其 Werror 级别；算法源未替换。源码构建 diff 位于 patches。
- 最初 /proc 观察子 PID 不可靠，已废弃对应 RSS 数字；最终用内核资源记录且双重核对。初始失败日志并未删去。
- DualReg：本次只核查依赖、原始数据与必要的法线增强对应关系。官方补充数据链接虽返回 HTTP 200，正文为 Site Unavailable，没有数据下载成功，也没有运行或凭空生成输入。访问记录在 runs/dualreg-access/access.json。

## 可重复执行

压缩包包括本次运行器、全部科学原始数组 / 结果、终端日志、执行回执、验证结果、源码版本、构建适配 diff、环境和依赖清单。大型官方输入与上游仓库可用 fetch_sources.py 按版本 / 哈希重新获取；包内不含完整上游仓库、Python 环境、编译产物或完整论文 PDF。

在 Ubuntu 24.04、Python 3.12 上，将包解压为 cpu-reproduction 后，从其父目录执行：

```bash
python3 cpu-reproduction/fetch_sources.py --external-data
python3 -m venv cpu-reproduction/.venv
cpu-reproduction/.venv/bin/python -m pip install -r cpu-reproduction/requirements-minimal.txt
cpu-reproduction/.venv/bin/python -m pip install torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu
cpu-reproduction/.venv/bin/python -m pip install cpu-reproduction/upstream/fair/ff_k_center-1.2.2-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
cpu-reproduction/.venv/bin/python cpu-reproduction/measure.py --seconds 600 replay-ocp -- cpu-reproduction/.venv/bin/python cpu-reproduction/run_case.py ocp
cpu-reproduction/.venv/bin/python cpu-reproduction/measure.py --seconds 600 replay-lowrank -- cpu-reproduction/.venv/bin/python cpu-reproduction/run_case.py lowrank
```

运行名必须是新目录名，避免把旧结果误当成新结果。其他命令见对应 runs/*/receipt.json；将原工作目录绝对路径替换为你的解压路径即可。其余 case 参数为 fair、boost、magsac；COP/UP 用 run_conformal.py cop AMZN_test.yaml 与 up AMZN.yaml / GOOGL.yaml / elec2.yaml；估值、Bandit、DMS、三视图分别用 run_utility.py、run_bandit.py、run_dense.py、run_pose3.py。

C++ 分支额外需要 GCC、Eigen 3.4.0、Ceres 2.2.0、glog/gflags、SuiteSparse 和 BLAS/LAPACK。native-dependency-manifest.json 保存本次 32 个官方 Ubuntu 包的确切版本 / SHA256；将包用 dpkg-deb -x 提取至 deps/native，再用 build_geometry.py dense / pose3 构建。build_geometry.py 使用单编译任务控制内存，依赖路径集中在脚本开头。

## 作者仓库及版本

| 标识 | 仓库 | 提交 |
|---|---|---|
| ocp | [aangelopoulos/online-conformal-decaying](https://github.com/aangelopoulos/online-conformal-decaying) | `d4d78942121cca37b980dbcd63b0927d4c7aba18` |
| boost | [cyrillewcombettes/boostfw](https://github.com/cyrillewcombettes/boostfw) | `309f5fa2af04790f15d24c96bc42e7178cc63b55` |
| cop | [creator-xi/Conformal-Optimistic-Prediction](https://github.com/creator-xi/Conformal-Optimistic-Prediction) | `a41c0dcadc10979d8521ab9b5b8f3d460807d883` |
| utility | [taminemelissa/utility-impact](https://github.com/taminemelissa/utility-impact) | `c63b23da220677dc628fd3f61ed0c74f6305534f` |
| bandit | [GurKeinan/code-for-Bandits-with-Single-Peaked-Preferences-and-Limited-Resources-paper](https://github.com/GurKeinan/code-for-Bandits-with-Single-Peaked-Preferences-and-Limited-Resources-paper) | `43c931dd8352d9654bcdbe2e4c03a5503ae428d2` |
| fair | [LeonSering/fair_and_fast_k_center_clustering](https://github.com/LeonSering/fair_and_fast_k_center_clustering) | `09eab62071fadc1ea9459581e7ff526e7d0086a2` |
| up | [AdaMLLab/up-for-ocp](https://github.com/AdaMLLab/up-for-ocp) | `3575f1f94a14620e089422f52cf9e1a6766ec7b1` |
| dense | [jastermark/DMS](https://github.com/jastermark/DMS) | `7d5b228de9b6fab460f43e466fb0ed8565ffe137` |
| dual | [LJY1229/DualReg](https://github.com/LJY1229/DualReg) | `4760096149ee3ef7a437ada1ef7d070e2d210d5f` |
| magsac | [danini/magsac](https://github.com/danini/magsac) | `d259f8b3a8925025e45667241fb68629b07603bb` |
| lowrank | [https://github.com/samsonzhou/consistent-LRA.git](https://github.com/samsonzhou/consistent-LRA.git) | `d607c4f6467216c470d1e3b93989d44d5fcdec97` |
| pose3 | [https://github.com/kocurvik/threeview.git](https://github.com/kocurvik/threeview.git) | `c9ac8e89ac02250f7a2f925a79408d15ef9586af` |
| pose3-lib | [https://github.com/kocurvik/PoseLib.git](https://github.com/kocurvik/PoseLib.git) | `272ce27dc3b6f44637c3bdea7ff460f06cb538d6` |

环境详情见 environment.json，完整冻结清单见 requirements-lock.txt，独立验证记录见 verification.json。

Python 原生绑定版本：pymagsac 0.2.3（作者 PyPI 发行）、ff_k_center 1.2.2（作者仓库随附 wheel，SHA256 在冻结清单中）、DMS 的 pysumopt 与三视图 PoseLib 为本次从各自固定源码提交编译。仓库提交和发行二进制版本分别记录；本次未重新编译前两个 wheel。

构建资源单独记录：DMS 最终成功构建约 54.32 s、最大子进程 RSS 1275.06 MiB；三视图最终成功构建约 390.75 s、最大子进程 RSS 2938.46 MiB。此前失败构建日志保留，完整首次安装耗时大于最后一次成功构建时间。它们没有混入科学运行资源表。

