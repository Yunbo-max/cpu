# R014：接续第二类原生任务——完整规模交通分配

项目：`boostfw-cpu-autochat-20261009`。日期：2026-10-10。

**本轮实际完成100次主对照和120次计时复测。V2主矩阵由160/700推进至260/700；另外300次计时复测单列，不能抵扣剩余440次主运行。整体研究未关闭，状态为`continuation_pending`。**

## 1. 连续推进了什么

本次从R013真实证据包恢复，校验原始ZIP SHA256，并保留其全部原字节；没有重新运行稀疏信号恢复实验。按V2已登记的第二类任务依次完成：作者源代码核对、完整500节点生成器与Oracle资格核验、100个主比较、另一套最短路评分重算、120次交叉顺序计时复测、配对统计与清单更新。不是仅更新定时任务或在单一小任务上无限加种子。

## 2. 原生问题与明确披露的实现差异

来源：Combettes & Pokutta，ICML2020，*Boosting Frank–Wolfe by Chasing Gradients*；仓库`cyrillewcombettes/boostfw`固定提交`309f5fa2af04790f15d24c96bc42e7178cc63b55`，notebook Git blob`11781a7a74b52b71abcd113c886c2785066ecd9a`。

保留作者20层×25节点、相邻层Bernoulli(.5)连边、全部可达OD对及原BFS需求生成顺序，20个独立网络/需求实例使用种子0–19。500节点全部保留，每实例5827–6041条边、112696–112910个OD对，没有用缩小图或手造替代benchmark。资格核验仅用单独种子700；确认种子1000–1019未生成。

目标仍为作者的`sum(x_e + .03*x_e**5/c**4)/250000`，其中`c=number_OD/500`；评分仍为原始绝对Frank–Wolfe gap。原代码`traffic=True`时对NNMP residual做非负截断，此分支原样保留。

当前运行是**兼容移植而非未经修改的作者notebook**：仅存已有边的等距坐标；Numba实现精确DAG最短路替代NetworkX路径枚举；解析梯度替代autograd；五个方法共享高精度凸一维导数求根，替代原绝对目标容差golden search。零成本平局时可以选取不同的最优路径，因此不宣称原作者逐步轨迹或原120秒时间结果精确复现。原notebook选定源码通过GitHub工具读取并转录保留，未取得全文件原始字节。

## 3. 前瞻主比较，不再半秒截断

`protocol/PREREG_R014.md`在主数据结果前登记，SHA256 `74eb79d119b0321975f46bf124a48f71b1c4792e89dd177bfc9726b7e99e08b2`。主假设H014：小K boosting是否在第二类原生问题上仍改善达到相同精度的实际耗时？主要比较BoostK5对FW-LS，主精度gap≤.01，实质优势阈值为FW时间/BoostK5时间≥1.10；其他精度为描述性完整曲线。

5个比较臂：FW-LS、AFW-LS、BCG、BoostK2、BoostK5，各20个实例，共100次。每次最多5CPU秒、7wall秒、10000外层步；实际达到最终gap≤.001才正常结束。记录100、1、.1、.01、.001五级观察达标时间。所有求解器初始化、在线评分和线搜索计入主CPU时间；公共生成器/JIT预热/初态另记且保留在OS进程总量。文件压缩、离线报告不计为time-to-accuracy。

**100/100全部达到最终目标；无已完成运行数值失败、无预算内未收敛、无删失。** 这些是100个方法–实例运行，统计独立单位是20个网络/需求实例。

| 方法 | 到gap≤.001的CPU中位秒 | 算法LMO中位数 | 外层步中位数 | 达标 |
|---|---:|---:|---:|---:|
| FW-LS | 1.1515 | 240 | 240 |20/20|
| AFW-LS | 1.3759 | 240 | 240 |20/20|
| BCG | 1.4857 | 256.5 | 260 |20/20|
| BoostK2 | 1.8042 | 420 | 210 |20/20|
| BoostK5 | 1.8644 | 442 | 200 |20/20|

BoostK5外层步更少，但实际调用更多LMO、耗时更长。与前一类稀疏恢复结果相比，排名发生变化。不过**不能只凭跨任务对比把变化因果归结于LMO成本**：损失、约束几何、NNMP截断分支及线搜索都不同，需要机制控制进一步区分。

## 4. 完整复测与统计

在100个主运行后、任何复测结果前固定计时补充协议。FW-LS和BoostK5在每个实例各新增3次完整运行，按实例和重复轮次交叉顺序，共120次。所有120次达到目标，最终向量SHA、外层步数和全部算法/诊断计数与对应主实验一致；不是额外120个独立网络。

先对每个实例/方法的3次CPU时间取中位，再以20个实例为单位做10000次配对bootstrap。区间是开发性、条件性的描述，不把同一轨迹检查点和同一实例重复当独立样本。

| 精度 | FW中位CPU秒 | BoostK5中位CPU秒 | BoostK5/FW配对几何均值 | 描述性95%区间 | FW更快的实例 |
|---|---:|---:|---:|---|---:|
| **.01，预设主终点** | 0.4914 | 0.5823 | 1.1690 | [1.1306, 1.2090] |20/20|
| .001，最终精度 | 1.1747 | 1.8923 | 1.6087 | [1.5859, 1.6312] |20/20|

H014结论：`DEVELOPMENT_COUNTEREVIDENCE_TO_TRANSFER`。当前问题/实现不支持把先前稀疏恢复中的小K CPU优势直接外推到交通任务；这不是对原论文一般有效性的否定，也不是新算法贡献或独立科学验收。

## 5. E04核验与失败记录

主比较的600个达标及最终状态，使用**不同实现的SciPy Dijkstra**重新计算OD加权最短路代价与真实gap，最大gap差`7.11e-15`；目标函数用原顺序和math.fsum检查，最大差`4.09e-14`。100个输入/初态绑定、2405条主轨迹、非负性与流量守恒、AFW/BCG凸分解及NNMP非负更新见证均检查。聚合流量守恒本身不能证明每个OD可行性，必须结合原OD路径构造和凸组合更新。

复测720个保存状态与已重算的主状态逐位相同，另检查2763条计时轨迹和全部实际调用计数；没有为增加检查次数重做相同评分。主比较23050外层步，复测26430外层步，不用这些相关步骤扩大样本数。

保留失败：预期RED测试；首个向量化目标函数与原标量求和在巨大目标值上差`2.21e-9`，通过保留原运算/求和顺序修复，未放宽`1e-9`容差；seed0初版记录模式出现objective数值/计数重名，在任何优化步前失败，修复为`calls_*`字段并补充回归测试；这是前轮出现过的模式，已记录重复工程错误。原源码、失败输出和CPU都保留。seed4外层工具超时后，核对原生退出码0、DONE和5份结果确认完成，没有重复已完成运行。

全部E04为**SELF工程审查**。使用独立最短路实现有助于发现实现错误，但不等于另一位研究者的独立科学审稿。

## 6. 本轮真实资源

宿主4核配额、4GiB内存，BLAS单线程，一个科学进程，无GPU/SSH/Docker/付费API/新服务。共51份不重叠GNU time原生日志，含测试/资格/失败/主实验/复测/评分检查：

- 新增子进程CPU：**470.67秒**；原生日志wall总和**471.18秒**，低于600秒实验/检查窗口。
- 最大单子进程wall：**11.99秒**，低于120秒限制。
- 最大RSS：**279292KiB（约272.7MiB）**。
- 继承R013已知子CPU下界594.83秒，累计**1065.50秒**。不含模型、检索、报告、绘图、打包或其他未量化成本，不是账单。
- 退出码0的原生日志47份；其余4份为保留的RED测试或已修复工程失败。100主运行和120计时复测均在成功退出的子进程中完成。

## 7. 全局完成清单与接续

| V2任务 | 主slot完成/计划 |
|---|---:|
| 稀疏信号恢复（R013）|160/160|
| 交通分配（本轮）|100/100|
| Gisette稀疏逻辑回归 |0/160|
| MovieLens100K |0/120|
| YouTube-Objects aeroplane |0/160|
| **总计**|**260/700**|

计时复测R013180+R014120=300次单列。V2共560次已完成运行，不意味着560独立数据集或700主任务已全部完成。近期强基线、必要机制/规模控制、第三至第五类真实数据、独立科学审查和未触及确认仍有明确缺口。

下一实际动作：R015: restore the260/700 executed primary inventory, not the old160/700 snapshot. Qualify a third published native task (Gisette, MovieLens100K, or YouTube-Objects) from authenticated full source data; inspect complete loader, preprocessing, objective, applicable baselines and oracle before registering its budget and executing its complete comparison. One bounded retrieval attempt only when a valid source/transfer capability is available; no repeated failed DNS or blocked Drive route. If raw data transfer is genuinely still blocked, perform a specified source-linked mechanism control on the saved full-size traffic task, separating native residual clipping, exact DAG LMO cost and line-search differences. This is an additional declared ablation, not a third dataset or a renamed original method, and does not reduce the440 remaining primary slots. Recent strong-baseline implementation qualification and independent scientific review also remain open. Never rerun already completed R001-R014 or interpret a report/phase completion as overall completion.

## 8. 保存与运行状态

证据包保存本轮全部源文件、输入、输出、凸分解、原生日志、失败、统计、图表、清单和本检查点，并内嵌未经改动的R013原始ZIP。保留完整源文件和输入SHA；归档SHA在归档外侧单列以避免自引用。没有重试或绕过此前被安全检查阻止的Drive上传，Drive规范JSON仍旧，不能当作本轮最新状态。

本轮科学子进程已结束，当前宿主未检测到遗留科研进程；原有小时接续任务继续使用，不新建任务。**整体目标未完成、未停用；周期触发不是触发间永久占用CPU的证明。**

## 来源入口

- 原论文：https://proceedings.mlr.press/v119/combettes20a.html
- 固定源码：https://github.com/cyrillewcombettes/boostfw/blob/309f5fa2af04790f15d24c96bc42e7178cc63b55/boostfw_code.ipynb
- 本地选定源码转录：`sources/author_traffic_reference.py`；原生资格核验：`results/QUALIFICATION.json`；全部计量见`environment/CUMULATIVE_LEDGER.json`。

## 证据分包

完整交付由一个主包和两个原始状态包构成。主包含全部代码、输入、逐项数值、轨迹、日志、统计、FW/Boost状态、计时复测状态及未修改R013包。另两包按网络实例0–9和10–19保存AFW/BCG完整原始`states.npz`（包括大规模active-set凸分解），不丢弃、不重新编码原字节。将三包解压到同一目录后才能完整重跑上述E04；各包自带成员哈希，主包`EVIDENCE_PARTS.json`提供另两包的SHA256。分包只是传输安排，不改变科学数据或运行次数。
