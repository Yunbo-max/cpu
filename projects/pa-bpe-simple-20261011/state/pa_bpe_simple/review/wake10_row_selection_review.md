# Wake10 独立审查：确定性行选择与匹配预算

审查对象是 `execution_windows/wake10/row_selection_protocol.json`、两版验证脚本/输出和固定作者 Classical/PA-BPE 源码。审查为只读；没有联网、修改共享文件或发起科学实验。

## 接受的窄结论

修订版的25项检查全部通过，可以表述为“扩展的软件与固定作者字典解析器不变量通过”。三语探针各精确形成256个作者预分词单元；输入顺序反转/固定置乱不改变选择；重复ID全副本拒绝；缺失ID导致数据集级硬失败；生成字典分别由固定 Classical 与 PA-BPE 源码 AST 提取的 `get_vocabulary(..., is_dict=True)` 回读并得到相同 Counter。显式合成的软件单元还覆盖了多文档边界截断、零pretoken跳过和预算不足硬失败。

## 已修复的审查项

- `--dict-input` 序列化现需固定作者解析器 round-trip；当前解析器层通过，但完整作者CLI尚未通过。
- 协议现明确 PA-BPE 的一个 `--dict-input` 开关同时作用于train和dev：dev-objective路径必须把dev也用同一预分词器字典化；ratio路径不得传dev。
- 缺失ID语义与实现统一为数据集级硬失败。
- 等量pretoken只被称为数据平衡对照，并新增作者初始symbol mass；256个pretoken时英/法/西分别为1418/1315/1429，不能视作全面质量匹配。

## 必须继续 HOLD

1. 结果盲 GlobalVoices URL/域名/精确/近似正文去污染规则及实现尚未冻结。
2. 正式全集需要受限内存的全局重复检测和hash排序/选择器；任何分片缺失必须硬失败。
3. 真实 row→repo/revision/shard/LFS SHA256→stable ID→raw text hash→included prefix 溯源尚未建立。
4. 正式 selected-row manifest 必须与payload原子生成并核验，不能事后补造。
5. 完整 wheel SHA256、Python与平台锁尚未完成。
6. 固定作者 Classical、PA-BPE dev-objective、PA-BPE ratio 的最小原生命令尚未验证。
7. tokenizer训练、跨域公平性和原论文复现结论全部继续HOLD。

因此本轮没有开启正式payload或训练是正确决定。
