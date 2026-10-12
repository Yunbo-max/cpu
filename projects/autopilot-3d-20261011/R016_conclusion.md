# R016 conclusion: internal gravity-pose status attribution

R016 is complete for its diagnostic scope. Under the pinned author solver commit, deterministic 5,000-problem generator, unchanged residual selector, and no positivity filter, the repaired v5 confirmation produced 10,000 solver rows and 28,574 candidate rows. The independent audit replayed every strict selector decision and the v5 output exactly reproduced the disclosed prior batch.

## Supported

- All unassigned diagnostic outputs coincide with zero returned real-root slots: UP1 96/96 (1.92%) and UP2 9/9 (0.18%). UP1 splits into 90 rows with invalid/degenerate recorded quartic state plus 6 finite/nondegenerate zero-slot rows; UP2 has 9 zero-slot rows.
- The native minimum-residual selector chose a nonpositive focal estimate despite at least one finite positive selectable candidate in 12 UP1 rows (0.24%) and 84 UP2 rows (1.68%).
- Exact candidate accounting, exclusive category partition, retained R015 generator identity, and no-positivity-filter markers all pass. The same binary's two full traces are byte-identical.

## Not supported

- The diagnostic NaN sentinel is not behavior-equivalent to the author's undefined read. It only prevents an invalid diagnostic access.
- R016 does not show that choosing the positive candidate improves pose or focal accuracy; full alternative poses were not retained and no intervention ran.

## Inconclusive

- The pose-quality effect of positivity-aware selection.
- Whether zero-root cases need polynomial scaling, an alternative real-root routine, or another numerical repair.
- Generalization beyond this deterministic synthetic author-generator stream.

## Repaired infrastructure and evidence

The generator's ambiguous function anchor, the analyzer's missing native-selector replay, runner database recovery, and the stale v2 plan binding were repaired with retained negative evidence. The initially observed batch was explicitly disclosed before the v5 confirmation; it was not retroactively presented as preregistered.

The next single hypothesis is `gravity-pose-positive-selector-v1`: record full alternative candidate poses and compare the unchanged native residual selector with the lowest-residual finite positive candidate only where a positive alternative exists. Zero-root and no-positive-candidate rows remain unchanged controls.
