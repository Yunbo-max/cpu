# Independent B15 verification

- Reviewer: `/root/b14_independent_verifier` acting as the independent B15 verifier
- Reviewed at: `2026-10-10T21:48:55.803Z`
- Verdict for the fixed B15 package: **REVISE**

The frozen comparator is genuinely falsified by the eta=0.1 run, and no full-policy rerun is needed. The package nevertheless needs a versioned evidence-identity and wording repair before closure.

## Fixed artifacts reviewed

| Artifact | SHA-256 |
|---|---|
| `B15_ROUND_CONTRACT.json` | `806dd9bd7487d70e5c336a7fefb8418eb4f3205dddb10a5e603f1ee0de65a0e3` |
| `B15_SOURCE_AND_DESIGN.md` | `bdd43e5b9f0f3381e91b3e8ecb6d1d801785cbd25fb927a84ff28d56b39a3c8e` |
| `run_b15_policy.py` | `0c8868cec74133896500dc0f49ffd03120f22d883836e8570105566fad30cbf5` |
| exact JSON / NPZ | `d3543cfdec2b7df84f040eb42bfc6e66d7269576681b4f37d74408a7e8635758` / `d6363727be36927e33d2f534a5ed673aac1c6845dc8371a667786288775b9bf1` |
| warm JSON / NPZ | `755e4387d615134a50ca3dd2740149956e7e3c1b415652ac3e9fc8fe48b4a95f` / `7ccf0a0a7b1d5df5f1c2496cb5c76cd3dd3469ad8b6015f21df15aaa894efb91` |
| `diagnose_b15_rank_deficiency.py` | `f49dfa07cbf5a4c3c8d9be583024cddcf3b6d924533510aa08d591584f459a14` |
| rank diagnosis JSON | `ada1e833257a4f16692b4faedac21c61f1f2ec7447e3418eed03de2fb2ea3850` |
| `audit_b15.py` | `76b01ed780f795c0fdc7821ea477012de069eccc6a5fa85f464e0b36c204ecf0` |
| `B15_AUDIT.json` | `a65a2b6f939f26e27b755fc7fcc0a192fe875f35e918d96a5aa640e7bc08d060` |

Both result NPZ files pass ZIP CRC, and their JSON-recorded SHA-256 values match.

## Input and reference binding

The Landmark input is correctly hash-bound in both the contract and executable:

`d0de6bb598161e85557321a309e9d720cb1c398b722140725e47d8365e3ec68a`.

The two B09V2 reference files are named but not hash-bound in the B15 contract or audit input ledger. Their currently inspected hashes are:

- eta 0.1: `b7ab2139b4f38289085d5ee2a10737330d68938ffe28ad939ad183d7c276d083`;
- eta 0.01: `66c6d97fed7983abc55c8ccf5b571f2613281a627a9993584e243632a76355e6`.

Only eta 0.1 was executed, so the first hash is scientifically consumed here. A versioned closure record must bind it explicitly; naming a mutable path is insufficient.

## Trajectory and endpoint audit: PASS

Independent raw-array comparison against `B09V2_baseline_eta0p1_r0.npz` gives, for both exact and warm arms:

- query-mask mismatches: 0;
- update-mask mismatches: 0;
- maximum incoming-loss difference: 0;
- maximum queried-OPT difference: 0.

Both arms have 205 post-growth queries and 100 post-growth refreshes. Endpoint objective violations after the actual runtime behavior are zero. The maximum exact-endpoint excess/tolerance ratio is `1.137870659023934e-05`, far below one.

This parity does **not** validate a LOBPCG endpoint: all 71 refreshes at prefixes `t>=125` triggered the residual fallback, and therefore no late LOBPCG endpoint was accepted. Before `t=125`, the design intentionally uses exact SVD.

## Fallback semantics and SciPy behavior: PASS, with source-identity repair required

The program takes `residual_history[-1]` from SciPy. In the installed SciPy 1.17.0 source, the final history entry is populated after postprocessing of the best iterate, so using it for the declared residual-triggered fallback is semantically valid.

The observed totals are internally exact:

- late refreshes: 71;
- late residual fallbacks: 71;
- warnings: 213;
- counted row-Gram matvec columns: 3,550;
- accepted late LOBPCG endpoints: 0.

The first late refresh is at `t=126`, following the exact endpoint at `t=124`, matching the diagnosis setup.

However, the contract attributes the installed solver to commit `95e01a4004e2781c91a26d9836d82c103dd8513c` and blob `500db09374082fd24944fbcf936ffc492c28004c`. The actual installed SciPy 1.17.0 reports `scipy.version.git_revision=8c75ae75176236f233824e9a0483c26a69e6dfec`, and the loaded `lobpcg.py` bytes hash to `2789d5f25416abeb27e3515e0948d7413b64e241f445b0a19ae3abb856cb4c38`. The claimed upstream commit/blob may be a literature locator, but it is not proven to be the executed source identity. This mismatch requires correction rather than silent substitution.

## Rank-deficiency attribution: SUPPORTED, narrowly

The installed implementation B-orthonormalizes the active residual block by Cholesky. If that Cholesky fails, `_b_orthonormalize` returns `None`; the iteration loop emits the exact “Failed at iteration ...” warning and stops.

I independently reconstructed the initial Rayleigh--Ritz residual block at `t=126`:

- zero-extended initial block rank: 25;
- initial-block orthogonality error: `5.35e-15`;
- active residual columns: 25;
- active residual numerical rank: 2;
- residual Gram minimum/maximum eigenvalues: approximately `-5.16e-18` / `1.963`;
- residual norm on the old 124 coordinates: `2.23e-14`;
- residual norm on the two appended coordinates: `1.405`.

Thus the failure is not a rank-deficient initial block. It is a rank-deficient active residual block caused by zero-extending an invariant 25-vector block while adding only two rows. This directly supports the SciPy Cholesky-failure attribution.

The deterministic perturbation diagnostic is also correctly interpreted at its narrow scope: requested residual tolerance `1e-4` is reached, but endpoint excess is `412.2206` times the frozen objective tolerance. It refutes that one perturbation/tolerance repair only; it does not prove that every rank-adaptive, perturbed, or differently toleranced warm LOBPCG variant must fail.

## Early stop and CPU claim: PASS

The frozen falsifier says any residual-triggered fallback after `t>=125` falsifies the scoped hypothesis. Since the eta=0.1 repeat has 71 such fallbacks, stopping before eta=0.01 and repeats 1--2 is logically valid and saves budget.

The observed single-run CPU values are:

- exact SVD arm: `6.927752805` seconds;
- warm-with-fallback arm: `6.891581866` seconds;
- exact/warm ratio: `1.005248568`.

This roughly 0.5% difference is not evidence of a LOBPCG speedup: no late LOBPCG endpoint was accepted, the warm timing includes failed attempts followed by exact SVD, and only one dependent development process pair was run. The B15 audit correctly gives `pass=false` and makes no valid positive CPU claim.

## Route and next-action logic

Early retirement is justified for the **exact frozen comparator**: zero-extended previous endpoint, block size 25, SciPy LOBPCG tolerance `1e-8`, maximum 40 iterations, and the declared fallback. The audit label `RETIRE_WARM_LOBPCG_UNDER_FROZEN_STRICT_TOLERANCE` is too broad if read as retiring all warm/rank-adaptive LOBPCG constructions. Narrow it to the frozen implementation.

A randomized block-Krylov endpoint is a reasonable next existing-method comparator, but it is not uniquely implied by this failure and is not a new method. Before execution it must receive its own attributed source/collision record, frozen randomness/iteration budget, fair matvec accounting, exact endpoint-objective and trajectory checks, and a bounded native-512 calibration. Native-5000 remains correctly deferred.

## Required versioned repairs

1. Preserve all current B15 files and the negative attempt. Add the actual executed SciPy identity: version, reported git revision, loaded source path/hash, and relevant source-line behavior. Keep the claimed upstream commit/blob only as a separately labelled locator if independently justified.
2. Hash-bind the consumed B09V2 eta-0.1 reference NPZ in the closure/audit. Record the eta-0.01 reference as unconsumed because early stopping was valid.
3. Narrow the route decision to retiring this frozen zero-extended warm-LOBPCG comparator. Do not generalize the one perturbation diagnostic to all warm LOBPCG repairs.
4. Preserve the single-pair CPU numbers as diagnostic process timing only; do not promote them to a speed result.
5. If block Krylov is selected next, treat it as attributed prior-art comparator work and freeze its own source, randomness, work budget, semantic audit, and falsifier before running.

After repairs 1--3, the B15 outcome should close as a supported negative result without rerunning the full policies.

## Reviewer command disclosure

This B15 review used eleven bounded shell/source-inspection commands including the final readback, plus one `apply_patch` operation to write this report. One combined inspection command contained a failed Python import but still completed its independent source search; the failure did not affect scientific evidence. No full 7-second policy was rerun.

Only the independent arithmetic/rank audit was internally instrumented: wall `0.074944882` seconds, process CPU `0.074374450` seconds, peak RSS `70,840` KiB. Exact aggregate CPU/RSS for all verifier commands is unknown. The approximate sum of tool-reported command wall times, including final readback, is about 8.3 seconds.

## Claim limits

This review supports rejection of the fixed B15 comparator on the saved dependent Landmark-512 eta=0.1 development trajectory. It is not independent benchmark confirmation and establishes no new method, general LOBPCG impossibility, native-5000 result, recourse improvement, originality, generalization, or paper/Gate PASS.

## Signature

`/root/b14_independent_verifier` — independent B15 reviewer; no candidate, source, or result artifact modified.
