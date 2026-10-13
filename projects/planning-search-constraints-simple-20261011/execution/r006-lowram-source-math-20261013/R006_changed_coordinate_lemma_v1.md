# 只复核改变坐标的条件恒等式

2026-10-13；这是当前R006的低内存数学/源码诊断。普通changed-coordinate复核是既有实现思路和强简单控制，非新算法。未修补native源码、未接纳新优化、未完成nativeCPU资格、无速度或新颖性结论。第一次source audit已注意到var/analysed_var的区别；本次新增其条件证明、必要假设的反例与可重复有限枚举，不能把已见的代码现象重新称发现新bug。

## 对象与源码绑定

Cartesian状态C=产品_i C_i；算子前置Q=产品_i Q_i，固定每var effect e_i，-1表示MULTIPLE_POSTCONDITIONS。对非空C，A_i(C,Q)=[C_i交Q_i非空]。R_i(C,T,Q,e)在e_i!=-1时为[e_i属于T_i]，否则为[C_i交Q_i交T_i非空]。app是全坐标A的合取并保留源empty guard；reach是全坐标R的合取并保留target empty guard。实际函数task_utils/cartesian_state.cc:86–105,186–224，operator常量disambiguated_operator.h:15。完整源码SHA与执行结果绑定于results/R006-changed-coordinate-lemma-diagnostic-v1.json。

父域P合法split成children C1,C2后可进一步传播缩小。定义D={i:P_i!=C1_i或P_i!=C2_i}，升序枚举。old edge必须已经有全坐标的app/reach有效证书，算子pre/effect在本次更新固定，且child与邻居之外域不变。此旧边证书是条件，现有final TSV并未提供pre/effect oracle，不能声称已在native每条旧边认证。empty guards不省略。

## 推导与用途

对i不属于D，两个child域都等于P_i。

- old P→W：A_i(Cj,Q)=A_i(P,Q)=true，R_i(Cj,W,Q,e)=R_i(P,W,Q,e)=true。因此新edge的全部app/reach条件等价于仅检查D并保留empty guards。
- old U→P：U不变，R_i(U,Cj,Q,e)=R_i(U,P,Q,e)=true；源适用性沿用旧有效证书，复核target的D与empty guard即可。
- old P→P loop：对任意child source/target，i不在D时两端都是P_i，同理四组child→child谓词只须复核D。非空guard仍单独检查，不能把空child当有效。

这是合取因子中已证true且输入不变的因子消去。若每条旧edge证书成立且D包含所有改变坐标，则eligibility布尔值一致；沿用原候选访问/emit顺序，可进一步条件推导同有序图/multiplicity。不能跳过上游split/propagation/caller契约，不能据此宣称heuristic trajectory、native最短路更新、完整plan或时间收益已经实证。

冻结abstraction.cc:230–232、369–371在遍历analysed_var时判断的是split var；proper split保证至少一个child在split var上异于P，因此进入传播分支时该条件对每个analysed_var均true，modified_vars会保守包含所有坐标。这与已有审计注记一致。可能多复核没有变化的坐标，但是否重要取决于实际propagation次数、D大小、short circuit、bitset成本、新增差异检测与完整planner开销。不能把19/D当wall或CPU加速，不立即改掉旧代码或归因上游bug。

更窄的D必须在传播后根据两个child所有实际坐标得到；不能只用原split var，传播可改变其他坐标。通过变量级比较生成D本身有成本，这一简单控制若以后执行，必须与原实现/普通app复用强对照及计数型测量比较，先资格再计时；与当前CPU-clock恢复是不同的未接纳后继，不绕过latest decision链。

## 必要假设的反例与实际数值检查

脚本scripts/check_r006_changed_coordinate_lemma_v1.py使用2变量×2值的bitmask形式，真实执行，RSS约10MB、CPU约0.43秒。96个proper split/额外坐标收缩组合，保持old-edge全谓词条件，比较incoming 71232、outgoing 60800、loop 25344次，共157376次，无布尔反例。覆盖两种effect语义与部分empty child，但有限域检查不是一般证明，也不是native实验/benchmark/研究周期。

同时两个明确反例已由脚本实际检验：去掉旧边有效证书，或把传播改变的坐标漏出D，均出现full=false而restricted=true。具体bitmask及结果保存在result的necessity_counterexamples中。结果不能拿来设置native PASS、声称图/VAL通过或绕过三次内存拒绝。一般条件证明仍以上述因子消去和native实际证书获取为边界；每split原生见证与完整规划效率仍未执行。
