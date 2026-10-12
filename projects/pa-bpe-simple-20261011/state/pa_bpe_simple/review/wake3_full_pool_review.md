# Wake 3 full-pool scalar/vector review

**Acceptable as a bounded exploratory implementation by inspection; no concrete scalar/vector selection defect found.** This is the same exposed reviewer as the preceding audits, not an independent confirmation evaluator. No training, scoring, numerical diagnostics, or further delegation was performed. Only this report was written.

Binding: `wake3-full-pool-vector-review`, generation 1; project `pa-bpe-simple-20261011`; goal contract 2; idea `pa-bpe-domain-robustness`, revision 1, method revision 3. All four assignment hashes independently matched:

| Input relative to `execution_windows/wake3b/` | SHA-256 |
|---|---|
| `scripts/train_full_pool.py` | `1ef86537ea2e3954a51ac9b2a80229d522fa166d3736381c64be2bb9511a5e2e` |
| `scripts/train_full_pool_vectorized.py` | `3979126eef319f75bd9244615849e0cc8cbb7872b2307c52dc9a69fd0988f4c0` |
| `full_pool_plan.json` | `09f3b5c9f190ca3b5a9376eb1fe0ef752f8d250c4bd356a422ae6e7a17977202` |
| `output/vector_equivalence.json` | `18997d7e488fa3419ec76b3dafaf4f4085d087c1689e10d9cbd05efd198506c9` |

## Equivalence and tie rules

Both scripts use identical eligibility and fallback selection (lines 45–48): all current training pairs with total adjacency frequency at least two and concatenated symbol not already produced. “Full pool” therefore means all **eligible training pairs**, not unrestricted possible merges. Both sort that pool, so set iteration cannot determine tie outcomes.

Scalar lines 50–53 evaluate a four-component gain vector and reshape post-merge costs to `(2 domains, 2 languages)`. Vector lines 50–58 stack those same gain vectors and reshape to `(number of candidates, 2 domains, 2 languages)`. Subtracting `lengths[None,:]` aligns the correct four slices. Minmax mode takes each domain's absolute language gap divided by twice its cost sum, then the maximum across domains. Pooled mode sums domain costs first (scalar axis 0; vector axis 1), preserving the language axis. These are corresponding operations; I found no axis swap, accidental pooling of candidates, changed normalization, or changed crossing treatment.

Both implementations select candidates below `before - 1e-12`. Among them they minimize the computed objective; **exact floating equality**, not tolerance equality, defines a best-objective tie. They then maximize total training frequency and finally the lexicographically largest pair (scalar lines 55–57; vector lines 60–62). The plan now states that direction explicitly. The global fallback uses the same frequency/lexicographic ordering. The gain vector included in each choice is not a tie key, avoiding array-comparison ambiguity. Vector gain rows remain valid after selection: they are backed by the materialized gain matrix, not by the subsequently updated statistics dictionary.

The same repeated-symbol scan remains in both scripts (lines 32–42): identical-symbol runs require nonoverlapping occurrence counting, while unequal-symbol occurrences cannot overlap. Both retain selected predicted-versus-applied gain checks, post-update objective checks, realized vocabulary checks, and separately encoded final development totals. This preserves the previous implementation's acceptance checks and limitations; neither version independently checks every unselected candidate statistic against a separate replacement implementation.

## Evidence and limits

The hash-bound equivalence record reports identical 100-step traces and merges for the **minmax** calibration, exit code zero, and wall time 1.399707926 seconds. That supports this executed calibration. The record does not establish a completed scalar/vector comparison for pooled mode or 1,000 steps; its underlying calibration traces are not separately bound in this assignment. Source inspection supports the same equivalence structure for pooled mode, but that is an analytical finding rather than an additional measured result. The runtime extrapolation is a planning estimate, not a completed full-run resource measurement.

Broadening the pool removes top-K coverage omissions within eligibility, but fallback still follows global frequency when there is no eligible descent exceeding the tolerance. It can increase the objective, including after zero Gini is reached: the code has no special zero-preservation rule. A final objective of zero therefore must not be described as evidence of monotone descent. Full-pool selection optimizes one immediate development step when a qualifying descent exists; it does not solve the multistep/global vocabulary problem or constrain efficiency.

The coordinator reports completed full-minmax training with zero development maximum Gini. That completion artifact is outside these four bound inputs and was not independently inspected here. If its final totals and checks pass, the scoped statement is exact token-total parity on both exposed development slices for that final tokenizer. It implies neither sentence-level parity, improved compression, population fairness, nor transfer success. Retain the planned cost and transfer measurements, matched pooled control, resource records, and exposure qualification before interpreting the new candidate. No novelty or causal conclusion follows from this review.
