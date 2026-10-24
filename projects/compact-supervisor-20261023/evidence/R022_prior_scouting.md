# R022 nearest source comparison and two scouting negatives
2026-10-24 research parent 3e0441a660973d8eacd2a5b61299a11b47fd18ca.

S9 precise prior list:
1. Li et al. ICML 2026 ARC-Decode https://proceedings.mlr.press/v306/li26gh.html . Official GitHub NeuraLiying/ARC-Decode@075e09aa11eedee798db6994d0265c57eca98160; model/utils.py blob caaaff31a217352f5070b161f940e39870c1e7bf, model/ea_model.py blob 38e1d9d250987050800cc8593de209c26aa0d574. Uses local shift/LTS with within-block accumulated margins/logit loss/U budget plus cross-round rolling quota. This is not a zero-budget method and published task quality is competitive.
2. Feng et al. *Approximate Speculative Decoding*, arXiv:2608.03447 (latest v3 Aug 2026, PREPRINT). https://arxiv.org/abs/2608.03447 . Source Kissmetothemoon/ASD@9426ce7b3b8cafb2d34f675a5bb9db2ebf0259f6 src/asd/budget.py blob 91ea4002e0a4796f8030a22d4e5b55ff35c75dd4 explicitly tracks RequestRiskState.spent across draft blocks. Objective greedy top-logit regret vs ARC probabilistic sampling distribution; related but NOT the same distribution metric or training/eval contract.
3. Classical KL chain rule + Pinsker and conditional TV maximal coupling, decades-old. No novel global-error theorem from these inequalities.

Separate scouting (not deep and NOT new active tree nodes):
- S10: diffusion few-step oracle-denoiser probability fidelity. ICML2026 Tang et al., *Is Your Diffusion Sampler Actually Correct?*, https://proceedings.mlr.press/v306/tang26ad.html already isolates sampler-only bias even under exact HMM posterior. Direct collision with broad “denoiser accurate but generated distribution incorrect”, also close to R014 diffusion factorization screen.
- S11: autonomous AI scientific experiment reproduction. ICLR2026 EXP-Bench https://proceedings.iclr.cc/paper_files/paper/2026/hash/c411f5b2d9c55f1685e72db224ad8b0e-Abstract-Conference.html and ICML2026 FIRE-Bench https://proceedings.mlr.press/v306/wang26d.html already establish weak end-to-end scientific experiment success, independent from any new proposed benchmark claim and overlaps R014 AI Scientist screens.
No model training, native CUDA, sampling distribution evaluation or paid API. All prior Await/Park nodes preserved.
