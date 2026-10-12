# Wake 3 preprocessing audit

Binding: `wake3-preprocessing-audit`, generation 1; project `pa-bpe-simple-20261011`; Simple0.3.0-simple.9 (coordinator-supplied); goal contract 2; idea `pa-bpe-domain-robustness`, revision 1; declared parent source digest `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`. This is fresh analytical review of exposed evidence, **not unseen confirmation**. No training, scoring, numerical diagnostics, or delegation was performed. Only this report was written.

## Identity verification

All five assignment inputs were read and independently SHA-256 checked against `review/wake3_preprocessing_assignment.json`; all matched. Paths below are relative to the project root.

| Input | Verified SHA-256 |
|---|---|
| `scripts/evaluate_pilot.py` | `612d66ff544e6cb72047d59f36e702766061abcc10e387453e3356ec231651eb` |
| `execution_windows/wake2/scripts/opus_selective_extract_wake2.py` | `63d956583e1b7926ae2675665505ab9062d15a4588d98dbf595306f1021c1040` |
| `execution_windows/wake2/output/opus_selective_extract/raw_xml/dev.en.xml` | `5f529f2e476bca967273b192930bb6321272a771593792f3f0612aac306d4b56` |
| `execution_windows/wake2/output/opus_selective_extract/raw_xml/dev.fr.xml` | `ca8c291e1ccef8f58ba9b14a35fc77dfae8b450f18458bed0ee0c3f35cf11cc2` |
| `execution_windows/wake2/output/grouped_books_evaluation_wake2_v2.json` | `b3ed10c45e50107adbfd730c25a5b262c5e3574266a6c6ee0899fa52bac29140` |

Additional source/code reads below were contextual inspection, not assignment-hash-bound inputs. The parent source digest/version were not independently recomputed or established.

## Findings

1. **The evaluated extraction is tokenized XML reconstruction, not verified raw prose.** `sentence_texts`, extraction script lines 60–69, concatenates all XML text/tails and collapses whitespace. English input lines 186–202 contain separate comma/quote and question-mark/quote elements with layout newlines between them. French `s5.0`, especially `w5.0.14` and `w5.0.15`, has an apostrophe in the first word element's tail, followed by a newline before the next word. Thus `itertext()` correctly preserves some punctuation outside `<w>` but also treats serialization layout as text spacing. Joining only `<w>` text would introduce a further defect by dropping tail punctuation. Source provenance reinforces this: `opus_selective_extract_manifest.json`, `splits.dev.raw.*.source_member`, names `Books/xml/...`, and `opus_zip_index_wake2_v3.json`, `archives.*.url`, points to `/v1/xml/{lang}.zip`. A directory or manifest field named `raw` does not change the format.

2. **Visible spacing differences do not prove a consequential tokenizer error.** Evaluator line 8 uses `Sequence([Whitespace(), ByteLevel(use_regex=False)])`; line 20 attaches it to every arm. Installed `tokenizers/pre_tokenizers/__init__.pyi` lines 576 onward documents `Whitespace` as `\w+|[^\w\s]+`, not a plain space splitter. Lines 93–108 document `ByteLevel`'s default `add_prefix_space=True`; `data/manifest.json` lines 620–630 explicitly records that configuration. Word/punctuation boundaries already separate ordinary apostrophes from letters, so many raw/reconstructed spelling-spacing differences can yield identical pretoken strings. Conversely, inserting spaces within a contiguous punctuation run can change its grouping: raw `?'` versus reconstructed `? '` is a concrete possible mechanism supported by the English XML example. Split lexical strings or altered characters can also matter. Frequency, direction, and arm dependence remain unmeasured; do not infer them from the example.

3. **Existing replay validates implementation consistency, not source fidelity.** Evaluator lines 22–33 and 44–48 replay the same preprocessing. Grouped evaluator `evaluate_grouped_books_wake2.py` lines 58–62 checks the first three rows per split against that same replay; it cannot detect a shared text-reconstruction error. Equal 1,000 merges/1,256 vocabulary checks (lines 49–52) are useful but likewise do not answer preprocessing sensitivity. Changing the pretokenizer during a raw-text comparison would confound extraction with the learned tokenizer definition; training preparation (`scripts/prepare_pilot.py`, lines 8, 16) and robust training (`scripts/train_robust.py`, line 17) use the same sequence.

4. **The present result supports a narrow fixed-pipeline statement.** It describes English/French token costs on selected one-to-one alignment intersections from two works, under this extraction and these existing tokenizers. Extraction lines 124–131 additionally require English/Spanish one-to-one membership, although the grouped evaluator only scores English/French. This is an ES-conditioned subset, not all aligned EN/FR text. Selection of the two smallest compressed works is recorded at extraction line 149; one work is not a population of independent books.

## Smallest decisive paired comparison

Coordinator should perform one bounded, evaluation-only comparison before changing training or opening another book:

1. Retrieve the **official untokenized raw-layer versions of the same two works and languages**, bind version/member/content hashes, and verify document and sentence-ID correspondence. Preserve actual intra-sentence characters and punctuation; do not heuristically detokenize the current XML. OPUS describes raw/XML layers as sentence-boundary compatible, but local ID coverage still requires verification. Any mismatch is a declared mapping failure, not silent row deletion or rematching.
2. Freeze the existing 682 dev and 264 confirm paired IDs, models/merges, pretokenizer options, and metrics. Compare existing reconstructed text (A) against source raw text (B) on exactly those IDs. Do not change ES filtering in this comparison. These counts are copied from the existing JSON, not recalculated. A single predeclared arm contrast, `robust_domain` versus `classical`, gives the minimal four cells per work (two representations × two arms) addressing the apparent candidate/comparator fairness comparison. If making claims against additional arms, include those frozen arms rather than selecting a winner afterward.
3. Record paired pretoken-string and token-string changes, language-specific token-cost changes, and for each work separately the raw and reconstructed arm differences in Gini, mean costs, worst cost, and total cost. The decisive sensitivity quantity is the change in the candidate-minus-comparator difference across B versus A, not just each tokenizer's absolute token-count shift. Prespecify practical tolerances before scoring; absent a prior tolerance, report exact changes and whether ranking/direction or an existing efficiency constraint changes, without declaring arbitrary statistical equivalence.
4. If every raw/reconstructed pretoken-string sequence is identical, deterministic frozen BPE outputs must match and the extraction concern is resolved **for these rows and this pretokenizer**. If they differ, paired scoring determines whether the fairness comparison changes materially. A changed ranking or violated cost constraint defeats the current robustness interpretation. A stable result supports only local preprocessing stability. Neither outcome confirms general raw-text fairness or supports another pretokenizer without further evidence.

One work could reveal a counterexample cheaply; it cannot settle stability of an existing two-work conclusion. Tiny handpicked punctuation examples establish plausibility only. No retraining is required for this question; changing training preprocessing would be a separate study.

## Aggregation and claim risks

- Grouped evaluator lines 64–75 compute Gini **of language means**, not mean sentence-level Gini. Signed language gaps can cancel across sentences or books. Pooling the unequal-size works additionally changes their weight. Keep per-work, per-language signed costs visible; any macro-book summary must state its weighting and cannot replace the separate results.
- A smaller relative disparity can result from raising the cheaper language's cost. Existing JSON already illustrates a trade-off: on `confirm`, `robust_domain` has Gini 0.0034923971 versus `classical` 0.0075046904, but worst cost 61.7083333 versus 61.4772727 and total 122.5606061 versus 121.1363636. These are quoted existing fields. Thus a Gini win is not cost dominance. On `dev`, the same Gini comparison favors `classical`; the result is work-dependent before any raw-text audit.
- “Whole-work-isolated” concerns split identity, not full-work inclusion, independent replication, representativeness, or unseen confirmation. Reusing the already exposed `confirm` work is a sensitivity check. Sentence resampling cannot create additional independent books.
- Token counts on translations reflect orthography, translation length, segmentation, and tokenizer behavior. Call the measured property token-cost parity; this evidence alone does not establish broader linguistic fairness, quality, or downstream utility.

## Sources, limits, and next action

Official sources read on 2026-10-11: [OPUS Books](https://opus.nlpl.eu/legacy/Books.php), download-format legend and corpus/alignment notes; [OPUS download formats](https://opus.nlpl.eu/download-formats), monolingual formats and native XML sections. They distinguish tokenized XML from untokenized raw files and explain compatible segmentation. Neither source guarantees lossless recovery of original published-book typography. An attempted legacy `download.php` lookup was inaccessible; it was not used as evidence.

This review inspected excerpts of the bound XML, existing result fields, and source code; it did not inspect an official raw-layer counterpart or execute the evaluator. The smallest useful next action is the frozen paired raw-layer comparison above. Until then retain existing results as **tokenized-XML-derived, exposed-work evidence**, with raw-text stability unresolved.
