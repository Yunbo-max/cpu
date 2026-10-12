# Wake16 independent development review

Assignment: `wake16-dev-evaluator-review`; goal version 1; idea `pa-bpe-domain-robustness`, revision 1. Reviewer performed only source/document inspection and input SHA-256 verification. No experiment, raw confirmation access, or child delegation. All four assignment input digests match. This reviews the pinned versions, not later amendments or training results.

## Verdict

The v3 970-row trilingual TICO development construction is suitable for the declared exploratory comparison. No claim-invalidating alignment issue was found. It joins unique string IDs, requires exact source URLs and English equivalence after only ASCII boundary whitespace trimming, checks native language labels including `es-419`, preserves translation strings, and rejects the single non-equivalent apostrophe row. The v3 amendment preceded the proposed 1000-merge outcomes. It does not establish untouched confirmation or generalization.

## Actionable findings

1. **Bind the actual preparation input to v3.** Pinned `scripts/train.py` reads `output/tico.trilingual.dev.json`, whereas the reviewed builder writes `output/v3_tico.trilingual.dev.json`. Before preparation, patch the path or preserve an explicit copy/hash receipt proving that the unversioned path equals v3 SHA-256 `fa3b4953e5bb696d0ef1e3a975e94db00c85e1cc63bcc2652443e7aeb3b1e12b`. Otherwise a stale v1/v2 file could silently train a different development objective.

2. **Keep the split license description.** The included official README releases translations under CC0. The retained English sources include public, CC BY 4.0, CC BY-SA 2.5, and CC BY-SA 3.0 labels. The builder preserves source URLs, row licenses, translator IDs, and raw TSVs, which supports provenance. Do not describe the entire trilingual derivative as CC0; preserve these attributions and applicable source licenses with redistribution. This is an artifact-description constraint, not a demand for another experiment.

3. **Do not replace the promised realized-vocabulary check with merge-line count.** The training wrapper checks 1000 merge records, but does not yet verify unique merged symbol strings plus the common initial alphabet or effective vocabulary. The protocol already promises this check. Report merge count and actual vocabulary separately before an equal-vocabulary comparison claim.

## Comparison and metric interpretation

- Classical pooled 100k pretoken occurrences per language is a valid simple balanced-data baseline, and all five arms use the same bounded training payload. It does not measure an unbalanced-vs-balanced intervention because no unbalanced arm is present. The convenience training frame limits population claims.
- Native base/window/hybrid use aligned development costs; ratio(1,1,1) instead balances relative training compression. It is a distinct objective and should not be described as enforcing equal sentence token costs. The pinned CLI arguments select the intended native variants; hybrid uses the first 500 global merges.
- For n paired rows and L=3 languages with costs c[i,l], define mean language costs m[l]=sum_i c[i,l]/n and Gini G(m)=sum_(l,k)|m[l]-m[k]|/(2 L sum_l m[l]). Mean per-sentence Gini is a separate statistic, mean_i G(c[i,:]); it need not agree with G(m). Report both, plus max_l m[l], sum_l m[l], language identities, and paired cost arrays. Zero-cost rows require an explicit convention or failure, not division by zero.
- Independent tokenization/count implementation was not in the assigned read scope, so evaluator correctness is not certified here. Native internal length tracking alone must not substitute for final token counts on paired sentences. All current TICO outcomes remain development results because English/French outcomes were already exposed; GlobalVoices remains sealed.

Proceed after the concrete input-path binding; the remaining items are existing output checks and claim boundaries, not new qualification gates.

## Authorized follow-up: input-path issue resolved

The coordinator expanded read scope to `scripts/train_v3.py` and `training_plan.json`. The reviewed replacement explicitly reads `output/v3_tico.trilingual.dev.json`, writes `v3_dev.*.dict` and `v3_pooled.dict`, and passes only these dictionaries to the native CLIs. Its SHA-256 is `0173874ddfdee5181d8e4f9bdc5f19e0ee70e904bc1dcb14732b0494eb63a0df`, matching each task's input reference in `training_plan.json`. That plan also pins the three training dictionaries, three prepared development dictionaries, pooled dictionary, preparation receipt, protocol and author sources. Finding 1 is resolved for these planned commands. No training output or fairness result was opened during this follow-up. Remaining vocabulary/evaluation and licensing descriptions are unchanged.
