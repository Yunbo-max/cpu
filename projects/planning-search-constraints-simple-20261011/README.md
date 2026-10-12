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
