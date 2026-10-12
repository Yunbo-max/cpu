# Wake 1 independent candidate review

Completed 2026-10-11. Goal contract v1; idea `pa-bpe-domain-robustness`; revision 1; design `domain-selector-pilot-v2`. This is static code/protocol review, not experimental validation. No candidate training or evaluation was executed by the reviewer. Only this review file was written.

## Exact reviewed binding

Root: `/workspace/scratch/42f1128b703b/pa_bpe_simple`.

| File | Observed SHA256 |
|---|---|
| `experiment_plan_v2.json` | `913e67b88ad4c16159a5c92e725f26a9131079e1cc2ba96b52edd4f89856ab15` |
| `scripts/train_robust.py` | `1a37f8d43000bb8a79739b479f8f69dd4cac81d366d8fe0cb3523132b704d39d` |
| `scripts/prepare_candidate.py` | `926a37d6f3d8433f65f58818cefa53fbbc9217e19075e571d06c268458760d00` |
| `scripts/evaluate_candidate.py` | `2c1e9a60ea5db489a557d305a12059e14713de3be1a1e96b976cbfb37d200d6e` |

Inherited native source reference: `author_source/parity_aware_bpe/parity_aware_learn_bpe.py`, commit supplied by coordinator `c7395d469a653f3e48e80984e37593256ff8f365`, SHA256 independently checked in the first audit: `5ee04ceaeba0c9958f313e9303398fbcc0c962a0323b80a96d87637e200c0ab5`. Imported scorer reference from second audit: `scripts/evaluate_pilot.py`, SHA256 `612d66ff544e6cb72047d59f36e702766061abcc10e387453e3356ec231651eb`. Those dependencies should remain pinned in actual task input refs. This review did not read resulting candidate outputs or independently certify their runtime state.

## Verdict: no static dimension blocker in the submitted candidate path

The four development files are passed in order TICO-English, TICO-French, Books-English, Books-French (`train_robust.py:18–19`). Native preprocessing allocates training frequency/statistics arrays from the TWO training corpora (`native:509–521,531–550`), while it independently allocates development vocabulary frequencies from FOUR dev corpora (`native:498–508,523–529`) and sums a four-entry lengths vector (`552–555`).

The modified base selector reshapes those four entries to 2x2 and selects a domain and LANGUAGE COLUMN (`train_robust.py:11–14`). The language column is 0 or 1, so the following unchanged native `stats[pair][max_index]` lookup is valid (`native:628`). Native development replacement (`398–430`) constructs its delta using `len(freq)`, which is four for development entries, or returns scalar zero for a no-op; either can be subtracted from four-entry lengths (`657–658`). Training pair replacement/statistic updates operate on the separate two-entry training frequencies (`651,660`). Threshold refresh is over `array_length=2` (`638–640`). No implicit dev=training dimension requirement appears in this executed base/no-ratio/no-global path.

Calling the learner directly bypasses the CLI's train/dev file-count assertion, intentionally. This does not make the general CLI accept four dev files; it is an explicitly adapted candidate implementation. The adaptation changes exactly one matched selector text, asserted at `train_robust.py:13`, while preserving native pair choice and updates. The source emitted at `runs/robust_domain_source.py` provides a useful audit artifact and should be hashed in acceptance.

The conclusion applies ONLY to this specified path. Native ratio/global/window variants retain their original array assumptions and must not be composed with the four-dev adaptation without a new review.

## Mathematics and mechanism scope

For two nonnegative costs a,b with a+b>0, population Gini is `|a-b|/[2(a+b)]`. Maximum within-domain relative cost is `2*max(a,b)/(a+b) = 1 + |a-b|/(a+b) = 1+2G`. Therefore argmax across all four normalized entries first identifies a domain with maximum development Gini, then its expensive language. The implementation's `numpy.argmax` chooses first flattened index on ties: TICO before Books and English before French. Record this deterministic convention; it is not random tie balancing.

Each domain uses TOTAL development token counts rather than explicit means. Because each domain has the same paired rows in its two languages, its shared row count cancels during within-domain normalization. Equal counts ACROSS domains are not required for this mathematical identity, but are part of the declared information-budget and matched-pooling control. Native training's chosen highest-frequency pair can have zero effect on the worst development domain or alter its relative costs unfavorably; no greedy minimax or Gini-descent guarantee follows. The plan and source correctly disclaim such a guarantee.

The observed v1 ordering reversal motivates a hypothesis, not proof that the selector caused transfer loss. Corpus composition, pretoken boundaries, and ratio calibration are competing mechanisms. Novelty is explicitly unassessed.

## Controls, leakage, and acceptance findings

1. **Matched pooled control is well specified at preparation.** `prepare_candidate.py:31–32` writes candidate domains and pooled control from the same `dev + books['dev']` objects, with consistent stripped strings. Candidate and pooled therefore have matched text information if the declared pooled training command consumes these exact files. The pooled training invocation itself was not among the inspected files and is not certified here. Comparison against pooled, rather than only original TICO-only base, is necessary and correctly appears in the decision rule.

2. **Fresh confirmation needs a stronger exposure audit.** TICO confirmation is next hash-ranked official test rows (`14–16`), after the 200 exposed v1 rows. Books IDs are acquired at the declared offset and checked disjoint from new Books dev (`33`). However, `19–27` excludes exact content overlap with NEW development and training only. It does not exclude content duplicates of previously scored `tico.test.json` and `books.pilot.json`, or all 200 original TICO dev rows consumed by old arms. Different IDs do not by themselves ensure unexposed text. No actual overlap was demonstrated in this static review. Before calling confirmation text unexposed, coordinator should audit exact normalized strings against all previously exposed partitions, preserve results, and label any overlap transparently. If outcomes are already scored, do not silently redefine the confirmation split.

3. **The overlap filter is conservative but not semantic deduplication.** `23` checks whether a whole stripped confirmation string is a substring of raw training text, not whether it equals a training document. It can exclude short common strings and change the evaluation population. The plan's phrase 'exact overlap' should specify this substring rule. It does not normalize internal whitespace, case, or Unicode equivalence; remaining duplicates/near-duplicates may survive. Excluded IDs and counts are preserved, which permits audit. Paired rows are removed if either language overlaps, correctly preserving bilingual alignment.

4. **Development validity is not fully asserted.** Books evidence checks truncation (`12`) but not exactly 100 rows, unique IDs, required en/fr keys, or nonempty text. Candidate division requires positive finite within-domain means. Confirmation is only checked to retain at least 90 rows (`28`). Frozen manifest and source data acceptance should establish the declared 100+100 dev composition and valid texts before interpreting the run; no actual invalid text was found by this static inspection. Fewer retained confirmation rows are legitimate if documented, and need not be equal across domains for domain-specific mean-cost Gini.

5. **Evaluation inventory and target sizes are now explicit.** `evaluate_candidate.py:5–11` requires the exact nine arms, 1000 merges and 1256 unique vocabulary entries each, and validates all v2 manifest hashes. This addresses the main evaluator-level acceptance gap from v1. Imported v1 evaluator source, native source, actual merge files and training files also need to remain bound by task/acceptance receipts, as the coordinator reported for v1.

6. **Scoring preserves paired data and the correct primary metric.** `14–22` calculates mean costs over paired rows, verifies pairwise-versus-sorted Gini, and reports worst cost and sum of language means. Replay checks first three rows in each of four splits and two languages: at most 24 texts per arm, assuming at least three rows per split. This is a sampled merge-engine check, not exhaustive equivalence. `checks()` independently supplies analytical metric checks. All runtime assertions require optimization disabled.

7. **Decision scope remains narrow.** Lower maximum confirmation-domain Gini relative to pooled can support the predeclared local inequality objective, while increased token costs or degraded individual domains remain material trade-offs. No significance or independent-book claim is justified from these slices. Source/title overlap between Books development and confirmation is explicitly acknowledged; unused record offsets are not independent books. Comparing nine arms on the same confirmation set exposes that set for all future candidate selection.

## Concrete next action

Retain the unchanged frozen source and let the authorized coordinator own execution. Before accepting candidate results, verify development counts/text validity and exact pooled inputs; bind generated candidate source and all output hashes; inspect runtime completion and scorer assertions; record exposure-overlap findings against v1 partitions without silently changing already-scored data. Report candidate versus pooled on both domains, the maximum Gini, per-language means, worst cost and total-cost trade-offs, and retain either outcome. Wider language/domain coverage and independent books remain required before a robustness claim.

No runtime failure, actual overlap, or scientific improvement was observed or established by this review. Model usage/cost remains unavailable.
