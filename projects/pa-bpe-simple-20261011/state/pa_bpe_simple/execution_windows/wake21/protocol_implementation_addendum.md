# Tatoeba pre-scoring implementation clarification, wake21

Parent protocol SHA256: `275c2dae7285fb0baa2a54ae2acbdf960382a9b6b1b54207d6fcfc61f6832aeb`.
Recorded on 2026-10-12 after source acquisition began, before source text parsing, row selection, or any tokenizer scoring. The original protocol remains immutable. This addendum resolves implementation ambiguity; the short-text exclusion below is an explicit conservative eligibility amendment, not retroactively part of the original freeze. No outcome informed it.

## Deterministic ordering

Serialize the ASCII prefix `pa-bpe-tatoeba-confirm-v1`, one NUL byte (00), canonical decimal English ID, NUL, French ID, NUL, Spanish ID. No trailing NUL. Example IDs 1,2,3 yield bytes `pa-bpe-tatoeba-confirm-v1` followed by hex `00 31 00 32 00 33`. Sort by SHA256 bytes, then numeric (English,French,Spanish) IDs in the event of a hash collision. Deduplicate direct edges; require all three edges. Unknown IDs, wrong-language IDs, duplicate sentence IDs and malformed records invalidate the relevant source.

Apply all contamination exclusions before selection. For each same-language normalized text retain the eligible triple with globally lowest ordering key; retain a triple only if it is the representative for all three normalized texts. Then sort these triples and greedily enforce sentence-ID uniqueness. This adopts the stronger 'lowest candidate hash' wording and may discard more triples than ordinary greedy text deduplication. Do not try alternative selectors based on yield. Fewer than 1024 admissible triples fails this protocol.

## Contamination

Normalize with Unicode NFKC, then casefold, collapse Unicode whitespace and strip. Tokens are whitespace-separated normalized tokens. Contiguous five-token shingles form a multiset. For candidate c and one prior same-language item p, D is the candidate's shingle multiplicity total and I is the sum of min(candidate multiplicity, prior multiplicity) for shared shingles. Exclude on exact normalized hash or `5*I >= 4*D`, with D>0. Never pool different prior items or replace this with Jaccard similarity.

Conservative amendment: exclude normalization-empty texts and candidates with fewer than five normalized tokens, recording these exclusions separately, because the frozen containment denominator would otherwise be zero. This narrows the population to sentences for which the specified shingle check is defined. The row target stays 1024.

All actual training and exposed-text inventories must be reconstructed and hashed before eligibility is finalized. Preserve original document/sentence item boundaries. If the final partially consumed training item cannot be reconstructed exactly, screen against that entire implicated item and disclose the conservative over-exclusion. Dictionary files and codes alone do not establish this inventory. Training, TICO, GlobalVoices, FLORES and Books remain required; missing inventory keeps scoring on HOLD.

## Statistics

Use integer language totals T_l and aggregate Gini `sum_{i,j}|T_i-T_j|/(2*3*sum_l T_l)`. Compare rational values exactly for the frozen point-estimate decision. Total mean cost is sum(T_l)/1024. Paired-row macro Gini is the arithmetic mean of each row's three-language Gini. Worst-language means use the same denominator; report ties.

Before scoring fix Python standard-library `random.Random(20261012)`, 2000 paired-row bootstrap replicates of 1024 indices sampled with replacement. Use the same resampled triples for all models/languages. Report percentile intervals with linear interpolation at positions `(B-1)*0.025` and `(B-1)*0.975`. Contrasts: hybrid-window minus Classical Gini; hybrid-window minus hybrid Gini; hybrid-window minus hybrid total mean cost. Intervals are descriptive uncertainty conditional on exchangeable rows, not a new promotion/significance gate. Translation components and paraphrases may violate row independence; sentence-ID uniqueness does not remove that limitation.

## Review integration

Read-only reviewer `/root/pa_bpe_tatoeba_review_wake21` verified the parent hash and identified the serialization, greedy representative, shingle denominator, short-text, prior-inventory and bootstrap ambiguities above. Coordinator accepts those findings and conservative pre-outcome resolutions. No reviewer commands were scientific experiments; native model use is unknown. The acquisition script streams compressed bytes with a 256 MiB address-space cap. Parsing will be separately measured, with SQLite cache bounded to avoid an in-memory sentence graph.
