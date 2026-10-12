# PA-BPE wake17：第二个未见三语域确认

在结果前冻结的 FLORES-200 `devtest` 全部 1,012 个英/法/西对齐句上，固定 500-global hybrid 把 Classical 的三语言平均 token 成本 Gini 从 `0.0406959383` 降到 `0.0227591358`，改善 `0.0179368025`；配对句 bootstrap 95% 区间 `[0.0161054038,0.0200599109]`。总 token 成本增加 `1.7938896%`，最差语言成本增加 `0.1674367%`，最差语言从法语转为西语。因此支持有代价的 scoped transfer，不支持无成本改进、广义多语言结论、下游收益或原论文复现。

计划在正文访问前冻结官方原始 FLORES-200、`devtest`、全部行、三语言、固定代码哈希和主指标。官方归档 URL 为 `https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz`，SHA256 `b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6`，25,585,843 字节；官方 archived README 标注 CC-BY-SA-4.0。新版 FLORES+ Hugging Face 文件在未接受 gated access 时返回 HTTP401，本轮没有绕过门禁。公开文本包没有文章 cluster ID，所以句级 bootstrap 只是描述性区间。

PyPI 被宿主 403 阻断，没有安装共享依赖。纯 Python evaluator 在旧 970 行 × 5 模型 × 3 语言共 14,550 个整数成本上逐项零差异后才打开 FLORES。三段 runner 共7 attempts：3成功、4失败；新增 charged wall `155.701309732s`，累计 `1577.437025541s`，reservation0，无活动科学进程。失败包括两次过严下载内存门禁、PyPI403和一次评分前路径错误；无 OOM。

下一步先独立核验 FLORES 对齐与算术，再补固定 base/window/ratio 次要 arms，并结合 GlobalVoices 的 signed-gap overshoot 分解 hybrid 前500次 global merge 的稳定机制。FLORES 已曝光，不能再用于调参后的新确认。
