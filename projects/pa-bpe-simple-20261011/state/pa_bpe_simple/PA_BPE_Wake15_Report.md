# PA-BPE 本轮实际结果

已从 GitHub commit fd7405b1a643dbecee1e5af712e6007e0cfcb6bb 完整核验1954个历史状态文件，再串行执行17项命令（14成功、3失败，失败均保留），新增计费wall 303.636533秒，累计1300.624903秒，无累计时间上限。

三份最小原始分片完整SHA256通过，独立不同batch重读通过；英语374条符合2013-20，法语4923和西语34861条均不符合。这是真实的来源负结果，未放宽年份。随后固定新协议，获取法西首个分片的第0完整行组各1000条；从固定HTTPS端点检查206范围、总长、字节SHA与Xet ETag，未声称验证整份4.8GB LFS对象。独立审查仅接受此条件来源链及有限便利样本。

冻结2374条便利开发帧，SQLite完整帧重复/缺失ID处理与盲化确认去污染实际运行；2374条均被当前规则接受（不是不存在所有语义重合的证明）。选中英209、法155、西151篇，分别恰好100000作者pretoken。词表唯一pretoken为14763/15713/16683，初始symbol mass506499/536419/548313。两个作者字典解析器均精确roundtrip。构建22.266秒，RSS169402368字节。

固定作者Classical、PA ratio、PA dev完整CLI各完成32合并，wall0.573/1.024/2.361秒，最高RSS114835456字节。**只作接口和资源诊断。PA dev故意复用非平行训练字典检查同一dict-input开关，所有这批codes不准进入公平性表。没有新公平性结果、没有打开确认raw或结果。**

两次4MiB footer guard失败后用分块上限修复；一次共享内存<384MiB提前退出，等余量恢复后成功。无OOM、无timeout。一次失败资源文件被重试覆盖后，已按原receipt SHA完整恢复到独立证据路径；原receipt未改。科学作业均终态、reservation0。有限执行器已退出，continuous_research和原任务继续；不承诺两轮间常驻CPU。

下一步：Independently confirm selected-row-to-dictionary budget reconstruction as needed, then freeze and recover content-aligned independent en/fr/es development texts distinct from untouched GlobalVoices confirmation. Use bounded convenience frame transparently; first run a representative merge/resource pilot and then Classical, PA base/window/hybrid/ratio and data-balance controls. Never score the32-merge CLI diagnostics or nonparallel dev dictionaries as fairness.

大原始分片及页脚按哈希拆块存档，索引有精确恢复路径；新生成的row manifest、字典、日志、代码和失败均保存。
