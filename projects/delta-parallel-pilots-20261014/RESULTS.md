# Parallel Delta pilot results — 2026-10-14

Two candidate mechanisms, not two completed papers. Track A: actual previous-loop read/error controls loop2 gates. Track B: prefix-conditioned block-level gate control on the same GDN host. B is not an RWKV-7 experiment. Query-protection remains preparation; the old relation-state novelty gate remains unchanged.

## Actual execution
16 training runs = 8 modes x2 seeds (17,29), each400 AdamW steps; **6,400 actual optimizer updates**, 13,107,200 input-token exposures across all runs (not unique tokens). Width32,2 heads,2 weight-shared loops,25,444 baseline parameters. Public Zoology MQAR basic-example scale: V256,T64,4 pairs,10k train,1k development; length128 development has500 examples and4 pairs. Final checkpoint only. Source and protocol pinned in PROTOCOL.md.

At most **2 real subprocesses** concurrently,one torch/BLAS thread each; not independent research agents. CPU quota4 cores,RAM4GiB,no GPU. Observed batch wall time214.372s,peak single-process RSS476.14MiB,observed whole-cgroup memory peak1.260536GiB. These concurrent wall times are not isolated method speed measurements.

## All final query accuracies

| Mode | Parameters | Seed17 T64 | Seed29 T64 | Mean T64 | Mean T128 |
|---|---:|---:|---:|---:|---:|
| plain |25444|2.000%|0.725%|1.3625%|1.150%|
| hidden_gate |27656|1.975%|0.700%|1.3375%|1.025%|
| value_gate |27656|2.000%|0.700%|1.3500%|1.075%|
| residual_gate |27656|2.025%|0.725%|1.3750%|1.175%|
| prefix_gate |27656|2.200%|0.725%|1.4625%|1.250%|
| static_gate |27656|2.025%|0.725%|1.3750%|1.175%|
| residual_hidden |27610|2.225%|0.725%|1.4750%|1.225%|
| value_hidden |27610|2.100%|0.700%|1.4000%|1.250%|

No winner is selected. Absolute recall is very low and both seeds are retained. This short first400-step learning pilot cannot establish mechanism superiority, failure, stability improvement, novelty, or final language-model quality. Before larger candidate sweeps, qualify stronger baseline learning/convergence and matched learning rates. Do not interpret small differences in this table as evidence of useful memory feedback.

## Correctness and integrity
6 final test methods passed, covering sequential/triangular output+read+error parity, gradient parity, nontrivial-control future-token noninterference, zero-controller identity for all7 controlled modes, prefix exclusion, full-model output/gradient parity. All16 training logs contain exactly400 unique steps. Paired base-parameter hashes and minibatch-schedule hashes match within each seed. All scored prediction arrays reproduce reported accuracy. Source unchanged from frozen protocol. No train/development exact-sequence overlap. All child PIDs verified terminal after completion; no ongoing background job.

The reference training path has O(T^2) temporary storage despite its recurrence-equivalent outputs; this is NOT a production FLA/GPU implementation. Hidden-routing controls have46 fewer parameters than gate controls; only the shared base and exposure are exact matches. The standalone generator ports published num_passes=1 semantics with explicit NumPy and Torch seeds; not a new hand-made benchmark. These small adapted controls are not official LT2/CLER-H/CLVR model reproductions. No independent scientific reviewer was available.

## Delivery
GitHub contains project coordination, frozen protocol and this complete outcomes digest. The full source, raw per-step logs, prediction arrays, final checkpoints, data manifests and reproducible data builder are in the Chat artifact `delta_parallel_pilots_20261014.zip`; do not assume that archive or all source files have been uploaded to this directory.

## Incidents
Direct container DNS download failed; connected GitHub reads succeeded. Streaming execution sessions were unavailable before any launch; verified no leftover process/file, then used a finite tracked subprocess runner. Neither incident was treated as a scientific failure.
