# PA-BPE continuous research — Wake 6 report

## Outcome

This window tested one bounded, exposed-data question: can the previously observed loss of PA-BPE fairness gain from TICO dev100 to Books be descriptively separated into changed baseline-row composition versus changed within-group method contrast?

For every existing non-Classical arm, the analysis froze Classical baseline gap sign and Classical baseline total-token length strata, then decomposed the Books-minus-TICO mean shift in row-level outcomes. The exact TICO-reference identity was checked for macro-row Gini gain, absolute-gap reduction, total-cost delta and worst-language-cost delta. This is an arithmetic standardization, not a causal decomposition.

For `full_minmax`, macro-row Gini gain was 0.01287954 on TICO and 0.00017125 on Books, a shift of -0.01270829. The allocation was incompatible across two reasonable frozen partitions:

| Partition | Composition contribution | Within-group residual |
|---|---:|---:|
| Classical baseline gap sign | -0.01771397 | +0.00500568 |
| Classical baseline length | -0.00047491 | -0.01223338 |

The same pattern held broadly across arms: for 14/15 contrasts the sign partition gave the composition term larger absolute magnitude, while for 15/15 the length partition gave the conditional residual larger absolute magnitude. For the pre-specified `full_minmax`, `eff_minmax`, and `exact_train` arms, the total-shift signs and the main opposing sign-partition pattern survived all six Books leave-one-author-block-out calculations.

This is a useful negative result. The total cross-domain degradation is present in the frozen samples, but the apparent attribution depends on the conditioning partition and therefore does not identify a unique mechanism. In particular, it would be wrong to conclude either that changed gap-sign proportions are the main cause or that changed within-length response is the main cause.

The descriptive sign association is still concrete. Classical TICO rows were 11% positive-gap, 4% zero-gap and 85% negative-gap, versus 51.8%, 6.6% and 41.6% across Books rows. `full_minmax` had positive TICO mean Gini gain only in the negative-gap group, while Books conditional gains were much smaller. This exposes where the sample arithmetic changes, but it does not privilege sign over length or omitted domain features.

## Joint-support stop rule

A separately frozen support-only diagnostic checked whether a joint sign-by-length refinement was even estimable before looking at joint outcome means. It was not: the 3-by-4 table contained one Books-positive/TICO-empty cell (`zero`, `q4`: 0 TICO versus 25 Books rows), and its minimum nonzero TICO cell contained one row. A coarse 2-by-2 table had no empty cells but its smallest TICO cell contained four rows. No joint outcome decomposition was run, because nonempty coarse cells would neither stabilize the estimates nor recover causal identification.

## Verification, execution and scope

- Coverage: 15 arm contrasts; 100 aligned TICO rows and 10 Books works × 512 aligned rows; six Books author blocks.
- The independent verifier performed 2,342 coverage, identity, leave-one-author ledger and prior-metric checks; all passed.
- Independent read-only mathematical review accepted the arithmetic protocol only with support-aware, reference-labelled, non-causal interpretation. It explicitly rejected categorical mechanism and method-selection rules.
- Three serial scientific attempts all exited 0. Measured scientific wall was 7.344077 seconds, reservation zero, and peak RSS 51,249,152 bytes.
- The empty writer-lock directory found on restoration had no owner or live project process and was replaced with explicit ownership. After all receipts were terminal, the idle supervisor was deliberately interrupted; its retained identity is consequently reported as lost, but no scientific attempt is unresolved.

All evidence remains deterministic, correlated, exposed English–French development diagnostics. It is not independent confirmation, general multilingual evidence, causal identification or reproduction of the original paper.

## Decision

Retain the partition-dependence result and do not choose another tokenizer from the exposed Books/TICO outcomes. The next scientifically useful step is data expansion rather than a finer retrospective partition: restore a substantially larger genuinely unexposed author/domain set and provenance-complete third-language training source, prospectively freeze support thresholds and separate development from confirmation, then test one sign-robust/no-harm candidate. Until those assets exist, a candidate motivated by the sign pattern is a hypothesis only, not an accepted method revision.
