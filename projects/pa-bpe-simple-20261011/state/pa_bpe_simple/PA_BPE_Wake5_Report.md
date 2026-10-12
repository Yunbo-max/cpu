# PA-BPE continuous research — Wake 5 report

## Outcome

This window tested a specific mechanism hypothesis on the already-exposed English–French evidence: whether PA-BPE's development-domain aggregate Gini gains are merely signed sentence-gap cancellation that fails to improve aligned-row fairness. The strict version of that hypothesis was **not supported**.

For aligned pair costs \((a_i,b_i)\), the audit independently computed

\[
G_{agg}=\frac{|\sum_i(a_i-b_i)|}{2\sum_i(a_i+b_i)},\qquad
G_{mass}=\frac{\sum_i|a_i-b_i|}{2\sum_i(a_i+b_i)}.
\]

The exact identity is \(G_{agg}=G_{mass}-C\), where \(C\) is signed-gap cancellation load. The predeclared mismatch condition was a lower aggregate Gini but a non-lower mass-weighted row Gini versus Classical.

Across all 15 existing alternative arms on TICO dev100, **zero** met that mismatch condition. For `full_minmax`, aggregate Gini fell from 0.03115302 to 0, but mass-weighted row Gini also fell from 0.03393809 to 0.01977180 (delta -0.01416629), and macro-row Gini fell by 0.01287954. Its cancellation fraction did become 1.0, so aggregate zero still hides nonzero row imbalance; however, the aggregate gain was not purely cancellation.

The failure is therefore better localized as domain transfer/cost instability. Within the 16 related arms, TICO aggregate-vs-row ranks were strongly aligned (Spearman 0.95), while TICO aggregate versus Books macro aggregate was -0.2441 and versus Books macro row Gini was -0.0294. `full_minmax` improved TICO mass-weighted row Gini but worsened Books macro aggregate Gini by 0.00093072 and total cost by 3.35176 tokens/pair; its Books mass-weighted row Gini improved only 0.00017800. No alternative met the earlier simple rule of improving Books row fairness/absolute gap without increasing total cost.

The exact all-arm audit also found zero stable Books cancellation-mismatch arms and zero stable Books aligned-improvement arms under leave-one-author-block-out checks. This rules out choosing a sentence-level candidate merely because aggregate Gini mathematically permits cancellation. It does not prove why domain transfer fails.

## Verification and scope

- 16 arms, 100 TICO dev pairs per arm, 10 Books works × 512 pairs per arm.
- First diagnostic independently checked 871 stored arithmetic fields; all passed.
- Exact mass audit checked 343 available stored fields; all passed. Nine legacy TICO macro-row fields were absent and were recomputed from integer `paired_costs` without claiming a stored comparator.
- Independent read-only mathematical review was accepted. It supplied the exact decomposition, author-block stability rule and interpretation limits.
- All Books/TICO observations remain exposed development diagnostics. Arms are deterministic and correlated; rank correlations are descriptive, not p-values. No causal, general multilingual, confirmation, or original-paper reproduction claim is made.

## Execution and incidents

Three serial scientific attempts consumed 2.917685 seconds of runner-accounted wall time with zero remaining reservation: two succeeded and one failed. The failed 0.265376-second attempt assumed every legacy TICO record stored `mean_sentence_gini`; it exited 1 before declared outputs. The repaired attempt only compared optional stored fields when present and still recomputed every metric from raw aligned integer costs. Successful peak RSS was 34,164,736 bytes; failed-attempt RSS was unavailable.

The runner CLI also recorded one wrong relative submit path before any attempt. The intermittent host `rg` loader fault recurred; process verification used `ps` plus `awk`. After all attempts were terminal, the idle supervisor was deliberately interrupted; runner status is `awaiting_decision`, reservation is zero, and no wake5 scientific process remains.

## Decision

Retain the negative result. Do not train or select a sentence-objective method from the exposed Books/TICO evidence. The next bounded diagnostic should test domain covariate/conditional shift—especially whether method gains depend on baseline signed-gap direction and sentence-cost strata—using frozen paired costs without tuning. In parallel, continue restoring genuinely unexposed author/domain confirmation assets and a provenance-complete third-language training source before broader conclusions.
