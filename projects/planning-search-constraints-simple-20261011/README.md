# 当前恢复授权 — 2026-10-13

用户已于英国时间 2026-10-13 15:05 明确要求恢复本项目的后台研究。先阅读 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) 与 [RESUME_AUTHORIZATION_20261013.json](RESUME_AUTHORIZATION_20261013.json)，按原有 R005 冻结实验接续，后续科研策略采用 Simple 0.3.0-simple.13。

旧停止快照、W0001/W0002、全部正负结果和累计消耗保留。执行器移交须在实际恢复后核验；恢复授权与定时启动不是实验已经执行的证据。以下正文是停止时的原始归档说明，后续恢复权限以新授权为准。

---

# Planning, search and constraint solving

Project `planning-search-constraints-simple-20261011`, using the pinned
Research Autopilot Simple 0.3.0-simple.9 runtime. Research is CPU-only and
must remain within the user's 8 GB total memory limit.

`LATEST.json` identifies the current incremental snapshot. Its manifest records
each original file's byte count, SHA256, mode, and pack location. Ordered 8 MiB
parts preserve the ZIP payload exactly. `archive_store.py` verifies parts and
original members and supports selective restoration. Historical results are
not new algorithmic claims.

Read [REMOTE_WORKFLOW.md](REMOTE_WORKFLOW.md) before restoring or evicting files.
The archive is not evidence that a process has stopped. Reconcile boot ID, PID,
start ticks, outstanding attempts, and receipts before resuming research.

Original complete and incomplete checkpoint packages are preserved separately
in `original-packages/MANIFEST.json`; incomplete downloads are history only.
The separate `historical/` namespace holds older BoostFW, Consistent LRA, and
CPU feasibility artifacts. These are research files, not chat conversations.
