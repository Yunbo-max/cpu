# Prospective staged protocol — not yet executable/admitted

Version: P001, authored 2026-10-17. Parent goal: distinguish textual copies versus independent evidence in causal LM attention. T001 source/mathematics is separate from a prospective experiment. Do not silently claim Gate A/B/C/D.

## Stage 0 — qualified execution prerequisites
1. Restore official Auto Chat .29 source bytes into the actual Chat CPU host, validate exact source manifest/hash and run chat_wake.py with original execution guard. Do not substitute a homebuilt controller or GitHub Actions.
2. Read shared cooperation ledger; pin original goal/inputs, guard policy and task-specific execution contracts. Only then admit a producer and approved scientific verifier.
3. One native serial CPU experiment program, <=4,000,000,000 total bytes including interpreter/data/workers, using cgroup cap if lower. Observed host 4 CPU quota, 4GiB cgroup. No GPU, Docker, remote/SSH, paid API.
4. On real producer timings, recalculate workload and 60–120-minute capacity. The target is not elapsed execution. The 3,600 seconds accepted *producer CPU* acceptance target is a separate later check with real receipts.
5. For cross-turn, verify checkpoint bytes, restore ancestry and cumulative budgets in independent host invocations; never infer continuation from unit tests or a new timer.

**Current admission: Gate A NOT_BOUND, workload B NOT_READY, multi-call C UNVERIFIED, question-update D UNVERIFIED.** A brief CPU arithmetic sanity check was performed for the proof in research notes; it is not a qualified producer run.

## Stage 1 — controlled attention/identifiability diagnostic (only after Stage 0)
Frozen factors:
- Copy multiplier m in {1, 2, 4, 8, 20, 64}; relevant-vs-distractor logits a=2, b=0; representative scalar values v_target=1,v_distractor=0.
- Conditions: (a) m copies from ONE distractor source; (b) m same-content distractors from m separate sources; (c) mixed support and contradiction; (d) all-identical-value control.
- Methods: vanilla Softmax; temperature-only baseline; globally de-duplicated fact identity; exact (evidence,source) quotient correction; explicit source dedup preprocessor; official LUCID faithful port after checking code and parity.
- Estimands: target attention-mass delta from m=1; independent-source response slope; exact quotient-equivalence absolute error; max absolute error vs direct class-level Softmax; source-vote posterior calibration.
- Numeric: float64 first and FP32 crosscheck, exact deterministic fixtures. Need not inflate seeds for a deterministic theorem.
- Necessary negative control: unknown provenance or spoofed origin; the proposed operator has no identifiability guarantee. Key equality with unequal values is invalid grouping and must be rejected.
- Failure interpretation: an algebraic mismatch implies code/protocol issue, not a scientific refutation; strong simple baseline equal to candidate implies no architecture contribution from this operator alone.

Prospective minimal reference script: src/attention_reference.py (math-only; NOT a native Transformer benchmark). Use a separate verified producer/verifier with pinned file SHA before execution.

## Stage 2 — CPU autoregressive task, conditional on qualified Stage 1
Question: With provenance visible to every model, can a source-conditioned attention module generalize to large within-source copy shifts while preserving independent votes and contradictory facts? Train a tiny causal next-token LM; choose size only after measured batch calibration.

Paired model family comparisons (not yet implementation-complete): (1) ordinary Softmax with provenance in token inputs, (2) same model with explicit source-dedup preprocessing, (3) direct source-count pooling / DeepSets strong simple alternative, (4) LUCID with faithful official computational rule, (5) proposed provenance-conditioned attention with equal access to source IDs. Compare trainable parameter counts, context length, optimization, tokens processed, score, memory and inference latency.

Data/labels: source-vote evidence streams followed by query/prediction token; independent source emissions have known reliability p (e.g., .75), dependent duplicates preserve the original emission and ID. Training source count 1–4; training duplicates 1–2. Frozen held-out copy counts 4/8/16, independent-source counts 5–8, conflicting-vote subsets and provenance corruption 0/10/30%, plus input position shifts. A task encoder without provenance cannot be expected to solve the constructed latent mixture; keep it as information ablation, not fair performance comparator.

Primary metric: per-example next-token NLL and Brier score against ground-truth Bayesian source count, with denominators and calibration bins. Secondary: answer accuracy, duplicate-invariance slope, independence-sensitive response, time, peak RSS, train/inference tokens per second. Freeze disjoint train/development/confirmation seeds and source IDs. Frozen final confirmation only after justified development model/hyperparameter selection. Explicit false-positive mechanism test: candidate may be only explicit preprocessor in disguise.

Strong external validity needed later: adapted independent-document FictionalQA-style task, public RULER/BABILong retrieval condition with provenance/source labels or another native task of the claim's scope. Large model quality and originality cannot be inferred from our tiny LM.

## Prespecified interpretations and successor actions
- Algebra passes, trained native gain over *all* simple baselines: deepen LUCID and position-aware/provenance-noise study; acquire independent review.
- Algebra passes, explicit dedup or source pooling matches candidate: do not call it new architecture; pivot to actual missing capability, possibly provenance inference or conflict-preserving state.
- Position/RoPE breaks invariance: derive query-relative class scoring or narrow claim, and test counterexample before proposing another mechanism.
- Bad provenance causes failure: report risk boundary; do not tune on frozen confirmation. Consider abstention or dependency uncertainty, not silent oracle IDs.
- Invalid run or missing native scorer: repair source/scoring contract and retain raw failed attempts; no scientific success/failure verdict from setup errors.

## Workload arithmetic and readiness
No matched native measured unit time, no restored execution gate, and no verified runnable LUCID comparator. Therefore qualified 60–120min coverage = 0 minutes, shortfall to default 90min = 90 minutes; workload is NOT_READY. Stage 1's 6 copy counts x 4 contexts x up to 6 comparators gives at most 144 deterministic settings, not 144 independent repetitions or a run-time promise. Later measured calibration plus result-dependent tasks determine actual executable capacity; mutually exclusive successor branches are not summed. No producer CPU seconds credited.
