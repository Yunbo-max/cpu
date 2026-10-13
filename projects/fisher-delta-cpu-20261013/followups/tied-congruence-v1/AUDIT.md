# Tied-congruence RNN: novelty and mathematical audit

2026-10-13. Task `tied-congruence-audit-v1`. The user authorized novelty/math checks and quality training only after both are qualified.

## Verdict

Core equations, gradients, causal outputs and exact chunk composition passed **36 tests**. The reference and a small projection-wrapped layer ran CPU forward/backward. **No task training occurred: zero optimizer steps, zero GPU runs, no independent scientific reviewer.**

No exact prior implementation of the complete tied, input-dependent row-stochastic diagonal-plus-rank-one construction was identified in inspected sources. This is **not** evidence that nobody has done it. GSA2 original full equations/code were not successfully obtained; the newer maintained SLiCEs implementation was not fully audited. **Novelty remains incomplete; the user's two gates are not both cleared. Formal quality training was not started.**

## Method and verified algebra

P=diag(1-g)+g p^T, where p=softmax(input projection), g=sigmoid(input projection).

S'=a P S P^T+(1-a)uv^T, with sigmoid a and tanh u,v. Query readout y=S'q. All step parameters depend on current layer input, not this layer's old recurrent state.

The exact O(r^2) expansion is D S D+(DSp)g^T+g(p^TSD)+(p^TSp)gg^T, D=diag(1-g).

Block action (a,P,U): aPSP^T+U. Later block 2 after earlier 1 composes as (a2*a1, P2@P1, a2*P2@U1@P2.T+U2). The implemented work-efficient Blelloch scan operates over block summaries, followed by parallel block replay. Block P/U become dense; total main work is O(T H r^2 + (T/C) H r^3), excluding projections/readout. This is ordinary PyTorch, not a fused GPU kernel or an optimized-backward-memory implementation.

## Important restrictions found

1. **Neutral-logit contraction.** With uniform p, g=0.5, a=0.5 and a doubly centered difference E between states receiving the same future writes, E'=E/8. After 8 steps its ratio is 5.96e-8; after 32, 1.26e-29. Entrywise boundedness does not establish useful memory. A near-identity initialization is a mitigation to test, not a solved learning problem.
2. **Not arbitrary rebinding.** det(P)=product_i(1-g_i)*(1+sum_i p_i*g_i/(1-g_i))>0. Products cannot directly implement an odd slot permutation, e.g. swapping two slots, in the same semantic coordinates. Hard copying is a valid singular boundary limit. This is not a theorem that a multilayer learned model cannot solve permutation tasks using another encoding.
3. **Only an entrywise norm bound.** max-entry(S_t)<=max(max-entry(S_0),1) under the stated ranges. Frobenius norm and gradient behavior need not be contractive.

## Actual CPU measurements

4-core cgroup quota, 4 GiB RAM, PyTorch 2.10.0+cpu, one torch thread; no CUDA. Includes projection, query/output layers and loss/backward; excludes optimizer and input generation. One warmup and three measured repetitions per method/configuration, fixed counterbalanced order. All parameter gradients finite.

| batch=2, heads=4, input width=64 | Sequential forward+backward median | Chunked forward+backward median |
|---|---:|---:|
| T=128,r=16,C=16 | 63.879 ms | 35.865 ms |
| T=512,r=16,C=32 | 350.983 ms | 117.461 ms |
| T=128,r=32,C=16 | 90.546 ms | 56.685 ms |

Whole-process peak RSS across all configurations/tests: 403.715 MiB, not per-method incremental memory. These are two implementations of the same candidate, not performance comparisons with DeltaNet or KDN.

T=37,r=8: FP64 output max absolute error 2.78e-17; gradient max absolute error 4.44e-16. FP32 corresponding errors 2.98e-8 and 7.15e-7.

## Closest-work evidence

- Learning Deep Matrix Representations, arXiv:1703.01454, sections2.1/2.3 eq3,6-8: two-sided matrix RNNs already exist; inspected rule uses fixed separate factors and nonlinear activation.
- Kronecker Recurrent Units, ICML2018, section3 eq4-8: Kronecker recurrent parametrizations are old; not the same input-generated tied stochastic map. https://proceedings.mlr.press/v80/jose18a/jose18a.pdf
- SLiCEs, arXiv:2505.17761, sections4.2/4.6 and appendixA.2: input-dependent structured maps, matrix/vector equivalence and scans are established. Original code `Benjamin-Walker/structured-linear-cdes@243cb30fcd85406a94f2810ec762c59e6e2bb1c7`, README and models/slcde.py lines1-280 inspected; model blob bd0ce7d02d0f7399a90c1ddb96f64574c2531bef. No tied-congruence implementation in that inspected class; newer maintained repo remains uninspected.
- M2RNN, arXiv:2603.14360v2, eq10-12/19-22: tanh(HW+kv^T) residual recurrence, not the proposed affine congruence.
- DeltaProduct, arXiv:2502.10297v7: products of Householder maps; needed strong state-tracking comparator.
- GSA2, arXiv:2610.02816: original abstract says key-side Oja-2 and value-side Delta-2 through shared slots. **Full mathematical comparison incomplete.** Third-party AI reviews were not used as primary evidence.

Original PDF parsing was available for some sources, but screenshot requests failed; no figure/table visual inspection claimed. Direct container Internet/DNS was unavailable. No source failure was silently counted as novelty evidence.

## Delivery and exact next step

`relation.py` is the verified reference. Full tests, initial expected failures, math proofs, source audit, raw repetitions and manifest are in the Chat artifact `tied_relation_audit.zip` (14 files,23755 bytes,SHA256 26b0f22c3737437d98e8a7a150de4d62d2e595f16ca05db6412758ffeb53d25b). The complete archive is not uploaded here.

Next: complete closest-source equation equivalence checks; restrict mechanism claims and freeze a retention-initialization/tuning protocol; admit a matched public-task comparison only after the conditions are qualified. No automatic/background continuation is active.
