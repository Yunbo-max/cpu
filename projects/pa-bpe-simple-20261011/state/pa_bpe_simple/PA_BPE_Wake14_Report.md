# PA-BPE wake14 进展报告

时间：2026-10-12（UTC）

## 本轮结论

已从 Library version 14 / generation 14 恢复并按 `evidence/wake13_adapter_recovery_spec.json` 重建丢失的修复版 production adapter。固定 SHA256 `26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7` 的结果盲确认索引实际导入成功；随后 20/20 项验证通过，独立只读审查给出无阻断缺陷的窄范围 PASS。

该 PASS 只覆盖：blinded confirmation adapter mechanics 与冻结索引的字段/集合保真。它不覆盖真实训练行来源、production development selection、tokenizer 训练或 PA-BPE 公平性。

## 实际新增证据

- 导入：1536 条 confirmation，英/法/西各 512；27225 条唯一 shingle 记录；shingle mass 27346；801 个唯一 URL hash；SQLite `integrity_check=ok`。
- 逐记录核验：exact/count 字段差异 0，shingle/multiplicity 差异 0；URL hash 集合双向差集均为 0。
- 语义 fixture：exact URL、exact content、五词 shingle near-content 均按冻结协议拒绝；无关行保留。
- 绑定/失败关闭：协议与合同的 early/late/completed mismatch 守卫通过；损坏 mass 在写入目标行前拒绝；完成态重导入幂等。
- 隐私/盲化边界：适配器未访问 raw confirmation text，输出中未计算 tokenizer 或公平性指标。

## 资源和运行状态

Simple runner 运行 2 个串行科学任务，均 exit 0。runner 计费 wall 为 0.539728273 秒，reservation 0；两个 Python wrapper 的 wall 分别为 0.219958969 秒和 0.190267491 秒，峰值 RSS 分别为 17,764,352 与 19,718,144 字节。执行时限制为单进程、单线程、CPU only。

停止标志已持久写入，两个 attempt 均 terminal/succeeded，`/proc` 确认无活动科学 PID。原 supervisor 因宿主 exec 会话收尾而消失，health 留为 `lost` 而非正常退出回执；这不改变已有 receipt，但作为事故保留。

## 独立审查的限制

正确的 early-bind→import 分支、completed wrong-source/wrong-manifest、更多 schema/type/orphan 动态损坏和并发 SQLite/WAL 竞态未单独执行；全语料 builder→selector URL/Unicode 规范化等价也未重证。因此下一阶段仍必须先建立真实开发行到固定 wake9 shard 的逐行 provenance，并在正式选择前保持确认结果盲。

## 下一步

只推进一个 active idea：从已固定的 wake9 英/法/西 shard 清单中物化有界代表性开发候选，给每一行保存 repo/revision/shard path/LFS SHA256/stable row id；将 wake10 的每语言 100,000-pretoken 预算与本轮 adapter 串接并生成原子 selected-row manifest。上述门通过后，才允许运行最小固定作者 Classical 与 PA-BPE 原生命令。
