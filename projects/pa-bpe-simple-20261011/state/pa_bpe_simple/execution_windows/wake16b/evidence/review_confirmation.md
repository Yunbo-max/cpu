# Wake16 confirmation evaluator independent review, generation 2

Assignment `wake16-confirmation-evaluator-review-g2`, goal version 1, idea revision 1. This review used the explicitly permitted evaluator sources, frozen plan, summary/count results and prior arithmetic audit. No new experiments, no raw text access, no delegation. All four frozen input SHA-256 digests match the assignment. Native model usage is unknown.

## Verdict

No claim-invalidating error was found in the reviewed scoring or paired cluster-bootstrap source. This is source/record review, not an independent re-execution or audit of the previously reviewed XML alignment helpers.

- The evaluator uses the declared Whitespace then ByteLevel preprocessing, a common complete 256-byte alphabet, and the frozen 1000-merge codes. It asserts merged-symbol dependencies and equal actual vocabulary size; all five recorded outputs have 1256 vocabulary entries. Token strings agree with a separate merge replay for 12 declared fixtures per arm. These fixtures are useful cross-checks, not exhaustive tokenization equivalence proof.
- Gini is correctly computed as the ordered absolute-difference sum divided by `2 * L * sum(costs)`. The independent sorted formula and known-value fixtures are appropriate. Gini of language mean costs and mean per-unit Gini are reported separately. Worst mean and summed language means use the same aligned rows. Positive-cost assertions exclude undefined zero denominators.
- The cluster bootstrap resamples 267 English-document clusters, preserves all selected units within each sampled cluster, and uses identical draws across methods. Dividing aggregated costs by the sampled unit count gives the declared sentence/unit-weighted mean. Gini is scale invariant, so computing it on language totals before this division is equivalent; the denominator `6 * total` is correct for three languages. The 1000 paired percentile replicates provide descriptive one-domain uncertainty, not broad domain-generalization uncertainty or simultaneous guarantees across arms.
- Confirmation code checks the frozen unit-manifest hash, native archive hashes, reconstructed unit identities and each model-code hash. The plan identifies window as primary based on development Gini and all other methods as secondary before confirmation. This review did not independently certify chronological sealing, but found the source/plan/result identities consistent with the stated freeze.

## Required interpretation of the recorded results

The primary window arm has confirmation Gini gain 0.0030303 versus classical, with paired cluster-bootstrap 95% interval [-0.0065397, 0.0097976]. Thus the positive point estimate alone does not establish a reliable retained fairness benefit in this sample. Total token cost rises 3.6965% and worst-language mean cost rises 4.8853%; the worst language changes from French to English. These costs must accompany the fairness claim.

Its confirmation/development absolute-Gini-gain ratio is 0.07179. Call this a descriptive 7.18% point-estimate retention of the development absolute Gini gain, not a confidence bound or proof that exactly 92.82% of a population effect vanished. Relative improvement against the domain-specific classical baseline is a different quantity.

The predeclared secondary hybrid arm has gain 0.0202501 and paired interval [0.0108378, 0.0245752], with total cost +1.7404% and worst mean cost -2.1452%. This supports a scoped secondary observation and a future mechanism hypothesis. It must not replace the frozen primary after seeing confirmation outcomes. Any later tuning informed by these outcomes makes this GlobalVoices set development evidence for that later candidate.

One output field needs careful labeling: ratio has negative development gain and negative confirmation gain. Its `gain_retention_vs_dev = 1.42698` is mathematically the ratio of two adverse effects; it is not a retained positive benefit of 142.7%. Retain the raw field for provenance but omit that interpretation or label it an adverse-effect ratio. No change to the primary result or rerun is needed.

The results answer a bounded three-language, one-held-out-domain question. Convenience training, possible semantic overlap despite exact/shingle/URL screening, and conditional French/Spanish source proof remain the existing limitations. No extra qualification gate is proposed.
