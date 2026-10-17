# Targeted literature triage

Search date: 2026-10-17. Provider: web search. Read depth is recorded per source;
this is a targeted triage and does not satisfy the research-autopilot's complete
collision-coverage protocol.

## Queries

1. `site:arxiv.org Rashomon set decision trees fairness COMPAS group fairness multiple accurate models`
2. `PRAXIS Rashomon sets sparse decision trees ICML 2026 paper`
3. `COMPAS binary dataset PRAXIS race feature dataset paper`
4. `CREDO conformalized decision risk assessment decision risk guarantee ICLR 2026 paper`
5. `conformal prediction decision risk time series temporal dependence distribution shift calibration sequential decisions primary paper`
6. `conformal prediction decision making under temporal distribution shift decision risk time series paper`
7. `"Conformal Risk-Averse Decision Making with Action Conditional Guarantee" abstract`
8. `"Conformalized Decision Risk Assessment" exchangeability assumption CREDO theorem 1`
9. `Rashomon set calibration probabilistic predictions calibration uncertainty set of models`
10. `calibration predictive multiplicity Rashomon set selective classification error auditing`
11. `PRAXIS disagreement error detection predictive multiplicity ensemble margin audit`
12. `conformal decision risk temporal dependence time series decision optimization CREDO distribution shift`

## Retrieved primary works and evidence

- Heile et al., [From Rashomon Theory to PRAXIS: Efficient Decision Tree
  Rashomon Sets](https://proceedings.mlr.press/v306/heile26a.html), ICML 2026.
  Read depth D1 (PMLR abstract and metadata). It establishes PRAXIS as an
  approximate Rashomon-set enumerator for sparse decision trees; this is the
  implemented base method, not a candidate contribution.
- Dai et al., [Be Intentional About Fairness!: Fairness, Size, and Multiplicity
  in the Rashomon Set](https://arxiv.org/abs/2501.15634), 2025.
  Read depth D2 (arXiv HTML abstract and introduction). The paper explicitly
  studies fairness variation, fair-model selection, and individual prediction
  flips in Rashomon sets. This is a direct collision with the broad candidate
  of auditing fairness/disagreement across near-optimal PRAXIS models.
- Kallus et al., [Characterizing Fairness Over the Set of Good Models Under
  Selective Labels](https://arxiv.org/abs/2101.00352), 2021.
  Read depth D2 (arXiv HTML abstract and COMPAS application). It evaluates
  fairness ranges over similarly performing models on recidivism prediction,
  including COMPAS; this further weakens a generic COMPAS/Rashomon fairness
  novelty claim.
- Zhou et al., [Conformalized Decision Risk Assessment](https://arxiv.org/abs/2505.13243),
  ICLR 2026. Read depth D1 (official ICLR abstract and paper metadata; theorem
  assumption also located in the primary PDF indexed result). CREDO targets a
  distribution-free upper bound on decision suboptimality under exchangeability.
- Xu and Xie, [Sequential Predictive Conformal Inference for Time Series](https://proceedings.mlr.press/v202/xu23r.html),
  ICML 2023. Read depth D1 (PMLR abstract). It explicitly treats temporal
  nonexchangeability for sequential prediction intervals; it is adjacent, not a
  direct CREDO decision-risk replacement.
- Zhu et al., [Conformal Risk-Averse Decision Making with Action Conditional
  Guarantee](https://proceedings.mlr.press/v306/zhu26z.html), ICML 2026.
  Read depth D1 (PMLR abstract). It studies action-conditional safety guarantees
  for risk-averse decisions; its stated focus differs from temporal calibration
  of CREDO.
- Zheng et al., [Deciding When to Decide: Testing Operational Suboptimality
  Under Distributional Shift](https://arxiv.org/abs/2608.29465), arXiv 2026.
  Read depth D1 (abstract and metadata). RADAR uses inverse optimization to
  test a deployed decision's optimality gap under distribution shift and has
  sequential changepoint procedures. This directly narrows any proposed
  CREDO/time-series monitoring claim.
- Zhai et al., [Conformal Coverage of Time Series: Validity and
  Inference](https://arxiv.org/abs/2609.33868), arXiv 2026. Read depth D1
  (abstract). It studies split conformal coverage with adjacent calibration and
  test sets under temporal dependence; it concerns prediction coverage rather
  than decision optimality.
- Banerjee et al., [Measuring consistency via ensemble margin and local
  prediction variability: Auditing decision systems in the presence of
  predictive multiplicity](https://arxiv.org/abs/2609.01397), arXiv 2026.
  Read depth D1 (abstract). It directly studies diverting likely incorrect
  ensemble predictions using a consistency score combining ensemble margin and
  local variability. This collides with the broad PRAXIS disagreement-as-error
  audit idea.
- Cavus, [Mitigating the Multiplicity Burden: The Role of Calibration in
  Reducing Predictive Multiplicity of Classifiers](https://arxiv.org/abs/2603.11750),
  arXiv 2026. Read depth D1 (abstract and version metadata). It studies Platt,
  isotonic, and temperature calibration as ways to reduce predictive
  multiplicity across nine credit-risk datasets. This is a direct collision
  with broad post-hoc calibration of Rashomon predictions as a novel method.
- Haghighat et al., [Resolving Predictive Multiplicity for the Rashomon
  Set](https://ojs.aaai.org/index.php/AAAI/article/view/41076), AAAI 2026.
  Read depth D1 (official abstract). It proposes outlier correction, local
  patching, and pairwise reconciliation to reduce prediction inconsistency.
- Hsu et al., [The Double-Edged Nature of the Rashomon Set for Trustworthy
  Machine Learning](https://proceedings.mlr.press/v306/hsu26a.html), ICML 2026.
  Read depth D1 (PMLR abstract). It studies the trustworthiness consequences
  of Rashomon-set diversity, including robustness and privacy.
- Nguyen et al., [When Does Model Multiplicity Affect Prediction Intervals? A
  Sharp Phase Transition](https://proceedings.mlr.press/v337/nguyen26c.html),
  UAI 2026. Read depth D1 (PMLR abstract). It studies prediction intervals
  widened by Rashomon multiplicity and a Rashomon–conformal bridge.
- Cavus et al., [The Rashomon Set Has It All: Analyzing Trustworthiness of
  Trees under Multiplicity](https://proceedings.neurips.cc/paper_files/paper/2025/hash/c914b154c323d4d6c681d09dd679438c-Abstract-Datasets_and_Benchmarks_Track.html),
  NeurIPS 2025 Datasets and Benchmarks track. Read depth D1 (official abstract
  page); this is adjacent to generic trustworthiness evaluation of tree
  Rashomon sets.

## Boundary

No complete query-family/citation-expansion collision audit was performed, and
no novelty verdict is issued. The targeted search found direct collisions for
the broad PRAXIS disagreement/error-audit and post-hoc Rashomon calibration
directions, and an important decision-shift collision adjacent to CREDO. The
local CPU experiments also did not establish a method advantage over logistic
regression or PTO. A distinct candidate requires a documented natural failure,
consequential endpoint, and fresh collision protocol before Gate A.

## Continued source audit — 2026-10-17

Additional primary-source checks were made after the saved continuation
checkpoint. The PRAXIS paper lists COMPAS and Bike among its benchmark datasets
and reports Rashomon-set recovery; it does not establish a deployment failure
or downstream consequence on these datasets ([paper](https://arxiv.org/abs/2606.00202)).
The bundled PRAXIS input is already binarized and the asset manifest contains
only those features and the label, so raw protected-group coding is not
available for a defensible subgroup-harm analysis from this copy. Our held-out
weakness versus logistic regression is a diagnostic outcome, not a naturally
occurring deployment incident. The direct multiplicity/error-audit and
calibration collisions above remain decisive against advancing those broad
claims.

The CREDO paper's own real-world appendix describes 2010–2024 monthly solar
installation increments at four anonymized substations, says the utility
anticipated substantial monthly adoption growth, and states that its actual
upgrade costs/capacities were unavailable and replaced by unit costs and a
historical-average threshold. Its validity theorem assumes exchangeability.
These facts make temporal reliability of this particular certificate a
plausible consequential audit question, but not yet an observed harmful
decision: our three chronological test blocks tied the paper-native decision
rank and showed conservative empirical lower bounds, with too few blocks for a
validity conclusion. The source itself discusses selection-induced loss of
validity. This is an unresolved assumption/data-mismatch concern, not a new
method claim ([CREDO paper](https://arxiv.org/abs/2505.13243)).

Follow-up targeted queries (web search, 2026-10-17):

1. `site:arxiv.org PRAXIS Rashomon sets COMPAS error disagreement model multiplicity decision tree`
2. `site:arxiv.org COMPAS decision tree Rashomon multiplicity individual disagreement fairness held-out predictions`
3. `site:arxiv.org CREDO Conformalized Decision Risk Assessment real data solar substation exchangeability guarantee`
4. `predictive multiplicity uncertainty detect errors Rashomon set error detection model disagreement primary paper`
5. `Rashomon set disagreement error detection uncertainty classifiers selective prediction model multiplicity paper`
6. `ensemble disagreement detect classification errors local variability margin audit decision systems paper`

Read depth D2: PRAXIS and CREDO primary full texts were searched at the relevant
dataset, assumption, and limitation passages; exact passages are preserved in
the local papers under `cpu-paper-repros/papers/`. The search found no
additional validated natural failure or novelty evidence. It does not
constitute the complete collision audit required for an advancement decision.

The additional PRAXIS-neighbor search found more exact prior-work overlap:
Haghighat et al. (AAAI 2026) reconcile predictions within a Rashomon set using
outlier correction, local patching, and pairwise reconciliation; Banerjee et
al. (2026) explicitly use ensemble margin plus local prediction variability
to divert likely incorrect predictions for human review; Hsu and Calmon (2022)
formalize predictive multiplicity in consequential classification settings;
and Coston et al. (ICML 2021) audit fairness over good models on recidivism
and credit-scoring tasks. These sources cover reconciliation, error auditing,
the task framing, and COMPAS fairness respectively. Together with the held-out
negative baseline results, this rules out advancing the generic “PRAXIS
disagreement predicts errors / calibration improves it” atom. It is a
provisional collision adjudication from targeted source abstracts/full-text
passages; it is not a complete citation-network audit.

- Haghighat et al., [Resolving Predictive Multiplicity for the Rashomon Set](https://ojs.aaai.org/index.php/AAAI/article/view/41076), AAAI 2026; read D1.
- Banerjee et al., [Measuring consistency via ensemble margin and local prediction variability](https://arxiv.org/abs/2609.01397), 2026; read D1.
- Hsu and Calmon, [Rashomon Capacity: A Metric for Predictive Multiplicity in Classification](https://arxiv.org/abs/2206.01295), 2022; read D1.
- Coston et al., [Characterizing Fairness Over the Set of Good Models Under Selective Labels](https://proceedings.mlr.press/v139/coston21a.html), ICML 2021; read D1.

## CREDO selection-target audit — 2026-10-17

The exact CREDO target is fixed-candidate optimality probability: for a
prescribed decision `z`, Eq. (2) targets
`P{z in pi(Y; theta)} >= 1 - alpha(z)`. Theorem 1 states expected
conservativeness under exchangeable calibration data. The authors separately
warn that selecting a decision using CREDO scores and re-evaluating that chosen
decision on the same calibration data can invalidate the original guarantee;
they name data splitting as a simple mitigation and leave selection-adjusted
guarantees as future work. This confirms that the current data-selected action
rank experiment is not a test of Theorem 1. The contemporaneous temporal data
also do not establish exchangeability. Our per-vertex comparisons were only
descriptive diagnostics, and the chosen-action benchmark used 24 future rows.

The latest collision screen found several adjacent directions that require
formal comparison before any proposal:

- Zhu et al., [Conformal Risk-Averse Decision Making with Action Conditional
  Guarantee](https://proceedings.mlr.press/v306/zhu26z.html), ICML 2026. It
  provides action-conditional safety/utility guarantees for actions selected
  by a risk-averse policy. This is close to selected-action guarantees but has
  a different target from CREDO's probability that a fixed decision is
  optimal under a random objective.
- Jin et al., [Confidence on the focal: conformal prediction with
  selection-conditional coverage](https://academic.oup.com/jrsssb/article/87/4/1239/8113856),
  JRSSB 2025. This addresses selection-conditional predictive coverage for
  selected units, not inverse-optimization decision optimality.
- [Conformal Prediction After Data-Dependent Model
  Selection](https://doi.org/10.1080/01621459.2026.2663588), JASA 2026, and
  [Online Selective Conformal Prediction](https://jmlr.org/beta/papers/v26/24-0452.html),
  JMLR 2025, cover post-selection validity or online selection for prediction
  sets/intervals. These are methodological neighbors, not yet adjudicated as
  exact functional matches to CREDO's decision-optimality event.
- Gao et al., [A constructive approach to selective risk
  control](https://arxiv.org/abs/2401.16651), 2024, gives a broader framework
  for selective and extra-selection risks in compound decision problems. Its
  scope is broad enough that a full comparison is required before a novelty
  claim about selection-adjusted CREDO.

This is a targeted update, not a complete collision audit. It does not
establish novelty. Primary CREDO statements were checked in the local ICLR
2026 paper at Eq. (2), Theorem 1, and the selection-bias discussion; the
action-conditional paper was read from the PMLR 2026 abstract page and paper
overview, while the remaining neighbors were screened by primary abstracts.

### Known-distribution diagnostic outcome

The CPU check in Cycle 13 used the paper's Setting I at `sigma=0.1`, matching
the notebook's one-component fitted Gaussian, and compared one prespecified
vertex with the vertex selected by maximizing the same-calibration `get_prob`
score. Across 200 independent replicates, selected scores averaged 0.050 while
the selected vertices' true optimality probability averaged 0.341; the score
was therefore strongly conservative in this setting. The fixed origin's true
optimality frequency was 0.390 and its score averaged 0.040. Selecting from
the same calibration sample reduced the true optimality of the chosen action
in this experiment, but did not create score optimism relative to its true
optimality frequency. This is only one synthetic setting; it neither refutes
the authors' stated selection caveat nor establishes the theorem for selected
decisions.

The first run used three fitted mixture components by mistake (the real-data
count), not the one component used by the synthetic notebook. That output is
retained as an excluded attempt; only the corrected one-component output is
used above.
