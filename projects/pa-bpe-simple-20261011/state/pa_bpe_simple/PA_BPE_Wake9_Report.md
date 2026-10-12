# PA-BPE Wake 9：固定提交训练分片身份

本轮没有下载语料正文、训练或评分 tokenizer。唯一科学目标是关闭正式英法西训练源的“候选分片能否被不可变引用”子门。

在固定提交下，官方 Hugging Face tree API 枚举出英语 FineWeb `data/CC-MAIN-2013-20` 的205个 Parquet 文件、法语 FineWeb2 `data/fra_Latn/train` 的135个文件、西语 FineWeb2 `data/spa_Latn/train` 的146个文件。每项保留 repo、固定 revision、tree path、文件路径、Git oid、LFS SHA-256、字节数、Xet hash 与 last commit。三份 manifest SHA256 分别为 `ada44ec3...`、`3943b5a6...`、`b9f5b032...`。

独立重算确认205/135/146共486个文件，总大小1,599,407,518,909字节；路径、Git oid、LFS SHA-256与Xet hash格式和语言内唯一性通过，三语两两整文件LFS哈希交集为0。本轮正文下载量为0。该PASS只表示候选分片身份可复核，不表示这些约1.60 TB文件已下载、形成训练集、跨语言无行级重叠或足以支持公平性结论。

独立审查指出两个证据边界：manifest只保留一个`size_bytes`，不能从产物独立复核API文件大小与LFS对象大小两个原字段相等；分页正文未保留，只有分页响应哈希、HTTP状态与条目计数。后续获取应分别保存两个大小字段；整文件哈希无重叠不能替代URL、域名、逐行和正文近重复去污染。

训练总门继续HOLD。开始payload抽样前必须前瞻冻结稳定行身份与hash-ranked选择、重复/缺失ID及tie规则、遍历和替补规则、三语匹配文档/信息预算、入选行manifest、GlobalVoices结果盲去污染、文本规范化/预分词以及tokenizer与公平/成本指标合同。英语FineWeb加法/西FineWeb2仍是明确标注的新伴生协议，不冒称单一管线或原论文复现。

本轮4个runner科学attempt全部exit0，计费wall 31.158552691秒，reservation 0，最高RSS 18,481,152字节；项目累计计费wall 857.887174104秒，无项目累计上限。任务完成后supervisor受控停止，alerts为空，无活动或未知科学作业。官方tree API最初因`limit=1000`超出支持范围返回HTTP400，改为`limit=100`后恢复；两次管理层回执命令在写状态前因路径和参数名错误退出，未启动或重跑科学任务，均已保留。

下一动作：制定并独立审查确定性行抽样与匹配预算协议，先用最小元数据/代表性payload验证稳定行ID和去污染可执行性；只有门禁通过，才允许资源标定和英法西Classical/PA-BPE强对照训练。
