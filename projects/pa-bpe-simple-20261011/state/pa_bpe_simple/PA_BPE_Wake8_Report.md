# PA-BPE Wake 8：三语训练来源门禁

本轮没有训练或评分分词器；唯一科学任务是恢复并验证西班牙语训练来源，避免在训练数据来源不一致时解释跨域公平性。

独立审查判定条件式GO：英语FineWeb与法/西FineWeb2是官方建议的伴生组合，但不是同一处理管线。现存英法各40行虽然都来自`CC-MAIN-2013-20`，却没有完整记录repo revision、config、split、抽样规则和响应身份，只能继续作为CPU/来源探针，不能作为正式训练输入。FineWeb固定commit为`9bb295ddab0e05d785b879661af7260fed5140fc`，FineWeb2为`af9c13333eb981300149d5ca60a8e9d659b276b9`，均公开非gated并标示ODC-By。

官方Dataset Viewer的普通西语`/rows`接口仍HTTP500，证据是服务端读取parquet的10秒超时；同一时刻法语接口正常。改用官方`first-rows`后实际取得44条`spa_Latn/train`记录：44个ID均唯一，全部属于`CC-MAIN-2013-20`，字段含text、id、url、file_path、语言及去重元数据，响应172,231字节，SHA256 `43d0fe0337fc8691724471e298c77c9f52f22230b3672cbc0af973b2b153b6a3`。这证明西语数据存在且可读，但返回被截断且按存储顺序，故明确禁止直接作为正式训练样本。

现有英法80行和西语44行的URL中都没有直接`globalvoices`命中；这只排除显式来源字符串，不排除转载或正文近重复。正式训练门继续HOLD，直到固定三语repo/config/split/dump与shard身份、按哈希确定性抽样、统一预算，以及冻结并执行GlobalVoices URL/域名和正文近重复去污染。

本轮1个runner科学attempt成功，计费wall 4.250019470秒，实测任务wall 4.175158583秒，user/system CPU 0.026165/0.038237秒，RSS峰值17,694,720字节。项目累计计费wall 826.728621413秒，无项目累计上限。任务后supervisor受控停止，reservation为0，无活动科学进程。

下一动作：从固定FineWeb/FineWeb2 commit的仓库文件清单建立不可变shard manifest，冻结共同dump下的hash-ranked抽样和三语信息量/文档数预算，再先运行结果盲的GlobalVoices去污染。门禁通过后才训练英法西Classical与PA-BPE强对照。
