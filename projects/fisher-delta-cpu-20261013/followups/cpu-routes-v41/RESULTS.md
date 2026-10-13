# CPU route feasibility and V4.1 report review

2026-10-13. Owner: chat-fisher-delta-20261013-a. Task: cpu-routes-v41-feasibility. Bounded engineering follow-up only; no native LM effectiveness, novelty or GPU claim. Previous Fisher/IMN experiments were not rerun.

## Actual allocation and measurements

4-core cgroup CPU quota, 4 GiB RAM limit; five affinity CPUs. One BLAS thread. NumPy 2.3.5, PyTorch 2.10.0+cpu. Each configuration: warmup plus three measured repetitions; input generation excluded. Full process peak RSS includes inputs, correctness checks and both compared methods. Timing variance is substantial.

| Test | Shape | Median time | Peak process RSS |
|---|---|---:|---:|
| Sequential register operations | T=16384, M=64, value width=8 | 162.88 ms | 334.55 MiB |
| Prefix-scan reference | same | 2149.63 ms | same process |
| Independent full top-k index/read | 65536 keys x64; 32 queries; k=512 | 439.70 ms | 193.41 MiB |
| Guarded reuse + fallback | same | 439.90 ms | same process |
| Independent full top-k index/read | 262144 keys x64; 32 queries; k=512 | 881.08 ms | 483.86 MiB |
| Guarded reuse + fallback | same | 923.00 ms | same process |
| Soft-route forward | batch4, T256, 16 registers x4, 23952 parameters | 38.56 ms | 272.08 MiB |
| Soft-route backward | same | 196.14 ms | same process |

13 tests passed. Register parity maximum absolute error 2.384185791015625e-7 in the long FP32 fixture. Every profiled top-k set matched its full-index reference. Gradients were finite.

The scan is a materializing Hillis-Steele reference with O(T log T) work, NOT an optimized linear-work GPU scan. Supplied hard addresses are not learned. The differentiable routing smoke test uses dense soft addresses with O(M^2) work and a random-target loss; no learning-success claim.

The index guard uses fixed K/V and dot-product scoring. Its exact-arithmetic sufficient condition is gap > 2 R ||q-q_ref||, R=max key norm /sqrt(d). Otherwise it rescans. This is an elementary control, not a novel method, CSA2 reproduction, certified floating-point implementation, complete hierarchical cache, or dense-attention equivalence. Key-norm preprocessing, selected readout and fallback are charged. It reused only 6/32 and 4/32 query selections in the explicit synthetic drift fixtures; these rates are not model observations. No clear acceleration was demonstrated.

Inputs to retrieval GEMV are FP32; NumPy scaling promotes scores/readout to FP64. The original dtype label was corrected in JSON metadata, with measured numbers and original logs preserved.

## Reading and decision

Official release: https://deepseek.com/en/news/deepseek-v4-1-flash/
Official model card: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
Official report HTML: https://arxiv.org/html/2609.19969 (v1 2026-09-17), focusing on 2.2, 2.3, 2.4.2 and 3.2.2.
Required prior-art controls: IndexCache https://arxiv.org/html/2603.12201 and LatentIndex https://arxiv.org/abs/2610.04635 (abstract only for the latter).
Prospective state-tracking task: https://arxiv.org/abs/2602.14814 (not reproduced).

Priority: test query-sensitive reuse/refinement against static/calibrated index-sharing under matched information and cost. The initial bound is too conservative to show benefit here. Investigate usefulness before adding seeds. Retain copy/overwrite as a separate architectural candidate. Engram parameter lookup does not validate a dynamic writable-register proposal.

## Incidents and delivery

Container DNS failed; connected reads and official HTML succeeded. PDF links failed, so no PDF-inspection claim. One combined profiling command hit 45 seconds; no benchmark process remained. Completed JSONs were retained, and incomplete/never-started configurations were executed separately. No background task was created.

Complete reproducible local artifact: cpu_memory_routes_v41.zip, 17 files, 19949 bytes, SHA256 c18efea6c9bd006e99678ed9ca30d0ab005f0c9e6e6599803930be5e15bb5ca6. ZIP CRC checked. It contains code, raw timing JSON/logs, red/green/final tests, sources and manifest. This GitHub file is a digest; the ZIP itself is delivered in Chat, not uploaded here.

Outcome: CPU feasibility supported for these shapes; research effectiveness, hard-routing learnability, tighter-gate usefulness, small-LM quality, full DeepSeek reproduction and GPU performance remain unestablished. Stop bounded task; no automatic continuation.
