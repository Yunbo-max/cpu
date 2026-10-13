# PA-BPE wake23：Tatoeba eligible-inner-join v2 审计

本轮在共享内存恢复后，按固定 SHA256 恢复了 6 份 Tatoeba 压缩源（14 个归档块，共 45,851,023 字节），实际执行了单线程 CPU 审计，并用第二个独立实现复核。没有训练或评分 tokenizer，也没有产生确认公平性结论。

严格协议 v1 的失败保留不变。另立的 `tatoeba-eligible-inner-join-v2` 只保留链接两端同时出现在固定、语种匹配句子导出中的边：英法 441,739 条中保留 441,232、排除 507；英西 283,852 中保留 283,642、排除 210；法西 61,696 中保留 61,669、排除 27。合计保留 786,543、排除 744。三张边表均无重复边。

合格图包含 38,091 个英—法—西闭合三角。SQLite 流式实现与独立内存集合实现对全部边分区计数及三角形精确成员完全一致；三角形归档 SHA256 为 `83af88f96911474cc7062c3a502c9865caedc2a04995590eb1ce300f9b6e2f5d`。

两个科学 attempt 均 exit 0。runner 计费 wall 分别 12.614652963 和 10.514313801 秒，合计 23.128966764 秒；测量脚本 wall 为 12.494578848 和 10.046949153 秒；峰值 RSS 分别 38,297,600 和 472,723,456 字节。reservation 已归零，无 OOM/oom_kill，累计项目计费 wall 更新为 1,946.170825403 秒；持续研究没有项目累计时间上限。

管理层保留四项异常：旧窗口绝对根不匹配而不能在新路径读取其 runner 状态（由旧终态回执和本轮无进程检查消歧）；一次稀疏恢复执行通道断开后有界重试成功；一次错误使用本机 Git 不支持的 `sparse-checkout add --no-cone` 后改用 `--skip-checks`；首次 runner 计划把 phase 写为 `verification` 被拒绝，改为合法的 `verify` 后提交。它们均未生成额外科学 attempt 或未知 reservation。有限 supervisor 在任务结清后受控中断；runner health 因未记录退出码显示 `lost`，但 PTY 已返回、两 attempt 均 terminal-success、reservation 0，无未知科学作业。

科学边界：v2 只修复固定源图的资格规则。开发选择、污染排除、tokenizer 训练和公平性评分仍为 HOLD。下一步必须恢复并绑定此前冻结的完整污染清单身份，把它应用到 38,091 个合格闭合三角后，才进行确定性的 production development selection；在这一来源阶段独立核验前不得评分。
