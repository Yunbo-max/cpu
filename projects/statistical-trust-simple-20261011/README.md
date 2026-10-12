# Statistical learning and trustworthy decision research

Project: `statistical-trust-simple-20261011` · rsi-simple `0.3.0-simple.9` · CPU only.

[最新中文进展：B050 失败、修复与资源等待](reports/B050_failure_wait.zh-CN.md)

Canonical cold-checkpoint index: [LATEST.json](LATEST.json). Read the current
index rather than assuming an older snapshot is latest. Immutable snapshots
preserve scientific evidence, negative results and failed attempts. Only this
project directory belongs to this workflow.

Current: PRAXIS `praxis-near-optimal-tree-sets-v1` r1; 48 terminal attempts,
26 recorded research cycles. B050's exact reference fit ran, but result
persistence failed because NumPy path arrays were not JSON serializable. The
attempt is retained and is not a scientific result. A persistence-only repair
is ready; B050v2 remains unsubmitted while shared memory exceeds the 7.5 GB
launch line. No resident supervisor or scientific task is claimed.

Use `checkpoint_io.py verify --repo REPO`, then `restore --repo REPO` at the
bound original root. Restore refuses overwrite. After publishing and full
commit-pinned readback verification, `cleanup --repo REPO` and then `--apply`
require exact local parity and terminal tasks; preserve newer files if checks
fail. `MIGRATION_RECEIPT.json` covers the initial migration; later publication
receipts are under `operations/`.
