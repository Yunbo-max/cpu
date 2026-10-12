# PA-BPE continuous research — Wake 4 report

Date: 2026-10-11 UTC  
Active idea: `pa-bpe-domain-robustness`, revision 1  
Method revision evaluated: 4, exact-train-compression-aware pair selection

## Outcome first

The prospective primary prediction failed. Maximizing immediate realized training compression among development-fairness-descending merges did **not** remove the out-of-domain cost penalty on the frozen exposed Books diagnostics. Compared with the prior full-minmax arm, `eff_minmax` increased mean Books total token cost by 0.42246094 and increased mean Books Gini by 0.00084014. It improved Gini relative to full-pooled by 0.00054904, but cost 2.10488281 more total tokens. Against Classical BPE it was worse on both mean Books Gini (+0.00177085) and total cost (+3.77421875).

The no-descent-constraint exact-train-gain control was the strongest of the three new arms and nearly matched Classical BPE, but was still slightly worse (+0.00011794 mean Books Gini; +0.05214844 mean total token cost). In this small bilingual setting, the development fairness constraint changed the merge path in a way that outweighed its local fairness benefit.

This is a negative mechanism result on exposed development diagnostics. It is not an unexposed confirmation result, a general multilingual fairness conclusion, or a reproduction of the original paper.

## Prospective rule and matched arms

The frozen rule considered native eligible pairs with raw adjacent frequency at least two and a novel concatenation. For `eff_minmax` and `eff_pooled`, it selected, when available, a pair whose thresholded floating-point development objective decreased by more than `1e-12`; among feasible pairs it maximized exact current-state nonoverlapping training-token reduction, then lower post-merge objective, then the lexicographically larger pair. If no improving candidate existed, it used the same train-gain/tie rule without the descent constraint.

The three full 1000-merge arms were:

| Arm | Development constraint | Final development costs | Fallbacks | Realized train compression |
|---|---|---:|---:|---:|
| `eff_minmax` | maximum of two domain Ginis | 6525, 6527, 3377, 3377 | 63 | 205063 |
| `eff_pooled` | pooled-domain language Gini | 6191, 6520, 3504, 3175 | 279 | 210572 |
| `exact_train` | none; minmax development objective only breaks train-gain ties | 5901, 6673, 3391, 3256 | not comparable (always marked fallback by construction) | 212934 |

`exact_train` must not be described as development-blind or literal train-only: its equal-gain tie is minmax-development-dependent. Eligibility is raw adjacency frequency while selection gain is corrected nonoverlap gain. These semantics are frozen in `cost_constrained_clarification.json`.

## Exposed Books results

The identical evaluation contains 10 OPUS Books works with 512 aligned English–French rows per work. All rows and TICO rows had already been exposed to method development.

| Method | Mean work Gini ↓ | Mean worst-language cost ↓ | Mean total cost ↓ |
|---|---:|---:|---:|
| Classical BPE | 0.01249223 | 56.04863 | 109.27031 |
| prior full-minmax | 0.01342295 | 57.87520 | 112.62207 |
| prior full-pooled | 0.01481212 | 57.21074 | 110.93965 |
| `eff_minmax` | 0.01426308 | 58.24512 | 113.04453 |
| `eff_pooled` | 0.01837250 | 57.54980 | 110.73770 |
| `exact_train` | 0.01261017 | 56.09316 | 109.32246 |

Paired work directions reinforce the aggregate result. `eff_minmax` had lower Gini than Classical on only 3/10 works, lower worst-language cost on 0/10 and lower total cost on 0/10. Relative to full-minmax it had lower Gini on 4/10 works and lower total cost on 2/10. Relative to full-pooled, its Gini improved on 6/10 works, but total cost improved on 0/10.

The independent verifier reconstructed 36 integer cost tables (three new arms × ten Books works plus two TICO splits), recomputed aggregates and contrasts, and passed all arithmetic checks. The two frozen prediction checks were: cost lower than full-minmax = false; Gini lower than full-pooled = true.

## Runtime and mathematical verification

An independent read-only reviewer accepted the repeated-symbol nonoverlap formula and deterministic selection order under the bound native semantics, while identifying five important scope corrections: the descent test is floating-point thresholded rather than symbolic exact; fallback steps break an unconditional monotonicity claim; `exact_train` uses a development tie-break; fallback counts are not comparable across modes; and the trainer's `assert` checks plus hard-coded true flags were not sufficient verification.

The coordinator therefore ran an explicit replay with `RuntimeError` checks, independent of those trainer flags:

- all 3000 selected merges across the three full arms were replayed;
- every selected train and development gain matched the realized state change;
- all trace lengths, merge files and independently tokenized final totals matched;
- every constrained selected step was a strict exact-rational descent;
- the smallest positive exact gap was `6.111940209382603e-08` for `eff_minmax` and `4.500999194929569e-06` for `eff_pooled`, both far above the implemented `1e-12` threshold.

The replay validates the selected sequence, not global optimality over every unselected pair. The static reviewer did not run the trainer or evaluator; the independent replay and arithmetic verifier cover the stated runtime checks.

## Source-overlap audit

The actual training sample consists of 40 English and 40 French FineWeb2 documents with recorded IDs/URLs. Against the frozen 5120 Books pairs, a same-language Unicode-NFKC/casefold exact word-shingle audit found zero matches at both 15 and 30 words across all ten works. This rules out detected verbatim overlap at those lengths within these 80 documents. It does not prove semantic, source or author independence, and it does not convert the exposed Books set into confirmation data.

## Execution and incidents

Eight scientific attempts ran serially with one process and one thread. All eight exited 0. Runner-charged scientific wall was 175.09700748 seconds; reservation was zero; peak measured RSS was 77,336,576 bytes (73.75 MiB). Project cumulative charged wall is now 770.02068227 seconds; continuous-research authorization has no project-wide time, attempt or cycle endpoint.

Two host administrative binaries, `rg` and later `jq`, transiently failed with `fatal library error, lookup self`. Python and the Simple runner remained usable; basic `ps` and Python JSON handling were used instead. Fresh probes later in the same window reported ripgrep 15.2.0 and jq 1.7 normally. No scientific task or score was affected. One first verification response was rejected before task creation because it contained two runner-owned task fields; the corrected response used identical frozen inputs, and both verification tasks succeeded. The rejected contract and runner alert are retained. After all attempts settled, the idle supervisor was deliberately interrupted; no scientific process or reservation remains.

## Interpretation and next discriminating action

The result argues against another scalar-tuning pass on the already exposed Books works. The next useful test under the same active idea is to diagnose objective mismatch: compare aggregate domain-mean Gini with sentence-aligned fairness and token cost across existing frozen arms, without using Books to select a winner. Only if that analysis discriminates a mechanism should one prospectively freeze a cost-budgeted or sentence-level candidate.

In parallel, broader evidence still requires a legally sourced, genuinely unexposed work/author/domain confirmation split and a provenance-complete third-language training sample. Until those are frozen, neither zero development Gini nor favorable exposed comparisons justify a multilingual or cross-domain stability claim.

## Primary evidence

- `execution_windows/wake4/cost_constrained_plan.json`
- `execution_windows/wake4/cost_constrained_clarification.json`
- `execution_windows/wake4/output/efficiency_candidate_summary.json`
- `execution_windows/wake4/output/efficiency_table_verification.json`
- `execution_windows/wake4/output/training_trace_replay.json`
- `execution_windows/wake4/output/source_overlap_audit.json`
- `review/wake4_cost_constraint_review.md`
- `review/wake4_cost_constraint_acceptance.json`
- `evidence/wake4_attempt_inventory.json`
- `evidence/wake4_resources_inventory.json`
- `evidence/incidents_wake4.json`
