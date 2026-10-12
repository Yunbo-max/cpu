# Wake 3 pair-gain review

Binding: delegation `wake3-pair-gain-review`, generation 1; project `pa-bpe-simple-20261011`; goal contract 2; idea `pa-bpe-domain-robustness`, revision 1, method revision 2; declared parent source digest `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`. I am the **same exposed reviewer** as the preprocessing audit, not a fresh-confirmation evaluator. Read-only source inspection, hashing, and analytic reasoning only; no training, scoring, numerical diagnostics, or delegation. Only this report was written.

## Bound input identity

All five SHA-256 values independently matched `review/wake3_pair_gain_assignment.json`:

| Input, relative to `execution_windows/wake3/` | SHA-256 |
|---|---|
| `scripts/train_pair_aware.py` | `ebb7b70bd4a1332dad35c43a0411fa2de09ec1d0ecb05abb31462ce855dfcc49` |
| `pair_candidate_plan.json` | `6a64ace4fc6a06dc390ef3289727b83b2aa25e805530f0f0b9be617a29446a11` |
| `output/merge_descent_audit.json` | `c13c05c9a06b371ac494728262b38c7c1dee2715dd520b3a0b620d089575cfff` |
| `output/multibook_analysis.json` | `b65764559c4e6efe60c13567ffdb607611fbdadc0e8edba1cca2b340d063e11c` |
| `output/paired_raw_rescore.json` | `5846a385ad344ebdd84bc7c96616af39ccb8658290aca649c2ca5d3eb1a47a94` |

Supplementary code reads: `scripts/native_pa_source.py`, `scripts/evaluator_reference.py`, and `scripts/audit_merge_descent.py` within that window. They were inspected but are not separately pinned by this assignment. Parent digest was not recomputed. No in-progress candidate/control output is assessed here.

## Derivation and selector logic

For positive costs a > b and compression gains x,y with positive post-merge costs and no order crossing, define S=a+b. Then

\[
G(a,b)=\frac{a-b}{2S},\qquad
G(a-x,b-y)-G(a,b)=\frac{ay-bx}{S(S-x-y)}.
\]

Therefore strict Gini descent holds **iff bx > ay**, equivalently x/a > y/b. Merely selecting the currently costlier language, or obtaining x>y, is insufficient. If ordering crosses, the signed derivation no longer applies; use the exact absolute-value comparison

\[
\frac{|a-b-x+y|}{S-x-y}<\frac{a-b}{S}.
\]

At a=b, strict descent is impossible because Gini is already zero. For maximum-domain Gini, improving the formerly worst domain is also insufficient: every post-merge domain Gini must be below the old maximum. `objective` at lines 27–30 recomputes absolute Gini for both domains and takes their maximum, so it handles crossings, changed worst domains, and ties directly.

**No concrete defect found in the new development-gain calculation by inspection.** `gains` at lines 32–42 uses adjacency statistics for unequal symbols. Two occurrences of the same unequal pair cannot overlap: overlapping occurrences would require its first and second symbols to be equal. For (A,A), adjacency counts overcount runs; the explicit left-to-right scan consumes two symbols per occurrence, producing floor(run length/2), matching nonoverlapping replacement. Frequency vectors weight the four development slices. Native `get_pair_statistics`, lines 323–344, counts adjacency occurrences; `replace_pair`, lines 349–379, performs nonoverlapping substitutions; this distinction justifies the special case.

Selected gain is checked against actual length reduction at lines 62–66, followed by final totals from a separately constructed tokenizer at lines 72–74. These are appropriate acceptance checks when completed successfully. They do not independently verify every *unselected* candidate's statistic or establish mathematical global optimality; the correctness argument additionally relies on native statistics updates. Final total agreement is weaker than token-string agreement, although totals are the objective here.

## Top-K, fallback, and comparison fairness

- Lines 45–49 implement the planned pool: total train adjacency frequency at least two, a novel concatenated symbol, global frequency winner, and four winners per language. The maximum pool size is nine before overlaps. Repeated-symbol **training** frequencies remain overlapping adjacency counts, so “top frequency” is not “greatest realizable compression.” This follows the stated frequency-pool design and does not invalidate exact development gain; it can affect coverage and fallback efficiency.
- Lines 54–59 select the lowest resulting objective among pool moves descending by more than 1e-12; ties favor greater total training frequency and then lexicographically larger pairs. The plan should specify the lexicographic direction for reproduction. No descending move *in this pool* does not imply none exists globally. Fallback selects the global frequency winner and can increase, preserve, or slightly decrease the objective within the tolerance. Accordingly neither monotone descent nor a global minimax guarantee is supported.
- Candidate and pooled control use the same inputs, pool construction, gain computation, vocabulary restriction, and fallback rule; only objective aggregation changes. After their trajectories diverge, actual vocabularies and candidate pools naturally differ. Describe them as sharing a pool-construction rule, not literally the same pair pool at every step. This is a reasonable diagnostic control for the complete policy difference, not a fixed-state causal isolation of one merge decision.
- Pooled mode sums domain token totals before computing Gini (line 29). It consequently weights domains by their token mass and any difference in sample size; it is not a macro-average of domain Ginis. Keep that distinction in interpretation. Minimax mode imposes no explicit efficiency constraint: a tiny parity improvement can be preferred to much greater compression. Both modes can sacrifice held-out cost performance despite exact objective calculations.
- `classical` remains useful as a simple frequency comparator, but comparisons with it alter objective and selection machinery together. Stronger mechanism attribution would require a separate controlled study, not a novelty or causality inference from these runs.

## What completed measurements establish

The bound replay records `robust_domain` with **345 strict maximum-Gini increases**, 463 decreases, and 192 unchanged steps. Thus 345/1000 must not be called the total number of “non-descent steps”: counting ties too gives 537. The source uses a 1e-12 tolerance (`audit_merge_descent.py`, line 42). The replay also records 206 increases in the selected domain, so maximum-objective increases and selected-domain increases are different events. Final tokenizer totals agree. These observations refute a per-step descent interpretation of the old proxy trajectory; they do not show that every increase was avoidable, that avoiding it improves the final objective, or that it caused transfer failure.

The ten-work JSON reports old `robust_domain` versus `classical`: higher mean book Gini (0.0182759 versus 0.0124922), Gini worse in eight works and better in two, worst-cost mean difference +1.6140625, and total-cost mean difference +1.6134765625 with all ten total-cost differences positive. Its Gini sensitivity interval crosses zero. These copied measurements constitute adverse descriptive transfer evidence on this observed set. Repeated authors and incomplete exposure mapping are explicitly acknowledged; they do not permit population-calibrated uncertainty or pristine-confirmation claims. Mean book Gini must not be replaced by Gini of pooled/macro language means, which can conceal opposing signed gaps.

The same-ID raw rescore materially narrows the earlier preprocessing concern: many text strings change, yet `robust_domain` changes cost pairs in only 9 dev rows and 15 confirm rows; its reported Gini shifts are approximately -0.0000081 and -0.0000160. The `robust_domain`/`classical` Gini ordering remains different across the two works: classical is better on dev, robust_domain on confirm. Thus these supplied results support local stability of that comparison under the raw-text repair, not preprocessing invariance on every row or for every tokenizer. They do not establish a cause of the ten-work result.

## Acceptable next conclusion

Direct pair-gain lookahead is a justified **diagnostic adaptation** to an observed mismatch between proxy selection and its stated development objective. It is neither demonstrated new science nor an established repair for generalization. Accept candidate/control runs only after the planned gain, final-total, realized-vocabulary, and resource checks complete. Report development trajectories and fallback behavior beside per-work raw token-cost parity and efficiency. If development improves while transfer or costs worsen, retain that negative result. The existing plan correctly requires unexposed confirmation before superiority claims; this report supplies no such confirmation.
