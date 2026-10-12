# History-Metric Delta: CPU Feasibility and Variable Blocks

Executed with Research Autopilot Autonomous Chat 0.2.0-autonomous-chat.10. This is a bounded engineering prototype, not a trained language model, an SSD reproduction, or evidence that semantic forgetting is solved.

## Delivered artifacts

This GitHub directory contains the tested standalone differentiable block/sequence kernel (`torch_memory.py`) and this measured-results digest. The **complete 50-file package**, including NumPy/SciPy implementations, 56 tests, timing scripts, raw measurements, licenses, failures and documentation, was delivered as `fisher_delta_cpu_variable_B.zip` in Chat. The complete ZIP is **not uploaded to this GitHub directory**.

ZIP size: 78817 bytes. SHA-256: `6e446438218a9c8827a58a0b7b51d167759e5c6a2ee9eaee1852f90c69d9363d`.

Published `torch_memory.py` SHA-256: `dfa13e70afb24071e8a1fdbda04027bce419553e44917d55fe86cfedab44d1c4`.

## Update and causality

With a positive definite block-start history metric C, P=C^{-1}, A=eta^{-1}I+K^T P K and E=V-SK, compute G^T=solve(A,K^T P), then S_new=S+E G^T. For full accumulated information, P_new=P-P K G^T. Cholesky/triangular solves replace explicit inversion.

B=1 reduces to the normalized metric residual update. For full RLS, fixed per-observation eta, summed loss and no forgetting, arbitrary partitions give the same exact model. B is then a scheduling choice. Diagonal/sketched/fixed-prior approximations and mean-loss normalization need not have this invariance.

Erase and write still share one gain: S_new=S(I-KG^T)+VG^T. They are not independent gates. Key second moments are not automatically empirical Fisher or semantic importance.

Causal prefix outputs use A=L L^T, U=solve(L,E^T)^T, W=solve(L,K^T P Q), Y=SQ+U triu(W). C must be supplied causally; computing it from the whole future-containing block can break causality. Known-input prefill speed is not unknown-future autoregressive decode speed. The residual-adaptive buffering routine emits its causally dependent outputs retrospectively at block completion, not with zero latency.

## Actual CPU measurements

Actual cgroup limit: **4 GiB**, **4-core quota**, five affinity CPUs. Primary measurements: one BLAS thread, FP32, one sequence/head, d_k=d_v. Times include history maintenance and all per-position causal readouts, but exclude imports, input generation and 128-token warmup.

At d=128, T=4096, B=32 (three repetitions):

| Method | Wall seconds, all three repeats | Median ms | Persistent state |
|---|---|---:|---:|
| Exact chunked Delta | 0.016062622, 0.014565622, 0.015326500 | 15.327 | 64 KiB |
| Diagonal history | 0.024125989, 0.022767848, 0.023414124 | 23.414 | 64.5 KiB |
| Full RLS history | 0.027503893, 0.028104079, 0.028373807 | 28.104 | 128 KiB |
| Rank-16 FD-style sketch | 0.100227370, 0.101345829, 0.099562817 | 100.227 | 80 KiB |

Full history is about 1.83x slower than the appropriately chunked Delta baseline here. The sketch saves persistent state relative to full RLS but its maintenance is slower in this implementation. State does not include buffers/workspaces.

Full RLS at d=128, T=4096: token recurrence 112.890 ms; B=8/16/32/64 gives 50.778/36.351/28.104/29.189 ms. Cyclic B=[8,16,32,64] gives 29.632 ms. Residual-adaptive B with scoring included gives 45.632 ms, using 87 blocks. The heuristic did not improve on fixed B=32.

Long streaming check: d=128, T=65536, B=32, input buffer <=1024 tokens, update+causal-read time **0.447309 seconds**, peak process RSS **108.39 MiB**, persistent state **128 KiB**. This is one streaming check, not a three-repeat estimate. Outputs were finite and final full-RLS covariance was positive definite.

PyTorch memory-only forward/backward: batch=2, heads=4, d=128, T=512, B=32, full history: median forward **39.851 ms**, backward **73.110 ms**, peak process RSS **326.62 MiB**; finite gradients. No projection layers, MLP, vocabulary/embedding, optimizer or language-model training is included.

## Evidence and limits

56 tests passed, including dense stationarity, B=1, zero-residual behavior, RLS/batch ridge agreement, arbitrary block partitioning, exact chunk-Delta parity, causal future-mutation/gradient checks and gradcheck. A scalar-Delta operator check used the inspected recurrent body of FLA at commit `1fe52b5d05c53601885610fab3d39157647d836d`, with explicit scaling and normalized keys; this is not full architecture reproduction.

93 core configurations / 279 timed repetitions; five separate long-stream checks; six forward/backward configurations. Timing repetitions are not scientific cycles. Peak process RSS in the core profiles ranged from 109.39 to 144.77 MiB.

Direct download/DNS and persistent-session failures were repaired with connected source reads and finite command batches. One interrupted parent batch was reconciled against the actual process list before resuming. Final primary indices 0..80 are present exactly once. Failures and incomplete cost accounting are retained in the full package. No background task was started.

Relevant prior work includes DeltaNet's chunkwise formulation (arXiv:2406.06484), RLS/Mesa updates and Kalman Delta Networks (arXiv:2609.07816). Neither chunking nor uncertainty-weighted memory is claimed as new here. No independent reviewer was available, and no native language-model effectiveness comparison was performed.

**Conclusion:** CPU feasibility is demonstrated for the measured memory operators and shapes. Full/diagonal variants are practical controls; low-rank runtime benefit, semantic retention/overwrite improvement, full-model training feasibility, GPU performance and novelty remain unestablished.
