# Wake 8 独立训练来源审查

审查时间：2026-10-12 UTC  
审查问题：现存英语/法语训练样本是否可比；如何合法、来源完整地取得英/法/西训练文本，同时不污染冻结的 GlobalVoices 确认集。  
约束：只审查元数据和官方一手资料；未下载正文、未运行分词实验。

## 结论

**条件式 GO，但现存两个 40 行文件不能直接作为可审计训练输入。**

1. `fineweb_en_v1.json` 与 `fineweb_fr.json` 不是同一处理管线的同分布样本。英语文件的字段（尤其 `token_count`、语言码 `en`）与 FineWeb 相符；法语文件的 `language_script`、`minhash_cluster_size`、`top_langs` 与 FineWeb2 相符。FineWeb2 论文明确说明其本身不含英语，并建议用 FineWeb 补足英语。因此这两者是作者官方建议的**伴生语料组合**，可用于新协议，但不得表述为同一管线或完全可比。
2. 两文件各 40 行，观察到的行都来自 `CC-MAIN-2013-20`，所以在抓取快照层面有一个有价值的共同控制；但文件本身没有嵌入仓库 ID、不可变 revision、config、split、offset/抽样规则或响应哈希。仅凭文件名、字段和总行数无法完整重建检索，故当前 provenance 不闭合。
3. 西语 FineWeb2 数据真实存在：保留的官方 Hub 元数据在 commit `af9c13333eb981300149d5ca60a8e9d659b276b9` 下列出 299 个含 `spa_Latn` 的文件（法语 `fra_Latn` 为 280 个）。先前 Dataset Viewer `/rows` 与 `/parquet` 的 HTTP 500 是服务路径失败，不是“西语数据不存在”的证据。
4. 现存 80 个 URL 中，`globalvoices` 字符串命中为 0；这只能排除这 80 条的直接显式来源，不能排除未来扩样中的 GlobalVoices 页面或转载。因此尚不能宣告确认集无污染。

## 证据

| 证据 | 观察 | 推论 |
|---|---|---|
| `evidence/fineweb_en_v1.json`，SHA256 `6811dc5a...` | 40 行；`text,id,dump,url,date,file_path,language,language_score,token_count`；行语言码 `en`；均为 `CC-MAIN-2013-20` | 与英语 FineWeb schema 一致 |
| `evidence/fineweb_fr.json`，SHA256 `69b869e9...` | 40 行；额外有 `language_script,minhash_cluster_size,top_langs`；行语言码 `fra`、脚本 `Latn`；均为 `CC-MAIN-2013-20` | 与 FineWeb2 schema 一致，不是英语文件的同管线复制 |
| `evidence/fineweb_meta.json`，SHA256 `fa6a0861...` | 官方仓库 `HuggingFaceFW/fineweb-2`；公开、非 gated；ODC-By；commit `af9c1333...`；存在 `fra_Latn` 与 `spa_Latn` 文件 | 法/西有合法、可固定版本的数据路线 |
| `source_probe_wake2.json`，SHA256 `a162de2f...` | 2026-10-11 三次西语 Dataset Viewer 查询均 HTTP 500 | 仅说明该 API 路径当时失败 |
| 2026-10-12 官方 Hub metadata API（本审查只读查询） | FineWeb commit `9bb295ddab0e05d785b879661af7260fed5140fc`；FineWeb2 commit 与保留元数据相同；两库公开且非 gated | 可以用不可变 revision 固定来源 |

官方一手资料：

- FineWeb2 论文及 HTML：<https://arxiv.org/abs/2506.20920>；<https://arxiv.org/html/2506.20920v1>。论文说明 FineWeb2 不含英语，推荐搭配 FineWeb，并说明其约 100 个 Common Crawl 快照与 ODC-By 发布。
- FineWeb2 官方数据页：<https://huggingface.co/datasets/HuggingFaceFW/fineweb-2>。页面给出 ODC-By、`load_dataset(..., name=<language_script>, split="train", streaming=True)` 和按语言路径读取的官方方法。
- FineWeb 官方数据页：<https://huggingface.co/datasets/HuggingFaceFW/fineweb>。页面标明英语、ODC-By 及其字段 schema。
- FineWeb2 官方代码：<https://github.com/huggingface/fineweb-2>。README 说明起点是原 FineWeb 英语筛选所排除的非英语数据，并列出语言识别、逐语言去重、逐语言过滤和 PII 处理。
- Dataset Viewer 官方 Parquet 说明：<https://huggingface.co/docs/dataset-viewer/en/parquet>。官方还提供 Hub `/api/datasets/{repo}/parquet/{config}/{split}` 路线；大型数据集 Viewer 失败时不应推断数据缺失。
- ODC-By 1.0 正文：<https://opendatacommons.org/licenses/by/>

## 建议的三语训练路线（需先冻结再取正文）

采用 FineWeb/FineWeb2 官方伴生方案，并明确标注为“新研究协议”，不是三语同管线原论文复现：

| 语言 | 固定来源 | 固定 config/split | 不可变 revision |
|---|---|---|---|
| 英语 | `HuggingFaceFW/fineweb` | `CC-MAIN-2013-20` / `train`（须由官方 split 元数据再次确认准确 config 名） | `9bb295ddab0e05d785b879661af7260fed5140fc` |
| 法语 | `HuggingFaceFW/fineweb-2` | `fra_Latn` / `train`，再保留 `dump == CC-MAIN-2013-20` | `af9c13333eb981300149d5ca60a8e9d659b276b9` |
| 西语 | `HuggingFaceFW/fineweb-2` | `spa_Latn` / `train`，再保留 `dump == CC-MAIN-2013-20` | `af9c13333eb981300149d5ca60a8e9d659b276b9` |

执行前写一份只含元数据的 source manifest，至少记录：repo、revision、config、split、原始 Parquet 相对路径与文件哈希、dump、稳定 `id`、原始 URL、`file_path`、抽样规则、许可证和获取时间。不要依赖会随仓库更新的 `main`，也不要把 Dataset Viewer 页码当唯一身份。

抽样建议：先应用统一排除规则，再按 `SHA256(language || id)` 排序做确定性抽样；不要使用“前 40 行”，因为存储顺序可能带来域名/抓取顺序偏差。三语使用相同 Common Crawl 快照并固定相同文档数；同时记录 Unicode 字符数、字节数和空白预分词单元数，后续另设等信息量平衡对照，不能把文档数相同误称为信息量相同。

## GlobalVoices 去污染门槛

在任何训练正文进入 tokenizer 之前，冻结且版本化以下规则；规则不得根据确认集得分调整：

1. 从冻结的 GlobalVoices source manifest 生成 canonical URL 与站点域名表；对三语训练候选做精确 URL、规范化 host/path 和注册域匹配。所有 GlobalVoices 主域、语言子域及 manifest 中出现的历史别名一律剔除。
2. 在不人工阅读确认文本的独立脚本中，做同语言正文的规范化精确哈希；再用预先固定阈值的 MinHash/SimHash 近重复检测排除转载。输出只保留命中计数与哈希身份，不根据命中内容或评测结果调参。
3. 把排除前后文档 ID、原因、哈希和数量写入 manifest；英/法/西执行完全相同的规则。
4. 将 GlobalVoices 确认集保持为只读、结果盲的确认材料；开发域/超参数选择不得读取其 token 公平性结果。

## 接受条件

只有以下条件同时满足，训练来源门才转为 GO：

- 三个 repo/config/split/dump 与不可变 revision 已写入 manifest；
- 西语通过官方 Hub 文件或 streaming 路线成功取得，并有原始 shard/行身份与哈希；
- 统一的确定性抽样和三语预算已冻结；
- GlobalVoices URL/域名与正文近重复排除已运行且留下机器可核验日志；
- 对 FineWeb 与 FineWeb2 的管线差异作为混杂因素明示，并至少预注册一个跨语同源/平衡敏感性对照。

在这些条件完成前，现存英法 40 行只可作为来源与 CPU 可行性探针，不能支撑多语言公平结论。
