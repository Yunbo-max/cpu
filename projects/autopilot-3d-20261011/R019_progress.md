# R019 telemetry-first causal localization progress

Updated: 2026-10-12T15:55:00Z

## Scope and claim boundary

R019 tests whether the native gravity-pose generator appends partially initialized points after the retry loop exhausts. It preserves the author RNG call order, retry boundary, and accepted-problem stream. The current evidence supports the append-incidence mechanism only. It does not establish value-level identity with R018 geometry because R018 did not serialize a safe, identity-bound copy of the stale or uninitialized feature bytes.

## Executed evidence

- `gravity-R019-build-v3` succeeded (`attempt-bed0ce51d7a543d3b153a6c317a11fd1`), elapsed 14.971073 s, child peak RSS 769840 KiB, no OOM. Binary SHA-256: `25c5e7b54929725c0cf63ae013eb111d508635a1a8f8f6cfd82747a63c756068`.
- Plan v3 passed the Simple design checker with zero structural gaps (`attempt-23e9b1d89a9543eca0a7137e10efa2d3`). It repairs the stale build-v2 mapping and comparison-basis enum without changing the active scientific question.
- Smoke8 and its independent audit succeeded: 8/8 accepted, 32 trace rows, exact call/GT agreement with R017, maximum scaled GT difference 0.
- Smoke100 and its independent audit succeeded: 100/100 accepted, 400 trace rows, 388 normal-success rows and 12 rejected-attempt-101 appended rows, exact call/GT agreement with R017, maximum scaled GT difference 0.
- Full5000 telemetry succeeded (`attempt-da5b8fd739554bfab93ae884ea79c1d7`): 5000 accepted problems, 5011 generator calls, 20023 trace rows, child peak RSS 7324 KiB, no OOM.
- Reviewed full audit v2 succeeded (`attempt-1ab2353bd0de4a2e88ae7b852ba1a6db`): audit SHA-256 `690afd5c32e051bf2939f11ce378d8432d6c073bed9e3ddb775f08658a94caa8`; counterfactual SHA-256 `07f083405cab80d5c2eb1baf2440c6564ffcac608fc67b93a66f7a430717a2f4`.

## Full5000 results

- Class counts: 19423 normal-success; 567 rejected-attempt-101 appended; 12 partial rows from failed prior calls; 11 successful-attempt-100 rejected; 10 successful-attempt-101 appended.
- Failure reasons among rejected terminal rows: reference depth negative 306; query depth negative 262; initial affine determinant negative 1.
- Rejected attempt-101 append affects 567 features in 331 accepted problems.
- Provenance audit: all 567 appended features have at least one required field never assigned on the terminal attempt; stale-but-initialized 0; all-current 0.
- Offline success-contract relabeling retains 4669 of 5000 original acceptances and rejects 331. It makes no geometry imputation and is not a solver-quality result.
- Integrity counters are all zero: duplicate references, duplicate accepted problems, missing accepted problems, orphan trace calls, and duplicate call/point rows.

## Scientific status

- `supported`: rejected terminal attempt-101 points are appended on the GT/call-identical native stream.
- `inconclusive`: value-level overlap with R018's specific geometry failures.
- `inconclusive`: the broader preregistered claim that this mechanism is a causal contributor to R018 solver failures.

## Repaired failures

- The first design-v3 submission attempted to supersede a successful design-v2 task and was rejected before execution. The corrected versioned task omitted the invalid supersession and passed.
- `gravity-R019-full5000-audit-v1` was invalidated before command execution because the reviewed audit script hash changed. No stale audit logic ran. Versioned audit-v2 pinned the reviewed hash and succeeded.

## Runner and cumulative accounting

Runner sequence 186; 142 database attempts, all terminal; elapsed command time 13210.756242288027 s. With three preserved external recovery receipts, observed totals are 145 attempts and 13212.617197288027 command-seconds. `source_error` and `user_stop` are null. The supervisor is intentionally absent at the all-terminal idle boundary.

## Next action

Keep the same active idea. Prepare plan v4 for same-execution, safe geometry serialization that emits only fields whose assignment mask proves initialization. Build only after a fresh raw-headroom check reaches the frozen 1536 MiB compile gate; then run smoke8, audit, smoke100, and full5000 serially. Do not use R018 cross-binary feature bytes as causal identities.
