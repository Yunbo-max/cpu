# Wake 11 independent decontamination/selector review

The first read-only review rated the v2 artifact **HOLD**: unit execution and prospective result-blind rules passed, but restart replay, bounded-memory production behavior and exact near-match semantics failed. It identified linear Python `dup`/`out` accumulation, non-idempotent stage replay, 64-bit shingle truncation, URL edge cases, incomplete transaction rollback, provenance truth limits and nominal-only atomic publication.

After v3, the same reviewer closed all three failures: completed stages were idempotent across close/reopen, duplicate aggregation moved to SQL with streamed manifest emission, and shingles used full 256-bit SHA-256. URL, transaction and provenance syntax tests passed; real source truth, production scale, crash recovery and scientific gates stayed HOLD.

The v5 spot check accepted the complete-stage guard, provenance-mode and implementation bindings, IPv6 canonicalization and test-only naming, but found one narrow bug: falsey non-string URLs bypassed type enforcement. v6 reordered the type checks and added `0`, `False`, and `b''` regressions. Final coordinator acceptance is therefore a prospective software milestone only.

No reviewer edited files, ran experiments, accessed network resources, or viewed raw confirmation outcomes.
