# R021 C1 — Early-exit continuation outcomes are censored by the stop policy
Parent research checkpoint: a7baafb3cd72bb39aa5bc762faac179ec9d92fb6. Status **deep_mathematical_record / ROOT screen**, not an accepted new leaf.

## D1. Exact information boundary and decision
ICML 2026 Kubaty et al., *Rethinking Calibration for Early-Exit Neural Networks*, https://proceedings.mlr.press/v306/kubaty26a.html, official MIT repository gmum/rethinking-calibration-for-eenns@c87113e7ab5a5813d0dc3c0c251bb77c859f52c0. At shallow exit i, policy sees hidden features Z and shallow predictive confidence p, chooses stop (loss L_e, zero extra compute) or continue (loss L_f, extra cost c). Deep result and L_f are NOT observable at decision time if computation stops. In offline training, original `eval.py` blob e6c0e9316d0caf4aa12dc6f047560c86052e723d `compute_meta_losses` explicitly constructs a `heads_correct` array over ALL model outputs to supervise the EEFP confidence/failure predictor. No published performance claim is challenged by this distinction: offline full-head supervision IS available in the authors' original experiment.

## D2. Condition for optimal continuation and observational impossibility
For Z=z, continue iff E[L_e−L_f | Z=z] > c. Prediction confidence P(correct early | z) alone does not determine E[L_f | z] or the value of continuation, even under PERFECT calibration.
Construct 2 observable equal-mass groups A/B with identical shallow confidence .8 (20% expected error) and c=.05. Environment W+ has final error (A=0,B=.4); W− has (A=.4,B=0). Under an installed stop-all policy, the entire observable history (Z, shallow prediction, shallow correctness, action, cost) has identical distribution in BOTH worlds, since deeper outcomes are unobserved. Yet the optimal policy in W+ continues A only, and in W− continues B only; each has expected cost .125.
With probabilities q_A,q_B of continuing by group, W+ risk=.2 +.5(−.15q_A+.25q_B), W− risk=.2 +.5(.25q_A−.15q_B). Their average=.2+.025(q_A+q_B)≥.2. Hence minimax risk under indistinguishability is .2 (stop all), and compared to a world-specific oracle the unavoidable one-shot regret is .075 absent audits/model assumptions. This is basic missing-potential-outcome identifiability, not novel statistics. If full-head offline labeled data are available the impossibility DOES NOT apply.

## D3. Falsification, confounders, simple baseline
10,000-row deterministic synthetic table with 5,000 per group and exact 20% shallow errors reproduces costs:
stop all: both worlds .200;
continue A: W+ .125, W− .325;
continue B: W+ .325, W− .125;
continue both: both .250.
Randomly auditing deeper computation with probability .05 yields 487 audits in one seed-20261024 draw (average compute cost .002435 per input), identifies group-specific deep-error estimates A=0, B≈.4336 in W+. Conditional audit positivity restores learnability, and standard importance weighting/doubly robust estimators can apply when assumptions hold. The absence of audits is the operative confounder, not imperfect early calibration.

## D4. Closest strong prior and originality downgrade
Kubaty ICML2026 already addresses the confidence/continuation-value mismatch with EEFP and full-depth offline labels. Singhvi & Singhvi, Operations Research 2025 *Online Learning with Sample Selection Bias* https://doi.org/10.1287/opre.2023.0223 analyze censored final outcomes and bandit selection bias; Gong & Zhang ICML2026 *The Cost of Information: Phase Transitions in Contextual Bandits with Paid Observations* https://proceedings.mlr.press/v306/gong26i.html study exploration with paid observation. Generic intervention censoring and random auditing therefore HAVE KNOWN REMEDIES. We found NO distinct proposed new theorem or trained-model advantage.

## D5. Discriminating experiment & gates
Possible future test: official early-exit ResNet (authors' repository datasets CIFAR-100 or TinyImageNet), fit EEFP on full-depth train split, simulate DEPLOYMENT-ONLY online label stream with deterministic early exit and compare (i) no-audit adaptation, (ii) 5% randomized deep audit + IPS/DR, (iii) full-depth oracle labels at SAME inference compute budget and held-out group/shift regrets. Include calibration ECE, group correctness, effective compute cost and data leakage checks. This is an experiment design, NOT executed. Without real training/reviewer/GPU admission we cannot claim novel fix.

## D6. Decision
C1 is a **scouting/deep mathematical source-collision screen only**, not inserted as ROOT science leaf (max_children=8 already occupied). Next actor DESIGNER for newer distinct mechanisms; a separate real Work reviewer could independently check the math but none has been deployed. Exact CPU receipt and independent script committed. Provider/GPU/subagent/schedule status unchanged.
