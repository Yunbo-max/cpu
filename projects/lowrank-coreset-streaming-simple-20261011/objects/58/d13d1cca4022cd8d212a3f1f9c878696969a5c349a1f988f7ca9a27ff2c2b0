# Independent B15 revision-closure check

- Reviewer: `/root/b14_independent_verifier` acting as the independent B15 verifier
- Reviewed at: `2026-10-10T21:51:12.988Z`
- Verdict: **PASS**
- Scope: closure of the three repairs in `INDEPENDENT_B15_VERIFICATION.md`; no policy rerun

## Fixed identities

| Artifact | SHA-256 |
|---|---|
| `B15_REVISION_RECORD.md` | `8d5449546df996caa5463f4d434d2c8251952df0a3bd7fd11d3590b65563f2fe` |
| `verify_b15_revision.py` | `acf0a5c8ff7c324095ca65e644c59efa09d4533190b857074931545ca728fce8` |
| `B15_REVISION_CLOSURE.json` | `6c7d827cb244128d10d3847563d6c92d6853060cd9bfdc491de20a9e154ed90d` |
| prior independent review | `2e5457d843dcb70d4c564d628a999df5dc18f23e4026a6d56ff63c86bb9a2e71` |

## Repair 1 — executed SciPy identity: PASS

Independent live readback matches the revision record and closure:

- SciPy version: `1.17.0`;
- `scipy.version.git_revision`: `8c75ae75176236f233824e9a0483c26a69e6dfec`;
- loaded source path: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/scipy/sparse/linalg/_eigen/lobpcg/lobpcg.py`;
- loaded source SHA-256: `2789d5f25416abeb27e3515e0948d7413b64e241f445b0a19ae3abb856cb4c38`.

The originally recorded upstream commit/blob is now explicitly retained only as a prior source-inspection locator, not the executed-source identity. This resolves the identity mismatch without mutating the failed run.

## Repair 2 — consumed and unconsumed references: PASS

The scientifically consumed eta 0.1 reference is explicitly bound:

`B09V2_baseline_eta0p1_r0.npz`  
`b7ab2139b4f38289085d5ee2a10737330d68938ffe28ad939ad183d7c276d083`.

The eta 0.01 file is explicitly recorded as unconsumed after the valid eta 0.1 early falsifier:

`B09V2_baseline_eta0p01_r0.npz`  
`66c6d97fed7983abc55c8ccf5b571f2613281a627a9993584e243632a76355e6`.

Independent hashing reproduces both values.

## Repair 3 — retirement wording: PASS

The closure decision is exactly:

`RETIRE_FROZEN_ZERO_EXTENDED_SCIPY_LOBPCG_COMPARATOR`.

The revision record binds it to block size 25, zero-extended prior endpoint, installed SciPy 1.17.0, tolerance `1e-8`, maximum 40 iterations, the `t<125` exact branch, and the frozen residual fallback. It explicitly rejects an impossibility interpretation for all warm, perturbed, rank-adaptive, or differently toleranced LOBPCG variants.

The deterministic `1e-4` perturbation remains a rejection of that single repair only. The CPU ratio `1.00525` remains diagnostic process timing and is explicitly forbidden as a LOBPCG speed result.

## Closure and limitations

The three required revisions are complete. The original negative experiment and prior `REVISE` review remain immutable; this record closes their evidence identity and wording only. No full policy rerun is needed because the eta 0.1 fallback falsifier already retired the exact frozen comparator.

This PASS does not establish a general LOBPCG limitation, a speed result, an independent benchmark confirmation, native-5000 behavior, recourse improvement, originality, a new method, or a paper/Gate PASS. The upstream locator itself was not re-authenticated; it is no longer used as execution identity.

## Command accounting

This revision check used four bounded shell commands including final readback, plus one `apply_patch` operation to write this report. No policy command was rerun. One audit command failed only because the verifier searched for a phrase without normalizing a Markdown line break; it did not reveal a candidate defect. The corrected independent check passed every identity/reference/scope predicate.

The corrected check was internally measured at wall `0.000407009` seconds, process CPU `0.000405242` seconds, and peak RSS `47,928` KiB. Aggregate CPU/RSS for all verifier commands is unknown; approximate tool-reported shell wall time including final readback is about 2.6 seconds.

## Signature

`/root/b14_independent_verifier` — independent B15 revision reviewer; no candidate, source, result, or closure artifact modified.
