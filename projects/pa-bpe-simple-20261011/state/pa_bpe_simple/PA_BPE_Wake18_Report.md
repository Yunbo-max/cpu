# Wake 18：固定次级臂与跨域稳健前沿

时间：2026-10-12 13:41–13:53 UTC。研究模式为 continuous_research；本轮只有一个 active idea：在不调参的条件下，对已经训练并冻结的 PA-BPE 次级臂做 FLORES-200 描述性评估，再与已暴露的 GlobalVoices 结果组成跨域稳健前沿。

## 新结果

FLORES-200 devtest 的 1012 个英/法/西内容对齐句子全部使用固定 1000-merge codes 重放。Classical Gini 为 0.04069594。base 和 window 的 Gini 分别为 0.00742502 和 0.00774125，但总 token 成本分别增加 4.0225% 和 4.0802%；hybrid 的 Gini 为 0.02275914，总 token 成本增加 1.7939%，最差语言成本增加 0.1674%；ratio 的 Gini 恶化至 0.04813398。base/window 虽比 hybrid 更低 Gini，但没有满足预先冻结的“Gini 更低且总成本、最差语言成本均不增加”三目标反证条件。ratio 在两个暴露域都产生负公平收益。

将 FLORES 与固定 GlobalVoices 结果合并后，以“跨域最小公平收益、最大总成本增幅、最大最差语言成本增幅”作稳健比较，Classical 与 hybrid 构成稳健 Pareto 前沿；hybrid 严格支配 base 和 window。hybrid 的跨域最小 Gini 改善为 0.01793680，最大总成本增幅为 1.7939%，最大最差语言成本增幅为 0.1674%。这支持“hybrid 是当前固定候选中的稳健折中”，但不支持“hybrid 在每个域都达到最低 Gini”，也不是机制因果证明。

## 核验与资源

独立 verifier 对 FLORES 的闭式三语言 Gini、成本变化与配对 bootstrap 共通过 42 项检查；跨域前沿与支配关系另通过 19 项独立检查。五个科学命令均 exit 0，累计计费 wall 74.569823 秒，单命令最大 wall 63.031307 秒，测得峰值 RSS 37,355,520 字节；无 OOM、无 timeout、无需进入 waiting_for_memory。

首次任务提交因证据路径包含跨窗口相对引用而在科学命令启动前被 runner 拒绝。修复为 wake18 内部复制并绑定 SHA256 后运行；该管理事件没有消耗 attempt 或科学预算，事件 ID 为 `cli:a7ecc2eaaa9c46cfa8293f328efe461c`。所有五个 attempt 已终态成功、reservation 为 0。闲置 supervisor 在任务结算后被受控中断，最终 health 因无 graceful-exit 记录为 `lost`；没有未决科学作业。其后的宿主 `ps/rg` 探针出现 `fatal library error, lookup self`，没有影响科学结果。

## 证据范围与下一步

本轮使用的两个评测域都已暴露，因此结果只作确认后描述和候选排序，不再用于选择新的超参数。下一 active idea 是在固定 codes 和既有开发产物上审计 hybrid 前 500 个 global merges 前后的 merge ownership 与逐语言边际 token 效果，以检验其避免 signed-gap overshoot 的机制；继续保持无新调参、确认域不作开发集。
