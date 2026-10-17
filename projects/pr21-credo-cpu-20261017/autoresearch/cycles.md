# Research cycle log

Project `a5a845ef-aa83-45c8-bc91-eec9bce23f33` · entry M · operating mode
run · current route `audit_method` · phase `landscape` · status active.

This is a research-loop record, not a Gate A protocol. All experiments are
retrospective developmental evidence because the assets and earlier results
were inspected before these follow-up designs.

## Cycle 1 — CREDO warning diagnosis

- **Hypothesis:** the GMM warnings (three components requested but only two
  clusters found) explain the worse CREDO decision ranks.
- **Test:** grouped the saved 72 run rows by split and warning presence.
- **Result:** random warned runs had mean paired delta +0.83 (n=6) vs +0.33
  without warning (n=30); forward warned runs were all ties (n=6) and the
  unwarned mean delta was 0 (n=30).
- **Interpretation:** warning association is not stable across split regimes;
  warning alone does not justify reducing component count.
- **Decision:** test the Monte Carlo estimator next, because K=100 is a
  consequential scoring choice and can be varied without refitting.
- **Evidence:** `credo_results.json` plus `README.md`.

## Cycle 2 — CREDO Monte Carlo K sensitivity

- **Hypothesis:** finite-K sampling noise at the author's K=100 materially
  changes action selection or explains CREDO's weak rank relative to PTO.
- **Test:** fixed each of the 72 model/calibration splits, varied only the
  score-sampling seed, and compared K=100, 1,000, and 10,000 over five score
  draws per K.
- **Result:** K=100 matched K=10,000 decisions in 83.9% of random draws and
  73.9% of forward-temporal draws; K=1,000 matched in 93.3% and 84.4%.
  Random-split mean ranks were 2.011, 1.994, 2.022 for K=100/1,000/10,000;
  forward-temporal ranks were 2.017, 2.089, 2.178.
- **Interpretation:** K increases selection stability but does not improve
  random-split decision rank; it does not explain away the PTO result.
- **Decision:** inspect GMM component count because each model saw only 10
  training rows in four dimensions with three components.
- **Evidence:** `../credo_mc_sensitivity.json`, `../credo_mc_sensitivity.py`,
  `../credo_mc_sensitivity.log`.

## Cycle 3 — CREDO component-count sensitivity

- **Hypothesis:** three GMM components overfit 10 training rows and hurt the
  selected decision.
- **Test:** same window/split seeds and test rows, K=1,000, components 1/2/3/4,
  three score draws per fit.
- **Result:** random mean ranks were 2.65/2.68/1.94/1.93; forward temporal
  ranks were 2.54/2.55/2.06/1.91. The 3-vs-4 difference was mostly tied at
  window level; four components had more convergence warnings.
- **Interpretation:** 1/2 components performed worse under this metric; the
  evidence does not select 4 over the source default 3 and is exposed,
  overlapping-window evidence.
- **Decision:** expand to all 168 months and a larger test subset to see if the
  earlier ties were only a tiny-test effect.
- **Evidence:** `../credo_component_sensitivity.json`,
  `../credo_component_sensitivity.py`, `../credo_component_sensitivity.log`.

## Cycle 4 — CREDO full-series random split

- **Hypothesis:** CREDO's disadvantage on 24-month windows is mainly caused by
  the eight-row test set; the full series will show a relative advantage.
- **Test:** 50 stratified random 67/33 outer splits of all 168 months, nested
  67/33 train/calibration split, CREDO ncomp=3/K=1,000, PTO comparator, three
  score draws per split; paper-native empirical decision rank.
- **Result:** mean CREDO rank 3.95, PTO 1.76; CREDO worse on 81.3% of score
  draws and tied on 2.0%.
- **Interpretation:** larger test sets did not reveal CREDO decision-quality
  benefit. Repeated random splits reuse the same temporal series and are not
  independent replication; exchangeability remains unverified.
- **Decision:** audit temporal dependence and run a chronological block check
  before interpreting the risk certificate.
- **Evidence:** `../credo_full_series_results.json`,
  `../credo_full_series_diagnostic.py`,
  `../credo_full_series_diagnostic.log`,
  `../credo_full_series_diagnostic_attempt1.log` (post-run version-attribute
  error retained; fixed before successful rerun).

## Cycle 5 — CREDO time structure and chronological holdout

- **Hypothesis:** random splits of the monthly series are inappropriate for
  claims about distribution-free risk guarantees because the data are
  temporally dependent and nonstationary.
- **Test:** descriptive autocorrelation/early-late summaries, then three
  chronological, non-overlapping 24-month test blocks with all prior history
  split chronologically into train/calibration. Compared paper-native rank and
  CREDO estimated optimality lower bounds with empirical test frequencies over
  20 score seeds/block.
- **Result:** lag-1 autocorrelation was 0.405/0.429/-0.040/0.250 across four
  stations; for three stations the early-vs-late means changed substantially.
  CREDO and PTO ranks tied in each future block (1, 5, 1). Empirical
  vertexwise lower-bound conservativeness fractions were 0.82/1.00/0.91.
- **Interpretation:** the random-split risk guarantee cannot be inferred from
  this dependent series. The three temporal blocks are too few to establish
  temporal validity; their ranking does not show CREDO decision advantage.
- **Decision:** targeted literature search; do not present temporal CREDO
  monitoring as novel without a distinct problem/guarantee.
- **Evidence:** `../credo_temporal_structure.json`,
  `../credo_temporal_holdout_results.json`, corresponding scripts/logs.

## Cycle 6 — PRAXIS held-out disagreement check

- **Hypothesis:** PRAXIS disagreement within a Rashomon set predicts held-out
  errors better than a simple classifier confidence score.
- **Test:** ten stratified 70/30 COMPAS splits; compare PRAXIS disagreement
  and logistic regression confidence, with error-detection AUROC/AUPRC, Brier
  score and ECE.
- **Result:** PRAXIS accuracy 0.656, error AUROC 0.577, Brier 0.290, ECE
  0.254; logistic values 0.674, 0.629, 0.210, 0.033.
- **Interpretation:** the in-sample association in the first diagnostic did
  not translate into strong held-out error detection.
- **Decision:** test whether calibration on a separate fold repairs probability
  quality without using test labels.
- **Evidence:** `../praxis_heldout_disagreement.json`, its script/log.

## Cycle 7 — PRAXIS Platt calibration on COMPAS

- **Hypothesis:** PRAXIS vote fractions are under-calibrated; a separate
  calibration fold may repair probabilities and improve selective error
  detection.
- **Test:** ten stratified 60/20/20 train/calibration/test splits; one-feature
  logistic Platt map of the PRAXIS vote fraction; logistic regression trained
  on the same training fold as baseline.
- **Result:** Platt changed PRAXIS Brier/ECE from 0.284/0.242 to 0.222/0.038.
  Error AUROC moved only 0.583→0.586 and 80%-coverage error 0.312→0.313;
  logistic Brier/ECE/AUROC/selective error were 0.210/0.033/0.636/0.295.
- **Interpretation:** calibration fixes probability scale but barely changes
  the ranking/selection utility; the simple comparator remains stronger.
- **Decision:** check the same pattern on the other substantive bundled CPU
  dataset, bike, with matched repeated splits.
- **Evidence:** `../praxis_calibrated_selective.json`, its script/log.

## Cycle 8 — PRAXIS bike replication and calibration

- **Hypothesis:** weak PRAXIS disagreement/error association is COMPAS-specific;
  bike data will show a useful Rashomon signal or calibration benefit.
- **Test:** first a one-split feasibility pilot; then ten stratified 70/30
  splits against logistic regression; then ten 60/20/20 splits with Platt
  calibration on a separate fold.
- **Result:** across ten 70/30 splits, PRAXIS accuracy/Brier/error-AUROC were
  0.843/0.136/0.642; logistic values were 0.883/0.083/0.856, and PRAXIS was
  worse on every split for those metrics. Calibration changed PRAXIS
  Brier/ECE from 0.1385/0.1199 to 0.1243/0.0258, but 80%-coverage selective
  error was 0.1155 vs logistic's 0.0554.
- **Interpretation:** the pattern is not specific to COMPAS; post-hoc
  calibration improves probability quality but does not make Rashomon vote
  uncertainty competitive with this simple baseline on these two tasks.
- **Decision:** targeted collision search. It found direct related work on
  ensemble-margin/local-variability error auditing and on calibration reducing
  Rashomon predictive multiplicity across credit-risk datasets. Do not advance
  this as a novel broad method.
- **Evidence:** `../praxis_bike_heldout_pilot.json`,
  `../praxis_bike_heldout_repeats.json`,
  `../praxis_bike_calibrated_selective.json`, corresponding scripts/logs.

## Current unresolved work and next selected action

The CREDO and PRAXIS broad candidate ideas are unadvanced: the local outcomes
are weak against simple baselines, and targeted literature searches found close
prior work. No visual task or CVPR-relevant outcome is present. The next action
is to continue method intake from an actual consequential failure represented
in the existing CPU assets, then perform a complete collision audit before
designing another method. Until that failure and its evaluator are identified,
do not add another parameter sweep or call the current observations a paper
result.

The conversation-level research goal is active. There is no configured or
verified background agent/scheduler in the workspace; these experiments run
only during an active session. Failed attempts/logs are kept adjacent to each
successful run, including CREDO path/import/version errors and the first
temporal-structure launch under the wrong Python environment.

## Cycle 9 — Continued natural-failure intake and source audit

- **Question:** do the existing PRAXIS or CREDO CPU assets contain an observed,
  consequential failure that can support the next research parent problem?
- **Inspection:** checked the reproduction inventory, retained COMPAS and Bike
  PRAXIS fixtures/results, the 2010–2024 four-substation CREDO data, and the
  corresponding primary papers at their dataset, theorem-assumption, and
  limitation passages. Refreshed targeted primary-literature search for
  Rashomon/COMPAS and CREDO/solar/exchangeability.
- **Finding — PRAXIS:** the paper's COMPAS/Bike entries are benchmark
  evaluations, not deployment incidents. The COMPAS copy is pre-binarized;
  raw group coding is absent. Our held-out regression-baseline gaps are
  researcher-generated diagnostics, not evidence of a naturally occurring
  harmful decision. Disagreement-as-error and post-hoc multiplicity
  calibration remain close to prior work.
- **Finding — CREDO:** the original real-world appendix says solar adoption
  was expected to grow, but the decision costs and capacity thresholds were
  unavailable and replaced by unit costs and a historical-average threshold.
  Exchangeability is an explicit theorem assumption. This is a concrete
  assumption/data mismatch worth auditing, but the available chronological
  check (three blocks) tied decision ranks and did not demonstrate harmful
  undercoverage; it is not a natural failure outcome yet.
- **Decision:** no parent problem passes the natural-failure/consequence
  screen from currently retained evidence. Do not invent a deployment claim
  or advance a method. PRAXIS intake remains first in the requested order;
  resume CREDO only after a defensible PRAXIS parent or a documented
  stop/reroute decision.
- **Evidence:** `../literature_notes.md`, the project README, local PRAXIS and
  CREDO papers, reproduction `RESULTS.md` files, and
  `../credo_temporal_holdout_results.json`.

## Cycle 10 — PRAXIS provisional collision screen and ordered reroute

- **Hypothesis:** the generic PRAXIS idea (Rashomon disagreement as held-out
  error signal, improved by post-hoc calibration) has a distinct mechanism or
  task-level result that survives closest-work comparison.
- **Test:** targeted retrieval across Rashomon multiplicity, error auditing,
  reconciliation, calibration, and recidivism/COMPAS; compare the local idea
  to each retrieved work's objective and observable outcome. Read the primary
  sources listed in `../literature_notes.md` at the abstract and relevant
  result/introduction passages.
- **Result:** direct prior work covers fairness over good models on recidivism,
  reconciliation of Rashomon predictions, calibration for multiplicity, and
  ensemble consistency for diverting incorrect predictions. The local held-out
  PRAXIS results were also worse than logistic regression on COMPAS and Bike.
- **Decision:** do not advance the broad PRAXIS disagreement/error-detection/
  calibration idea: it has multiple likely functional collisions and no
  benchmark advantage. This is a provisional screen, not the skill's formal
  collision `KILL` (coverage and independent adjudication are incomplete).
  Record the practical PRAXIS stop/reroute and continue in the user's fixed
  order with CREDO, examining the solar-grid temporal assumption/data mismatch.
  The CREDO line still needs a natural consequential failure, a complete
  collision audit, and a frozen parent/Gate 0 before any new method experiment.
- **Evidence:** `../literature_notes.md`,
  `../praxis_heldout_disagreement.json`,
  `../praxis_calibrated_selective.json`,
  `../praxis_bike_heldout_repeats.json`, and
  `../praxis_bike_calibrated_selective.json`.

## Cycle 11 — CREDO chronological comparison with source baselines

- **Hypothesis:** CREDO's tie with PTO on the three future blocks may change
  when compared with the paper's robust optimization (RO) and SPO+ baselines
  under the same chronological stress protocol.
- **Design:** reuse the three already exposed non-overlapping 24-month test
  blocks and the same 67/33 fit/calibration split. Run the repository's
  implementations of CREDO, PTO, RO, and SPO+ with the same transformed data,
  feasible decisions, and empirical decision-rank endpoint. CREDO uses one
  fixed score draw per block; SPO+ uses the source hyperparameters (lr=0.1,
  100 iterations) with its worker count constrained to one. No parameter sweep.
- **Result:** ranks (lower is better) by block were CREDO 1/5/1, PTO 1/5/1,
  RO 1/4/5, and SPO+ 1/6/1. CREDO therefore tied PTO and SPO+ in all three
  blocks; RO was better in the middle block and worse in the last. This small
  dataset does not establish relative superiority. The run took 65.3 seconds.
- **Interpretation:** against the available source baselines, CREDO has no
  observed rank advantage over PTO or SPO+ in this chronological diagnostic.
  DFL could not be run because `cvxpy` and `cvxpylayers` are missing from the
  pinned Mac environment. The three blocks remain one dependent time series,
  the endpoint is a rank over 24 observations, and exchangeability is
  unverified; this is not evidence about the advertised distribution-free
  guarantee.
- **Decision:** keep CREDO at diagnostic status. The next research action is
  to inspect the exact decision-risk theorem and assess whether this dataset
  can support a valid test of any advertised risk statement, then continue
  the collision audit. Do not propose a temporal method until a decision
  failure and valid evaluator are identified.
- **Evidence:** `../credo_temporal_baseline_audit.py`,
  `../credo_temporal_baseline_results.json`,
  `../runs/19-iclr26-credo/model/{ro,spo}.py`, and
  `../runs/19-iclr26-credo/exp2_decision.ipynb`.

## Cycle 12 — Map the formal guarantee to the available evaluator

- **Question:** does the chronological decision-rank experiment evaluate the
  guarantee CREDO claims, and is same-calibration selection an open direction
  after a targeted collision check?
- **Source audit:** Eq. (2) is about the probability that a *prescribed*
  decision is optimal under a random objective. Theorem 1 gives expected
  conservativeness when calibration data are exchangeable. The paper itself
  warns that choosing a decision using CREDO's estimates and then evaluating
  that chosen decision with the same calibration data can invalidate the
  original guarantee; it suggests splitting data and lists selection-adjusted
  guarantees as future work.
- **Evaluator finding:** our solar experiment selects the CREDO action by
  maximizing `get_prob`, then ranks that selected action on 24 future months.
  That endpoint is not Theorem 1's expectation over exchangeable calibration
  samples, and the observed time series does not establish exchangeability.
  Thus the baseline comparison is a decision-quality stress diagnostic only;
  it neither verifies nor falsifies CREDO's formal guarantee.
- **Collision screen:** found adjacent work on action-conditional risk-averse
  decision guarantees (ICML 2026), selection-conditional conformal coverage
  (JRSSB 2025), post-selection prediction-set validity (JASA 2026), online
  selective conformal prediction (JMLR 2025), and general selective/extra-
  selection risk control (2024). They do not all target the same event, but
  they make a broad “conformal guarantees after action selection” claim
  untenable without a theorem-level comparison. See
  `../literature_notes.md` for primary links and scope notes.
- **Decision:** keep the contribution question open but do not advance a
  method. The next bounded CPU task is a known-distribution synthetic check
  using the repository's CREDO generator: compare a decision fixed before
  calibration against a decision chosen from the CREDO scores, with repeated
  independent calibration/test draws and the theorem's exact fixed-decision
  event. This can determine whether a selection effect is measurable in the
  available setting; it cannot by itself establish novelty or repair the
  dependence problem in the solar series.
- **Evidence:** local `../papers/iclr26-21-credo.pdf`, especially Eq. (2),
  Theorem 1, and the selection-bias discussion; source implementation
  `../runs/19-iclr26-credo/model/conformal_dra.py`; targeted primary-source
  references in `../literature_notes.md`.

## Cycle 13 — Known-distribution fixed vs. selected decision diagnostic

- **Hypothesis:** selecting the highest CREDO score among the three feasible
  decisions using the same calibration sample may make the selected score
  optimistic relative to that selected decision's true optimality frequency.
- **Protocol:** use CREDO's published synthetic Setting I (`sigma=0.1`),
  `n_train=n_cal=100`, `K=100`, a 1-component fitted Gaussian (as in the
  notebook), 200 independent train/calibration replicates, and an independent
  1,000,000-draw reference sample for the three true vertex probabilities.
  Compare one decision fixed in advance (the origin) with the per-replicate
  argmax of source `get_prob`. Single-threaded CPU; no parameter sweep.
- **Invalid attempt:** the first implementation mistakenly used the 3-component
  model from the real-data experiment. It is preserved as
  `../credo_synthetic_selection_attempt3comp.json` and excluded. The corrected
  run follows the synthetic notebook's 1-component model.
- **Result:** true optimality frequencies were approximately 0.305/0.305/0.390
  for the two axis vertices and origin. Mean source scores were 0.036/0.037/0.040
  for these fixed decisions. The fixed origin score averaged 0.040 (normal
  95% interval 0.038–0.042). Under same-calibration selection, the score
  averaged 0.050 (0.048–0.051), while the selected decisions' true optimality
  averaged 0.341 (0.335–0.347); score minus true probability was -0.291
  (-0.297 to -0.285). Selection chose the origin in 84/200 replicates.
- **Interpretation:** in this one simple setting, selection increased the
  score modestly but did not produce an optimistic score-vs-frequency result;
  the score remained very conservative. The selected decision's true
  optimality was lower than the fixed origin's 0.390. This is not a
  counterexample to the paper's selection warning and cannot show general
  validity; it shows that this small setting does not expose the suspected
  guarantee failure.
- **Decision:** do not advance a selection-bias failure claim from this
  diagnostic. Next, read the paper's synthetic risk-estimation experiment and
  supplement carefully to verify whether this `get_prob` score and the
  fixed-decision theorem are being compared on the same scale. If compatible,
  stop the synthetic line as non-discriminating and return to a full collision
  audit before any method proposal.
- **Evidence:** `../credo_synthetic_selection_audit.py`,
  `../credo_synthetic_selection_results.json`, excluded
  `../credo_synthetic_selection_attempt3comp.json`, and the original
  `../runs/19-iclr26-credo/exp2_decision.ipynb`.
