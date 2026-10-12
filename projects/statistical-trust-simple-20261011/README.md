# Statistical learning and trustworthy decision research

Project: `statistical-trust-simple-20261011` · rsi-simple `0.3.0-simple.9` · CPU only.

[最新中文进展：B047v2–B049](reports/B047v2_B049.zh-CN.md)

Canonical cold-checkpoint index: [LATEST.json](LATEST.json). Read the current index, never assume the initial migration snapshot is latest. The immutable snapshots preserve all research evidence, including negative results and failed attempts. Only this project directory belongs to this research workflow.

Current: PRAXIS `praxis-near-optimal-tree-sets-v1` r1; 47 terminal attempts, 26 recorded research cycles. B047v2 and B049 completed. B050 is prepared but unsubmitted, awaiting the retained 7.5GB/OOM0 prelaunch condition. No resident supervisor or scientific task is claimed.

Use `checkpoint_io.py verify --repo REPO` then `restore --repo REPO` at the bound original root. Restore refuses overwrite. After publishing and full readback verification, `cleanup --repo REPO` and then `--apply` require exact local parity and terminal tasks; preserve newer files if checks fail. See [MIGRATION_RECEIPT.json](MIGRATION_RECEIPT.json) for the initial migration only and `operations/` for later receipts.
