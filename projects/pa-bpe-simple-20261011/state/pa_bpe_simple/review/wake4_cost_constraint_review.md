# Independent review: Wake 4 cost-constrained PA-BPE

## Review boundary and input integrity

This is a read-only static mathematics/code review of the three assignment-bound inputs. I did not run the trainer, tokenizer, evaluator, scoring, or any numerical diagnostic, and I did not inspect or mutate runner/shared state.

All assigned SHA-256 digests match:

| Input | Assigned and observed SHA-256 |
|---|---|
| `execution_windows/wake4/scripts/train_efficiency_constrained.py` | `8cf94da571e44a12ee2ab00d390dd28768ee104c5913383d1f547854ddf6fc1b` |
| `execution_windows/wake4/cost_constrained_plan.json` | `579cf6e3a820546fc720a66174cccb7437446377787ac46dd2377f407a663d19` |
| `execution_windows/wake3b/output/full_candidate_summary.json` | `971ba8f34c25681c3636e1ec990125420b38d049698bcc34054505076d21a113` |

Verdict: the one-step realized compression accounting and deterministic selector are coherent under the imported native routine's assumed semantics. The repeated-symbol correction is mathematically right. However, the implementation is not literally an **exact** strict-descent test, the fallback makes the full trajectory only conditionally constrained, and the arm called `trainonly` is development-objective-tiebroken. These are material scope/wording issues. Verification is also implemented with removable `assert` statements followed by hard-coded success flags. No empirical or scientific-effectiveness claim is established by this review.

## Exact realized train-gain logic

At a current vocabulary state, one replacement of a selected pair reduces the token length by one for each nonoverlapping occurrence replaced. The code keeps this quantity as a vector over the two training languages and selects using its sum (`train_gain_matrix`, `train_totals`, lines 53--55).

For a pair `(x, y)` with `x != y`, two occurrences of that same ordered pair cannot start at consecutive positions: starts at `i` and `i+1` would require the shared symbol to be both `y` and `x`. Therefore occurrences of the selected pair cannot self-overlap, and an up-to-date adjacent-pair count is exactly the realizable replacement count. Returning the native `pair_stats` vector in lines 34--35 is consequently correct, conditional on `get_pair_statistics`/`update_pair_statistics` maintaining weighted current adjacent counts.

For `(x, x)`, raw adjacent counts do overlap. In every maximal run of `x` of length `r`, a greedy left-to-right replacement realizes exactly `floor(r/2)` merges. Lines 36--44 scan left to right, advance by two on a match and by one otherwise, so they compute that value and multiply it by the word's per-language or per-domain frequency vector. This is the correct nonoverlap correction for a native `replace_pair` routine with the same left-to-right semantics. The selected-pair assertions in lines 78 and 82 would detect a discrepancy in a normal, non-optimized Python run.

The accumulated `realized_train_compression` is a telescoping token-count reduction across the selected sequence: each `actual_train` is `old length - new length`, frequency-weighted, and `train_lengths` is decremented by it. It is exact for the realized current-state sequence, not a globally optimal final compression, a normalized per-language gain, or a future-corpus gain. Summing the two language components also optimizes raw aggregate training tokens; equal document counts do not by themselves make the two languages equally weighted by bytes or initial tokens.

Two qualifications are necessary:

1. Eligibility uses the native raw statistic `sum(ts[pair]) >= 2` (line 50), not the corrected nonoverlap gain. For a repeated-symbol run such as three identical current symbols, the raw adjacent count is two while only one merge is realizable. Selection still uses the corrected exact gain, so its optimization is internally coherent, but the plan must define whether “eligible” and the minimum-frequency threshold mean raw adjacent frequency or realizable nonoverlap frequency. The present files do not state that distinction.
2. Static inspection proves the counting formula but cannot verify the imported `native_pa_source.py` or `evaluator_reference.py`; neither is hash-bound in this assignment. In particular, current-statistic maintenance, pair-index contents, replacement order, and independent tokenizer construction remain outside this review's evidence.

## Selector, ties, and fallback semantics

For `minmax` and `pooled`, the code constructs the candidate set

`I = {j : objective_after[j] < objective_before - 1e-12}`.

If `I` is nonempty, it selects the maximum tuple

`(aggregate realized training gain, -post-merge objective, pair tuple)`

over `I` (lines 63--69). Thus the actual order is: require thresholded development-objective descent; maximize aggregate current-state training compression; among equal gains choose the lower post-merge objective; among remaining ties choose the lexicographically larger Python tuple of token strings. This matches the written tie order, including “larger,” and is deterministic. `pooled` uses the pooled two-language objective, while `minmax` uses the maximum of the two domain-specific two-language Ginis. The two-value Gini formula used, `|a-b| / (2(a+b))`, is correct.

If no candidate passes the descent test, the code selects over all eligible pairs with the same tuple key (lines 70--73). Therefore fairness is a feasibility constraint only on steps where a thresholded improving pair exists. On fallback steps the objective may stay flat or increase. The rule does **not** guarantee monotone fairness, and the plan's unqualified description “training compression is optimized subject to strict fairness descent” needs the explicit “when feasible; otherwise unconstrained fallback” exception.

`trainonly` always takes the fallback branch, regardless of whether improving candidates exist. It maximizes train gain but then breaks gain ties using the **minmax development objective**, followed by the pair tuple. It is therefore not development-blind or literally train-only. Relative to `eff_minmax`, it is a useful matched selector control: same candidate set, train-gain accounting, secondary minmax objective and deterministic final tie, with the descent-feasibility filter removed. It is not equivalently matched to `eff_pooled`, whose secondary objective is pooled, and it is not interchangeable with classical BPE. Claims should call it a “no-descent-constraint, minmax-tiebroken train-gain control,” or the implementation/control set should be changed.

## Concrete defects and ambiguities

1. **“Exact strict descent” is not implemented exactly.** Costs are integers and the objective is rational, but lines 31 and 60--63 convert to floating point and define improvement using an absolute `1e-12` tolerance. A positive rational decrease of at most that amount is rejected, and exact rational ties/order are not the implemented semantics. No bound in the three inputs proves that such cases are impossible. Either use exact integer/rational cross-products (including exact comparison of the domain maximum) or change the contract to “floating-point descent greater than `1e-12`.” The same qualification applies to `strict_descent_steps` and the prediction check.
2. **The fallback is omitted from the mathematical-role sentence.** The implementation deliberately violates the descent constraint when its thresholded feasible set is empty. This is coherent as a totalized algorithm but not as an unqualified constrained-optimization claim.
3. **`trainonly` has a development-dependent tie rule.** This is consistent with the plan's “same secondary ties,” but inconsistent with a literal train-only reading and potentially misleading when interpreting the control as removing development information. It is directly matched only to the minmax arm's secondary tie rule.
4. **`fallbacks` has different meanings across arms.** For `minmax`/`pooled`, `fallback=True` means no candidate passed the descent threshold; for `trainonly`, it is always true by construction. Its count cannot be compared across these arms as the frequency of an empty fairness-feasible set. Record `has_improving_candidate` and `constraint_applied` separately.
5. **Verification can disappear under optimized Python.** All gain/final-total checks use `assert`, which `python -O` removes, while lines 105--107 unconditionally write the three verification fields as `True`. A completed optimized run could therefore report verification without performing it. Use unconditional explicit checks that raise on failure, and derive reported fields from those checks. Even normally, the per-step assertions validate selected pairs only; the name `predicted_*_gains_all_equal_actual` should not be read as runtime validation of every unselected candidate's predicted gain.
6. **Repeated-pair eligibility is underspecified.** Raw overlapping frequency controls the `>=2` threshold, whereas corrected nonoverlap gain controls selection. This may be intentional compatibility with the parent trainer, but it must be frozen explicitly for reproducibility and comparator matching.

None of defects 1--4 changes the deterministic tuple selected under the implementation's actual declared floating/tie semantics; they change whether the stronger mathematical and control descriptions are justified. Defect 5 affects whether successful execution would really certify the reported verification flags.

## Matched controls and supported claim scope

The three new arms hold fixed the listed data, merge budgets, byte alphabet, pretokenizer description, candidate enumeration and gain-accounting code. Within this script, `exact_train` isolates removal of the minmax descent-feasibility filter while retaining a minmax development tiebreak. It does not isolate all use of development data. A separately pooled-tiebroken train-gain control would be needed for an exactly analogous `eff_pooled` control. The Classical BPE comparison mentioned in the plan is an external strong baseline, not an arm produced or qualified by this script.

The prior `full_candidate_summary.json` supports only the recorded Wake 3b developmental observations for its bound implementation and data. It motivates the new prospective rule; it is not evidence for the new rule's outcomes. The new plan explicitly classifies all ten Books works and both TICO files as exposed development diagnostics. Consequently:

- Any future Wake 4 result on those assets can support only a developmental, dataset/implementation-specific statement about token counts and the stated aggregate Gini objectives.
- It cannot support unexposed confirmation, source/author-level generalization, third-language robustness, downstream task quality, global compression optimality, or a general fairness claim.
- The file label `tico.confirm` in the prior summary does not make that split independent confirmation under the Wake 4 exposure statement.
- Mean book comparisons require their actual denominators, paired work identity, uncertainty policy, complete run inventory, and native-scoring evidence before inferential wording. Point summaries alone do not establish a population effect.
- A successful run plus the internal checks would establish only selected-step gain consistency and final token-total consistency for the executed bytes. It would not establish scientific effectiveness or validate the broader prediction.

The plan's own decision boundary is appropriate: even favorable exposed-development results would retain this only as an efficiency-aware candidate and would still require truly unexposed confirmation and the proposed language extension. Until such evidence exists, the primary prediction remains a prospective falsifiable hypothesis, not a supported claim.
