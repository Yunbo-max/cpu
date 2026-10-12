# B15 versioned evidence-identity and wording repair

This record responds to `INDEPENDENT_B15_VERIFICATION.md` without mutating the
frozen contract, executable, raw outputs or failed attempt.

## Executed solver identity

- Installed package: SciPy `1.17.0`.
- Installed package git revision: `8c75ae75176236f233824e9a0483c26a69e6dfec`
  from `scipy.version.git_revision`.
- Loaded source path:
  `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/scipy/sparse/linalg/_eigen/lobpcg/lobpcg.py`.
- Loaded source SHA-256:
  `2789d5f25416abeb27e3515e0948d7413b64e241f445b0a19ae3abb856cb4c38`.

The upstream SciPy commit/blob recorded in the original contract is retained
only as a prior source-inspection locator. It is not the executed-source
identity. The installed source orthonormalizes the active residual block by
Cholesky; a failed factorization returns `None`, causing the observed
`Failed at iteration 0` exit.

## Consumed reference binding

The executed eta=0.1 B09 V2 reference is
`B09V2_baseline_eta0p1_r0.npz`, SHA-256
`b7ab2139b4f38289085d5ee2a10737330d68938ffe28ad939ad183d7c276d083`.
The unexecuted eta=0.01 reference is recorded for continuity but was not
scientifically consumed after the frozen eta=0.1 falsifier:
`66c6d97fed7983abc55c8ccf5b571f2613281a627a9993584e243632a76355e6`.

## Narrowed decision

The supported decision is:

`RETIRE_FROZEN_ZERO_EXTENDED_SCIPY_LOBPCG_COMPARATOR`.

It applies only to block size 25, the zero-extended previous endpoint, installed
SciPy 1.17.0, tolerance `1e-8`, maximum 40 iterations, `t<125` exact fallback,
and the frozen residual fallback. It is not an impossibility result for all
warm, perturbed, rank-adaptive or differently toleranced LOBPCG variants.
The deterministic `1e-4` perturbation diagnostic rejects only that one repair.

The single paired CPU ratio `1.00525` is retained solely as diagnostic process
timing. Because every late LOBPCG endpoint fell back to exact SVD, it cannot be
reported as an LOBPCG speed result.
