# Wake 7 independent confirmation-source review

Access date for every web source and HTTP metadata check below: **2026-10-12 (UTC)**. This is a research-source audit, not legal advice. No corpus payload was downloaded and no outcome text was inspected.

## Bound-input verification

Both assignment bindings matched before review:

| Input | Expected SHA-256 | Observed SHA-256 | Result |
|---|---|---|---|
| `execution_windows/wake2/output/source_probe/source_probe_wake2.json` | `a162de2f46e6f12a8bebea31b163975b81ad65dadbc7b37d0c4accdd8ef6337d` | `a162de2f46e6f12a8bebea31b163975b81ad65dadbc7b37d0c4accdd8ef6337d` | match |
| `PA_BPE_Wake3_Report.md` | `7cd13ab3ddfefabf67901b6dbe005f1f3b2b2dfa5ba58b447cb0ed4d4b7c1ab6` | `7cd13ab3ddfefabf67901b6dbe005f1f3b2b2dfa5ba58b447cb0ed4d4b7c1ab6` | match |

The bound report says all existing Books/TICO data are exposed and cannot regain confirmation status by renaming or resplitting. I therefore treat any reuse of those rows as ineligible.

## Recommendation

**Conditional GO: OPUS GlobalVoices `v2018q4`, used as a new, project-defined news-domain confirmation corpus, provided the structural and provenance gates below pass before any tokenizer outcome is computed.**

This is not an unconditional GO and it is not an official benchmark claim. The source has materially stronger evidence than TED/IWSLT for the requested use:

1. OPUS identifies the immutable release as `GlobalVoices v2018q4`, calls it “truly multilingual,” and exposes English, French, and Spanish plus all three pairwise XCES alignment files.
2. Global Voices itself licenses its own content under CC BY 3.0 unless otherwise stated; that is affirmative source-level permission, unlike OPUS's redistribution disclaimer alone.
3. OPUS XCES alignments retain document references and sentence IDs, allowing a trilingual intersection and sample to be frozen from structural IDs without selecting on text or tokenizer outcomes.
4. It is a news/story domain, distinct from the exposed literary Books domain and the TICO health domain. Distinct domain does **not** by itself prove absence of training leakage.

**NO-GO: current TED/IWSLT releases under the evidence located here.** IWSLT 2017's official multilingual task did not include Spanish, while French was only in a separate English-paired bilingual task. More importantly, current TED terms explicitly prohibit incorporating TED content into ML/AI evaluation or research datasets without a separate written license. The historical statement that IWSLT data were free to registered participants is not evidence of a current license for this project.

## Candidate A — OPUS GlobalVoices v2018q4

### Official identity and availability

- Exact corpus page: <https://opus.nlpl.eu/legacy/GlobalVoices.php>
- Exact release: `v2018q4`; OPUS describes it as a parallel corpus of Global Voices news stories, adjusted for OPUS, with 46 languages and 851 bitexts.
- Primary content source: <https://globalvoices.org/>
- Primary description of its multilingual translation operation: <https://globalvoices.org/about/>
- OPUS reports pairwise aligned-unit counts rounded on the release page: approximately `0.4M` for en–es, `0.2M` for en–fr, and `59.0k` for es–fr. These are pairwise counts, **not** a trilingual-row count.
- OPUS native-format specification: <https://opus.nlpl.eu/download-formats>. It states that bilingual XML is XCES standoff alignment, with `fromDoc`/`toDoc`, sentence IDs, and possibly many-to-many links. This is the required stable structural identity. Moses rows are insufficient for a three-way identity because they erase document/sentence references.

The exact six objects required for structural trilingual reconstruction were confirmed by HTTP HEAD only; no body was fetched:

| Object | Exact official URL | Bytes | MiB | ETag | Last-Modified |
|---|---|---:|---:|---|---|
| English raw XML ZIP | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/raw/en.zip> | 115,069,300 | 109.739 | `784830696482dfd4ee1ed7096b3d3547` | 2020-11-13 07:42:11 GMT |
| Spanish raw XML ZIP | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/raw/es.zip> | 80,028,192 | 76.321 | `85c840e723f7faabba7fd7b569c3c695` | 2020-11-13 07:42:11 GMT |
| French raw XML ZIP | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/raw/fr.zip> | 37,776,586 | 36.027 | `90f2f70b8fec375179f371ed633553de` | 2020-11-13 07:42:11 GMT |
| en–fr XCES | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/xml/en-fr.xml.gz> | 1,693,015 | 1.615 | `d39ba637ceffde73bc8e338b179db3e3` | 2020-11-13 07:42:48 GMT |
| en–es XCES | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/xml/en-es.xml.gz> | 4,082,911 | 3.894 | `2c84367ba7396de8ec62e1ad1f75f818` | 2020-11-13 07:42:54 GMT |
| es–fr XCES | <https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/xml/es-fr.xml.gz> | 1,616,380 | 1.542 | `266291d62556db51cde2b4f2dd94df58` | 2020-11-13 07:42:46 GMT |

Total advertised transfer for those six objects is 240,266,384 bytes (229.136 MiB), comfortably inside the host storage/RAM constraints if later streamed rather than loaded together. ETags are provenance metadata, not substitutes for computing SHA-256 after an authorized download.

### License and terms

- Global Voices republishing policy: <https://globalvoices.org/about/global-voices-attribution-policy/>. It states that, unless otherwise stated, content created by Global Voices is under Creative Commons Attribution, permits sharing and adaptation for any purpose, and requires credit, license link, and change indication. The page identifies the site license as **CC BY 3.0** and requires the original story link and author name for republication.
- Canonical license: <https://creativecommons.org/licenses/by/3.0/>.
- OPUS release-page disclaimer: OPUS says it does not own extracted text and only offers files it believes it may redistribute, with notice-and-takedown. That disclaimer is **not** affirmative permission; the affirmative evidence is Global Voices' own CC BY policy.

Scope limitation: “unless otherwise stated” means the license must not be generalized to excluded third-party media or exceptional stories. This tokenizer study should use text only, keep an attribution ledger at story/document level, and should not redistribute raw text or a repackaged corpus. If the OPUS XML lacks original story URL/author metadata sufficient for attribution, that is a **missing-license-evidence condition**, not permission; pause publication/re-distribution and resolve it before release. Internal non-commercial measurement with provenance retained is the intended current use.

### Required trilingual identity and frozen sampling

Pairwise availability is not proof of same-content trilingual rows. Before any tokenization outcome is computed, the coordinator should run a structure-only gate:

1. Hash each downloaded object and pin the six hashes alongside release `v2018q4`.
2. Parse only XCES metadata first. Intersect the three pairwise `linkGrp` document references to obtain story/document triples present in en, fr, and es.
3. Within each document triple, form a tripartite graph whose nodes are `(language, document-reference, sentence-id)` and whose edges are the three XCES pair links. Retain only closed connected components containing all three languages and at least one edge for each of the three language pairs. Concatenate many-to-many sentence IDs in source order; never align by row number or text similarity.
4. Reject duplicate IDs, missing raw references, cross-document components, and components with a node linked outside the retained component. Record all rejection counts before scoring.
5. Define the unit ID as SHA-256 of the release name plus sorted document references and sorted per-language sentence-ID lists. Freeze units by ascending hash of `"pa-bpe-globalvoices-v2018q4-confirm-v1\0" + unit_id`; do not inspect text to choose units.
6. Require at least 512 valid trilingual units after all gates. If fewer exist, report **no-go for the predeclared protocol** rather than relaxing the identity rule after seeing outcomes. If more exist, use the first 512 only as the fixed project confirmation subset and keep the remainder sealed. This is a project protocol, not a claim that OPUS supplied an official split.

No tokenizer, candidate, threshold, merge rule, or model may be selected from these confirmation outcomes. If a development domain is still needed, obtain it separately; do not split GlobalVoices after looking at results and then call the residual independent confirmation.

### Leakage and domain limitations

- **Training leakage is unresolved.** Global Voices pages could occur in web-crawl training sources. Before opening outcome text, compare source URLs/document IDs against every training/dev manifest. After the subset is frozen, perform a preregistered exact-overlap audit against training text; exclude at story level using a rule frozen before tokenizer comparison. A lack of exact shingles would not prove semantic independence.
- The release is historical (`v2018q4`) and the objects were last modified in 2020; it tests story/news domain shift, not current news or temporal robustness.
- OPUS alignments are automatically processed pairwise, not a gold trilingual annotation. The closed-component rule improves identity consistency but does not establish translation quality. Report retained/rejected support and, if permitted later, conduct an alignment-quality audit blind to method outcomes.
- Translations can have different editors and may omit or restructure passages. Many-to-many units must remain intact; sentence-row truncation would change the estimand.
- The domain is generated by one multilingual newsroom/community. It is one new domain, not evidence for multilingual fairness generally.
- Source-level CC BY does not cover third-party photos/video/audio, and exceptional text may be separately marked. Use textual XML only and preserve exceptions/provenance.

## Candidate B — official IWSLT/TED releases

### Availability and identity

- IWSLT 2017 official evaluation page: <https://workshop2017.iwslt.org/59.php>.
- IWSLT 2017 organizer site: <https://sites.google.com/site/iwsltevaluation2017/>.
- Task specification: <https://sites.google.com/site/iwsltevaluation2017/TED-tasks>.

The task page defines the official multilingual set as English, Dutch, German, Italian, and Romanian. It offers French only in a separate unofficial English-paired bilingual task; Spanish is absent. Therefore this release does not provide one official en/fr/es same-talk evaluation set. The organizer page says data were freely available to participants and points to WIT3, but participation/access language is not a reusable license and does not establish trilingual row identity.

### Current terms and recommendation

- TED Talks Usage Policy: <https://www.ted.com/about/our-organization/our-policies-terms/ted-talks-usage-policy>. It places talks, transcripts, and subtitles under CC BY-NC-ND 4.0 only within stated uses; transcripts/subtitles are tied to use with the talk and edits/alternate uses require permission.
- TED Terms of Use, updated 2024-05-07: <https://www.ted.com/about/our-organization/our-policies-terms/ted-com-terms-of-use>. Sections 6.3–6.4 explicitly exclude incorporating TED content into research datasets and using it for ML/AI development, training, **evaluation**, or analysis without a separate written license; automated extraction is also prohibited outside those terms.

Hence: **NO-GO for this project unless the project obtains a separate written TED license that expressly covers automated access, storage, trilingual reconstruction, tokenization evaluation, and research reporting.** Missing an accessible old IWSLT/WIT3 license is not permission, and the historical participant release cannot be assumed to override current TED terms.

## Candidate C — MDN Web Docs (fallback audit only)

- Primary license page: <https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Attrib_copyright_license>. MDN documentation is CC BY-SA 2.5 or later unless otherwise indicated, with explicit attribution requirements; code samples have separate CC0/MIT rules.
- Official English source: <https://github.com/mdn/content>.
- Official translated source: <https://github.com/mdn/translated-content>, which covers Spanish and French among seven maintained translations.
- OPUS entry: <https://opus.nlpl.eu/datasets/MDN_Web_Docs>.

This candidate has clearer source licensing and commit-pinnable article paths than TED. However, this review did not verify an immutable OPUS release, exact en/fr/es trilingual intersection, official sentence-level alignment, or download sizes from a static official page. Repository path equality identifies corresponding articles, not aligned sentence units. Therefore it is **HOLD / no-go for the present confirmation run**, not a substitute to be adopted by silently building a new alignment benchmark. It can be revisited only with a separate, pre-outcome structural protocol and pinned repository commits.

## Final go/no-go table

| Candidate | License evidence | Same-content en/fr/es identity | Present decision |
|---|---|---|---|
| OPUS GlobalVoices `v2018q4` | Source CC BY 3.0; OPUS disclaimer alone insufficient | Feasible from three XCES files, but triple support must be proven structurally | **Conditional GO** after all six preregistered gates; internal confirmation, no raw redistribution |
| IWSLT/TED | Current TED terms expressly restrict ML evaluation without separate written license | IWSLT 2017 official multilingual task lacks Spanish; French is separate bilingual task | **NO-GO** absent written license |
| MDN Web Docs | Clear CC BY-SA 2.5+ for documentation | Article paths exist, but no verified immutable trilingual sentence alignment in this review | **HOLD / NO-GO now** |

The recommended next action is therefore a **metadata-first GlobalVoices gate**, not an experiment: acquire the six pinned `v2018q4` objects under coordinator control, hash them, reconstruct closed trilingual components from XCES IDs, record support/rejections and attribution fields, check source-manifest leakage, and freeze the first 512 hash-ranked units before any tokenizer output is produced. If any gate fails, GlobalVoices must be reported as unavailable for confirmation rather than repaired after observing outcomes.
