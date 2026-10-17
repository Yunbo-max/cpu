# Sequential CPU research diagnostics: PRAXIS then CREDO

Date: 2026-10-17. Work was performed on the local Mac CPU only. The order was
PRAXIS first, then CREDO, as requested. These are developmental diagnostics, not
confirmatory experiments, a Gate A result, or evidence that either direction is
ready for a paper.

## 1. PRAXIS — completed first

Input: the author's `examples/compas_binarized.csv` bundled with the pinned
PRAXIS source (`ef6ce624cc40bcb00fcd39f4520364a3a05c8c80`). The source file
contains 4,966 rows, 44 binary features, and a binary label. We used the same
parameters as the existing reproduction: `lambda_reg=0.02`, `depth_budget=5`,
`rashomon_mult=0.03`, `lookahead_k=1`.

The fit returned the already reported objective 1992 and 28 trees. The additional
exploratory diagnostic computed each row's fraction of trees predicting the
positive class, then `2 * min(p, 1-p)` as a disagreement score. On the same data
used to fit PRAXIS, accuracy was 0.6623. Mean disagreement was 0.1459 among
in-sample correct rows and 0.2235 among in-sample errors. This is descriptive
only: there is no held-out split, and the sensitive-attribute columns are
derived threshold columns whose raw group coding was not recovered. Do not read
the result as a test-set uncertainty result or a fairness finding.

The initially considered Rashomon-group-fairness angle overlaps directly with
prior work on fairness, individual prediction flips, and selecting fair models
inside a Rashomon set. See [Dai et al., *Be Intentional About Fairness!*]
(https://arxiv.org/abs/2501.15634) and [Kallus et al., *Characterizing Fairness
Over the Set of Good Models Under Selective Labels*]
(https://arxiv.org/abs/2101.00352). This rules out presenting that broad angle as
our new contribution without a distinct observed failure and mechanism.

## 2. CREDO — started only after the PRAXIS diagnostic

Input: `runs/19-iclr26-credo/data/real_records.csv`, 168 monthly rows from
2011-01-31 through 2024-12-31 for four substations. We used the author's
`n_components=3`, `K=100`, `beta=0.5`, and empirical decision-rank metric, with
the source PTO baseline. Lower decision rank is better.

The pilot used 12 overlapping 24-month windows at 12-month stride, ordered by
increasing date so the temporal test period is in the future. Each window/split
had three fixed-seed replicates, for 36 runs per split protocol:

| Split protocol | CREDO mean rank (run-level SD) | PTO mean rank (run-level SD) | Mean paired CREDO−PTO rank |
|---|---:|---:|---:|
| Random | 2.056 (1.286) | 1.639 (1.199) | +0.417 |
| Forward temporal | 1.917 (1.381) | 1.917 (1.339) | 0.000 |

The pilot shows no stable CREDO advantage over PTO on this metric. These SDs are
descriptive only: the windows overlap, and replicates within a window are not
independent. The source metric ranks a chosen decision against the modal
test-period optimal decision; it does not measure conformal risk coverage or
calibration validity. Therefore this experiment cannot establish a temporal
calibration failure or support a CREDO method claim.

The existing notebook reports one unseeded random split per window with ranks
1.50±0.76 for CREDO and 1.67±1.31 for PTO. The repeated seeded random pilot
above gives 2.056 and 1.639 instead. It is not an exact rerun of that notebook
protocol; the difference confirms sensitivity to split/random-number sequence
on these small windows and must not be presented as a matched reproduction.

The implementation also recorded GMM convergence warnings in 6/36 runs under
each split protocol: only two distinct clusters were found where three were
requested. The full warning text and all run-level outputs are retained in
`credo_results.json`.

### Invalid temporal attempt retained in the audit trail

The source notebook reverses the data before forming its windows. My first
adaptation split those reversed rows as though they were ascending, so the
nominal temporal test data was actually older than training/calibration data.
That run is invalid and excluded from the table above. It yielded CREDO/PTO
mean ranks 1.806/1.417 on the incorrectly oriented split. The corrected run
above uses ascending dates. An initial launch through the lightweight `.venv`
also stopped at import because NumPy was absent; a subsequent run setup had a
`DatetimeIndex.iloc` coding error before executing any model fits. Both were
repaired before the captured final runs.

## Reproduction

From the PRAXIS run directory:

```bash
MPLCONFIGDIR=/tmp/praxis-mpl .venv/bin/python \
  -u ../../research/2026-10-17-sequential-pr21-credo/praxis_diagnostic.py
```

After that completes, from the CREDO run directory:

```bash
MPLCONFIGDIR=/tmp/credo-mpl OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .conda-env/bin/python -u \
  ../../research/2026-10-17-sequential-pr21-credo/credo_temporal_diagnostic.py
```

The scripts write JSON only into this new diagnostic directory. Existing
`runs/19-*` and `runs/21-*` reproduction outputs are not modified.

## Research disposition

- **PRAXIS:** the current broad model-multiplicity/fairness question has a close
  prior-work collision, while this local evidence lacks a held-out evaluation,
  verified group coding, and a natural downstream-harm census. No new PRAXIS
  claim is advanced from this round.
- **CREDO:** the small CPU pilot does not show an advantage over PTO and does not
  evaluate the method's advertised calibration guarantee. Any next step would
  first need a defensible failure endpoint and a better matched real-data
  evaluator. The current evidence does not justify a CVPR claim; no visual task
  is present in these assets.
- **Literature boundary:** CREDO's official ICLR 2026 paper describes a
  distribution-free decision-suboptimality bound; its theorem uses
  exchangeability. Sequential conformal work such as SPCI addresses temporal
  dependence for prediction intervals, while 2026 action-conditional conformal
  decision work addresses a different guarantee. A simple transfer of temporal
  calibration ideas to CREDO would therefore need a natural failure and a
  clearly distinct decision-level prediction before it could be considered a
  contribution. The search was a targeted triage, not a complete collision
  audit; see `literature_notes.md`.
- Do not convert either result into a confirmatory claim. A future research
  round must start from a documented natural failure, a qualified evaluator,
  and a prospective split/protocol frozen before unblinding.

## Autoresearch continuation — 2026-10-17

I resumed the loop from the saved results and initialized the skill's local
project record at `autoresearch/` (project ID
`a5a845ef-aa83-45c8-bc91-eec9bce23f33`). The record remains on
`audit_method/landscape`; no candidate or Gate A has been advanced. The full
hypothesis → test → result → decision chain is in
[`autoresearch/cycles.md`](autoresearch/cycles.md).

### CREDO continuation

- Warning audit: GMM warnings did not consistently track worse decisions;
  every warned forward-temporal run was tied with PTO.
- Monte Carlo audit: K=100 and K=10,000 chose the same action in 83.9% of
  matched random-split score draws and 73.9% of forward-temporal draws. The
  mean random-split rank stayed about 2.01 at all three K values, so larger K
  did not recover a CREDO advantage.
- Component-count diagnostic: on 24-month windows, 1/2 components had mean
  ranks 2.65/2.68, while 3/4 had 1.94/1.93 under random splits. The 3-vs-4
  difference was nearly all ties across windows; no component change is
  justified by these exposed data.
- Full-series diagnostic: on 50 random splits of all 168 months, CREDO mean
  rank was 3.95 versus PTO 1.76; CREDO ranked worse on 81% of score draws.
  Repeated splits reuse a single dependent time series and are not independent
  evidence.
- Data audit found lag-1 autocorrelation of 0.25–0.43 for three substations
  and large early/late mean shifts. In three chronological 24-month blocks,
  CREDO and PTO tied in rank each time (1, 5, 1). The observed vertexwise
  estimates were conservative in 82%–100% of comparisons, but there are only
  three blocks and exchangeability is not established.
- A targeted collision search found RADAR's decision-focused detection of
  operational suboptimality under distribution shift. This makes a broad
  “temporal decision-risk monitoring” claim unsuitable without a genuinely
  distinct problem or guarantee.

### PRAXIS continuation

- Ten stratified COMPAS 70/30 splits: PRAXIS accuracy 0.656 and disagreement
  error AUROC 0.577, versus logistic regression accuracy 0.674 and confidence
  error AUROC 0.629. PRAXIS Brier/ECE were 0.290/0.254 versus 0.210/0.033.
- A separate calibration-fold Platt map improved PRAXIS Brier/ECE to
  0.222/0.038 on COMPAS but did not improve selective error over the raw vote
  score; logistic regression remained better.
- On the 17,379-row bike dataset, ten matched splits showed PRAXIS below
  logistic regression on accuracy (0.843 vs 0.883), Brier (0.136 vs 0.083),
  and error AUROC (0.642 vs 0.856) in every split. Platt scaling improved
  calibration (Brier 0.1385→0.1243; ECE 0.1199→0.0258), but 80%-coverage
  selective error remained 0.116 versus logistic's 0.055.
- The new literature search found direct prior work on auditing incorrect
  predictions using ensemble margin plus local variability and on using
  calibration to reduce predictive multiplicity across credit-risk datasets.
  The broad “Rashomon disagreement/calibration as error detection” direction is
  therefore not advanced as a new contribution.

### Current decision and next action

These runs are developmental and retrospective. They do not support a CVPR
claim: none of the inspected tasks is visual, and no downstream impact study
was run. The two currently tested broad hypotheses have weak local performance
and close prior-work collisions. The next useful step is a bounded problem
intake from a consequential failure represented in the existing CPU assets,
then a fresh collision check before proposing another method. Do not treat
parameter tuning or a new split seed as a research contribution.

The conversation goal is active, but no unattended host continuation task has
been configured or verified. Experiments execute while the workspace session
is active; the saved checkpoint preserves the exact next step for a later
resume.

## Ordered continuation update — 2026-10-17

The additional PRAXIS collision screen found primary work directly covering
fairness over good models on recidivism/credit tasks, Rashomon prediction
reconciliation, calibration for predictive multiplicity, and consistency
scores for identifying likely incorrect ensemble predictions. Together with
the local held-out results (PRAXIS below logistic regression on both COMPAS
and Bike), there is no basis to advance the broad “Rashomon disagreement as
error signal, repaired by calibration” idea. This is a provisional screen,
not a formal collision `KILL`: the full query/citation protocol and separate
adjudication remain incomplete. It is a candidate-level stop/reroute, not a
failure of PRAXIS's core reproduction.

The next ordered line is CREDO. Its local chronological analysis shows
dependence and the primary paper's real-grid appendix uses assumed costs and
historical-average thresholds, while exchangeability underlies the guarantee.
The current 3-block check does not show decision harm or undercoverage, so the
next task remains literature/collision and natural-failure adjudication; no
new CREDO method or Gate A is authorized by the current evidence.

### CREDO source-baseline continuation — 2026-10-17

To strengthen the chronological diagnostic without tuning, we ran the pinned
source implementations of PTO, RO, and SPO+ beside CREDO on the same three
24-month future blocks and 67/33 pre-test fit/calibration partitions. All
methods used the same decision objective and empirical decision-rank endpoint.
Ranks (lower is better) by block were CREDO `1/5/1`, PTO `1/5/1`, RO `1/4/5`,
and SPO+ `1/6/1`. Thus CREDO tied PTO and SPO+ on every block; RO varied across
blocks. This is one dependent time series and three small test blocks, so the
comparison is descriptive only. DFL was unavailable because `cvxpy` and
`cvxpylayers` are absent from the pinned Mac environment. The script constrained
SPO+ to one worker and completed in 65.3 seconds. See
[`autoresearch/cycles.md`](autoresearch/cycles.md), Cycle 11, and the saved
JSON for per-block actions and details.

Cycle 13 then tested same-calibration selection in the paper's Setting I
(`sigma=0.1`) with 200 independent train/calibration replicates. The corrected
notebook-matched one-component GMM gave a mean selected score of 0.050 versus
mean true selected-decision optimality 0.341 (95% interval 0.335–0.347); the
prespecified origin's score/true rate were 0.040/0.390. The selected score was
very conservative, so this run did not expose the suspected optimistic
guarantee failure. The first 3-component attempt was a protocol error and is
retained but excluded. See `autoresearch/cycles.md` and
`credo_synthetic_selection_results.json`.

Cycle 14 checked this diagnostic against the paper's two separate evaluations:
pointwise conservativeness/accuracy over independent trials, and selected
decision rank on a test set. The paper itself already flags the same-calibration
selection caveat; adjacent post-selection and action-conditional conformal
work makes a broad correction claim unpromising. No failure or new method is
advanced. The next step is to search the retained CPU assets for a distinct,
documented failure with a measurable consequence.

Cycle 15 paired same-sample selection with fresh recalibration for the selected
vertex. Across 200 repeats, the selected score was 0.0500 on the selection
calibration set and 0.0413 on independent recalibration; paired difference
0.00869 (95% interval 0.00629–0.01110). The same-sample score remained far
below true selected-decision optimality (0.3445), so this diagnostic shows
score reuse inflation but no false certificate. This limitation is already
acknowledged in the CREDO paper and overlaps post-selection conformal work; no
new correction claim is advanced. See the frozen protocol and outputs linked
from Cycle 15.

Cycle 16 checked the retained task assets for an observed consequential
failure. COMPAS/Bike/MAGIC/breast-cancer are benchmark datasets, and the
deferral JSON files are visualization payloads rather than real deferral logs.
The CREDO solar appendix lacks actual upgrade costs/capacities and uses
assumptions; its temporal mismatch is a diagnostic concern, not an observed
harm event. No natural failure in the current assets supports a fresh method
experiment. The next step is to finish the collision audit and preserve this
provisional no-go boundary until a natural endpoint is available.
