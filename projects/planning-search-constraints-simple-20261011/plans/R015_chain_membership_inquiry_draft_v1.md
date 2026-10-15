# R015 连续同变量分支的普通强简单对照：数学与结构问题草案

状态：尚未accepted/build/run；不是新颖算法，不用未完整验证的R014 S/P来选择。依据是R013限定普通ID成本线索与原作者get_node_id/split源码。R014原生一次成功但事件尾部缺失，两次official wrapper/audit失败，cycle仍14；该原问题incomplete，禁止重复solver来取有利trace。

## 对象与条件

固定某个converted subtask的rooted acyclic equalityDAG，节点存(left,right,var,pivot)，leaf保留原抽象stateID。每个component独立绑定DAG/domain/subtask/source身份，无跨target/split缓存、无parentcallback/父ID假设。原作者split将values逐一变为同var、共享right child的left helper chain。当前readonly保留见证前段含28个完整H记录的候选；必须实际证明header/H数量、所有H有完整JSON/无环/可达/范围和文件SHA绑定，才准把这些H用于结构分析。不能把H结构检查升级为全selected事件或operator/cost/goal语义完整。

## 推导：case partition / 归纳

设起点n0至n(k-1)沿left相连，所有测试同变量v，所有right是同一节点r，pivot为a_i，末端left为t，且此链不跨非法节点/环。原逐一比较对任意合法state s 的出口为：若s[v]属于A={a_0,...,a_(k-1)}则r，否则t。证明：最早命中的a_i沿此前left后取r；全部未命中沿left到t。重复pivot无需特殊推理；membership按集合语义。之后r或t的原DAG继续执行，故出口相等加有限无环归纳保持最终原leafID。物理编号无需递增，共享节点不阻碍证明。不改变hierarchy构造、抽象图/启发式值、online残余cost/原operatorcost、RNG、cache_estimates或TaskProxy转换逻辑。

该数学仅说明普通等价representation rewrite。bitset/table或sorted-membership的读/分支/存储代价不同，短chain可能更慢。构建静态membership付出初始化、内存和源码依赖代价；不是免费O(1)或node减少=CPU提高。

## 先做的可证伪结构询问

正式选择时用固定Simple13 math-handoff/goal-quality/reasoning/design新frame，消费69old+39W5=108真实feedback，previous_ref接actual latest retained-DAG-v4-v2 SHA801a83b3b4dfb9d1a0c8978861fa1d583f7abd784dfb37be19ccdc53d956b5cd；保留两失败observations/所有旧route/trace/experiments及待补quality债。

冻结只读28H组件身份/内容manifest和chain提取规则；每个macro的所有合法domain值逐一比较原链出口与membership出口，拒绝非法/循环/不完整输入。输出全部组件/chain长度分布、静态node表示/额外membership存储成本与不适用数量，保留负/零结果。literal fixtures只验工具，不是新native case/benchmark/cycle。若没有足够长chain或成本不可取，park这项普通对照，不强行构建。

结构空间若存活，才隔离source/依赖闭包，先资格（所有实际component的const instance-safe witness、convertedtask/operator/cost/domain/goals、独立graph/SP/原PDDL VAL），比较强简单原逐一比较/合理membership实现。原单path exactoneabstraction exporter不能当ensemble证明。真正性能仍用observer-off完整wait4 childCPU，含exec/init/construction/search/exit、所有失败/censor、冻结匹配schedule；不可复用R014事件尾部或拿诊断109s称author timing。

closestprimary/相似decisiondiagram变换、exactC458 baseline properties与多公开domain义务保持pending；不宣称 novelty/CI/global or stable speed。只有真实stop/永久边界/无可行授权动作才暂停长期goal，局部证据失败不结束。

