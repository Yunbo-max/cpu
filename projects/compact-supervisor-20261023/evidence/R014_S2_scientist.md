# R014 S2 — best-of-N noisy experiments inflate reported gains, even if true gains are zero

Assume N independent scientific candidate methods all have real effect mu_i=0. Reported validation score is ε_i iid standard normal; the AI scientist chooses max_i ε_i. Then E[reported best] = integral_0^infinity [1-Phi(t)^N-(1-Phi(t))^N]dt >0 for N>1. It grows approximately sqrt(2 log N) as N grows, whereas the expected TRUE selected gain stays zero. This is classical Winner's Curse, not a new AI-scientist theorem. Without selection on noisy held-out metrics, the argument does not apply as stated. With correlations or varied true effects, the formula requires adjustment.

Actually evaluated values (sigma=1) via SciPy quadrature and independently by stdlib Simpson 3000 subintervals in this wake: N=1 0; N=2 0.56418958; N=8 1.42360031; N=32 2.06966883; N=128 2.59459737. Record at evidence/R014_root_math_receipt.json. These are mathematical expectations, NOT measured LLM agent discoveries, result p-values, or genuine false discoveries.

Very close paper: *The more you automate, the less you see: Hidden pitfalls of autonomous AI scientists* (2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC13663820/) directly documents post hoc selection and hidden methodological pitfalls of AI Scientist v2 and Agent Laboratory. ICML 2026 FIRE-Bench evaluates genuine rediscovery. Basic independent evaluation and noise penalty are existing statistical remedies.

Decision: source collision; broad S2 parked at screening without creating a new node. No statistical multiple-hypothesis training was run, and independent Work reviewer has not approved any new rule.
