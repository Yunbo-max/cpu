# Wake 9 immutable training-shard identity audit

## Decision

- **Immutable candidate-shard identity subgate: PASS.** For every listed candidate, the tuple `(dataset repository, pinned repository revision, tree path, file path, LFS SHA-256, byte size)` is sufficiently specific to name and later verify an immutable payload. The Git object id and Xet hash provide additional recorded identities.
- **Permission to sample payloads or train tokenizers: HOLD.** This audit qualifies source-file identities only. It does not qualify a row sampler, selected rows, balanced training budgets, evaluation decontamination, preprocessing, or a tokenizer experiment.

These decisions are intentionally separate. The PASS must not be reported as restoration of a training set, a three-language tokenizer result, a FineWeb2-only protocol, or reproduction of the PA-BPE paper.

## Artifacts audited

I read only the assigned protocol and four output artifacts. I independently recomputed the manifest hashes, record counts, path/hash uniqueness, formats, byte sums, pagination totals, and pairwise LFS-hash intersections from the three manifests rather than relying only on the aggregate verifier.

The protocol SHA-256 is `93fd7de78520369112449c9d0e0f75b1be004e330db45daa92d9fca37b10abcb`, matching the aggregate verifier. The three manifest SHA-256 values also match its declarations:

| Language | Repository and pinned revision | Tree path | Files | Bytes | Manifest SHA-256 |
|---|---|---|---:|---:|---|
| English | `HuggingFaceFW/fineweb@9bb295ddab0e05d785b879661af7260fed5140fc` | `data/CC-MAIN-2013-20` | 205 | 421,898,767,606 | `ada44ec35d38c51e1126efc82014d41f652a33990d06ff5ffd7fb3bc5b8cdb32` |
| French | `HuggingFaceFW/fineweb-2@af9c13333eb981300149d5ca60a8e9d659b276b9` | `data/fra_Latn/train` | 135 | 539,897,427,722 | `3943b5a6502ad2ceae04293e0a4fdeda9eaa7c0712dbdcedc7c4b3208b06e435` |
| Spanish | `HuggingFaceFW/fineweb-2@af9c13333eb981300149d5ca60a8e9d659b276b9` | `data/spa_Latn/train` | 146 | 637,611,323,581 | `b9f5b0328054a96f0de46f29b25915a4bcbc378cfceaf6ff8c9472f2b1d4abd8` |

The independently recomputed total is 486 files and 1,599,407,518,909 bytes.

## Directly supported claims

For each language:

- the manifest repository, revision, and tree path equal the frozen protocol values;
- the file count equals the protocol's expected count;
- all paths are unique, lie below the declared tree path, and end in `.parquet`;
- all Git object ids are distinct valid 40-hex strings;
- all LFS SHA-256 values are distinct valid 64-hex strings;
- all Xet hashes are valid 64-hex strings;
- every recorded byte size is a positive integer, and summing the records exactly reproduces the declared language total;
- all recorded API pages report HTTP 200, and their entry-count sums are respectively 205, 135, and 146;
- `payload_bytes_downloaded` is declared as zero.

Across languages, all three pairwise intersections of LFS SHA-256 values are empty. The union contains 486 distinct LFS objects, so the stated zero cross-language payload-hash overlap is supported at whole-file granularity.

The French and Spanish `last_commit_id` is `fb082501d32b7eacfa14d5f2b12fccb3968ab4f8`, not the pinned repository revision. This is not a contradiction: it is the last commit touching those files, while the containing repository tree is addressed at the later pinned revision. Identity should continue to be expressed using the pinned revision plus path and LFS SHA-256, not `last_commit_id` alone.

## Limitations of the evidence

1. Each file record contains one `size_bytes` value. It does not retain separate API file-size and LFS-object-size fields. Therefore the stronger protocol phrase “matching LFS/file size” cannot be independently rechecked from the assigned artifacts; only positivity and internal sums can be checked. A future fetch should retain both raw size fields or a per-file equality result.
2. The manifests retain page response hashes and entry counts, but not the raw page bodies. Their reported HTTP status and `payload_bytes_downloaded: 0` are auditable declarations, not facts recoverable solely from the summarized JSON. This does not undermine the immutable identity tuple, but it limits independent transport-level verification.
3. Zero LFS-hash overlap proves only that no entire Parquet file is byte-identical across languages. It does not test duplicate rows, translated/republished documents, URLs, domains, or semantic/near-duplicate contamination.
4. English comes from FineWeb while French and Spanish come from FineWeb2. Fixed identities make this mixed-source companion protocol reproducible; they do not make it a single uniform processing pipeline.
5. The retained repository-metadata hashes are commitments, but the underlying metadata documents were not among the assigned inputs. I therefore verified equality to the protocol's expected counts, not how those expectations were derived.

## Conditions still required before payload sampling

Keep the overall gate at HOLD until all of the following are frozen prospectively:

1. a deterministic row identity and selection rule (for example, hash-ranking a canonical `language || stable-row-id`), including tie handling, missing/duplicate IDs, shard traversal order, and replacement policy;
2. a common-dump policy and matched per-language budget (documents/rows and an explicit token, byte, or character constraint), with truncation and length filtering defined before inspecting outcomes;
3. a selected-row manifest that records source shard identity, stable row identity, exact payload/content hash, selection rank, and exclusion reason, so later retrieval can be reproduced and checked;
4. URL/domain and exact/near-duplicate text decontamination against all GlobalVoices development/confirmation material, while preserving the confirmation set's information boundary;
5. language/script validation and all text normalization, document concatenation, pre-tokenization, deduplication, and malformed-row handling;
6. the tokenizer comparison contract: methods/variants, vocabulary or merge budget, random seeds if any, stopping criteria, and the matched-cost/fairness metrics;
7. explicit labeling of the English FineWeb plus French/Spanish FineWeb2 design as a new companion protocol, plus any remaining access, attribution, and license checks not evidenced here.

After those items are frozen, payload retrieval can be a separately logged step with observed payload hashes. Only then can resource-scaled smoke tests and tokenizer training become scientifically interpretable.
