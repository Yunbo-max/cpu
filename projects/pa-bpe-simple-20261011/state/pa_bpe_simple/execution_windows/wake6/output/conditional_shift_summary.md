# Conditional domain-shift decomposition

Retrospective exposed English-French diagnostics. Values below decompose Books mean minus TICO mean for each arm-vs-Classical row outcome.

Classical TICO length thresholds (nearest rank): q25=76, q50=120, q75=157 total tokens.

| arm | partition | outcome | TICO mean | Books mean | total shift | composition | conditional | larger |
|---|---|---|---:|---:|---:|---:|---:|---|
| full_minmax | baseline_gap_sign | macro_row_gini_gain | 0.01287954 | 0.00017125 | -0.01270829 | -0.01771397 | 0.00500568 | composition |
| full_minmax | baseline_gap_sign | absolute_gap_reduction | 3.47000000 | -0.26347656 | -3.73347656 | -4.52361067 | 0.79013411 | composition |
| full_minmax | baseline_gap_sign | total_cost_delta | 2.29000000 | 3.35175781 | 1.06175781 | 0.28522456 | 0.77653326 | conditional |
| full_minmax | baseline_length | macro_row_gini_gain | 0.01287954 | 0.00017125 | -0.01270829 | -0.00047491 | -0.01223338 | conditional |
| full_minmax | baseline_length | absolute_gap_reduction | 3.47000000 | -0.26347656 | -3.73347656 | -0.58451562 | -3.14896094 | conditional |
| full_minmax | baseline_length | total_cost_delta | 2.29000000 | 3.35175781 | 1.06175781 | -0.12301563 | 1.18477344 | conditional |
| eff_minmax | baseline_gap_sign | macro_row_gini_gain | 0.01401234 | 0.00023474 | -0.01377760 | -0.01800171 | 0.00422411 | composition |
| eff_minmax | baseline_gap_sign | absolute_gap_reduction | 3.51000000 | -0.41562500 | -3.92562500 | -4.01939067 | 0.09376567 | composition |
| eff_minmax | baseline_gap_sign | total_cost_delta | 4.85000000 | 3.77421875 | -1.07578125 | -0.67989743 | -0.39588382 | composition |
| eff_minmax | baseline_length | macro_row_gini_gain | 0.01401234 | 0.00023474 | -0.01377760 | 0.00080512 | -0.01458272 | conditional |
| eff_minmax | baseline_length | absolute_gap_reduction | 3.51000000 | -0.41562500 | -3.92562500 | -0.41270313 | -3.51292187 | conditional |
| eff_minmax | baseline_length | total_cost_delta | 4.85000000 | 3.77421875 | -1.07578125 | -0.45428125 | -0.62150000 | conditional |
| exact_train | baseline_gap_sign | macro_row_gini_gain | 0.00023637 | 0.00003567 | -0.00020070 | -0.00034918 | 0.00014848 | composition |
| exact_train | baseline_gap_sign | absolute_gap_reduction | 0.07000000 | -0.00253906 | -0.07253906 | -0.08960541 | 0.01706634 | composition |
| exact_train | baseline_gap_sign | total_cost_delta | 0.07000000 | 0.05214844 | -0.01785156 | -0.00528890 | -0.01256267 | conditional |
| exact_train | baseline_length | macro_row_gini_gain | 0.00023637 | 0.00003567 | -0.00020070 | 0.00003835 | -0.00023905 | conditional |
| exact_train | baseline_length | absolute_gap_reduction | 0.07000000 | -0.00253906 | -0.07253906 | -0.00303125 | -0.06950781 | conditional |
| exact_train | baseline_length | total_cost_delta | 0.07000000 | 0.05214844 | -0.01785156 | 0.01903125 | -0.03688281 | conditional |

Component size is not a causal attribution. Author-block sign checks and all 15 contrasts are retained in the JSON.
