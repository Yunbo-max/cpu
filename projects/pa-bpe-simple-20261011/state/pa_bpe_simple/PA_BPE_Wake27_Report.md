# PA-BPE Wake 27：按用户要求写回并停止

时间：2026-10-13 09:39 UTC（英国夏令时 10:39）

用户明确要求“你更新github然后停止”。本轮在任何新科学命令启动前停止了准备中的 Tatoeba 开发集筛选。没有创建 runner、没有提交新的科学 attempt、没有打开确认结果，也没有产生 tokenizer 或公平性分数。

停止前复核了 generation 27：上一轮唯一 attempt 已终态失败、reservation 为 0、supervisor 已退出、writer 已释放。远端项目树仍为 `da6985dcdbb2fc75b6ce107e7453d4e29e1d9f82`。本轮实测 cgroup 硬上限 8,589,934,592 字节、计账 7,081,676,800 字节、余量 1,508,257,792 字节，OOM 与 OOM-kill 均为 0；内存本可满足既定 746,586,112 字节门槛，但因用户停止，没有启动筛选。

保留的未完成工作不变：修正后的完整污染清单筛选器与独立复核器尚未运行；1,024 行开发选择、tokenizer 训练和跨域公平性评分继续 HOLD。这是用户停止，不是研究完成、科学失败或资源失败。若未来用户明确恢复，应从本代状态重新获取 GitHub 最新提交、核对唯一 writer 和真实内存，再以新执行窗口运行修正后的选择器。

恢复阶段有一项管理异常：协议文字中的 `tools/cache_io.py` 路径与仓库实际 `cache_io.py` 不一致，首次只读恢复命令在读取实验输入前退出；修正路径后 partial state 验证通过（225 个已检出文件，3,515 个因稀疏检出缺失）。该异常没有形成科学 attempt，也没有消耗 runner 预算。

持久化阶段发生一次 GitHub `create_blob` ReadTimeout，以及一次本地 32 GiB overlay 的 ENOSPC。上传器保留已有逐项回执后续传；仅删除本轮已按哈希核验、可从 GitHub 恢复的 PA-BPE 大输入与归档块，未动其他项目或全局缓存。generation 28 最终提交 `f7d28f300a95ce2d8063403bcde4055cad6046e9`，项目树 `d2f246adb046b10c55eb439a4fe3a29fc7f016f4`；独立新克隆重算 manifest 与关键文件哈希全部一致。

本轮停止证据：`evidence/user_stop_20261013.json`。异常记录：`evidence/incidents_wake27.json`。独立回读：`receipts/wake27_stop_remote_verification.json`。generation 27 的失败、修复和等待证据均原样保留。
