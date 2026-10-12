# PA-BPE wake12 report

## Outcome

The official OPUS GlobalVoices v2018q4 English, French and Spanish raw archives were recovered and pinned. All 512 pre-frozen trilingual units resolved to unique raw members and sentence IDs. A hash-only, result-blind SQLite confirmation index was built, independently verified and separately reviewed after a first version was held for provenance defects.

## Accepted evidence

- Repaired builder: 23.815434837 s wall, 103,018,496 B peak RSS.
- Database: 7,794,688 B; SHA256 `26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7`.
- Entries: 512 per language; words en 10,415 / fr 11,908 / es 11,106; five-word shingle mass en 8,390 / fr 9,876 / es 9,080.
- Independent verification: 2,286 assertions, 45 unique labels, SQLite integrity `ok`; all three archives rehashed from disk.
- Plaintext scan: 1,536 document references, 512 unblinded unit IDs, 96 raw URLs and 96 normalized sentence samples absent from the database.
- Independent repair review: PASS on all five prior HOLD findings.

## Negative results and repairs

The initial raw-schema attempt failed because external XCES references used `.xml.gz` while raw ZIP members used `.xml`; the repaired unique-member mapping passed. The first fail-closed builder submission used stale CLI argument names and exited before producing a database; the corrected contract passed. Both failures remain in runner receipts and resource accounting.

## Scope

This milestone establishes content identity, provenance and result-blind confirmation fingerprints only. It is not tokenizer training, a fairness score, production-selector qualification, or a reproduction of the paper. Production adapter compatibility, truthful row-to-shard identity, 100,000-pretoken budget integration and all confirmation outcomes remain HOLD.

## Resources and persistence

Wake12 used 10 attempts (8 succeeded, 2 retained failures), 116.766455980003 s charged wall and zero reservation; cumulative charged wall is 994.4588047509768 s. The runner exited cleanly. The 232,883,564-byte raw-source bundle is stored separately under Library ID `libfile_fab29332f8248191850f2decc6e6b5a4`, version 0, SHA256 `825a8c063b19d4b1dc21f8a540ea2acbe5e11fa1da1cd6bfdeac5200c6805b6c`.
