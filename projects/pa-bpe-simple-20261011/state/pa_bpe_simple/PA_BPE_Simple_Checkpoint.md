# 最新规范状态：generation 20，2026-10-12

本轮对固定Classical、hybrid（前500次global）和base的1000个merge逐步做了精确重放，输入是既有每语100000预分词训练字典与已暴露TICO开发集；独立Python预分词重建在rank1000逐语言均值上与旧tokenizers评测精确一致。hybrid与Classical前500个merge逐字节相同，rank500开发Gini均为0.0386621。

hybrid后500步把当前最高成本语言作为selector；500步中428步该语言也获得最大实际开发token降幅，487步获得正降幅。相对Classical后500步，hybrid多减少法语2305个token，但少减少英语4836、西语633，净少减少3164；开发Gini从0.0386621降到0.0175252，而Classical尾部升到0.0430154。这支持“global前缀保留高效共享压缩，有限parity尾部重新分配收益”。

但冻结的“hybrid尾部更平滑”预测被否定：hybrid与base在rank501–1000均有208次精确pair-gap符号翻转；hybrid的208次全部发生在法西之间，目标切换222次，反而多于base的215次。hybrid的稳健折中更符合“延迟/限制暴露于同一反应式控制器”，而不是尾部控制器消除了局部chattering。负结果完整保留。机制主核验36项、解释核验16项全部通过。

四个科学attempt均exit0，新增wall 100.866952147秒，累计1752.873801133秒；峰值RSS 52,617,216字节，无OOM、timeout或内存等待。一次重复supervisor启动被现有锁阻止，原supervisor随后安全完成任务，无重复科学命令；宿主`ps`管理探针再次出现`fatal library error, lookup self`，runner状态与科学结果不受影响。全部attempt终态、reservation0，supervisor正常停止并确认退出。

下一步仅在TICO开发上训练预先指定的`hybrid-window`候选：前500次global，后500次采用作者现有moving-window控制器，沿用已冻结`window=100, alpha=2`。检验它是否降低法西翻转与目标切换，同时保持正Gini收益和受限总成本；不得在新确认域上调参。若开发门通过，再另行锁定一个未曝光合法对齐域作确认。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake19_Report.md`、`evidence/wake19_handoff.json`、`evidence/incidents_wake19.json`、`execution_windows/wake19/output/mechanism_summary.json`、`mechanism_verification.json`、`mechanism_interpretation.json`及`mechanism_interpretation_verification.json`。

# 历史原字节段落保留

# 最新规范状态：generation 19，2026-10-12

本轮对已经冻结的Classical、PA base/window/hybrid/ratio 1000-merge codes，在FLORES-200 devtest的1012个英法西内容对齐句子上完成固定重放，并以既有GlobalVoices结果计算暴露域稳健前沿。FLORES上base/window Gini最低（0.007425/0.007741），但总token成本均增加约4.0%；hybrid Gini 0.022759、总成本+1.7939%、最差语言成本+0.1674%；ratio Gini 0.048134，较Classical恶化。

冻结三目标反证未成立：没有次级臂同时比hybrid更低Gini且不增加总成本或最差语言成本。跨域最小公平收益/最大成本准则下，Classical与hybrid构成稳健Pareto前沿；hybrid严格支配base/window，跨域最小Gini改善0.0179368、最大总成本增幅1.7939%、最大最差语言成本增幅0.1674%。这只支持固定候选中的稳健折中，不证明hybrid在每域Gini最低或其机制具有因果性。两组独立核验分别通过42和19项检查。

五个科学attempt均exit0，新增计费wall 74.569823445秒，累计1652.006848986秒；峰值RSS 37,355,520字节，无OOM、timeout或内存等待。首次提交因跨窗口证据路径不安全在科学启动前被拒绝，复制并哈希绑定为本窗口输入后修复；未消耗attempt。任务全部终态且reservation0，闲置supervisor受控中断后的health为lost，保留为管理事故而非科学失败。

下一步：只用既有固定codes和开发产物，审计hybrid前500个global merges前后merge ownership与逐语言边际token效果，解释其为何避免signed-gap overshoot；两个已暴露确认域不得用于新调参。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake18_Report.md`、`evidence/wake18_handoff.json`、`evidence/incidents_wake18.json`、`execution_windows/wake18/output/flores_secondary.json`、`flores_secondary_verification.json`、`cross_domain_frontier.json`及`cross_domain_frontier_verification.json`。

# 历史原字节段落保留

# 最新规范状态：generation18，2026-10-12

FLORES-200 `devtest` 1,012 个英/法/西对齐句的结果前冻结主比较：fixed hybrid 将 aggregate Gini 从 Classical `0.0406959383` 降至 `0.0227591358`，改善 `0.0179368025`，配对句 bootstrap95 `[0.0161054038,0.0200599109]`；总成本 `+1.7938896%`、最差语言成本 `+0.1674367%`。这支持有代价的第二未见域 transfer，不是无成本、广义多语言或下游结论。

官方公开归档 SHA256 `b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6`，CC-BY-SA-4.0；新版 FLORES+ gated 文件 HTTP401，未绕过。计划在正文访问前冻结。纯 Python evaluator 在旧14,550个整数成本上零差异后才打开新文本。三段有限窗口共7 attempts（3成功、4失败），新增wall `155.701309732s`，累计 `1577.437025541s`，reservation0，无活动科学进程。恢复必读 `PA_BPE_Wake17_Report.md`、`evidence/wake17_handoff.json` 与 `execution_windows/wake17c/output/flores_primary.json`。下一步独立核验、补固定次要arms并分析hybrid机制；FLORES和GlobalVoices均已曝光，禁止后验调参后冒称新确认。

## generation17 历史状态


英/法/西训练各100000个作者预分词单元；1000合并；实际词表均1256。训练是有限便利样本，不是论文完整复现。TICO官方开发971组中，970组在仅去除英文首尾ASCII空白后按句ID、英文正文与URL一致；1组撇号差异排除。旧双语TICO已有暴露，开发结果不是独立评测。

| 方法 | TICO开发Gini | GlobalVoices首次确认Gini | 确认总token成本变化 | 确认最差语言成本变化 |
|---|---:|---:|---:|---:|
| Classical（等预分词数据量对照） | .043015 | .022573 | 0 | 0 |
| PA base | .001295 | .018368 | +3.91% | +4.70% |
| PA window（冻结主比较） | .000806 | .019543 | +3.70% | +4.89% |
| PA hybrid（前500全局，冻结次比较） | .017525 | .002323 | +1.74% | -2.15% |
| PA ratio(1,1,1) | .048972 | .031072 | +1.29% | +3.29% |

GlobalVoices为预封存512三语单元、267英文文档cluster。主window绝对Gini改善0.003030，paired文档bootstrap95%区间[-0.006540,.009798]跨0；开发改善保留率7.18%仅为点估计描述，不代表统计显著衰减比例。Hybrid次比较改善0.020250，区间[.010838,.024575]；不能确认后改成主比较。Ratio两域都比Classical差，负收益比1.427不能解释为保留正收益。

机制分解：window把TICO英法差距-12.568纠正到-.219；同类纠正搬到GlobalVoices把-5.578推到+4.932，英语成为最差成本语言。这是可核验成本分解，不是完整因果机制证明。

基于该证据，只构造并测试一个half-damped target候选：按Classical开发成本固定weights=(1+各语成本/均值)/2，其余作者base不变。开发Gini .021564、总成本+1.50%；已暴露GV探索Gini .006022、总成本+1.45%。它缓解过度纠正，但公平性仍差于强hybrid，故不宣称方法改进或新颖性。GV对未来自适应候选已不再是盲确认。

已保留每句成本、全部代码/模型、计划、原始输出、失败与CPU/wall/RSS。Gini两独立公式、整数总量复核、真实词表与独立merge replay通过；三次只读审查记录其范围。来源CC许可、条件法西分片证明与语义泄漏不能完全排除等限制仍保留。

两次内存保护提前退出后等待/释放本项目可恢复副本并成功续跑，无OOM观测。20次命令attempt不是20个科研循环。完成的是一个固定比较→跨域失效证据→机制→单候选→负结果反馈链。

下一步：保留候选负结果，研究hybrid稳定性及语言差距变化；在新合法三语域冻结真正独立确认，不继续用已暴露GV调参并冒称确认。持续研究不停止。

新增wall 121.11081243499211 秒，累计 1421.7357158089917 秒，无累计时间上限。读取evidence/wake16_handoff.json、incidents_wake16.json、wake16b/confirmation_plan.json与三个review。

# 历史原字节段落保留

# 最新规范状态：generation16，2026-10-12

已从 GitHub commit fd7405b1a643dbecee1e5af712e6007e0cfcb6bb 完整核验1954个历史状态文件，再串行执行17项命令（14成功、3失败，失败均保留），新增计费wall 303.636533秒，累计1300.624903秒，无累计时间上限。

三份最小原始分片完整SHA256通过，独立不同batch重读通过；英语374条符合2013-20，法语4923和西语34861条均不符合。这是真实的来源负结果，未放宽年份。随后固定新协议，获取法西首个分片的第0完整行组各1000条；从固定HTTPS端点检查206范围、总长、字节SHA与Xet ETag，未声称验证整份4.8GB LFS对象。独立审查仅接受此条件来源链及有限便利样本。

冻结2374条便利开发帧，SQLite完整帧重复/缺失ID处理与盲化确认去污染实际运行；2374条均被当前规则接受（不是不存在所有语义重合的证明）。选中英209、法155、西151篇，分别恰好100000作者pretoken。词表唯一pretoken为14763/15713/16683，初始symbol mass506499/536419/548313。两个作者字典解析器均精确roundtrip。构建22.266秒，RSS169402368字节。

固定作者Classical、PA ratio、PA dev完整CLI各完成32合并，wall0.573/1.024/2.361秒，最高RSS114835456字节。**只作接口和资源诊断。PA dev故意复用非平行训练字典检查同一dict-input开关，所有这批codes不准进入公平性表。没有新公平性结果、没有打开确认raw或结果。**

两次4MiB footer guard失败后用分块上限修复；一次共享内存<384MiB提前退出，等余量恢复后成功。无OOM、无timeout。一次失败资源文件被重试覆盖后，已按原receipt SHA完整恢复到独立证据路径；原receipt未改。科学作业均终态、reservation0。有限执行器已退出，continuous_research和原任务继续；不承诺两轮间常驻CPU。

下一步：Independently confirm selected-row-to-dictionary budget reconstruction as needed, then freeze and recover content-aligned independent en/fr/es development texts distinct from untouched GlobalVoices confirmation. Use bounded convenience frame transparently; first run a representative merge/resource pilot and then Classical, PA base/window/hybrid/ratio and data-balance controls. Never score the32-merge CLI diagnostics or nonparallel dev dictionaries as fairness.

大原始分片及页脚按哈希拆块存档，索引有精确恢复路径；新生成的row manifest、字典、日志、代码和失败均保存。


# 以下为原历史，原Library首选写回要求已被GitHub WORKFLOW替代

# 最新规范状态：generation 15，2026-10-12

本轮从generation14 recovery checkpoint恢复，并按`evidence/wake13_adapter_recovery_spec.json`重建、实际复跑和立即保存了修复版盲化确认索引adapter。固定SHA256 `26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7`的索引导入1536条确认记录（英/法/西各512）、27225条唯一shingle、总mass27346和801个URL hash；20/20项验证通过，exact/shingle逐记录差异与URL集合双向差集均为0。独立只读审查无阻断缺陷，因此`blinded_confirmation_adapter`窄门正式PASS。

PASS只覆盖adapter mechanics与冻结索引字段/集合保真；正确early-bind路径、wrong-source/manifest完成态重导入、并发SQLite/WAL竞态及全语料规范化等价仍是非阻断未覆盖。真实row→fixed shard、production development selection、100000-pretoken预算整合、tokenizer训练和公平性结论继续HOLD。两条runner科学任务均exit0，计费wall合计0.539728273秒、reservation0、峰值RSS低于20MiB；累计计费wall为996.9883702889974秒。停止状态已持久化、attempt全终态且无活动PID；supervisor最后health为lost而非正常退出回执，已作为收尾事故保留。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake14_Report.md`、`evidence/incidents_wake14.json`、`evidence/wake14_handoff.json`、`execution_windows/wake14/output/blinded_adapter_verification.json`及`execution_windows/wake14/evidence/independent_review.json`。下一步只做真实开发候选的逐行固定shard provenance与有界物化，再把wake10预算合同和本轮结果盲selector串接；这些门通过前不训练tokenizer。

本代从Library version14、archive SHA256 `911121ca7d8d5f65e2c8fa30674f8268a95629f113d0e383d2281f790d1c827f`恢复，内部1873个非manifest成员全部匹配；写回必须使用`expected_current_version=14`，成功后才释放writer。持续研究授权与原调度不变。

# generation 14 历史状态（保留）

本轮实际实现并两次运行了wake12盲化确认索引→wake11 selector adapter。初版导入1536条确认记录（英/西/法各512）、27225条唯一shingle、总mass27346及801个URL哈希，12项检查通过；独立审查随后发现调用顺序相关的协议绑定漏洞及oracle/URL集合/type核验不足。修复版加入顺序无关protocol/contract/source绑定、最终emission守卫、SQLite列与runtime type检查、读取后重哈希、硬编码独立oracle及URL集合双向差集，实际20项检查通过。四个科学命令均exit0，runner计费wall合计1.989837265秒。

但是在持久写回前，宿主于07:50 UTC清除了整个scratch根，源码、SQLite、JSON和runner receipts全部丢失。本代仅从Library version13恢复并保存事故、审查和精确重建规范；终端观察不能替代可哈希证据。因此production adapter正式状态仍为HOLD，下一轮必须按`evidence/wake13_adapter_recovery_spec.json`重建复跑并立即持久化。真实row→shard、训练、tokenizer与公平性门均未打开。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake13_Report.md`、`evidence/incidents_wake13.json`、`evidence/wake13_handoff.json`、`evidence/wake13_adapter_recovery_spec.json`及`review/wake13_blinded_adapter_review.md`。本代从Library version13、archive SHA256 `8c0c6b716d093d7b78b58c83516e5396a03f8bd5ec8a6030a6e31699510a200a`恢复；写回必须使用`expected_current_version=13`。

# generation 13 历史状态（保留）

本轮恢复并固定了官方 OPUS GlobalVoices `v2018q4` 英/法/西三份 raw archive，实际内容 SHA256 分别为 `974c2b10…fa9b3f`、`84cfd37d…36587`、`2af6fb98…be55`。512 个预冻结三语单元全部解析成功；三语各涉及267个文档，目标句数为英567、法561、西572。所有工作仍处于结果盲确认基础设施阶段，没有计算 tokenizer 或公平性结果。

首版盲索引虽通过结构核验，独立审阅仍给出 HOLD：未从磁盘重哈希 archive、未重算 canonical unit identity、URL 尾点/IPv6 规则不完全一致、缺少项目/协议/检查点绑定。修复版 builder 逐项 fail-closed 后重新实际运行：23.815434837秒、峰值103,018,496字节，SQLite SHA256 `26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7`。独立 verifier 再次流式哈希三份archive并通过2,286个断言/45类检查，SQLite integrity=`ok`；1536个文档引用、512个未盲化unit ID、96个URL与96个规范化句样本均未以明文出现。独立修复审阅对原5项逐项PASS，但明确不代表production selector、row→shard、预算整合、tokenizer或公平性门通过。

本轮runner共10个attempt：8项成功、2项真实失败并保留（raw archive成员`.xml.gz`引用与ZIP内`.xml`表示不一致；首次修复提交CLI参数名错误）。科学命令计费wall 116.766455980003秒、reservation0，累计994.4588047509768秒。runner受控停止；无活动或未知科学进程。三份raw archive另存持久大档案 `PA_BPE_GlobalVoices_v2018q4_Raw_Source.zip`，Library ID `libfile_fab29332f8248191850f2decc6e6b5a4`、version0、SHA256 `825a8c063b19d4b1dc21f8a540ea2acbe5e11fa1da1cd6bfdeac5200c6805b6c`，主检查点不重复嵌入这233MB payload。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake12_Report.md`、`evidence/wake12_handoff.json`、`evidence/incidents_wake12.json`、`external_artifacts.json`、`execution_windows/wake12/output/blinded_index_verification_v2.json`、`review/wake12_blinded_index_repair_review.md`及`review/wake12_blinded_index_acceptance.json`。下一步只做仍结果盲的 production adapter：把 wake12 hash-only confirmation index 接入 wake11 selector，并对真实 wake9 shard 行建立逐行来源身份与100,000-pretoken预算；这些绑定通过前禁止训练或打开确认公平性结果。

本代从Library version12、archive SHA256 `8cc548d96af4eff85c50f543f2e732d642f9d55fa0967b0d10d1eb1cc1ced04c`恢复，内部1687个非manifest成员全部匹配；写回必须使用`expected_current_version=12`，成功后才释放writer。持续研究授权与原调度不变。

# generation 12 历史状态（保留）

本轮冻结并实现了结果盲GlobalVoices去污染与SQLite外排的有序行流，最终v6的25项检查全部通过。规则覆盖GlobalVoices域名、规范URL、NFKC/casefold/空白折叠后的精确正文、同语种完整SHA-256五词shingle多重集containment≥0.80、非法/非字符串URL、DNS根尾点与IPv6；重复ID全部副本拒绝，缺失ID硬失败。协议/实现/严格模式/训练输入/确认manifest全部绑定，完成阶段可关闭重开幂等，未完成阶段禁止输出，异常事务回滚，accepted行以流式原子manifest写出。

英法西已曝光探针40/40/44行与直接SHA256排序完全一致；20,000行生成器软件探针全部流式通过，进程内峰值从18,872增至20,664 KiB，外部测量峰值21,159,936字节。该探针不等于1.60TB生产资格。独立审查先否定并促成修复了三项：假重启幂等、Python线性`dup/out`累积和64位截断shingle；后续URL/阶段绑定缺口亦已修复。最终只接受“前瞻软件里程碑”，真实确认集builder、日志审计、row→固定shard真实性、100,000-pretoken预算整合、正式payload、生产规模、崩溃恢复、tokenizer训练与公平性结论全部HOLD。

本轮6个runner attempt中4项exit0、2项真实exit1并保留：v1 SQLite schema lock（0.087114321秒）与v4测试helper通配导入`NameError`（0.084865906秒）。总计费wall 3.370233824986秒、reservation0；最终runner受控停止，无活动或未知科学作业。宿主`ps` loader错误与两次资源探针CLI拒绝均在科学任务前发生，已降级/修复并记录。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake11_Report.md`、`evidence/wake11_handoff.json`、`evidence/incidents_wake11.json`、`execution_windows/wake11/decontamination_selector_protocol.json`、`execution_windows/wake11/output/decontam_selector_verification.json`、`review/wake11_decontam_selector_review.md`及`review/wake11_decontam_selector_acceptance.json`。下一步先以结果盲方式对真实GlobalVoices源manifest构建指纹并核验row→wake9固定shard，再整合wake10预分词预算路径；不重跑本轮软件检查。

本代从Library version11、archive SHA256 `6ef4c0be3a093e370841b0b48805298e82ed1833d15d22be840f4abc862db480`恢复，内部1562成员全部匹配；写回须使用`expected_current_version=11`，成功后才释放writer。持续研究授权和原调度不变。

# generation 11 历史状态（保留）

本轮将确定性行选择与匹配训练质量推进为可执行、独立审查的软件合同，但正式payload与训练总门仍HOLD。协议固定语言分离的stable-ID SHA256排序、缺失ID数据集级硬失败、重复ID全副本拒绝、原始UTF-8正文哈希、作者`Whitespace()+ByteLevel(use_regex=False)`预分词、每语第一批100,000 pretoken开发预算及边界行确定性前缀；训练表示采用作者`--dict-input`精确Counter。

项目隔离环境固定`tokenizers==0.22.1`。修订版25项检查全部通过：英/法/西已曝光源探针各精确256个pretoken；输入反转/固定置乱不变；重复/缺失ID行为、Counter总量、多文档边界、零pretoken及预算不足均通过；固定Classical和PA源码AST提取的字典解析器对三语全部round-trip一致。该结果仅是软件/作者解析器不变量PASS，不是生产selector或原生命令PASS。等256 pretoken时作者初始symbol mass为1418/1315/1429，故后续必须单独报告。

独立审查修正了PA-BPE输入合同：作者一个`--dict-input`开关同时作用train/dev，因此dev-objective路径必须将dev也按同一预分词器字典化；ratio路径不得传dev。完整作者CLI仍未验证。结果盲GlobalVoices去污染、受限内存全局selector、真实row→固定shard溯源、完整wheel/Python/platform锁及与payload原子生成的selected-row manifest均未完成；payload接受、tokenizer训练与公平性结论全部HOLD。

本轮4个runner任务全部exit0（2项隔离环境准备、2项协议验证），总计费wall 16.434940842秒、reservation0；验证最高RSS23,875,584字节；累计计费wall 874.322114946秒。supervisor受控停止，无活动或未知科学作业。初始共享内存余量约317MiB，因此未做payload/训练；随后验证受384MiB安全门保护。缺依赖、未知phase拒绝与重复supervisor启动阻止均已向用户报告并保留，未产生并发科学作业。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake10_Report.md`、`evidence/wake10_handoff.json`、`evidence/incidents_wake10.json`、`execution_windows/wake10/row_selection_protocol.json`、`execution_windows/wake10/output/row_selection_verification_v2.json`、`review/wake10_row_selection_review.md`及`review/wake10_row_selection_acceptance.json`。下一步先冻结去污染与生产selector/原子manifest，再做固定作者三类最小原生命令，不重跑本轮单元检查。

本代从Library version10、archive SHA256 `4f144fd91536fdedecd262d968b333c00b0e004890fd19eeb15cfa8fdbcee784`恢复，内部1478成员全部匹配；写回须使用`expected_current_version=10`，成功后才释放writer。持续研究授权和原调度不变。

# generation 10 历史状态（保留）

本轮关闭了正式三语训练来源的“候选分片不可变身份”子门，但payload抽样与tokenizer训练总门仍为HOLD。固定提交下已枚举：英语FineWeb `data/CC-MAIN-2013-20` 205个Parquet文件，法语FineWeb2 `data/fra_Latn/train` 135个，西语FineWeb2 `data/spa_Latn/train` 146个。每项保留repo/revision/tree path/file path/Git oid/LFS SHA256/字节数/Xet hash/last commit；正文下载量为0。

独立审查重算205/135/146共486个文件，总大小1,599,407,518,909字节，语言内路径与对象身份唯一，三语两两整文件LFS哈希交集为0；因此immutable candidate-shard identity子门PASS。该结果不表示约1.60TB数据已下载，也不证明行、URL、转载或语义近重复无泄漏。manifest只保留一个`size_bytes`，不能从产物独立重核API file-size与LFS-size两个原字段相等；后续获取必须分别保存或保存逐文件相等证据。

正式训练门继续HOLD。下一步前瞻冻结稳定行身份、`SHA256(language||stable-row-id)`排序、tie/重复/缺失ID/遍历/替补规则、三语匹配文档与信息预算、入选行manifest、结果盲GlobalVoices URL/域名/正文去污染、规范化/预分词及tokenizer/公平/成本合同。先用最小代表性payload验证协议可执行；通过后才允许资源标定与英法西Classical/PA-BPE强对照。英语FineWeb加法/西FineWeb2是明确标注的新伴生协议，不称单一处理管线或原论文复现。

本轮4个科学attempt全部exit0，runner计费wall 31.158552691秒、reservation0、最高RSS18,481,152 bytes；累计计费wall 857.887174104秒。任务完成后supervisor受控停止，alerts为空，无活动或未知科学作业。官方tree API首次因`limit=1000`超限返回HTTP400，改为支持的`limit=100`后恢复；另有两次管理回执命令在写状态前因重定向路径与CLI参数错误退出，未启动或重跑科学任务，已保留。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake9_Report.md`、`evidence/wake9_handoff.json`、`evidence/incidents_wake9.json`、`execution_windows/wake9/training_shard_protocol.json`、`execution_windows/wake9/output/training_shard_manifest_verification.json`、`review/wake9_training_shard_review.md`及`review/wake9_training_shard_acceptance.json`。下一宿主先核对Library最新版本、唯一writer、alerts/health和作业身份，不重跑本轮分片枚举。

本代从Library version9、archive SHA256 `ffc0017a343c3722426fd87d31ce3d49c38e7771b49034acca1ec9b3f581dd56`恢复，内部1390成员全部匹配；写回须使用`expected_current_version=9`，成功后才释放writer。持续研究授权和原调度不变。

# generation 9 历史状态（保留）

本轮关闭了“西语 FineWeb2 是否实际存在/可读”的来源不确定性，但正式训练来源门仍为 HOLD。官方 `first-rows` 对 `spa_Latn/train` 返回44条唯一记录，全部来自 `CC-MAIN-2013-20`，响应SHA256 `43d0fe03...`，schema与法语FineWeb2一致，URL中直接`globalvoices`命中0。它们是存储顺序探针，不是确定性训练样本，未训练或评分任何tokenizer。

独立审查确认：现有英语40行来自 FineWeb 固定commit `9bb295dd...`，法语40行来自 FineWeb2固定commit `af9c1333...`；二者虽同属`CC-MAIN-2013-20`，但不是同一处理管线且现存文件缺完整不可变检索身份。FineWeb2官方设计本来不含英语并建议与FineWeb伴生，因此可建立明确标注的新协议，但不能称三语同管线复现。当前80行与新增44条URL均无直接GlobalVoices字符串命中，这不足以排除转载或正文近重复。

西语普通`/rows`请求仍由服务端读取parquet的10秒超时导致HTTP500；Hub parquet清单路径复用同一失败并返回HTTP400。已保留真实响应。固定Hub元数据仍列出299个`spa_Latn`文件，故这些错误不是数据缺失证据。下一步以固定commit内文件清单建立不可变shard身份，冻结按`SHA256(language||id)`排序的等文档抽样、共同dump、三语预算与GlobalVoices URL/域名/正文去污染；满足后才允许训练输入。

本轮1个科学attempt exit0，runner计费wall 4.250019470秒、reservation0、RSS峰值17,694,720 bytes；累计计费wall 826.728621413秒。任务完成后supervisor受控停止，无活动或未知科学作业。一次宿主管理命令出现`fatal library error, lookup self`，用Python标准库安全降级；不影响科学命令或结果。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake8_Report.md`、`evidence/wake8_handoff.json`、`evidence/incidents_wake8.json`、`execution_windows/wake8/output/spanish_source_qualification.json`、`review/wake8_training_source_review.md`及`review/wake8_training_source_acceptance.json`。下一宿主先核对Library最新版本、唯一writer、alerts/health和作业身份，不重跑本轮来源探针。

本代从Library version8、archive SHA256 `743313eaf59caa02f7cdabb05e590635ed1d5dc55fdf60ae445cd8d3e7ddf3d6`恢复，内部1331成员全部匹配；写回须使用`expected_current_version=8`，成功后才释放writer。持续研究授权和原调度不变。

# generation 8 历史状态（保留）

本轮完成未曝光确认源的许可/身份结构门禁，没有读取正文或 tokenizer 结果。独立审查接受 OPUS GlobalVoices `v2018q4` 为条件性 GO；IWSLT/TED 当前 NO-GO，MDN 暂 HOLD。官方 ILSP PGV 元数据确认 11,004 个三边闭合英法西文档三角，但句段身份仍未资格化。

OPUS `v2018q4` 三份 XCES 哈希已固定；它们具有文档引用与句 ID。结果前冻结的 512 文档三角范围内得到 11,919 个唯一闭合三语全边单位，重复 ID 为0，按哈希预留512个单位。该里程碑只证明内容身份结构可构造，不证明翻译质量、独立性、任何 tokenizer 公平性、原论文复现或法律结论。确认结果仍封存。

本轮4个串行科学attempt全部exit0，runner计费wall 42.196157121秒、reservation0、最高RSS86,224,896 bytes；累计wall 822.478601943秒。全部任务终态后受控退出空闲supervisor，无活动或未知科学作业。两次提交契约错误都在进程启动前拒绝并已修复。恢复时共享余量仅约1.24GB，因此未训练。

下一步：打开raw文本前先核查署名字段、许可例外和训练/开发来源清单泄漏；独立恢复来源完整的西语训练；再冻结 tokenizer 候选、词表、预分词、逐行Gini、最差语言与总token成本约束及确认分析。不得从GlobalVoices确认结果调参。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake7_Report.md`、`evidence/wake7_handoff.json`、`evidence/incidents_wake7.json`、`execution_windows/wake7/output/opus_gv_closed_components.json`、`execution_windows/wake7/output/pgv_triangle_qualification.json`、`review/wake7_confirmation_source_review.md`及`review/wake7_confirmation_source_acceptance.json`。新宿主先核对最新Library版本、唯一writer、alerts/health和未完成作业身份，不重跑已完成结构诊断。

本代从Library version7、archive SHA256 `8a6f4cfd468be787671e52e35a83d89e060a8f38f57d6a77bc857de9f82cd7e3`恢复，内部1228成员全部匹配；写回须使用`expected_current_version=7`，成功后才释放writer。持续研究授权和原调度不变。

# generation 7 历史状态（保留）

本轮完成已曝光 TICO dev100→Books 公平收益偏移的条件分解与支持度核验。`full_minmax` 的逐句 macro Gini 收益从 0.01287954 降至 0.00017125，总偏移 -0.01270829；但按 Classical 基线差值符号分层时组成项为 -0.01771397、层内残差 +0.00500568，按 Classical 基线句长分层时组成项仅 -0.00047491、层内残差 -0.01223338。15个对照中，符号分层有14个由组成项绝对值更大，长度分层15个全部由层内残差绝对值更大。因此总偏移是实在的样本描述，机制归因却随分层改变，不能称“主要由组成变化”或“主要由同层响应变化”。

符号关联本身保留为机制线索：TICO Classical 差值组为正11、零4、负85，Books 为2650、340、2130；`full_minmax` 的TICO公平收益集中在负差值组，Books同组收益大幅缩小。但这不优先于长度或未测域特征，也不构成因果或方法选择依据。联合3×4支持度诊断发现`zero/q4`为TICO 0、Books 25，最小非零TICO格仅1；因此未计算稀疏联合结果。粗2×2虽无空格，最小TICO格也只有4，同样不用于补救因果识别。

本轮3个串行科学attempt全部exit0，实测科学wall 7.344077398秒、reservation 0、最高RSS 51,249,152 bytes。独立核验2,342项全部通过；独立数学审查已接受，但明确把结果限定为support-aware、标明参考域的描述性分解。恢复时发现无owner且无活进程的空全局锁目录，核查后安全接管。全部任务终态后中断空闲supervisor，health因此显示 retained identity lost；3份receipt均成功、声明输出存在、无未知科学作业。

项目累计科学wall 780.282444822秒，不清零、无项目累计上限。同一active idea `pa-bpe-domain-robustness` revision1继续；本代仍只是已曝光英法诊断，不能称独立确认、一般多语言公平、因果机制或原论文复现。

下一步不继续在Books/TICO上细分或选方法，而是恢复显著更大的真正未曝光作者/域确认集和来源完整的第三语言训练数据；前瞻冻结最小格支持、开发/确认隔离及信息边界后，再检验一个“基线差值符号稳健/无伤害”候选。当前它只是待检验假设。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake6_Report.md`、`evidence/wake6_handoff.json`、`evidence/incidents_wake6.json`、`execution_windows/wake6/output/conditional_shift_decomposition.json`、`execution_windows/wake6/output/conditional_shift_verification.json`、`execution_windows/wake6/output/joint_support_diagnostic.json`、`review/wake6_conditional_shift_review.md`及`review/wake6_conditional_shift_acceptance.json`。新宿主仍须先核对最新规范版本、唯一writer、alerts/health与未完成作业身份，不重跑已完成诊断。

本代从Library version6、archive SHA256 `4867648e58ebd652d7feed97422a1b686765ef8946dee7a8f056081c1800e8f4`恢复，内部1151成员全部匹配；写回须使用`expected_current_version=6`，成功后才释放writer。持续研究授权与原调度保持，不创建重复automation或递归`run_now`。

# generation 6 历史状态（保留）

本轮完成聚合Gini、逐句macro Gini、token-mass加权逐句Gini及符号抵消的精确机制审计。预先定义的“aggregate改善但mass逐句公平不改善”条件在TICO dev100的15个非Classical arms中命中0个；Books按作者块留一后稳定抵消错配命中0个，稳定aligned improvement也为0个。因此“开发公平提升主要只是符号抵消”这一严格解释被否定，不能据此从已曝光Books/TICO选择sentence-level新方法。

`full_minmax`在TICO上把aggregate Gini从0.03115302降到0，同时mass逐句Gini从0.03393809降到0.01977180、macro逐句Gini下降0.01287954；抵消比例为1仍说明aggregate零不等于逐句零，但实际逐句公平也有改善。跨16个相关arms，TICO aggregate与TICO逐句排序Spearman=0.95，而TICO aggregate与Books aggregate=-0.2441、与Books逐句=-0.0294。更符合“跨域迁移/成本不稳定”而非单纯开发目标错配：`full_minmax`的Books宏aggregate Gini反而+0.00093072、总成本+3.35176，mass逐句仅-0.00017800。

本轮3个串行科学attempt，2成功、1失败；runner计费wall 2.917685s、reservation 0，成功任务最高RSS34,164,736 bytes，失败任务RSS不可得。失败源于旧TICO记录缺少可选`mean_sentence_gini`存储字段，0.265376s后exit1且没有声明输出；修订为有字段才比对、仍从`paired_costs`独立重算后成功。首项诊断871项算术检查全过；精确mass诊断343个可用存储字段全过，9个缺失的旧TICO macro字段只重算不伪称比对。独立数学审查已接受。

恢复异常与范围：generation4遗留writer元数据在确认Library version5及无活动项目进程后归档；旧runner因绝对root绑定不能在新路径直接查询，原终态仍保留。一次错误submit相对路径未启动科学任务；宿主`rg`再次间歇性`fatal library error, lookup self`，改用ps/awk，不影响Python/runner/结果。全部attempt结清后主动中断空闲supervisor；当前runner `awaiting_decision`、reservation0、无wake5科学进程。项目累计科学wall 772.938367s，不清零、无项目累计上限。

本代仍是已曝光英法小样本机制诊断，不能称因果、独立确认、一般多语言公平或原论文复现。同一active idea `pa-bpe-domain-robustness` revision1继续。下一步不在Books上选sentence候选；用冻结paired costs检验baseline gap方向与长度/成本分层的条件域偏移，同时继续恢复真正未曝光作者/域确认集和来源完整的第三语言训练样本。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake5_Report.md`、`evidence/wake5_handoff.json`、`evidence/incidents_wake5.json`、`execution_windows/wake5/output/objective_mismatch_summary.md`、`execution_windows/wake5/output/mass_cancellation_summary.md`、`execution_windows/wake5/output/mass_cancellation_audit.json`、`review/wake5_metric_diagnostic_review.md`及`review/wake5_metric_diagnostic_acceptance.json`。新宿主仍需先核对最新Library版本、唯一writer、alerts/health和未完成作业身份，不重跑已完成诊断。

本代从Library version5、archive SHA256 `7eef55a8365196eb5a67483fc13d90bd5d2854d7a67b8e1f8753bedcb98438fa`恢复，内部1070成员全部匹配；写回须使用`expected_current_version=5`，成功后才释放writer。持续研究授权与原调度保持，不创建重复automation或递归run_now。

# generation 5 历史状态（保留）

本轮完成方法修订4：在开发公平性下降可行集合内优先最大化精确当前状态训练压缩，并与 pooled 约束及无下降约束的 exact-train 控制比较。主预测为负：`eff_minmax` 相对 prior full-minmax 的10作品平均总 token 成本高0.42246094、Gini高0.00084014；相对 full-pooled 的Gini低0.00054904，但总成本高2.10488281；相对 Classical 的Gini高0.00177085、总成本高3.77421875。无下降约束的 `exact_train` 最接近 Classical，但仍略差（Gini +0.00011794，总成本 +0.05214844）。因此即时训练压缩最大化加开发Gini下降约束没有修复当前跨作品公平/成本迁移失效。

本代所有 Books/TICO 仍是已曝光开发诊断，不能称独立确认、原论文复现或一般多语言结论。10作品每部512对、共5120对。实际80篇 FineWeb2 训练文档与 Books 的同语种15词、30词 NFKC/casefold 精确 shingle 均为0匹配；只排除该长度的可检测逐字重叠，不证明语义、作者或来源独立。

本轮8个科学 attempt 串行执行、全部exit0；科学wall 175.097007s，reservation 0，最高RSS 73.75MiB。项目累计wall 770.020682s，不清零且无项目累计上限。显式重放全部3000个选中合并，train/dev gain、trace长度、merge文件和独立最终token总数全部匹配；约束步最小精确正下降分别为6.11194e-08与4.50100e-06。36张整数成本表独立重算通过。独立静态审查已接受并修正表述：实现是阈值浮点下降；fallback破坏无条件单调性；`exact_train`有minmax开发目标tie-break；各模式fallback数不可直接比较；raw adjacency决定资格而非修正后的nonoverlap gain。

宿主管理工具`rg`、`jq`分别短暂出现`fatal library error, lookup self`，Python/runner正常，已降级为`ps`和Python处理；同一窗口后续复测`rg 15.2.0`与`jq 1.7`均恢复，不影响科学结果。第一次核验response因多带runner自有task字段被拒绝，未创建attempt；相同冻结输入修正后两项核验均成功，异常保留。空闲supervisor在8项结清后由协调者中断；final status为`awaiting_decision`，8 attempts terminal-success，reservation 0，无活动科学进程。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake4_Report.md`、`evidence/wake4_handoff.json`、`evidence/incidents_wake4.json`、`evidence/wake4_final_status.json`、`evidence/wake4_final_health.json`、`evidence/wake4_final_alerts.json`、`execution_windows/wake4/output/efficiency_candidate_summary.json`、`execution_windows/wake4/output/efficiency_table_verification.json`、`execution_windows/wake4/output/training_trace_replay.json`、`review/wake4_cost_constraint_review.md`与`review/wake4_cost_constraint_acceptance.json`。新宿主仍需恢复最新版本、核对唯一writer与未完成作业身份、重新测资源，不重跑已完成实验。

同一active idea `pa-bpe-domain-robustness` revision 1继续。下一判别动作不是继续在Books上调标量，而是用现有冻结arms诊断aggregate domain-mean Gini与逐句对齐公平/成本是否错位；只有机制证据可区分时才前瞻冻结一个cost-budgeted或sentence-level候选。同时恢复真正未曝光的作品/作者/域确认资产和来源完整的第三语言训练样本，之后才能扩大结论。

本代从 Library version4、archive SHA256 `47b9c8e6688dec17da28c7205b29f3fdcf64297576fa0f373f646e71ec83a49e`恢复，内部904个成员全部匹配；写回必须使用`expected_current_version=4`并在成功后才释放本代writer锁。持续研究授权与原有调度保持，不创建重复任务或递归`run_now`。

# 最新规范状态：generation 4，2026-10-11

本轮实际完成原始 OPUS Books 恢复、原始/注释文本配对敏感性、10作品×512对英法跨作品比较、合并目标审计、小池与全池候选及各自匹配 pooled 对照、独立计数复核。详见 PA_BPE_Wake3_Report.md。当前同一 active idea pa-bpe-domain-robustness revision 1；方法修订2、3仅为该idea内诊断变体。

主要结果：旧 robust 在8/10作品Gini差于Classical、10/10总成本更高。小池精确选择未改善开发最大Gini；10/10固定回退状态存在被漏掉的下降合并。扩大为全候选池后，两个开发域的均值Gini达到0，但10作品宏Gini0.01342295仍差于Classical0.01249223，总成本112.62207高于109.27031。精确开发拟合不等于迁移或效率改善。所有当前Books/TICO均已曝光，训练作品映射不完备、作者非独立，不称独立确认。西语raw已恢复，但没有三语训练或三语公平结论。

新增18科学命令，分两个串行有限窗口，全部exit0；本轮wall 192.896069s，累计594.923675s，不清零、不设项目累计上限。18不是科研循环数，本轮3条有证据的研究链。最高RSS128.07MiB。156张整数成本表复核通过，3份独立代码/数学审查已接受。

恢复先读本文件、resources_initial.json、manifest.json、phase_budget.json、evidence/wake3_handoff.json、evidence/resources_wake3.json、evidence/incidents_wake3.json、最新两窗口final_status/health/alerts、两批output及review/wake3_review_acceptance.json。旧source/实验/失败/授权均保留。wake3科学attempt12已结清、自然paused_budget退出；wake3b科学attempt6已结清、空闲supervisor由协调者退出130；无活动科学进程或未知reservation。新宿主需重新测资源和核对最新规范版本/唯一writer，不重跑已完成任务。

下一动作：建立含压缩成本约束的pair选择诊断计划，同时解决训练来源/作品重叠、第三语言训练源和真正未曝光的作品/作者级确认。当前数据只用于开发，不能把零开发Gini、命令成功或局部方法里程碑当研究完成。持续研究授权有效，原有任务保持，未创建新调度。

本代基于规范文件version3，archive SHA256 b4aad3b434649a79619ad69a799a579a1b9efb53f3d4892b9e4dd0f06bf271f6；恢复核验493个成员全部匹配。写回使用expected_current_version=3。下文generation3和更早是历史，仅最新连续授权/状态有效。

# 最新规范状态：generation 3，持续研究授权更新，2026-10-11

用户最新明确授权：**“没有预算呀，你可以一直跑下去时间”**。据此取消原有阶段累计科学 wall 3600 秒上限；项目不设累计时间、总 attempt、总科研轮数或自动完成终点，采用 `continuous_research`。当前 wake2 runner 通过受支持的 `revise-goal` 接口由 goal contract version 1 更新为 2；同一 active idea `pa-bpe-domain-robustness` revision 1、全部证据、曝光、失败、来源、已耗用时间和旧窗口 deadline 均保留。本次仅更新授权，不是新增实验或科研循环。

授权证据：`evidence/continuous_authorization_20261011.json`；当前目标合同：`goal_contract_continuous.json`；项目用量总账：`phase_budget.json`。历史预算另保存在 `evidence/phase_budget_before_continuous.json`。累计已观察的科学命令 wall 仍为 402.0276058989711 秒，不因取消上限而清零；未知模型 token/费用仍未知。

继续保留 CPU-only、1 个科学进程、1 线程、单命令最多 120 秒及服从真实可用内存的初始 2 GiB RSS 目标。12 attempts / 600 秒科学命令 wall / 最多 30 分钟主动宿主窗口是**可自动续接的有限安全批次**，不是研究总预算。边界处结清或核对原作业、保存证据与累计账，再串行建立下一窗口，不需每批另问用户；当次宿主仍可用则继续有价值工作。旧执行窗口已经到 deadline，不去改写它的历史；下一窗口继承本授权、同一科学身份及完整累计账。单候选或单阶段回答完成，不意味着整个持续研究完成。

实际状态：已有 10 个 wake2 attempts 均 terminal，reservation 为 0；无活动 PA-BPE 科学进程。旧 supervisor 已在上一窗口主动退出，残留写锁已保留后接管。原有后台任务保持启用并同步此授权，不创建重复任务或递归 run_now。此设置不保证两次恢复之间 24 小时常驻 CPU；继续报告真实阻塞，保留用户停止，不增加 GPU/付费 API/收费云/SSH 权限。

下一科学动作：先核对 OPUS Books 当前抽取究竟是 raw 还是 tokenized XML，修正相应协议表述；随后恢复更多完整三语作品和第三语言训练源，冻结未曝光的作品级开发/确认方案，再比较作品宏平均 Gini、最差语言与总 token 成本。保留既有混合/负结果，不重跑已完成任务冒充进展。

以下 generation 2 及更早章节是历史记录。凡其中 3600 秒累计上限、总目标自动完成条件或仅 `research` 模式与本节冲突，均已被此次用户授权覆盖；历史实验与证据资格不因此改变。

## generation 2 状态（历史保留）

第二次后台窗口已完成原生 OPUS Books 身份恢复、作品级两书管道烟测和九个现有英法 tokenizer 的重新评分。详见 `PA_BPE_Wake2_Report.md`、`execution_windows/wake2/output/opus_selective_extract_manifest.json` 和 `execution_windows/wake2/output/grouped_books_evaluation_wake2_v2.json`。

关键修订：旧 Books 连续行偏移不能支持跨书结论，相关确认分数降格为行级描述；原生 XCES 证明存在 12 部三语共同作品。Alice/Poe 的作品级结果对 robust-domain 给出方向相反的公平性比较，且 Poe 上公平性改善伴随成本上升，因此 active idea 保持 revision 1、总体目标未完成。下一步做多作品宏平均和作品级不确定性，再决定是否实现“正开发收益过滤”候选。当前三语训练源尚未完成，禁止把本轮西语对齐文本用于宣称现有英法 tokenizer 的三语公平性。

累计阶段科学 wall 约 402.028/3600 秒，剩余约 3197.972 秒；本窗口 10 attempts，所有作业结清，无活动科学进程或未知 reservation。两份无效 ZIP 匹配诊断和一次失败评测均保留，不得作为结果。独立 Books 审查已接受并整合；其模型 token/费用未知。

以下为 generation 1 恢复说明（历史保留）：

首轮完成9个分词器的训练及两个有冻结计划的研究检验；具体真实结果见 PA_BPE_Wake1_Report.md。base跨域公平性反转；候选优于同信息pooled，但最大域Gini仍未胜普通BPE，未完成总体目标。所有作业已结清，runner=paused_budget（本窗口12尝试用尽），无未完成科学进程。禁止重跑本轮已完成实验。

恢复必读：phase_budget.json（累计约49.404秒含历史9.545秒）、experiment_plan_v1.json、experiment_plan_v2.json、runs/evaluation_v1.json、runs/evaluation_v2.json、evidence/attempt_inventory_w1.json、evidence/incidents_w1.json、review三份独立审查。最新manifest是包内全部实际文件SHA；原始版本0整包hash只匹配初始包。

下一步：按真实书/源文档分组数据并恢复第三语言，检查机制后决定候选修订。当前所有v1/v2已评分确认数据均标为曝光；不得继续调参后再把它们称独立确认。CPU/RSS前9次未知，后2次有实测；无数据/分数伪造。旧runner状态永久保留，不修改其有限预算/deadline；下一授权窗口使用单独子执行根且先保留父项目累计phase账，不准将新窗口当新科研目标或重置总资源。

项目持久标识 libfile_8bb70b367b948191bfed83a45933917f；唯一writer在成功归档后释放。每次先读最新版本及内部manifest，不覆盖他人更新。后台调度未改变，无新的自动任务创建。

以下为初始bootstrap历史（内容保留，不代表最新状态）：

# PA-BPE Simple 研究启动与恢复记录

项目：pa-bpe-simple-20261011。用户在本会话明确授权：使用 Autopilot Simple，以 NLP 分词这个主题开始研究并设置后台任务。

## 目标与当前状态

总体目标：研究多语言分词公平性在跨领域情况下的稳定性；从原生 PA-BPE 对照出发，提出、实现并检验一个可证伪的改进，保留正负结果和适用边界。目标不是仅证明代码能运行，也不承诺新颖性或正结果。

goal_contract.mode = research。一条 active idea：pa-bpe-domain-robustness，revision 1。

完成条件：①建立可复核的公开数据、内容对齐公平性指标与强对照；②实际比较一个有文献依据的候选，含必要简单对照/机制检验；③报告支持、不支持或证据不足及跨域范围，保存完整原始记录。数据/权限受阻不是科研成功。完成局部检查应继续下一个必要动作。

启动交接时状态：原论文及实验附录已阅读；作者普通 BPE 固定版本源文件通过 GitHub 读取；CPU 资源已实测；历史原生结果日志已恢复；尚未执行本项目的新训练/评测，尚未部署本项目 Simple runner。后台 automation 的 create/run_now 回执单独报告，不能把排队当作执行完成。

## 已加载科学策略

Research Autopilot Simple 0.3.0-simple.9，源 skill://plugins_6ac8ad1eb9648191a0b6c1941de5d6b2/research-autopilot/SKILL.md（cloud package c23/research-autopilot）。已阅读 rsi-simple.md、simple-experiment-design.md 及 simple-runner.md 的启动/决策/异常部分。

一次一个 active idea；用数学、实现、实际实验与反馈迭代。没有 20→15 或全版 Gate 0 前置门槛。独立就绪的工作可按 simple-collaboration.md 委派原生子代理，唯一协调者负责预算、实验调度及存档；小任务可串行。恢复时核实当次实际可读的技能版本；不要将其他 Auto / Auto Chat 流程静默替换进来。

## 固定来源

- 论文：https://aclanthology.org/2026.acl-long.342/ 与 https://aclanthology.org/2026.acl-long.342.pdf 。ACL 2026。方法 §4，实验 §5–6，公平性公式附录 B，变体附录 C，下游训练附录 F。
- 作者代码：https://github.com/swiss-ai/parity-aware-bpe ，固定提交 c7395d469a653f3e48e80984e37593256ff8f365。
- 普通 BPE：parity_aware_bpe/learn_bpe.py。
- PA-BPE：parity_aware_bpe/parity_aware_learn_bpe.py；编码包装：parity_aware_bpe/HF_tokenizer.py。需读取真实源及 CLI，不能猜参数。
- 原生训练数据 FineWeb2：https://huggingface.co/datasets/HuggingFaceFW/fineweb-2。
- 原文对齐评测数据 FLORES+：https://huggingface.co/datasets/openlanguagedata/flores_plus 。遵循真实访问条款，不绕过 gated 数据。若没有合法可用的原文数据，定位许可清楚、内容对齐的公开基准作为明确标注的新研究协议；不得称原文公平性复现，不得自造 benchmark 或伪造翻译数据。

## 已有证据（不是本项目的新结果）

上传清单 library_file_id=libfile_40cca10484908191a12c695f648531d8，原名 CPU_8GiB_2026_Passed_Only(4).md。其副本在 evidence/。
历史 nlp_parity_native 记录：80 train + 20 diagnostic 文档/语言，德语与法语、1000 merges、1 worker、ratio 1:1。Classical 的诊断 token 数为 47370/17973；ratio 为 45861/18513；进程组峰值 RSS 118325248 bytes（112.84 MiB），wall=9.545s，exit=0。原日志已保存在 evidence/previous_native_*。
这些文档不对齐；token 总数差不能代表语言公平性，不能把已有两语言小样本标成全文复现或方法优越。1:1 是压缩率目标，不是非平行文本 token 总数的目标比例。
2026-10-11 恢复检查发现旧目录 /workspace/scratch/9d37bb7c32a8/cpu_reproduction_20261011/workers/nlp/{data,parity_results,parity-aware-bpe} 虽存在但已为空。已向用户报告。只有日志存活，不能声称原代码/数据已恢复。应从固定来源重取合法数据并保留 provenance，不重复运行历史诊断冒充新进展。

## 首轮具体工作

1. 核对 checkpoint 最新版本、作业/进程和暂停状态。首次没有本项目 active job；后续不得在身份不确定时重启同一实验。
2. 恢复固定作者源，记录 commit、文件 hash、真实运行依赖。优先复用已安装依赖；必要的项目隔离依赖可以安装，不修改其他项目的共享环境。
3. 获取合法可用的原生训练样本与对齐开发/评测文本，保存数据版本、许可、split、样本 ID 与 hash。先解决 metric 和数据资格，不能用非平行原始总数作为公平分数。
4. 定义并独立核验 Gini、每语言对齐句子的平均 token 数、最差语言成本、总 token 成本；区分开发集与未见确认集。固定同一词表大小、预分词、训练数据、信息权限和调参预算。
5. 先校准代表性 CPU 子集，再提交有限比较：Classical BPE、PA-BPE base、window、hybrid、ratio（适用版本需读取原实现），以及训练语料平衡/重采样的简单对照。缺少强对照时相应优越性结论保持 pending。
6. 一个可证伪研究问题：当用于选择语言的开发域与评测域不同，PA-BPE 的公平性改善是否显著减弱？如果出现真实失效，分析压缩收益/开发统计/预分词约束，再提出针对该机制的改进。没有真实失效时，不强行造问题，依据证据调整同一研究线。
7. 首批是资源与机制诊断。后续按必要覆盖扩展语言、域、词表规模与独立确认；不把小样本扩大措辞，不用固定 run 数代替科学证据。论文的 3B/256 H100 下游训练不在这次 CPU 阶段范围；不宣称下游模型能力获益。

## 资源与执行边界

用户授权的是当前宿主 CPU 研究。实际初始容量记录见 resources_initial.json：cgroup 8 CPU 配额、8 GiB 内存上限；这也是多个任务共享的宿主限制，不是本项目独占。
项目初始调度护栏（由协调者为新项目选定，不冒称用户曾给定）：同时 1 个科学进程、数值库/Tokenizer 线程 1；单次命令最多 120s，首轮最多 12 次 attempt、科学命令累计 wall ≤600s；每次唤醒主动工作窗口 ≤30min。先测子集，单实验初始 RSS 目标 ≤2 GiB，并服从更小真实剩余容量。
首阶段累计科学命令 wall 上限 3600s，所有历史、失败与已占用预算累加，不随唤醒重置；达到边界时保存结论与待办并报告，仍可整理已有结果，不能自动增加昂贵资源。命令 wall、CPU、RSS、模型 token/费用可见性分别记录，未知不填零。
不使用 GPU、付费模型 API、付费云作业或凭空假定 SSH。当前没有为该项目指定 GitHub/HF 写入目的地，使用私有文件检查点保留，不发布到其他研究仓库，不改其他后台任务。
需要当前主机命令队列时采用已读取版本对应的 simple_runner.py，按 simple-runner.md 初始化、固定计划输入 hash、保留真实回执；技能加载/调度启用不等于 runner 部署，也不等于常驻模型决策器。

## 后台行为与异常反馈

每次真实唤醒：先读取最新检查点与 alerts/health（若 runner 已初始化），核对 CPU、实际工具、数据与旧作业身份；继续下一项有必要的研究动作，不只发提醒、不重复从头审计，不人为每次只跑一个命令就等下轮。报告中文：当前问题、本轮真实运行/结果、支持范围、下一步。

任何 CPU/Python/执行工具不可用、源或数据访问失败、OOM、超时、评分错误、状态不确定、检查点保存失败均在当次仍可响应时主动报告：时间、项目/attempt、现象、证据、影响、有限修复和下一动作。未知不等于零资源，timeout 不等于 OOM，触发成功不等于实验执行。重复同一事件去重，修复/升级再报告。保留故障与待通知记录；无法写文件时优先在任务输出里报告。

每小时调度是续研/恢复机会，不保证两次之间持续占 CPU，也不保证平台未唤醒时能即时通知。禁止在定时任务内部递归调用 run_now 创建自触发循环。不要把本地日志记为已推送收悉。

## 保存与恢复

本包包含启动记录、实际资源观测、历史原始日志和用户清单，顶层 manifest.json 给出全部成员 SHA256。没有包含尚未恢复的代码、数据或新实验结果。
持续保存：更新同一规范恢复档案的最新版本，保存完整代码、实际数据来源/小样本、计划、raw 结果与失败；大文件另建有 hash 的版本档案并在索引记录。替换前先读最新版本/锁定唯一 writer；定时工作不得覆盖当前前台正在写入的版本。第一轮接管依据 automation prompt 指向的真实 Library ID 和最新本包。前台 bootstrap 在创建自动任务和立即触发请求后释放写入权。

