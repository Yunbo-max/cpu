# PA-BPE Wake 10：确定性行选择与精确训练质量协议

本轮没有下载正式语料payload、训练或评分tokenizer。唯一科学目标是把wake9之后的确定性行选择与匹配训练质量从文字要求推进到可执行、可审查的软件合同。

协议固定了：以 `SHA256("pa-bpe-train-v1\\0" + language + "\\0" + stable_id)` 排序；缺失ID为数据集级硬失败，重复ID全副本拒绝；原始UTF-8正文哈希不做Unicode规范化；使用作者 `Sequence([Whitespace(), ByteLevel(use_regex=False)])` 预分词；第一批正式开发目标为每语言100,000个pretoken occurrence；边界文档只取确定性pretoken前缀；训练输入使用作者`--dict-input`表示精确Counter。等pretoken只是数据平衡对照，不是公平结果或全面信息质量匹配。

系统Python起初缺少`tokenizers`，作者`pyproject.toml`又未锁版本。本轮在项目隔离环境固定`tokenizers==0.22.1`并保留完整pip report。初版12项检查通过后，独立审查指出作者解析器与PA-BPE train/dev共享`--dict-input`开关尚未覆盖。修订后25项检查全部通过：三语探针各精确256个pretoken；反转/固定置乱输入结果不变；重复ID全副本拒绝；缺失ID硬失败；固定Classical和PA源码AST提取的`get_vocabulary(..., is_dict=True)`对三语字典均回读为相同Counter；显式合成的软件单元覆盖多文档边界、全空白行和预算不足。验证wall 0.072639秒、峰值RSS23,846,912字节。

同为256个pretoken，作者初始symbol mass英/法/西分别为1418/1315/1429，证实等pretoken不能替代作者内部长度成本。协议现明确：PA-BPE dev-objective路径必须把train和dev都字典化；ratio路径不得传dev。完整作者CLI仍未运行，因此只接受“扩展的软件及作者解析器不变量PASS”，不接受“原生训练PASS”。

正式门继续HOLD：GlobalVoices结果盲URL/域名/精确与近似正文去污染尚未冻结；没有受限内存的全局重复检测/hash选择器；没有真实row→repo/revision/shard/LFS SHA→stable ID→raw text hash→prefix溯源；selected-row manifest尚未与payload原子生成；wheel/Python/platform锁不完整；Classical及PA-BPE两类原生命令尚未验证。所有训练、公平性和复现结论继续HOLD。

本轮runner共4项任务全部exit0，其中2项隔离环境准备、2项协议验证；总计费wall 16.434940842秒、reservation 0。验证任务最高RSS23,875,584字节。项目累计计费wall 874.322114946秒，无项目累计上限。任务结清后supervisor受控停止，无活动或未知科学作业。两项runner告警均已在运行中向用户报告并保留：一次不支持的phase在执行前拒绝；一次第二个supervisor启动被活锁阻止，原supervisor身份核实后继续，未并发执行。

下一动作：前瞻冻结并实现结果盲GlobalVoices去污染及受限内存生产selector，使selected-row manifest与payload原子生成；随后做最小固定作者Classical、PA-BPE dev-objective和ratio原生命令验证。只有这些门通过，才允许第一批英法西100,000 pretoken开发训练与强对照。
