# Prior-item inventory recovery notes
Read-only source inspection during memory wait; not an experiment.

Production training payload wake15b consumed 209 English, 155 French, and 151 Spanish documents, each language truncated to 100000 pretokens. selected_rows.json records raw_text_sha256, fixed shard identity and shard row, included prefix and available pretokens. Reconstruct raw selected items from wake15b/inputs/en.parquet and fr_rowgroup0.jsonl, es_rowgroup0.jsonl; dictionary and BPE codes are insufficient. Screen the entire final partially consumed document conservatively. These files have not been restored during this wait.

TICO development text is recorded at wake16/output/v3_tico.trilingual.dev.json. Prior exposed GlobalVoices, FLORES, and Books texts must additionally be recovered from their fixed history/archive identities, retaining language and original item boundaries. Exact archive/file mapping still needs verification. No incomplete inventory may release confirmation scoring.

Next executable action remains compressed-source structural audit, before candidate selection and all tokenizer scoring. Source hashes are now persisted in source_manifest.json and archive references.
