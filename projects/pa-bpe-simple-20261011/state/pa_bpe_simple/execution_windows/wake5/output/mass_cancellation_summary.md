# Exact token-mass cancellation audit

Retrospective exposed English-French diagnostics only. Deltas are method minus Classical.

| arm | TICO dGagg | TICO dGmass | TICO mismatch | Books dGagg | Books dGmass | Books stable mismatch | Books stable aligned improvement |
|---|---:|---:|:---:|---:|---:|:---:|:---:|
| full_minmax | -0.03115302 | -0.01416629 | False | 0.00093072 | -0.00017800 | False | False |
| eff_minmax | -0.03107640 | -0.01470732 | False | 0.00177085 | 0.00035605 | False | False |
| exact_train | -0.00045475 | -0.00029725 | False | 0.00011794 | -0.00001070 | False | False |
| full_pooled | -0.02033367 | -0.01128634 | False | 0.00231989 | 0.00041569 | False | False |
| eff_pooled | -0.01821147 | -0.01171325 | False | 0.00588027 | 0.00179426 | False | False |

TICO cancellation-mismatch arms: []
Stable Books cancellation-mismatch arms: []
Stable Books aligned-improvement arms: []

These are deterministic exposed-set signatures, not causal or prospective evidence.
