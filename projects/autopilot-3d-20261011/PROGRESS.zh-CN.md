# 3D CPU 研究进展（sequence 186）

- 当前活跃假设：`gravity-pose-root-reconstruction-localization-v1`；整体研究继续。
- R019 在保持作者 RNG/调用流一致的原生 5000 题执行中，记录 5011 次生成调用和 20023 条点级遥测。
- **supported**：331 个已接受问题含有失败穷尽后的 attempt-101 追加，共 567 个点；567 个点均至少有一个必需字段未在终止尝试中赋值。
- **inconclusive**：这些点与 R018 具体异常几何的逐值重合，以及该机制对求解器失败的整体因果贡献。R018 的跨二进制特征字节没有建立身份，不能用 ordinal 替代值级对应。
- 离线成功契约在不补值、不重采样条件下保留 4669/5000 个原接受，拒绝 331 个；这不是求解器质量结果。
- 审计完整性计数全部为 0；build-v3 峰值 RSS 769840 KiB，full5000 峰值 7324 KiB，无 OOM。
- Runner sequence 186，142 个数据库尝试全部终止；含 3 份外部恢复回执累计观察 145 次、13212.617197288027 command-seconds。
- 下一步：plan-v4 在同一次执行中仅对 assignment mask 证明已初始化的字段做安全几何序列化，再按 smoke8→audit→smoke100→full5000 串行推进。
