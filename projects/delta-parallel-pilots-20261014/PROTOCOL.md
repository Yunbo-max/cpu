# Parallel Delta development pilot — frozen 2026-10-14

Two separate hypotheses: A=previous-loop read/error controlling second-loop gates; B=exclusive prefix-summary controller updating gates once per16 tokens. B is a mechanism pilot on the same GDN host, not RWKV-7. Neither is an established novel paper. Old tied-congruence tasks stay blocked.

Public data: Zoology MQAR, HazyResearch/zoology@1ad20d193b6113cae1e8f3c655c300d7b4b3f4bb, zoology/data/multiquery_ar.py blob831bc8efded6f18096cb1385fababf91af0cb451. Standalone port retains published sampling/labels/causal query scoring; only config wrappers removed, explicit Torch seed added, num_passes=1. Vocab256, train length64,4 pairs,10,000 train examples(seed311),1,000 development examples(seed312). Separate longer development check:length128,500 examples,4 pairs(seed313). No train/dev exact sequence overlap. This is the public basic-example scale, not a new benchmark and not a full published model reproduction.

Shared model: width32,2 heads,shared GDN block repeated2 times,causal width3 QKV convolution,FFN,normalizations,separate state per loop. Ordinary PyTorch full-segment triangular solve is checked against recurrence; O(T^2) temporary storage, not a claimed efficient GPU kernel. Current-step target/query masks are never inputs to the model.

Eight modes: plain, hidden_gate, value_gate, residual_gate, residual_hidden, value_hidden, prefix_gate, static_gate. Gates change only in loop2. Error/read candidate sees [old_read,error]; hidden-side controls see [error,0] or [value,0]. Prefix source is mean of embeddings strictly before the block, with controller computed once per block. Controller output is zero initialized, preserving baseline predictions and shared initial weights. Controls are bounded by0.5*tanh. These are small adapted controls, not official LT2/CLER-H/CLVR reproductions.

Seeds17 and29. Each mode/seed has400 AdamW steps,batch32,lr0.002,weight_decay0.01,clip1.0. Same batch schedule within each seed. Total16 jobs,6,400 optimizer steps. Final checkpoint only, no development-driven extra steps or hyperparameter tuning. Parameter counts: plain25,444; gate modes27,656; hidden-injection modes27,610. Report the46-parameter difference; do not claim exact matching for every mode.

Primary: final development query accuracy, cross-entropy, all-queries-correct rate. Secondary:length128 development. Only2 model seeds and short training; pilot rankings are not final efficacy evidence or proof that a mechanism is useless. Concurrent CPU wall time is not isolated efficiency measurement. A must beat hidden/value feedback controls, not just plain. B must beat static/local controls. Required but not done here: full learning-rate calibration, stronger native configurations, frozen confirmation,>=5 prospective seeds,LM/state-tracking/overwrite tasks,official CUDA parity and whole-GPU-training cost.

Observed host:4-core quota,4GiB cap,torch2.10.0+cpu,no GPU. At most2 real subprocesses concurrently,one torch/BLAS thread each. No subagents or autonomous background service claimed. PIDs/exit codes/logs/model and batch hashes are retained. No independent scientific reviewer available.

Local detailed protocol SHA256:1ce581da83a02b4a305b27fa5515ae35b0e4227ae918d7ee352d84a21ffe2677
Local model.py SHA256:fa7bdae7e7f2384aec5ccd590a24ea2ae83f7a7cea51f5e6ef4985a3d59ca756
