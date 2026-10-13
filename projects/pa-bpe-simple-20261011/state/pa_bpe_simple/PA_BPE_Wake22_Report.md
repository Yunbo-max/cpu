# PA-BPE wake22 研究简报

时间：2026-10-13 05:34–05:46 UTC。单一 active idea 仍为 `pa-bpe-domain-robustness`；本轮只处理 Tatoeba 固定源的导出语义，不选择确认样本、不运行 tokenizer、公平性或候选比较。

## 新结论

上一轮 6 份冻结 Tatoeba 文件出现的缺失端点，原因已经由官方源码定位。官方 `Tatoeba/tatoeba2` 提交 `0fbb4506ce071827f85375bd4c8c8f9c7cf23d41` 中：

- `sentences.csv` 只导出 `correctness > -1 AND license != ''` 的句子；
- 全局 links 直接导出 `sentences_translations`，没有套用相同的句子资格过滤；
- 逐语言句子文件由已经过滤的 `sentences.csv` 分拆；
- 逐语言 pair links 又直接查询 `sentences_translations`。

因此 pair-link 文件合法地可能引用未进入逐语言句子文件的 ID。wake21 的英法507、英西210、法西27条异常边，共744条，与这个导出规则差异相符；它们不再是“6份文件必然来自不同快照”的证据。该判断来自上游主源码，不是根据 tokenizer 结果倒推。

严格协议 v1 仍按原规则保留为失败，不能事后删边冒称通过。可辩护的修订必须另立版本：把每个冻结 pair-link 表与两侧冻结且语种匹配的句子表做 inner join，以此定义 eligible graph；逐条记录所有被排除边，缺端点条目不得进入选择或评分。该规则目前只是来源机制修复，尚未生成新确认集。

## 实际执行与资源

通过固定的 Research Autopilot Simple `0.3.0-simple.9` runner 完成1个低内存来源核验任务，exit 0。命令 wall `0.008751049s`、峰值 RSS `13,238,272` bytes；runner计费wall `0.083672724s`、reservation 0。项目累计计费wall更新为 `1923.041858639s`，无项目累计上限。

完整固定源包共45,851,023 bytes。恢复该包并执行流式 membership 审计前仍沿用512MiB启动余量门限。05:46:01 UTC 实测8GiB cgroup已用8,341,356,544 bytes，仅余248,578,048 bytes；anon 526,508,032、file 7,395,381,248、shmem 0。低于536,870,912 bytes，因此该实验没有启动，记为持续等待而不是科学失败；没有 OOM 或 oom_kill。

## 管理异常

四个 runner 管理错误均发生在科学命令外并已修复：跨窗口相对路径被安全检查拒绝后改为本窗口哈希副本；事件多带 `target_phase` 字段被拒后删除；重复启动 supervisor 被现有锁拒绝，没有第二个科学任务；结构化 continuation 的自定义原因被拒后改用受支持的 `partial`。所有原始 alerts 保留。

唯一科学 attempt 已终态成功、reservation为0。有限窗口结束时停止空闲 supervisor；持续研究目标及原定时任务未停止。未发现活动 PA-BPE 科学进程。

## 证据边界与下一步

本轮没有产生确认公平性数值，也没有证明新协议最终可用。下一次真实唤醒先复测共享内存；余量达到512MiB且无重复或未知 PA-BPE 作业后，按既有14个哈希块恢复6份固定源，实际执行 eligible inner join 和逐端点归属审计，报告精确保留/排除边与闭合三角数量。之后仍须恢复完整历史污染排除清单，才能冻结选择；在此之前 tokenizer/公平性继续 HOLD。

主要证据：`execution_windows/wake22/output/official_export_semantics.json`、对应资源记录、runner receipt、`evidence/waiting_for_memory*.json`、`evidence/incidents_wake22.json`。
