# R022 S9 — local acceptance risk versus full-sequence distribution (D1–D6)

Project parent 3e0441a660973d8eacd2a5b61299a11b47fd18ca. **Status** deep_mathematical_record, source-bounded negative novelty, NOT active tree node / accepted paper contribution.

### D1 operator, information and objective
At decoding step t with realized prefix x_<t, target conditional law P_t(.|x_<t) and relaxed speculative output conditional law Q_t(.|x_<t) are distinct. ARC-Decode uses target verifier logits, draft token proposals and embedding/logit local tolerance tests to accept an extended prefix. Decision-time information: target scores for proposed nodes, not complete future generation. Cost is target-model verification passes, objective is throughput under sampling with quality constraints. Distinguish local next-token distribution shift from law of an entire sequence or semantic event after T steps.

Primary ICML2026 original: https://proceedings.mlr.press/v306/li26gh.html . Code: NeuraLiying/ARC-Decode@075e09aa11eedee798db6994d0265c57eca98160, model/utils.py blob caaaff31a217352f5070b161f940e39870c1e7bf (evaluate_lts around lines 1219, 1262, 1394); model/ea_model.py blob 38e1d9d250987050800cc8593de209c26aa0d574. Within ONE verification call, `alive` branches start at cum_margin=cum_logit=cum_u=0 and accumulate through proposal depth with local gates/budget table. Persistent across rounds is a rolling token window `win_soft`; the exact code read does NOT establish a global request-wide distributional divergence certificate. Do not claim no risk accounting.

### D2 exact math with all assumptions
For positive-probability target P and Q on sequences x_1:T,
KL(P_1:T || Q_1:T)=sum_{t=1}^T E_{x_<t~P}[KL(P_t(.|x_<t)||Q_t(.|x_<t))].
This is the KL chain rule (exact). Uniform per-prefix conditional bound ≤κ gives sequence KL≤Tκ and Pinsker sequence TV≤sqrt(Tκ/2) (conditional sufficient bound). Alternatively uniform conditional TV≤δ gives coupling sequence TV≤1-(1-δ)^T. Neither local JSD nor a local logit margin alone is directly a KL chain-rule bound without extra distribution/support assumptions.

Take independent sequences P=Bernoulli(.5)^T and Q=Bernoulli(.51)^T. Single-token JSD=.00005000583437 nats, TV=.01. Sum over binomial counts yields exact full sequence TV at T=10: .02484215, T=60: .0619216, T=100: .07986038, T=1000: .24812852, T=5000: .52051116. By choosing threshold sample mean between .5 and .51, the LLN implies a test event whose probabilities under P/Q tend to 0/1; hence sequence TV→1 even though every per-step JSD stays tiny.

### D3 falsifier, stronger semantic event and simplest repair
Independent target P(1)=1, perturbed Q(1)=.99 => single step TV=.01 and JS≈.0034783 nats. Task event “all T bits exactly 1” has P-success=1, Q-success=.99^T; at T=60 Q-success=.54715664, a .45284336 drop. No LLM assertion; this synthetic exact-match semantic constraint is adversarial by design, other tasks may be tolerant.
Simplest baseline zero relaxation (lossless EAGLE3 verifier) preserves target law. Sufficient request-level TV ledger: to ensure ≤ε via a uniform per-step bound, require δ≤1-(1-ε)^(1/T), for ε=.05,T=60 gives δ≤.000854522927. It is conservative, may slash speed, and depends on calibrated per-prefix conditional TV not local surrogate JSD. Adaptive risk allocation and recovery may help, but those are known decision/control motifs.

### D4 closest paper+code equivalence
ASD (Feng et al., arXiv:2608.03447, published as PREPRINT Aug 2026) already solves a RELATED issue: cross-block budget resetting, using a persistent regret ledger. Official code Kissmetothemoon/ASD@9426ce7b3b8cafb2d34f675a5bb9db2ebf0259f6 src/asd/budget.py blob 91ea4002e0a4796f8030a22d4e5b55ff35c75dd4 maintains RequestRiskState(spent,total_budget) and charges each relaxed mismatch. It is designed for GREEDY mismatch logit regret, not sample-level JSD guarantee; do not equate them. Most of the mathematical composition is classical; novelty UNRESOLVED/WEAK and no separate Work review accepted.

### D5 discriminating task-level protocol (NOT RUN)
Use ARC original GitHub Qwen3-8B and matching EAGLE3 checkpoint, with baseline posterior-lossless, original LTS, and verified request-budget variant. Predeclare length bins 60, 300, 1000; evaluate throughput, acceptance length, likelihood-ratio drift on synthetic tractable distributions, paired GSM8K/HumanEval pass rates; compare sample distributions with repeated-seed draws on small controlled vocab only. Control draft/tree depth, temperature, GPU/precision, calibration split, task difficulty, and failed/rejected tokens. Compare budget against throughput at matched absolute costs. Native model not run or authorized.

### D6 disposition and receipt
R022 exact CPU probe output pinned by SHA256 for executed program fb028ea0... and receipt 46791622... in conversation container; GitHub includes an equivalent program under evidence/. Actual process CPU 0.004123s, provider spend otherwise unknown. No new model result, no accepted theorem; S9 kept as screened-only candidate. Next actor designer for different source-backed scientific search, real independent reviewer for any S9 method/claim approval.
