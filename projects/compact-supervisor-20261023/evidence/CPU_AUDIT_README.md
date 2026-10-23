# Prefix-buffer balancing: reproducible CPU evidence

This is a research diagnostic, not a trained-model release. No accuracy/perplexity improvement is claimed.

## Run

Use Python 3.12. Install CPU PyTorch 2.14.1+cpu from the official CPU wheel index and NumPy, then run:

```bash
python -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install numpy
python fresh_native_cpu_audit.py > rerun_native_cpu.json
python fresh_prefix_estimator_audit.py > rerun_estimators.json
python fresh_prefix_router_witness.py > rerun_router.json
```

The original receipts are included; use different output names to preserve them. Assertions verify results. Timing may vary. Exact package versions used are in environment.json.

## What is executed

Six unchanged AST-extracted functions/methods from NVIDIA/Megatron-LM commit `72d23540d0358ae24a41ff289d1461b094a770fa`. Entire source files are included, with original copyright and license, and their Git blob hashes are checked before execution. Single-rank reduction and logging are explicit stubs. Auxiliary loss scaling is manually matched to the inspected schedule, and gradients are computed by actual PyTorch autograd.

The positive and HT controls use new coefficients through the native loss helper and backward. They are not an upstream patch. CUDA TopKRouter construction, distributed communication, complete model training, pipeline lifecycle, masking and recomputation are not tested.

## Contents

- `Fresh_Topic_Research_2026-10-23.md`: full research record, theory, failures, planned/unrun rows.
- `fresh_native_cpu_audit.py` and `.json`: 74-permutation CPU component checks and receipts.
- `fresh_native_cpu_review.md`: internal review of the exact script hash.
- `fresh_ht_variance_audit.md`: exact HT covariance/MSE and reverse-pair proof, rational enumeration.
- `fresh_prefix_audit.md`: harmonic-mixture proof and exact enumeration.
- Additional estimator/witness scripts and receipts: exploratory numerical evidence.
- `evidence/`: pinned upstream source and license.
- `manifest.json`: SHA256 of packaged files (except the manifest itself).

Current evidence supports a conditional implementation-grounded estimator result. Originality and practical training benefit remain unresolved. Internal reviewers participated in the project; they are not a separate independent Work acceptance.
