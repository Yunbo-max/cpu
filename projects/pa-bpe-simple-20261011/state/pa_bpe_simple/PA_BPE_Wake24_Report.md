# PA-BPE wake24：冻结污染源兼容性审计

时间：2026-10-13 07:34–07:40 UTC。当前 active idea 为 `frozen-contamination-source-recovery`；没有训练或评分 tokenizer。

## 实际结果

受控 runner 对 24 个固定输入执行了结果盲来源审计。有效替代任务 `wake24-contamination-source-audit-v2` exit 0，wall 0.384761473 秒，输出 SHA256 `5aa5eeb5bf1e5d5be291afd8f622c5dfd7906e64770da748bc30ef971a5caac4`。已核验可恢复污染清单范围：训练入选文档 515 个（英209、法155、西151），TICO 970 个三语对齐行/2910项，GlobalVoices 指纹记录1536项（每语512），FLORES devtest预期每语1012行，书籍诊断10部作品/5120个抽样对齐单元。

关键负结果：wake12保存的 GlobalVoices 五词 shingle 使用 Unicode `\w+` 词元并以 NUL 连接；Tatoeba 冻结实施补充要求 NFKC→casefold→Unicode空白折叠后的“空白分隔词元”连续五词多重集。两者不兼容。GlobalVoices raw text 没有写入指纹库，而三份冻结raw archive也不在 GitHub `archives/index.json`。既有exact/shingle哈希不能反演所需正文或新shingle，因此不能合法地把旧指纹直接应用到38,091个合格三角。

三份待恢复归档的固定 SHA256：英语 `974c2b104717a99662e6756272e2463989e7e78002e1a78e8e0e83c046fa9b3f`，法语 `84cfd37dec57098be81c7309ca878cad104c71e37087bbc9f70f4f16b5c36587`，西语 `2af6fb985de8965c5ae722a6ce0fdaf61477d3faa083a32cf2490a86e983be55`。

## 执行与失败账

第一次任务 `wake24-contamination-source-audit-v1` 的命令本身 exit 0、wall 0.343137346 秒，但 SQLite WAL 只读查询仍更新了固定输入 `selection.sqlite3-shm`，runner 因输入哈希变化将其标为 `invalid_inputs`。该尝试和原输出均保留。修复仅把三个 selection SQLite 文件复制到临时目录后查询；新任务ID显式 supersede旧任务，24个固定输入在执行后保持不变并成功收据化。

本窗口共2 attempts、计费wall 0.727898819 秒，累计计费wall 1946.898724222 秒，reservation 0。runner没有记录逐进程CPU时间或RSS，本轮不推测；这是测量缺口而非零值。cgroup为8GiB/8 CPU，启动前 `memory.current=8,015,712,256`、余量574,222,336字节，刚高于既有512MiB门限；全程 `oom=0`、`oom_kill=0`。早先曾观察到仅1,048,576字节余量并按规则等待，随后恢复才启动低内存审计。所有科学进程均终态，有限runner受控停止。

## 科学边界与下一步

本轮证明的是来源协议不兼容，不是公平性、跨域收益或token成本结果。Tatoeba production selection、tokenizer训练和公平性评分继续 HOLD。

下一步只恢复并逐一哈希核验三份冻结 OPUS GlobalVoices raw archive，按冻结source manifest重建精确512×3单位，再构造空白词元五词指纹。完成独立核验后，才能把完整污染清单应用到38,091个合格三角并做确定性开发选择。
