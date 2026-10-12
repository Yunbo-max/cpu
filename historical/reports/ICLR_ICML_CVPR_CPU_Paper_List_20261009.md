# ICLR / ICML / CVPR：约 8 核 CPU、8 GiB 内存的研究论文清单

核查日期：2026-10-09（英国时间）

目标：寻找无需 LLM API、可在约 8 核 CPU / 8 GiB 内存环境推进的研究路线。下面是 12 篇论文，其中 8 篇来自 2025–2026 年，另 4 篇是成熟基线。会议论文、作者全文和作者代码是主要证据来源。

**证据边界：原论文使用 CPU，不等于完整复现在 8 GiB 上已通过。只有 Consistent Low-Rank Approximation 和 Boosting Frank-Wolfe 明确报告了 8 GB RAM 的 CPU 实验。本清单未在目标环境执行任何完整复现，未测峰值内存或总耗时。GB 与 GiB 保留原文及目标预算的各自单位。**

CVPR 条目中特别注明是否使用预计算特征/对应关系。以公开对应点作为研究输入时，可在 CPU 上研究几何后端；神经特征提取器的重新训练和提取不自动包含在这个判断里。

## 快速清单

| 编号 | 会议 | 论文 | 资源证据摘要 | 作者代码 |
|---|---|---|---|---|
| 1 | ICLR 2026 | [Consistent Low-Rank Approximation](https://proceedings.iclr.cc/paper_files/paper/2026/hash/b14d76c7266be21b338527cd25deac45-Abstract-Conference.html) | 全部实验：8 核 CPU、8 GB RAM | [代码](https://github.com/samsonzhou/consistent-LRA) |
| 2 | ICLR 2026 | [Distribution-informed Online Conformal Prediction](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5f8241131e6fd428aa49914da76b8ad0-Abstract-Conference.html) | 校准更新：单核 CPU；基础预测器训练另计 | [代码](https://github.com/creator-xi/Conformal-Optimistic-Prediction) |
| 3 | ICLR 2026 | [On the Impact of the Utility in Semivalue-based Data Valuation](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a99c41c85cd1ce4dbddfeba8908a531a-Abstract-Conference.html) | 全部实验：8 核 CPU、16 GB RAM | [代码](https://github.com/taminemelissa/utility-impact) |
| 4 | ICLR 2026 | [Bandits with Single-Peaked Preferences and Limited Resources](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e1cf57f1e104c6c05e31894c15a65e99-Abstract-Conference.html) | 全部模拟：8 核 CPU、18 GB RAM | [代码](https://github.com/GurKeinan/code-for-Bandits-with-Single-Peaked-Preferences-and-Limited-Resources-paper) |
| 5 | ICML 2026 | [Online Conformal Prediction via Universal Portfolio Algorithms](https://proceedings.mlr.press/v306/liu26y.html) | 轻量结构推断；硬件/官方代码未核实 | 官方仓库本轮未核实 |
| 6 | ICML 2024 | [Online conformal prediction with decaying step sizes](https://proceedings.mlr.press/v235/angelopoulos24a.html) | 轻量校准代码；ImageNet 使用预计算输入 | [代码](https://github.com/aangelopoulos/online-conformal-decaying) |
| 7 | ICML 2022 | [Fair and Fast k-Center Clustering for Data Summarization](https://proceedings.mlr.press/v162/angelidakis22a.html) | CPU 笔记本、16 GB RAM | [代码](https://github.com/LeonSering/fair_and_fast_k_center_clustering) |
| 8 | ICML 2020 | [Boosting Frank-Wolfe by Chasing Gradients](https://proceedings.mlr.press/v119/combettes20a.html) | CPU 笔记本、8 GB RAM | [代码](https://github.com/cyrillewcombettes/boostfw) |
| 9 | CVPR 2026 | [DualReg: Dual-Space Filtering and Reinforcement for Rigid Registration](https://ustc3dv.github.io/DualReg/) | CPU 计时证据；FPFH/预计算输入条件 | [代码](https://github.com/LJY1229/DualReg) |
| 10 | CVPR 2025 | [Dense Match Summarization for Faster Two-view Estimation](https://openaccess.thecvf.com/content/CVPR2025/html/Astermark_Dense_Match_Summarization_for_Faster_Two-view_Estimation_CVPR_2025_paper.html) | CPU 聚类和估计；预计算 DKM/RoMa 匹配 | [代码](https://github.com/jastermark/DMS) |
| 11 | CVPR 2025 | [Practical Solutions to the Relative Pose of Three Calibrated Cameras](https://openaccess.thecvf.com/content/CVPR2025/html/Tzamos_Practical_Solutions_to_the_Relative_Pose_of_Three_Calibrated_Cameras_CVPR_2025_paper.html) | 单核 CPU 计时；公开预提取对应点 | [代码](https://github.com/kocurvik/threeview) |
| 12 | CVPR 2020 | [MAGSAC++, a Fast, Reliable and Accurate Robust Estimator](https://openaccess.thecvf.com/content_CVPR_2020/html/Barath_MAGSAC_a_Fast_Reliable_and_Accurate_Robust_Estimator_CVPR_2020_paper.html) | CPU 几何核心候选；8 GiB 未验证 | [代码](https://github.com/danini/magsac) |

## 每篇的研究问题与复现条件

### 1. Consistent Low-Rank Approximation — ICLR 2026

- 研究问题：新数据逐行到来时，在保持低秩重建准确性的同时控制子空间更新。
- 作者资源证据：第 4 节明确报告全部实验使用 AMD Ryzen 7 5700U、8 核 CPU、8 GB RAM、Python 3.10.4。
- CPU 判断范围：论文实验以低秩矩阵算法为主，不需要训练大模型。原文硬件与目标预算最接近；这里尚未运行全套。
- 数据与实验：SuiteSparse Landmark（实验取前 5,000 行、2,704 特征）、UCI Skin、UCI Rice、原论文模拟数据。
- 本轮核查：公开脚本和数据已核对。Landmark 脚本先将整矩阵转为稠密，再截取；重复 SVD 是耗时部分。正式运行需记录峰值内存与线程数。
- 阅读/复现用途：优先复现；硬件证据最强。
- [会议页面或作者项目](https://proceedings.iclr.cc/paper_files/paper/2026/hash/b14d76c7266be21b338527cd25deac45-Abstract-Conference.html)；[作者全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/b14d76c7266be21b338527cd25deac45-Paper-Conference.pdf)；[作者代码](https://github.com/samsonzhou/consistent-LRA)

### 2. Distribution-informed Online Conformal Prediction — ICLR 2026

- 研究问题：数据分布变化时，结合残差分布信息调整预测区间，兼顾覆盖率和区间宽度。
- 作者资源证据：附录 J 使用单核 Xeon CPU 测量 3,020 步校准更新；COP 平均 0.011 ms/步。该数值不包含基础预测器训练。
- CPU 判断范围：实验基础预测器为 Prophet、AR(3)、Theta。CPU 路线有依据，完整实验的 8 GiB 峰值内存未验证。
- 数据与实验：Amazon、Google 时间序列、用电需求、Delhi 温度，以及变点、漂移、重尾等原论文模拟设置。
- 本轮核查：已读 requirements、model_scores.py 和 AMZN 配置。通用代码还导入 torch/Darts；默认 AMZN 配置使用 Prophet、AR、Theta，不启用 Transformer。
- 阅读/复现用途：优先考虑；适合真实时间序列与分布漂移研究。
- [会议页面或作者项目](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5f8241131e6fd428aa49914da76b8ad0-Abstract-Conference.html)；[作者全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/5f8241131e6fd428aa49914da76b8ad0-Paper-Conference.pdf)；[作者代码](https://github.com/creator-xi/Conformal-Optimistic-Prediction)

### 3. On the Impact of the Utility in Semivalue-based Data Valuation — ICLR 2026

- 研究问题：评价指标或效用改变后，Shapley、Banzhaf 等数据价值排序是否稳定。
- 作者资源证据：附录 A.1 报告全部实验在 Apple M1 8 核 CPU、16 GB RAM 上运行，无并行。100 个数据点的一次完整估值（5 个独立 Monte Carlo 近似）约 15 分钟。
- CPU 判断范围：使用逻辑回归、小型 MLP、线性岭回归。CPU 全流程有作者证据，8 GiB 是否足够仍需实测；15 分钟不是整篇论文总时间。
- 数据与实验：论文涵盖二分类、多分类、回归数据，包括 Breast、Titanic、Credit、Heart、Digits、Wine、Iris 等。
- 本轮核查：作者仓库与 README 已核对。估值涉及多次重复拟合，样本数增加会显著影响总耗时。
- 阅读/复现用途：适合数据选择、多目标评价与数据价值稳定性研究。
- [会议页面或作者项目](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a99c41c85cd1ce4dbddfeba8908a531a-Abstract-Conference.html)；[作者全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/a99c41c85cd1ce4dbddfeba8908a531a-Paper-Conference.pdf)；[作者代码](https://github.com/taminemelissa/utility-impact)

### 4. Bandits with Single-Peaked Preferences and Limited Resources — ICLR 2026

- 研究问题：结构化偏好和有限预算下，如何在线探索未知收益并选择行动。
- 作者资源证据：附录 H.1 报告完整模拟在 MacBook Pro、8 核 CPU、18 GB RAM 上执行，使用 5 核并行，整套约 6 小时。
- CPU 判断范围：NumPy/Pandas、动态规划与 SageMath；没有 GPU 加速。8 GiB 适配尚未验证，原机器的 6 小时不能作为这里的预计时间。
- 数据与实验：原论文公开模拟协议：100 用户、20 个行动、10 个实例，每实例 10 次独立运行；部分时域达 10^6。
- 本轮核查：作者代码目录与运行入口已核对；未知排序算法需要 SageMath。可减少并发以控制内存，但应保留正式实验实例数与时域。
- 阅读/复现用途：适合数学理论、在线决策和预算分配。
- [会议页面或作者项目](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e1cf57f1e104c6c05e31894c15a65e99-Abstract-Conference.html)；[作者全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/e1cf57f1e104c6c05e31894c15a65e99-Paper-Conference.pdf)；[作者代码](https://github.com/GurKeinan/code-for-Bandits-with-Single-Peaked-Preferences-and-Limited-Resources-paper)

### 5. Online Conformal Prediction via Universal Portfolio Algorithms — ICML 2026

- 研究问题：通过两资产组合选择与 regret-to-coverage 分析，实现不需要手调学习率的在线保形预测。
- 作者资源证据：已读到的作者预印本没有明确 CPU/RAM 配置。CPU 可行性来自其标量在线更新及 Prophet/AR 基础预测器的计算结构，是推断。
- CPU 判断范围：公开论文的真实与模拟时间序列实验适合进一步检查 CPU 预算；作者官方代码本轮未核实，不能宣称现成全套可复现。
- 数据与实验：AXP、AAPL、AMZN、GOOGL、用电需求及正弦、平稳/二次趋势的原论文模拟序列。
- 本轮核查：会议身份由 PMLR 确认；实验设置由作者 arXiv 全文核对。没有把第三方 CPU 复现耗时当作原论文证据。
- 阅读/复现用途：前沿阅读与数学比较；先补齐官方代码和资源核查。
- [会议页面或作者项目](https://proceedings.mlr.press/v306/liu26y.html)；[作者全文](https://arxiv.org/html/2602.03168v1)；作者官方代码未核实。

### 6. Online conformal prediction with decaying step sizes — ICML 2024

- 研究问题：用递减步长兼顾任意序列上的长期覆盖，以及稳定分布下的分位数收敛。
- 作者资源证据：作者 README 称其为轻量实验代码；依赖 Jupyter、NumPy、Matplotlib、Seaborn、Pandas、gdown。没有核实明确 8 GiB 硬件记录。
- CPU 判断范围：可用于 CPU 校准研究。ImageNet 分支以预计算预测结果为输入；不包含从零训练图像分类器。
- 数据与实验：elec2.ipynb 与 imagenet-smallest-sets.ipynb；真实预测分数作为校准输入。
- 本轮核查：官方 README 与会议页面已核对；完整 notebook 的数据下载、峰值内存和总耗时未实测。
- 阅读/复现用途：成熟、轻量的在线保形预测基线。
- [会议页面或作者项目](https://proceedings.mlr.press/v235/angelopoulos24a.html)；[作者代码](https://github.com/aangelopoulos/online-conformal-decaying)

### 7. Fair and Fast k-Center Clustering for Data Summarization — ICML 2022

- 研究问题：用少量代表点概括数据，同时满足群体代表性和簇大小约束。
- 作者资源证据：第 5 节报告 i7-10510U 笔记本、16 GB RAM。作者算法在 Diabetes 示例不足 1 秒，在超过 200 万记录的 Electric 示例不足 2 分钟；不是全参数扫描总时间。
- CPU 判断范围：Rust 实现与 Python 接口，CPU 路线明确。全套参数扫描可耗数小时；8 GiB 峰值未验证。
- 数据与实验：Adult、Diabetes、Query Analytics、Electric。
- 本轮核查：作者代码、Python wheel、复现实验 notebook 与随附数据均在公开仓库；官方包文档也给出 thread_count。
- 阅读/复现用途：成熟的数据摘要、公平聚类与代表点选择基线。
- [会议页面或作者项目](https://proceedings.mlr.press/v162/angelidakis22a.html)；[作者全文](https://proceedings.mlr.press/v162/angelidakis22a/angelidakis22a.pdf)；[作者代码](https://github.com/LeonSering/fair_and_fast_k_center_clustering)

### 8. Boosting Frank-Wolfe by Chasing Gradients — ICML 2020

- 研究问题：改善 Frank-Wolfe 的搜索方向，提高有约束优化的收敛速度。
- 作者资源证据：第 4 节明确报告 Python 实验运行于 Intel Core i7 3.5 GHz CPU、8 GB RAM 的 Ubuntu 笔记本。
- CPU 判断范围：原论文有 8 GB CPU 实验依据；不需要 LLM API。属于成熟方法基线，不是 2026 新论文。
- 数据与实验：稀疏信号恢复、Gisette、MovieLens 100K、航空图像共定位等。
- 本轮核查：作者仓库包含实验 notebook 与多份数据；本环境还没有执行复现。
- 阅读/复现用途：硬件匹配的约束优化基线；适合先建立完整 CPU 实验流程。
- [会议页面或作者项目](https://proceedings.mlr.press/v119/combettes20a.html)；[作者全文](https://proceedings.mlr.press/v119/combettes20a/combettes20a-supp.pdf)；[作者代码](https://github.com/cyrillewcombettes/boostfw)

### 9. DualReg: Dual-Space Filtering and Reinforcement for Rigid Registration — CVPR 2026

- 研究问题：结合特征对应关系过滤和局部几何优化，实现刚性点云配准。
- 作者资源证据：作者项目页报告 KITTI 上相对 MAC 的 32 倍 CPU 时间加速；该数字是方法对比，不是本环境测量。RAM 配置本轮未核实。
- CPU 判断范围：有 FPFH 与 FCGF 两条分支。纯 CPU 项目可优先核查手工 FPFH 分支或公开预计算对应关系；FCGF 特征网络的训练/重新提取不包含在这一 CPU 判断里。
- 数据与实验：3DMatch、3DLoMatch、KITTI。
- 本轮核查：作者仓库已核对 C++ 运行入口。额外带法向的对应关系下载指向百度网盘，当前环境能否下载未验证。
- 阅读/复现用途：前沿 CVPR CPU 几何候选；需先验证数据获取、编译与内存。
- [会议页面或作者项目](https://ustc3dv.github.io/DualReg/)；[作者全文](https://arxiv.org/abs/2508.17034)；[作者代码](https://github.com/LJY1229/DualReg)

### 10. Dense Match Summarization for Faster Two-view Estimation — CVPR 2025

- 研究问题：把大量图像匹配点压缩为代表匹配与小矩阵，减少两视图 RANSAC 和优化的计算量。
- 作者资源证据：第 4.1 节报告全部计时在桌面 CPU 上完成；K-means 使用 CPU FAISS。没有明确 8 GiB RAM 记录。
- CPU 判断范围：CPU 判断覆盖聚类、摘要、位姿求解和评测，以已有匹配点为输入。作者提供 DKM/RoMa 预计算匹配下载；不含这些神经匹配器的训练或重新提取。
- 数据与实验：MegaDepth-1500、ScanNet-1500、WxBS；主实验包含每图像对 10,000 个匹配、128 簇的设置。
- 本轮核查：已读作者 README、requirements 和论文实现节；仓库提供 demo、run_clustering.py、完整 benchmark notebook。
- 阅读/复现用途：优先核查的 CVPR 候选；公开预计算输入使 CPU 研究更实际。
- [会议页面或作者项目](https://openaccess.thecvf.com/content/CVPR2025/html/Astermark_Dense_Match_Summarization_for_Faster_Two-view_Estimation_CVPR_2025_paper.html)；[作者全文](https://arxiv.org/html/2506.02893v1)；[作者代码](https://github.com/jastermark/DMS)

### 11. Practical Solutions to the Relative Pose of Three Calibrated Cameras — CVPR 2025

- 研究问题：用四组对应点构造近似几何，并结合最小求解器与 RANSAC 求三相机相对位姿。
- 作者资源证据：作者报告 RANSAC 计时使用单核 Xeon Gold 6338；附录求解器计时使用 i9-10900X。RAM 配置没有核实。
- CPU 判断范围：位姿后端在 CPU 上运行。公开预提取对应点可避免重新运行神经特征提取器；8 GiB 全实验尚未验证。
- 数据与实验：PhotoTourism、Cambridge Landmarks、Aachen Day-Night v1.1；公开测试涵盖多个场景与相机三元组。
- 本轮核查：作者提供 PoseLib 分支、eval.py 与预提取数据的 Zenodo 链接。README 示例为 64 workers，目标机器需降低并发并记录总耗时。
- 阅读/复现用途：适合几何求解、近似误差与鲁棒估计研究。
- [会议页面或作者项目](https://openaccess.thecvf.com/content/CVPR2025/html/Tzamos_Practical_Solutions_to_the_Relative_Pose_of_Three_Calibrated_Cameras_CVPR_2025_paper.html)；[作者全文](https://arxiv.org/html/2303.16078v5)；[作者代码](https://github.com/kocurvik/threeview)

### 12. MAGSAC++, a Fast, Reliable and Accurate Robust Estimator — CVPR 2020

- 研究问题：利用噪声尺度边缘化和迭代重加权，提高存在错误匹配时的几何估计质量与速度。
- 作者资源证据：作者提供 C++ 与 Python 实现，并已集成 OpenCV；8 GiB 硬件配置本轮没有核实。
- CPU 判断范围：几何估计核心适合 CPU，这是基于算法与实现的判断。完整原论文实验、输入数据处理与峰值内存仍需验证。
- 数据与实验：单应矩阵、基础矩阵、本质矩阵、位姿估计；可与 DMS/三视图工作构成鲁棒几何估计基线链。
- 本轮核查：已核对作者仓库、例程、数据目录与编译依赖；本环境 Python 3.12 的安装兼容性尚未验证。
- 阅读/复现用途：成熟鲁棒估计基线，不应当作 2026 前沿论文。
- [会议页面或作者项目](https://openaccess.thecvf.com/content_CVPR_2020/html/Barath_MAGSAC_a_Fast_Reliable_and_Accurate_Robust_Estimator_CVPR_2020_paper.html)；[作者全文](https://arxiv.org/pdf/1912.05909)；[作者代码](https://github.com/danini/magsac)

## 优先讨论的研究路线

1. **流式矩阵表示与稳定性**：先读第 1 篇。数据依次到来时，比较整体重建误差、历史数据误差与更新成本。原论文已经研究低 recourse，不能把“少改动”重新包装成创新点；少改动也不等于旧任务能力保留。
2. **分布漂移下的在线不确定性**：一起读第 2、5、6 篇。比较覆盖率、区间宽度、漂移后的恢复时间与学习率敏感性。优先使用原论文公开真实数据与协议。
3. **视觉几何中的计算量与可靠性**：一起读第 10、11、12 篇，再看第 9 篇点云方向。以公开对应关系/手工特征为输入，研究求解、摘要和鲁棒性的权衡。
4. **数据选择与多目标稳定性**：一起读第 3、7 篇。第 8 篇提供约束优化方法参考，第 4 篇提供预算约束与在线决策视角。

这些是方向和文献入口，不代表已经确认新颖性、发现可投稿缺口或完成新方法实验。下一步应冻结原论文配置，核实数据和依赖，在目标环境测单次任务的峰值内存与耗时，再安排完整基线及多随机种子实验。降低并发可以控制内存，但改变样本量、时间长度或 benchmark 时，应明确标为缩减实验。

