# Wake 2: independent Books grouping audit

Decision: **the current Hugging Face rows cannot establish book-disjoint development/confirmation.** Native OPUS document alignments provide a credible route to a new grouped protocol, but a full native document inventory, bibliographic grouping, and exposure mapping are still prerequisites. No new split is certified by this audit.

Review date: 2026-10-11. Scope: read-only local evidence and public primary-source review. No training, scoring, experiments, nested delegation, dependency installation, shared runner changes, or external writes. Only this report was written. Model token/cost usage is unknown. Scientific command budget consumed: zero; local commands were evidence reads/hashes and metadata inspection, not scientific execution.

## Exact binding and checked hashes

```json
{
  "delegation_id": "wake2-books-protocol-audit",
  "generation": 1,
  "goal_contract_version": 1,
  "idea": "pa-bpe-domain-robustness",
  "revision": 1,
  "scientific_policy": "rsi-simple 0.3.0-simple.9",
  "executor_source_digest": "e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8",
  "library_generation": 1
}
```

Project root: `/workspace/scratch/42f1128b703b/wake2_project/pa_bpe_simple`. All three assigned input hashes matched exactly.

| Relative path | SHA256 |
|---|---|
| `review/assignment_wake2_books.json` | `e71904aa002cbb144cd53b91a010e3d63a43ccdedad2c74084f5efb2b7a3536c` |
| `PA_BPE_Wake1_Report.md` | `6bcea50231a066f1c00cbfd488184d3a7dd811f2bdd0a30f643151653559cff3` |
| `phase_budget.json` | `25507450950ee56b81ce312699757775d6594645db3ec1b1761f5fffeecd3cae` |
| `data/manifest_v2.json` | `3975732ee246e2f74d0c072f27aadfe43c8fec2ee81536a87feb41799bbbd2d9` |
| `data/books.pilot.json` | `94e7a72d936235f4fac923913b13b476673cf7030eaef4b80f2ccd411bad6061` |
| `data/books.dev100.json` | `f6a8943432c90f0edeefaf8a216a431d668a56e4636b1d32f963792e6bc3d82e` |
| `data/books.confirm.json` | `eb52fff152849289326120d4e01bf7aa639c9c035f7a66b09cb441ffe45c2add` |
| `evidence/books_enfr.json` | `12c1a0fae33a2361cae027895e109af24c8cfcd7d852849eab921b5edebd4445` |
| `evidence/books_dev_v2.json` | `18f5cbac409f68c4cf8116d95a24afc8cfb6e19e947ade2f1f735b4728e04b01` |
| `evidence/books_confirm_v2.json` | `793e83695cf269e8fee3bfcfb9b101f2b865d1f5fea95d45b5fb9e8f7256aa46` |
| `evidence/books_meta.json` | `a97bbbe0dd109562cb46b5204d9a78eb1dfcd4728fae10402e4e12f2267115aa` |
| `evidence/books_readme.txt` | `8fe3dbccd26f6830432b32fe9cb6a5d287181613a566ab137ade8ebd353432d6` |
| `evidence/books_fetch_v2.json` | `dc4306b9d9336097aaaadeefa9b358324ddd9d7b0ef90ecdf6ec37a042fe43ee` |

The executor digest is copied from the assignment binding, not independently rehashed by this reviewer.

## Established facts

**Local evidence.** Each of the three retained Books slices contains 100 rows and only `en`, `fr`, `id`. Their IDs are respectively 0–99, 1000–1099, and 2000–2099. Original viewer responses add `row_idx` and truncation indicators, but no book, author, source-document, sentence-link, edition, or translation-direction metadata. Fetch receipts for v2 explicitly use the HF rows endpoint with offsets 1000 and 2000, length 100, config en-fr, split train. The recorded HF dataset metadata revision is `1f9f6191d0e91a3c539c2595e2fe48fc1420de9b`; viewer-request URLs themselves did not pin that revision, so the local response hashes remain the reliable binding for already used content.

**HF representation.** The pinned historical HF builder [S1] declares only ID and translation features. Its `_generate_examples` enumerates paired Moses lines and sets ID from that running counter; its download is OPUS Books v1 Moses EN-FR. Thus this ID is not an underlying XML sentence ID or book ID. The current EN-FR card [S2] likewise exposes only those fields and a single train split. Historical loader provenance supports the semantics, but an exact native-to-current-Parquet content mapping must still be verified rather than assumed across revisions.

**Native OPUS structure.** Official format documentation [S3] describes XCES alignment groups referencing source/target document paths and sentence IDs, with raw and tokenized XML layers. Its example includes one-to-many sentence links. The official Books catalog [S4] provides CES and monolingual XML downloads and distinguishes duplicate-preserving Moses/XML from deduplicated TMX. These format differences rule out treating row offsets as portable document boundaries.

**Concrete native identity is visible.** The official EN-FR sample [S5] identifies both paths as `en/Alain_Fournier-Le_grand_Meaulnes.xml.gz` and `fr/Alain_Fournier-Le_grand_Meaulnes.xml.gz`. Its opening title/author entries correspond to local pilot IDs 0 and 1. The monolingual French sample [S6] demonstrates actual metadata: a work title and author, aligner/review note, and source/translator information in surrounding XML. These fields are free-text content, not a demonstrated universal normalized bibliography schema.

**Terms.** The Books catalog [S4] permits personal, educational, and research use, asks for source acknowledgement, and withholds commercial use/mass redistribution without permission. The HF code's Apache software license is not the Books text license. A private research reconstruction with retained attribution fits the stated use category; this audit does not authorize publication of the corpus or make a blanket copyright determination for every edition.

## Inferences and unknowns

- **Strong inference, not yet a complete mapping:** the v2 development and confirmation slices appear to be further passages of the already exposed Alain-Fournier work. Development contains Meaulnes and Frantz; confirmation contains Frantz de Galais and Augustin Meaulnes (`data/books.confirm.json:68–69,103`). Combined with the official opening document and sequential IDs, this is strong evidence of shared-work dependence. It is not a verified interval-to-document table for every row.
- **Established negative conclusion:** neither disjoint offsets nor the v2 exact-string exclusions establishes source-document or work disjointness. The prior report already limits its claims appropriately; this audit does not retroactively invalidate its descriptive row-level scores.
- **Unknown:** complete EN-FR native document pairs, exact number of distinct canonical works, duplicate editions/chapters, precise HF boundaries, original-language direction, and the number of remaining unexposed works. A normalized `en-fr` filename is a language-pair order, not proof the original was English.
- **Access limitation:** official catalog and HTML samples were readable. Several legacy/API variants and binary archive opens failed through the browsing tool; no full native archive was acquired or parsed in this assignment. Therefore live archive contents, hashes, and a usable grouped split remain unverified. Failed archive opens are an access/tool result, not evidence that the corpus is unavailable.

## Proposed reproducible protocol (not executed)

1. **Freeze upstream inputs.** Obtain exact OPUS Books v1 EN-FR XCES alignment plus English and French **raw XML**, following the catalog's actual CES/raw links. Record final URL, retrieval time, bytes, SHA256 and archive member paths. Retain terms and source attribution. Raw text is required for a tokenizer study; reconstructing text from tokenized XML or displayed tokenized HTML would introduce a preprocessing change. Candidate conventional URLs are listed below but were not successfully verified as binary downloads here.

2. **Inventory documents before looking at outcomes.** Extract each alignment group's `fromDoc`/`toDoc`; read the corresponding XML headers and source/translator lines. Build a reviewed table with document paths/hashes, canonical work ID, author, title aliases, edition/translator where present, original language if evidenced, and metadata confidence. Keep uncertain metadata explicitly unknown. A different file does not necessarily mean a different book: join chapters, editions and alternate translations of the same work into one group. At minimum, connected components of shared document paths must remain indivisible. Union components that bibliography establishes as the same underlying work. Do not group unrelated works solely because of a common short quotation.

3. **Quarantine exposure by whole work.** Match all previously consumed Books texts, including v1/v2 dev and confirmation, against native aligned units under a documented text normalization. Preserve exact match evidence and ambiguity counts. Quarantine every work matching previously exposed material. Treat the Alain-Fournier work as exposed now. For repeated or ambiguously mapped sentences, exclude the ambiguous material or conservatively quarantine candidate groups; never assign a guessed document from ordinal position alone. Exact text exclusion alone is insufficient to restore unseen-work status.

4. **Construct semantic units from links.** Use a stable row key such as `(release_hash, fromDoc, toDoc, ordered_source_sentence_IDs, ordered_target_sentence_IDs, link_ordinal)`. Join the ordered sentences on each side of one XCES link using a fixed separator. Keep both languages together, skip empty links with logged reasons, and retain source paragraph IDs when available. Preserve original text and a separate normalized dedup key. Titles, page numbers, annotations and metadata need a prospectively fixed exclusion policy shared across languages and methods.

5. **Assign groups deterministically.** After inventory and exposure quarantine, sort canonical work groups by `SHA256(protocol_seed || canonical_work_ID)` and allocate complete groups to dev and locked confirmation under a predeclared ratio/count rule. Publish the seed, exact group list and split manifest before training. Stratify only on predeclared available metadata such as original language/review status; missing metadata is its own category. Require at least two eligible groups to form any disjoint split, and several confirmation books for book-level uncertainty; if inventory is too small, report a limited paired-book diagnostic or use another lawful benchmark. Never manufacture a 'book' by cutting a long work at arbitrary row offsets.

6. **Freeze sampling and fairness aggregation.** If CPU budgets require subsampling, choose a fixed number of aligned units within each already assigned group by hashed row key, with no outcome filtering. For a book-macro target, compute each book's per-language means and average those equally across books before language Gini; separately retain book-wise Gini and token costs. If instead using sentence-micro weights, state this because long books dominate. Candidate and pooled control must receive identical dev units and counts. Pair method comparisons on the same confirmation units; cluster uncertainty by canonical work, not individual sentences. No uncertainty estimate can compensate for only one independent confirmation work.

7. **Acceptance gates.** Verify zero shared canonical work IDs, zero shared native document IDs, paired language coverage, all hashes, no previously exposed confirmation work, and retained duplicate audit. Freeze confirmation membership before candidate revisions. Parsing and decontamination can inspect text for integrity; candidate selection must not use confirmation outcome scores. Record any protocol changes without silently replacing the already exposed wake-1 results.

A source-document-disjoint split is a weaker fallback than a canonical-work-disjoint split. If headers cannot resolve works/editions, label the former precisely and do not claim independent books.

## Sources and exact next action

- **S1, pinned HF builder:** https://huggingface.co/datasets/Helsinki-NLP/opus_books/blob/712506e9827b2b4b3adaa30b4208dac516273198/opus_books.py — `_BASE_URL`, `_info`, `_generate_examples`.
- **S2, HF EN-FR files/card:** https://huggingface.co/datasets/Helsinki-NLP/opus_books/tree/main/en-fr and https://huggingface.co/datasets/Helsinki-NLP/opus_books/blob/main/README.md — mutable public views; local metadata revision recorded above.
- **S3, official formats:** https://opus.nlpl.eu/download-formats — native XML and XCES document/sentence mapping.
- **S4, official Books catalog/terms:** https://opus.nlpl.eu/legacy/Books.php — metadata, download links, format caveats, terms.
- **S5, official EN-FR sample:** https://opus.nlpl.eu/legacy/Books/v1/en-fr_sample.html — concrete Alain-Fournier document paths and opening links.
- **S6, official French XML sample:** https://opus.nlpl.eu/legacy/Books/v1/fr_sample.html — work/review/source/translator metadata example.
- Official API documentation: https://opus.nlpl.eu/opusapi — query semantics; a Books-specific query was not retrieved successfully here.
- Candidate binary addresses attempted but NOT content-verified: `https://object.pouta.csc.fi/OPUS-Books/v1/xml/en-fr.xml.gz`, `https://object.pouta.csc.fi/OPUS-Books/v1/raw/en.zip`, `https://object.pouta.csc.fi/OPUS-Books/v1/raw/fr.zip`. Prefer resolving and retaining the official catalog links rather than assuming these paths.

**Next coordinator action:** acquire and hash the native alignment/document inventory, map every already exposed HF slice to canonical work groups, then decide whether enough unexposed EN-FR works remain. Until that succeeds, current HF rows support only the existing within-corpus row diagnostics, not a new book-disjoint confirmation claim. No new experiment should be presented as book-disjoint on the strength of offsets 1000/2000 or fresh row IDs.
