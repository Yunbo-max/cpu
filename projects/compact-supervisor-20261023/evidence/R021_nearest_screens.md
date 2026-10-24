# R021 additional mechanism-distinct primary-source screens (SCOUTING, not deep_complete)
Parent a7baafb3cd72bb39aa5bc762faac179ec9d92fb6. Four relevant 2026 primary papers inspected. These ideas were not converted to independent research nodes because a strong source already directly studies the same broad claim.

S1 — Visual token pruning retains confidence after removing decisive evidence: already arXiv:2604.12035 (Oct 4 2026), *Confidence under Visual Token Pruning*, and ECCV 2026 Kim et al., *Why and When Visual Token Pruning Fails?* https://research.nvidia.com/labs/twn/publication/eccv_2026_dstp/ (token relevance shifts during decoding). Query-adaptive and risk controlled remedies have been explicitly proposed. No trained MLLM was executed here; do not claim new finding.

S2 — Multi-agent teams prematurely converge on common information before asking for private clues: ICML 2026 HiddenBench, Li/Naito/Shirado https://proceedings.mlr.press/v306/li26ej.html, directly measures distributed info aggregation failures (published 30.1% vs 80.7% fully informed single agent) and structured communication improves. This is distinct from P1 and E1 but already occupied at a broad level; did not launch agents.

S3 — Calibrated confidence alone is inadequate for early-exit compute allocation: original ICML2026 EEFP paper and current repository already specifically derive and operationalize this; its online label-censoring version is fully detailed in separate deep record C1, but general selective-feedback methods exist.

S4 — Generic straight-through gradients in clipped/guarded operators can be biased: source explicitly acknowledges STE; AISTATS2026 Hooper/Shekhovtsov https://proceedings.mlr.press/v300/hooper26a.html is direct gradient-estimator theory. E1 adds concrete NVIDIA margin discontinuity, not a novel STE principle.

No automatic primary topic chosen; no new model/GPU experiments, no Work subagent reviewers, provider token charges unknown.
