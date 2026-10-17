# R007 full protocol boundary, recorded after first full-run failure

The prospective script exited after source-row equivalence (2836/2836) at the
assertion requiring at least six initial 3-pixel inliers for non-minimal
refinement. The source R006 model rows show exactly two affected arm rows:
pair 83 and pair 101, both oracle arm, each with four inliers; both are valid
source hypotheses. The 48-pair pilot did not contain these two rows. No model,
correspondence, threshold, or candidate-pair eligibility has changed.

Correction before any full metrics were observed: for a source-valid arm with
fewer than six initial inliers, retain the initial pose as its refined output,
record `optimizer_success=false`, `nfev=0`, and an explicit skip reason. Count
these two rows in all 1418 paired qualified cases and disclose the skipped
optimization count. Other arms use exactly the frozen local optimizer. This
is a documented after-failure execution amendment, not a preregistered
decision. Report the overall metrics with these retained failures and avoid
describing this as a source-native LO-RANSAC baseline or independent test.

Failed first attempt: `runs/R007/full/first_attempt.log`, exit 1 in 2.25 s
wall time at the `mask.sum() >= 6` assertion. The source-equivalence check
printed 2836 matched rows before the failure. The failed run produced no
`result.json` and no outcome metrics.
