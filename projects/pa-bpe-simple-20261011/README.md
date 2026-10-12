# PA-BPE 多语言分词研究

本目录是用户于 2026-10-12 指定的 PA-BPE 持久存档与续研入口。项目采用 continuous_research，一次一个 active idea，保留负结果、失败、真实用量及独立审查。仓库中的其他研究项目各自独立。

## 当前进展

当前导入检查点为 generation 15（原 version 15）。最新结果是确认集哈希适配器的 20/20 项机械核验通过；真实训练行到固定 shard 的来源、正式开发集选择、tokenizer 与公平性验证仍为 HOLD。这不是新的公平性正结果。

此前已曝光英法小实验发现：开发域的公平性收益转到 Books 域时显著缩小；条件分解的机制解释随分层方式变化。不能把这些探索结果当成独立确认或原论文复现。详细证据和限制见检查点与各轮报告。

- [当前状态指针](CURRENT.json)
- [检查点与历轮进展](state/pa_bpe_simple/PA_BPE_Simple_Checkpoint.md)
- [最新研究报告](state/pa_bpe_simple/PA_BPE_Wake14_Report.md)
- [按需恢复、上传核验和清理协议](WORKFLOW.md)
- [完整历史包、大数据包及失败下载的索引](archives/index.json)
- [迁移清单](migration/import_summary.json)

`state/pa_bpe_simple` 是可直接查看、增量提交的规范研究树。`archives` 保留所有现存独立 ZIP、一个未完成下载的取证副本、旧目录中未被 ZIP 覆盖的补充文件，以及独立原始数据包。重复副本由 SHA256 去重；每个大包按 4 MiB 分块并记录逐块和整包哈希。

原作者代码固定为 `swiss-ai/parity-aware-bpe@c7395d469a653f3e48e80984e37593256ff8f365`，原论文为 <https://aclanthology.org/2026.acl-long.342.pdf>。第三方代码、数据及文章保留原有署名和许可，本仓库不对第三方内容授予新许可。参见 [来源说明](THIRD_PARTY_NOTICES.md)。

迁移保留已存在的证据，不声称恢复了此前已记录为丢失的临时文件，也不把迁移与代码测试计为科研结论。
