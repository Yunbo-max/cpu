# PA-BPE Wake 11 report

## Outcome

This window froze and implemented a result-blind GlobalVoices decontamination contract and a disk-backed ranked-row stream. The final v6 verifier passed 25/25 checks. The software blocks GlobalVoices publisher hosts, canonical URL matches, exact normalized content and same-language five-word multiset containment at 0.80; shingles use full SHA-256. It rejects invalid or non-string URLs, handles DNS root dots and IPv6, rejects all copies of duplicate IDs, and emits accepted rows through a streamed atomic manifest.

The SQLite path binds protocol, implementation, provenance mode, training input and confirmation manifests. Completed stages are idempotent across close/reopen, incomplete stages cannot emit, and late schema/provenance errors roll back. English/French/Spanish exposed probes (40/40/44 rows) matched direct deterministic ranking exactly. A 20,000-row generator-only probe selected all rows while the in-process peak grew from 18,872 to 20,664 KiB; external peak RSS was 21,159,936 bytes. This is a bounded software probe, not production qualification.

## Independent review and negative results

The initial independent review rejected three claims: restart replay was not truly tested, Python accumulated dataset-sized duplicate/output lists, and 64-bit shingle truncation was not exact. All were repaired and independently accepted. Subsequent review found URL and stage-binding edge cases; the final falsey non-string URL gap was fixed in v6.

Two scientific attempts failed and remain retained. v1 hit a SQLite schema lock after 0.087114321 seconds. v4 hit a test-helper `NameError` after 0.084865906 seconds. Four attempts succeeded. Total charged runner wall was 3.3702338249859167 seconds; reservation ended at zero. Final runner status is stopped with no live scientific process.

## Claim boundary

This is only a prospective software milestone. Real GlobalVoices fingerprints have not been built, raw confirmation outcomes remain unopened, row-to-fixed-shard truth is unverified, the pretoken budget is not yet integrated with this stream, and the 1.60 TB candidate universe was not scanned. Formal payload, production-scale RSS, crash recovery, tokenizer training, fairness, cross-domain and reproduction claims all remain HOLD.

## Next action

Run the frozen builder against the real confirmation source in a blinded mode that emits only hashes, blinded identities and aggregate counts; independently verify row-to-wake9-shard provenance; then integrate the wake10 100,000-pretoken budget path and run the smallest fixed-author native Classical/PA-BPE input-contract commands.
