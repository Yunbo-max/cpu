# R028 S15: integer one-point peer-forecast inversion in EPC-AW

D1 Source: accepted ICML2026 EPC-AW https://proceedings.mlr.press/v306/wang26ct.html and wzhSteve/EPC-AW@f9cc88080e929b29cfa909c2196d3121fd5129d1. Original MAS/epc_aw/models/planner.py blob 550bb08e50eff14087652bbbb6fb556e10436d58 and solver.py blob 515df206fec2684493624e8fd135733f5625db54. BTS(plan)=average across three agents of log[(own+eps)/(average two predicted peer scores+eps)]. Solver maximizes BTS then mean own score only as tie-break. Own and predictions are integer ratings1..5, not normalized success probabilities.

D2 Exact counterexample: all three agents assign high plan5 and low plan2, and all six peer forecasts per plan initially agree. Both BTS=0, high selected by tie-break. Change any SINGLE low forecast 2→1. One peer average becomes1.5; low BTS=(1/3)ln(2/1.5)=.0958940241505 >0 BTS high. Low rated plan selected.

D3 Negative control and synthetic sampling: Restore predictions to own scores -> select high again. Assume each of six forecasts of low plan independently underpredicts by exactly one point with probability epsilon while high forecasts stay exact: low selected iff at least one error, probability=1-(1-epsilon)^6. epsilon=.05 gives .264908109375. CPU 100000 NumPy draws seed20261024 gives .26638. All 25 constant integer peer forecast combinations were enumerated; 3 choose low. These are NOT empirical agent errors; lower own feasibility does not necessarily mean lower real task success, and BTS is intended to find underestimated candidates.

D4 Closest prior: Prelec 2004 Bayesian Truth Serum (https://pubmed.ncbi.nlm.nih.gov/15486294/), EPC-AW own epistemic calibration, UAI2026 Kostka correlated agent uncertainty and PMLR327 2026 ensemble miscalibration. No new theorem or calibrated selector proposed.

D5 GitHub recursive tree of pinned EPC-AW has 138 entries including only benchmark question JSON and scripts for log generation, not archived own/second-order score traces. No native LLM/agent run or paid API. Original scoring method transcribed verbatim into isolated CPU class script /mnt/data/r028/epc_bts_stress.py, SHA256 8fcdcf8c90cbac1e2278d88f999b2dae8e9778e175b582dd0b99cf175ae83f73, receipt SHA256 d6e6e696ef5d38b32efa5122d3151b3f52d368ab40737a7083d3311a2250d4a8. Proper test needs recorded real plan score forecasts with true verifiable outcomes and matched inference budget.

D6 Disposition: deep mathematical source audit only, no new active node or accepted ML method. Independent Work reviewer pending. No native model result, no GPU/API.
