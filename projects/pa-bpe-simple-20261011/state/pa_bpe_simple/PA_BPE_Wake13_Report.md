# Wake 13 — 结果盲 adapter 运行后宿主擦除事故

本轮从 Library version 13 / generation 13 恢复并核验后，在唯一 writer 下实现了 wake12 hash-only confirmation index 到 wake11 selector 的结果盲 adapter。首次实际运行导入 1,536 条确认记录（en/es/fr 各512）、27,225 个唯一 shingle 记录、shingle mass 27,346、801 个唯一 URL 哈希；12项检查全部通过，两个科学命令 exit0，runner wall 分别0.601705039和0.370986853秒。

独立只读审查没有接受生产级 PASS。它发现一个高严重度调用顺序漏洞：selector 若先绑定协议P1，再用P2导入，旧实现可能完成；还指出fixture oracle与被测实现同源、真实URL只比基数未比集合、SQLite runtime type未硬校验。协调器据此修复：导入前与完成后均核对protocol/contract/source/manifest/representation绑定；最终 emission 再核对协议一致；固定contract hash；校验精确列合同和`typeof`；读取后重哈希source；加入硬编码normalization/URL/IPv6/shingle oracle、early/completed错协议与错contract负测、URL集合双向`EXCEPT`。

修复版实际再次运行，20项检查全部通过；生产复制计数仍为1,536 / 27,225 / 27,346 / 801，URL双向差集0，exact与shingle逐记录差异0。两个v2科学命令exit0，runner wall分别0.559136995和0.458008378秒；内层测量峰值约17.8MB和19.7MB。该范围若证据保存成功，本可支持“production adapter mechanics PASS”，仍不能支持真实开发行选择、tokenizer或公平性结论。

但在写回持久检查点之前，宿主于2026-10-12 07:50 UTC清除了整个`/workspace/scratch/42f1128b703b`。v1/v2源码、SQLite目标、runner receipts与JSON验证产物全部丢失；当前文件仅依据本轮已显示终端输出和独立审查消息重建，不能代替可哈希原始证据。因此本代正式结论降级为：**adapter设计缺陷与修复方案已定位，四次exit0及v2 20项PASS属于未归档观察；production adapter gate仍HOLD，必须在新宿主重建并复跑。**

事故后已从Library version13重新物化并验证archive SHA256 `8c0c6b716d093d7b78b58c83516e5396a03f8bd5ec8a6030a6e31699510a200a`。未重跑wake12实验，没有读取确认原文、训练tokenizer或计算公平性结果。

下一步：按`evidence/wake13_adapter_recovery_spec.json`重建修复版adapter和20项verifier，以新的有限runner窗口实际复跑并立即写回；成功前不得进入真实row→shard或训练。
