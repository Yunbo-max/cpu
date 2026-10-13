# PA-BPE wake25：GlobalVoices 冻结来源恢复与空白词元指纹修复

时间：2026-10-13 08:27–08:48 UTC。当前 active idea 仍为 `frozen-contamination-source-recovery`；没有训练或评分 tokenizer。

## 实际新增结果

更正 wake24 的过强来源缺口判断：`archives/index.json` 没有三份语言归档的独立键，但包含完整 raw-source bundle（232,883,564 bytes，SHA256 `825a8c063b19d4b1dc21f8a540ea2acbe5e11fa1da1cd6bfdeac5200c6805b6c`）。流式 CRC/哈希审计确认 bundle 内英语、法语、西语归档分别精确匹配冻结身份：

- en：115,069,300 bytes，`974c2b104717a99662e6756272e2463989e7e78002e1a78e8e0e83c046fa9b3f`
- fr：37,776,586 bytes，`84cfd37dec57098be81c7309ca878cad104c71e37087bbc9f70f4f16b5c36587`
- es：80,028,192 bytes，`2af6fb985de8965c5ae722a6ce0fdaf61477d3faa083a32cf2490a86e983be55`

在不输出 raw text 的前提下，按冻结 512×3 单元重新构建空白分隔词元索引。新 SQLite 为 6,549,504 bytes，SHA256 `2ec1dc4b27d9f4f842ce220610cd06b0bea9da25394173c59390d6650869d95a`。每语512单元；词元总数 en/fr/es 为 10,254/11,457/11,097，连续五词 shingle mass 为 8,231/9,420/9,072。

独立实现重新解析全部冻结来源，逐一重算并比对1,536个规范化exact hash和1,536个五词shingle multiset，全部一致。旧regex-word索引作为负结果保留，新索引仅修复污染检查的协议兼容性；尚未证明任一Tatoeba三角无污染，也不是公平性结果。

## 执行与资源

三项runner科学任务均exit0：raw bundle审计wall 1.029550185秒；指纹构建wall 17.981780234秒；独立核验wall 17.021212432秒。合计计费wall 36.032542851秒，累计计费wall 1,982.931267073秒，reservation 0。测量包装器给出的命令内部wall/CPU/峰值RSS分别为：审计0.479962秒/0.479613 CPU秒/15,204,352 bytes，构建17.626125秒/17.624196 CPU秒/103,268,352 bytes，核验16.656045秒/16.652015 CPU秒/102,158,336 bytes。

8GiB共享cgroup最初仅余约435MiB；按规则等待后余量恢复到约1.48GiB才提交。中间归档物化造成余量短暂下降，再等待恢复。全程 `oom=0`、`oom_kill=0`。所有attempt终态，有限runner在安静边界受控停止，continuous research保持active。

## 边界与下一步

本轮只修复并核验 GlobalVoices 污染指纹来源。production development selection、tokenizer训练与公平性评分仍HOLD。

下一步把训练、TICO、新GlobalVoices、FLORES和Books的完整冻结清单应用到38,091个合格Tatoeba三角，独立核验确定性1,024行开发选择；只有该门通过后才释放开发集进行固定tokenizer比较。
