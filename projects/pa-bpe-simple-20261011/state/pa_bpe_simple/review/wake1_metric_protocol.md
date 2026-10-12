# PA-BPE wake 1: independent metric and protocol audit

Status: completed read-only source/protocol review, 2026-10-11. This is not scientific validation. No experiments, dependency installation, data acquisition, runner mutation, or nested delegation were performed. Only this review file was written. Model token/cost usage is unavailable, not zero.

## Exact assignment binding

```json
{
  "request_id": "pa-bpe-wake1",
  "delegation_id": "metric_protocol_audit",
  "generation": 1,
  "goal_contract_version": 1,
  "idea_id": "pa-bpe-domain-robustness",
  "idea_revision": 1,
  "source_digest": null,
  "checkpoint_ref": {
    "path": "/workspace/scratch/42f1128b703b/pa_bpe_simple/PA_BPE_Simple_Checkpoint.md",
    "sha256": "4b5a0b6e608fd866daa58250c47bc647520a50908bcc5be63d6b870db1bd3f1a"
  },
  "plan_ref": null,
  "input_refs": [{
    "path": "author_source/parity_aware_bpe/parity_aware_learn_bpe.py",
    "sha256": "5ee04ceaeba0c9958f313e9303398fbcc0c962a0323b80a96d87637e200c0ab5"
  }],
  "not_applicable_reasons": {
    "runner": "not initialized; Simple .9 policy, bootstrap checkpoint is active plan"
  }
}
```

Checkpoint and assigned input hashes independently matched the binding. Author commit supplied by the coordinator: `c7395d469a653f3e48e80984e37593256ff8f365`; this audit independently hashed the restored files, but did not redo the coordinator's Git blob verification. All code locations below are relative to `author_source/` at this pin.

| Inspected source | SHA256 |
|---|---|
| `parity_aware_bpe/parity_aware_learn_bpe.py` | `5ee04ceaeba0c9958f313e9303398fbcc0c962a0323b80a96d87637e200c0ab5` |
| `parity_aware_bpe/learn_bpe.py` | `f24dfe59d37d03a84e3721ad37f6f2dd20685af1da3078cfd5ff0465f5d47d35` |
| `parity_aware_bpe/HF_tokenizer.py` | `b76fa043107be1b6aa40a8befc1bef93c509d9fd6451a8cd36bef9c8ab2e5a91` |
| `README.md` | `feb9bbfe19ee4ced06b2b29e3d66f2e454f9bfe6497511cc456b42e926ee0855` |
| `pyproject.toml` | `7827502b1ccab6b7f888ab6daee244e3b966dd0a2c179e322234370bde21eb6e` |

## Independently derived metric reference

Fix a domain, L languages, and N semantic units with the same aligned IDs in every language. Let t[s,l] be the tokenizer's token count for translation l of unit s, with an explicit, identical convention for special tokens, normalization, preprocessing, and boundaries. Define c[l] = sum_s t[s,l] / N. Every language has weight 1/L regardless of its training-corpus size.

Define the population Gini of these language costs by

`G = sum_l sum_k abs(c[l] - c[k]) / (2 * L * sum_l c[l])`.

An independently implementable equivalent is `sum_{l<k} abs(c[l]-c[k]) / (L * sum_l c[l])`. For sorted ascending costs c_(i), each cost contributes positively in i-1 unordered comparisons and negatively in L-i, giving coefficient 2i-L-1. Consequently:

`G = sum_i (2*i - L - 1)*c_(i) / (L*sum_i c_(i))`.

This derivation does not require a library Gini implementation. For equal N, totals T[l] can replace means because the shared factor N cancels; this does NOT license using totals on nonparallel corpora. Unequal-N means do not repair a missing-content alignment problem. Reject negative/nonfinite costs, absent languages, empty aligned sets, and zero total cost rather than silently returning a scientific score.

Analytic implementation oracles, not benchmark observations: [10,10] gives 0; [10,20] gives 1/6; [1,2,3] gives 2/9; [0,0,3] gives 2/3. Permutations and positive common rescaling leave G unchanged. With fixed L, the maximum is (L-1)/L, not 1; for two languages G = abs(c1-c2)/(2*(c1+c2)) and is at most 1/2. Do not multiply by L/(L-1) when comparing to the paper's uncorrected convention. Do not compute the mean of per-sentence Ginies, or Gini over all individual sentence costs: these are different estimands. Gini of reciprocal costs is generally different for L>2.

Alongside G, retain all c[l], worst language and max_l c[l], macro mean cost, total tokens, and per-language change from Classical BPE. G can improve while all languages become more expensive. Increasing every cost by a fixed special-token overhead lowers G's denominator-normalized inequality even though absolute gaps are unchanged: use zero automatically inserted special tokens for the primary intrinsic score and record this explicitly.

Use paired resampling of aligned semantic IDs across languages AND tokenizer methods when estimating uncertainty. Cluster by document/source where sentences are dependent. Domain A and B need their own aligned sets; do not pool away domain-specific failures. Small samples yield diagnostic uncertainty, not evidence of universal multilingual fairness. Language panels of different sizes should be reported separately.

## Paper check, kept separate from code findings

Primary source inspected: [ACL paper](https://aclanthology.org/2026.acl-long.342.pdf), especially §§4–5 and Appendix B–C. Appendix B Eq. 13 matches the sorted reference above. Its prose describes an upper endpoint of 1; for its formula at finite L the attainable maximum is (L-1)/L. Section 4 motivates aligned development costs while training supplies merge frequencies. Section 5 uses FLORES+ development data and W=100, alpha=2; hybrid uses half global merges. Appendix C.2 appears to conflate window size with a parameter ranging from 1 to L, whereas the stated window ablation is 50–200; use the explicit algorithm and actual code parameters. Domain mismatch is already discussed, so merely observing it would not establish novelty. No results or dataset availability from that paper are asserted for this project.

## Consequential native code findings

1. **Development input is supervised language-selection data, not an evaluation split.** `parity_aware_learn_bpe.py:498–508,523–555` builds per-language development totals, then `623–628` selects the longest development language and its most frequent TRAINING pair; `657–658` updates development costs after every merge. It does not validate alignment, line counts, language order, or disjointness. CLI `854–856` checks only the number of files. Thus paired language order, shared semantic IDs, equal nonempty N, and disjoint confirmation data must be enforced externally. Reading a confirmation set into `--dev` leaks the outcome directly into every merge.

2. **A two-language window comparison with default alpha=2 is structurally inactive.** `668–699,760–786` uses count/W <= alpha/L. Without a global prefix, L=2 gives threshold 1, and no language can exceed it. Window and base therefore use the same selection rule (including first-index ties), so their equality cannot show robustness of balancing. For a useful native window diagnostic use at least three languages, or predeclare alpha=1 as an explicit changed setting for a two-language study. CLI alpha is integer (`112–113`); W must be positive. Code does not enforce sensible alpha/W values. Selection tests the PREVIOUS history before appending, so boundary counts may exceed the nominal limit by one; do not interpret it as an exact hard fraction cap.

3. **Hybrid+window changes the cap denominator.** Setting nonzero `--global-merges` adds a concatenation statistics column (`509–521`), while dev costs still have L elements. `760` divides alpha by `len(threshold)=L+1`, not L. Global steps are not appended to the window (`765–785`). This is a static paper/code discrepancy for the stated alpha/L rule; preserve native behavior for a native result, record it, and label any fix as a separate implementation revision. For two languages hybrid+window may differ even when plain window is inactive.

4. **`--total-symbols` is broken in the PA path.** `preprocess_input_data` has no num_symbols argument (`444`), yet assigns `num_symbols -= ...` at `545`, so that branch raises an unbound-local error. Ordinary BPE's analogous adjustment is inside its learner (`learn_bpe.py:302–312`). Avoid this flag. Use explicit merge count and independently record emitted merges and unique vocabulary size; same requested symbols need not mean same actual vocabulary.

5. **Early stop can selectively reduce PA vocabulary size.** PA `642–644` and `804–806` stop the WHOLE run when the selected language's best pair misses min_frequency, even if another language still has useful pairs. Ordinary BPE stops on a global count (`learn_bpe.py:329–331`). This can confound a small-corpus method comparison. Record actual merge counts, stopping language, and realized vocabulary; compare common reachable merge prefixes or predeclare another size-matching protocol. Do not silently add merges or change frequency thresholds to rescue one arm. Choosing min_frequency=1 alone does not guarantee a language has remaining pairs.

6. **Ratio means relative compression, not equal token totals.** `603–618` initializes training representation lengths and minimizes `(initial_length/current_length)/ratio`. CLI `858–863` normalizes ratios by the first entry, requires same count as input files, and prohibits dev simultaneously, but does not reject zero, negative or nonfinite values. Validate these externally. Under the default pretokenizer, initial lengths are lengths of byte-mapped pretokens, including its prefix-space behavior, not necessarily raw UTF-8 byte counts. A ratio calibrated from raw bytes and one calibrated from actual initialized token counts can diverge. Clearly distinguish equal target ratios from ratios estimated on a permitted calibration corpus.

7. **Ratio with nonzero global prefix is dimensionally incompatible for L>=2.** The global column makes initial/current vectors L+1 (`509–521,603–604` or `757–758`), while the CLI requires L ratios (`860`). Division at `617`/`774` therefore has incompatible shapes after the prefix. Do not schedule this combination as a valid native arm. This is a static deduction, not a runtime reproduction.

8. **Encoding wrapper requires semantic verification before any score.** Training defaults to `Whitespace()` then `ByteLevel(use_regex=False)` (`884–893`); Classical fixes the same sequence at `learn_bpe.py:30–31`. `HF_tokenizer.py:43–52` constructs the backend without a pretokenizer then assigns a `pre_tokenizer` attribute to the Transformers wrapper. This is a strong risk that the backend remains unconfigured; no installed Transformers behavior was executed here, so runtime effect remains unverified. The README's loading example instead sets `tokenizer.pre_tokenizer` on the backend before wrapping, highlighting the inconsistency. Inspect serialized backend configuration and compare counts to a transparent independent merge replay before using the wrapper. The wrapper also imports Transformers (`4`), absent from declared required dependencies. Byte mapping and unknown-token handling must be checked on all selected scripts; a score from dropped/unrepresented Unicode is invalid.

9. **Preprocessing and vocabulary bookkeeping can hide comparisons.** Whitespace pretokens constrain merges and suppress original whitespace distinctions; ByteLevel defaults are not fully specified in source, so record dependency versions and effective configuration. Use matching preprocessing in every arm and label any change as a separate factor. `HF_tokenizer.py:20–33` starts with the byte alphabet and overwrites the entry for an already-seen merged string while incrementing the ID, so requested merges, unique token strings, and ID range may differ. Audit actual unique vocabulary and emitted merges. Do not claim raw-text lossless reconstruction solely from full byte alphabet: preprocessing matters.

10. **Native CLI mapping differs from README examples.** Classical accepts one input file and no dev flag (`learn_bpe.py:50–74`), despite README's Classical command showing dev and plural training files. Concatenate exactly the PA training files with safe document boundaries for the global baseline. PA has only `--variant base|window` in dispatch (`895–900`); hybrid is `--global-merges J`, and ratio is `--ratio ...`, not extra variant names. `--symbols M` is TOTAL merges, including the first J (`606–611,763–768`), so half hybrid is M total and floor(M/2) global, not M+M/2.

11. **Keep to the declared single-worker, no-preload diagnostic.** Multiworker vocabulary paths write/read pickle through text-mode files (`193–210,185–187`; analogous Classical `130–155`), a Python 3 incompatibility. `--num-workers <=0` expands to host CPU count (`846–847`), so use explicit 1. Preload detection tests `version` although output header is `#version:` (`469–475`), which can admit a bogus header pair; base only writes a new header (`598`) whereas window copies preload content (`745–748`). Avoid preload until separately verified. These issues do not require modification to run the intended simple baseline.

Additional mechanism implication: a large dev length can persist because useful training merges never occur in dev. `replace_pair_dict:414–430` then gives zero development gain while training still advances. Record selected-language frequency and dev length changes from verbose logs to distinguish this mismatch from exhausting the pretokenization floor. This is a candidate mechanism, not an observed failure.

## Required controls and concrete next action

Before a scientific run, coordinator should finish legitimate aligned-data acquisition and freeze manifests: source/version/license, exact IDs, language order, domain labels, sample sizes, and split membership. No FLORES access or alternative dataset is assumed here.

Then make encoding and metric semantics reviewable: pairwise-versus-sorted Gini equality on analytic fixtures; independent merge replay versus the chosen backend on a tiny multilingual fixture; serialized pretokenizer inspection; special-token policy; coverage/unknown and actual vocabulary checks. Those are proposed future checks, not experiments executed by this reviewer. They should be recorded as implementation checks distinct from benchmark results.

For the first useful comparison, hold training samples and preprocessing fixed; compare Classical, PA base, valid window, half-global hybrid, and ratio with explicit calibration. Include Classical trained on balanced/resampled language data as a simple strong control with its own precisely stated budget unit (equal documents does not imply equal bytes). If resources only support a subset, report missing controls and restrict conclusions. At least three languages make default window meaningful and avoid overinterpreting a two-language Gini. Preserve the exact same total training-budget policy for each balancing condition.

Use development A to train, with disjoint confirmation A and genuinely different-domain confirmation B. Report improvement I_d = G(Classical,d) - G(PA,d); attenuation is I_A - I_B, with paired uncertainty and cost trade-offs. A+B pooled development is a necessary simple control for a proposed domain-robust selection method, but compare it with the SAME total development-unit budget, e.g. split the A-only budget across A/B. Also swap A/B as development where lawful data support it, keeping merge-frequency training fixed, to separate domain-selection sensitivity from a universally difficult test domain. A matched B-development arm may use B-development only, never B-confirmation. Preserve an untouched confirmation partition after any candidate selection.

No superiority, reproduction, robustness, or novelty conclusion is available from this review. The immediate next action is to validate the scorer/backend and aligned manifest, then run a bounded native calibration with actual-size accounting; do not interpret variant differences until these gates pass. Parent remains the only scheduler and shared-state writer.
