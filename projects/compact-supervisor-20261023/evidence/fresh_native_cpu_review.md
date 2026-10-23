# Informal review of extracted Megatron CPU audit

Date: 2026-10-23. Reviewer: sparse-training leaf worker. This is an implementation/math check by a participating worker, **not independent Work acceptance**, design approval, actual-code gate approval, or full native-model validation. I did not modify the audited script or evidence files.

## Verdict

No blocking defect found for the stated narrow claim: the unchanged non-fused, top-1 softmax loss/helper bodies, run on CPU with equal-size microbatches and single-rank stubs, reproduce the prefix auxiliary gradient and its permutation-average mixture identity. The script correctly handles the unusual custom auxiliary backward by setting the scaler directly rather than relying on scaling a dummy main loss.

It must not be described as a completed Megatron distributed training reproduction, a Qwen benchmark result, an audit of current main, or proof of practical damage. The source pin is historical `72d23540d0358ae24a41ff289d1461b094a770fa`.

## Actual review actions and receipt

Read the entire `fresh_native_cpu_audit.py`; inspected relevant original source sections in `evidence/megatron_router_72d2354.py` and `evidence/megatron_moe_utils_72d2354.py`. Executed once with `python fresh_native_cpu_audit.py`; exit code 0. Runtime: torch 2.14.1+cpu, Python 3.12.14. Tool process wall time 2.503 s; script's measured inner audit time 0.803 s. Four fixtures, 74 permutations total (2 + 3*24); each permutation runs ordinary, per-token-scaled, and reset/repeated variants.

Observed maxima across reported fixtures:

- Native extracted versus independently written prefix gradient: 2.0489096641540527e-8.
- Mean native versus harmonic-mixture identity: 1.30385160446167e-8.
- Per-token equivalent final scaling difference: 3.725290298461914e-8.
- Logged loss difference: 1.1920928955078125e-7.
- All reset/repeat comparisons exact in this run.

This review rerun is additional verification work; do not merge its time with an earlier run or count it as an independent seed/model experiment.

## Correct aspects

1. AST extraction compiles original function/class statement nodes without body rewriting. Names and exact extracted-source hashes are emitted. Technically this is five functions/methods plus one class, rather than six functions. Missing module initialization is replaced deliberately by supplied globals and SimpleNamespace state.
2. `_apply_global_aux_loss` includes the historical count accumulation, ga_steps update, and current-score loss; these are the mechanism under examination.
3. Native route counts are discrete and non-differentiable, matching the independent detached-frequency reference. Immediate backward after each forward avoids an accidental buffer-mutation/autograd lifetime divergence from normal sequential accumulation.
4. `MoEAuxLossAutoScaler.backward` injects its configured auxiliary gradient regardless of zero main upstream gradient. Consequently `(out.sum()*0).backward()` legitimately isolates auxiliary gradients here. This is not a vanishing-loss false negative.
5. Setting the scaler to 1/G explicitly makes the ordinary auxiliary gradient equal the average of G microbatch contributions. The reference separately constructs the corresponding scalar objective; it does not call the extracted loss function.
6. For equal-size n and single rank, the per-token arm multiplies the aux loss by n internally, sets scaler 1/G, then divides the resulting gradient by n. This has the same final factor as multiplying by n, setting scaler 1, and finalizing by 1/(Gn). Hence the reported final gradient equivalence is valid for these fixtures.

## Scope restrictions and possible misleading conclusions

### Binary fixture is not an order-sensitivity witness

The binary fixture uses opposite input signs and a symmetric score derivative. Both permutations yield the same nonzero gradient; its exact-global gradient is zero. It is a clean witness of **systematic micro-batch contamination even after permutation averaging**, but not of variation between the two orders. Do not show its gradient as an order-dependence demonstration. The random fixtures may show order variation, but the script currently does not emit a max/rms permutation-spread metric or explicitly assert it is nonzero.

### Per-token scaling tests a final algebraic equivalence, not pipeline integration

The scaler value and final n division are hand-set. `finalize_model_grads`, pipeline schedules, gradient scaling, optimizer step, data-parallel normalization and token count aggregation are not executed. The comment correctly calls this explicit replacement. Because all batches have equal size, this test cannot address uneven valid tokens, padding, packed sequences, or issue #7213. Also it does not establish exact scaling under TP/CP/DP group overlaps or multiple pipeline stages.

### Reset is directly invoked, not scheduled

The repeated-router check verifies `reset_global_aux_loss_tracker()` clears these two buffers and restores repeated behavior. It does not verify that production code calls reset at the right lifecycle boundary, after activation recomputation, on skipped optimizer updates, or on failures. Do not present it as production reset-scheduling coverage.

### Dtype and top-k boundaries

All fixture tensors are float32 and CPU. The source softmax explicitly casts to float32; the independent reference does not specify a dtype but agrees because inputs are float32. Extending to float64 or mixed precision would require reference semantics to match that cast. The audit does not cover BF16/FP16, loss scaling/overflow, fused TE kernels, stochastic jitter, top-k>1, sigmoid routing, capacity/token dropping, or expert outputs.

Native `torch.topk` and reference `argmax` can disagree on tied scores; present fixtures appear to avoid ties. The fixture contract should remain “no score ties,” or tie handling should be aligned before adding adversarial tests. This is not an observed failure in the run.

### Receipt strength

The script records extracted segment hashes but does not itself verify complete downloaded files against a trusted remote artifact. Provenance must come from the owner's download receipt/source pin. It reports `loss_max_abs_error` without asserting a tolerance on that metric; gradient equality is asserted. Calling the loss comparison a passing automated assertion would overstate the script, though observed values are small. With coefficient fixed at 1, the audit does not check configuration-driven coefficient retrieval/disabled-loss branches.

## Minimal useful follow-up, if needed

No broad testing sweep is necessary to support the already scoped identity. Before using the audit to support a separate order-dependence claim, add/record a permutation-spread statistic or an asymmetric two-batch fixture. Before claiming production training behavior, inspect and execute the actual pipeline scaling/reset path on a pinned full setup; the present CPU extraction is deliberately narrower. A GPU training run is not needed merely to validate this finite gradient identity.

Suggested precise description: “We executed unchanged AST-extracted non-fused Megatron routing-loss components from a fixed commit in a single-rank CPU harness, with explicit auxiliary-loss scaling. Across 74 permutations, their gradients matched an independent prefix reference and the derived permutation-average identity to float32 tolerance.”

## Scientific interpretation

The CPU audit supports the algebra-to-implementation connection. It does not settle novelty, native effect size, training convergence, specialization harm, or advantage of any correction. The original paper openly calls its buffer approximate. A deviation from the exact global objective therefore establishes an approximation property, not by itself an implementation bug or refutation of reported performance.

## Final revision addendum — supersedes the receipt/spread omissions above

Reviewed the added source-blob assertions, loss assertion, permutation spread, and two coefficient-control arms. The final audited script SHA256 is `eb8604d9314a9378380255980d702bd37a890fe5383d61740fa7eef0c4f816f2`. This addendum applies to that exact file, not to later edits.

Source SHA256 values:

- Router: `fae1518fcc97e85c972a7699a898ddcf7920d717185e7a7efaa505562f69f882`.
- MoE utilities: `0ca558ad82bd8a03f70b2e3f04c4cf0435c5394031aa4fb210fe3c7572c731c7`.

The new Git blob hash calculation correctly includes the `blob <byte-length>\0` prefix and asserts the entire original byte sequence. The assertions passed for router blob `8cb8936a785d4d02ed6e240a61912d3aa2b29cbf` and utility blob `739283ee8b72cce835f94d6109e76169edfa0112`. Root reports matching GitHub API blob receipts; this reviewer verified local assertions, not an independent remote refetch. The former complete-file-hash gap is closed conditional on those remote receipts. The new `maxloss < 3e-7` assertion also closes the formerly descriptive-only loss check.

Executed the revised script once successfully: exit 0, torch 2.14.1+cpu, Python 3.12.14, outer wall time 2.916 s, inner time 0.952 s. This is a separate final-revision rerun; do not combine timing with the earlier revision. Across the same 74 permutations, maximum prefix/reference gradient error was 2.0489096641540527e-8; maximum logged-loss error 1.1920928955078125e-7; maximum per-token equivalence error 3.725290298461914e-8; all direct reset/repeat checks remained exact.

The new prefix coordinate-range maxima are 1.4901161193847656e-8 for binary, and 0.1566033512353897, 0.15156501531600952, 0.12750288844108582 for the three asymmetric fixtures. Thus the latter provide concrete order-dependence witnesses. The binary result remains roundoff-level order variation and must remain a systematic-bias witness rather than an order-spread witness.

### Added controls: mathematically consistent, bounded claim

For current microbatch frequency f and accumulated previous frequencies P at zero-based position j, the new code supplies effective coefficients `a = f/G + P/j` (with the previous term zero at j=0) or `a = (f+2P)/G`. Passing `a*n` into the unchanged native loss helper yields the intended weighted linear score objective; these are effective counts, not actual observed token counts or necessarily normalized frequency vectors. Detached top-1 routing makes the coefficient treatment consistent with the existing derivation.

Under frozen parameters, equal microbatch sizes, no stochastic forward changes, and uniform random permutations, both controls have the exact-global gradient in expectation. For the first control, the diagonal coefficient is 1/G before the outer 1/G, and the expectation of the previous-average term assigns 1/G to every off-diagonal item. For the second, each ordered pair appears with probability one half and receives weight 2/G. Pairing an ordering with its reversal therefore recovers all ordered cross terms exactly, with the correct diagonal weight. These facts justify the added mean/reverse-pair comparisons.

Observed maximum errors across fixtures: positive-control mean versus global 1.30385160446167e-8; pair-HT mean versus global 1.30385160446167e-8; pair-HT forward/reverse average versus global 1.6763806343078613e-8. All corresponding assertions passed.

Crucial scope: the controls use newly written coefficient logic and unchanged native score/loss/custom-backward helpers. They do **not** execute an unchanged production `_apply_global_aux_loss` correction, and reverse pairing is two executions, not an exact causal single-pass solution. This verifies coefficient algebra through the original helper/autograd path, not estimator novelty, variance benefit, training improvement, or a production implementation. All earlier dtype, single-rank, equal-size, manual-scaling, reset-lifecycle and no-full-model limits remain.

No new blocking defect found in the added segments. The original setup/stub failure receipt should remain in root's chronological report; a successful corrected run must not erase it. This reviewer did not independently inspect that first failed receipt and makes no claim about its exact failure text.

### Final stable scaling revision

The last small revision changes the per-token arm to set auxiliary scaler 1 and divide the resulting gradient by G*n, matching root's inspected scheduler/finalizer sequence more directly. I inspected this changed block and reran the stable script: exit 0; outer process time 2.729 s, inner 0.897 s. Maximum per-token equivalence error remains 3.725290298461914e-8. All other assertions passed. The final script SHA256 verified before and after that run is **`ff3fa89cef4b27f0ee7001b7c9c2ca71447e681b6ce243f23daa5102d78dce6a`**, superseding the script hash in the preceding addendum; both source hashes remain unchanged.

The old review description of scaler 1/G followed by division by n describes the earlier script only. The final code uses scaler 1 then division by G*n, while ordinary mode uses scaler 1/G. The finalizer and scheduler themselves still do not execute in the harness. I have not separately fetched their source in this review. Reset remains manually invoked at the beginning of each harness run; production end-of-step reset timing is not validated here. This final revision preserves the narrow no-blocker verdict and does not expand evidence to full pipeline integration.
