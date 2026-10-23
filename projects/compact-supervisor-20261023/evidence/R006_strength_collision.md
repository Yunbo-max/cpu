# R006 alpha-spectrum novelty collision
Source: Yunbo-max/EventTune pinned commit 3150cae1eecf2ee82e508d32fe7f2e80913f8149;
reports/rank16_full_diagonal_alpha_sweep.md, 48 completed configurations,
not replicated model jobs in this Work turn.
Full KV descriptive mean Macro-F1 across four events:
alpha=.5: .271300; alpha=1: .281100; alpha=2: .333575;
alpha=3: .320825; alpha=5: .303150; alpha=10: .294175.
alpha2 - alpha10 = +.039400. Source explicitly warns that per-event
maxima are query-oracle, and nominally matching Hawaii alpha3 runs
disagreed (.3295 vs .2957). No significant training/robustness claim.

Nested effective edit sets A=alpha R/(1+||R||_F) do NOT mean
trained query Macro-F1 must be monotone in alpha, since fixed-step
raw-parameter optimization and generalization need not be nested.
Closest ICML 2026 theory already establishes steering-strength
non-monotonicity: https://proceedings.mlr.press/v306/taimeskhanov26a.html
Related expressive intervention work:
https://proceedings.mlr.press/v306/adila26a.html
Distinct trainable KV context does not warrant a broad novelty claim
without direct comparisons. Record this candidate as parked.
