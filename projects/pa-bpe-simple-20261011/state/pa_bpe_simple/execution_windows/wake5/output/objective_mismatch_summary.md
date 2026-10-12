# Aggregate-versus-sentence fairness diagnostic

All inputs are exposed English–French development diagnostics. Lower values are better; correlations are descriptive across related method variants.

## Central decomposition

- Classical TICO dev100 aggregate Gini: 0.03115302
- full_minmax TICO dev100 aggregate Gini: 0.00000000
- Classical mean sentence Gini: 0.03596402
- full_minmax mean sentence Gini: 0.02308448
- Aggregate relative reduction: 100.0000%
- Sentence relative reduction: 35.8123%
- full_minmax cancellation ratio: 1.00000000
- full_minmax mean absolute token gap: 5.06000000

## Descriptive rank correlations

- tico_aggregate_vs_tico_sentence: 0.950000
- tico_aggregate_vs_books_aggregate: -0.244118
- tico_aggregate_vs_books_sentence: -0.029412
- tico_sentence_vs_books_sentence: 0.029412
- books_aggregate_vs_books_sentence: 0.894118
- tico_aggregate_vs_books_cost: -0.914706

## Focus contrasts versus Classical

| arm | TICO agg Δ | TICO sentence Δ | Books agg Δ | Books sentence Δ | Books cost Δ |
|---|---:|---:|---:|---:|---:|
| full_minmax | -0.03115302 | -0.01287954 | 0.00093072 | -0.00017125 | 3.35175781 |
| eff_minmax | -0.03107640 | -0.01401234 | 0.00177085 | -0.00023474 | 3.77421875 |
| exact_train | -0.00045475 | -0.00023637 | 0.00011794 | -0.00003567 | 0.05214844 |
| full_pooled | -0.02033367 | -0.01068248 | 0.00231989 | 0.00024832 | 1.66933594 |
| eff_pooled | -0.01821147 | -0.01139299 | 0.00588027 | 0.00140193 | 1.46738281 |

## Frozen simple decision rule

Arms that improve Books mean sentence Gini or mean absolute token gap without increasing total token cost versus Classical:

[]

Arithmetic checks passed: 871 / 871.

This diagnostic can motivate a new objective derivation, but it cannot select or confirm a method on these already inspected data.
