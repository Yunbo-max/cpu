# R004 exact-prior and cross-domain scan (source-grounded)
Date: 2026-10-23. Parent Q-adam-prior-equivalence. Original research-project SHA: f27f6361919a9c375e4418c6d1f22de55f893496.

## Closest MoE papers and code
- Qiu et al., ACL 2025, Demons in the Detail: https://aclanthology.org/2025.acl-long.249/ and its paper Section 3 + Appendix A.2. Explicitly contrasts microbatch LBL with global-batch LBL, uses synchronized expert-frequency estimates and a running gradient-accumulation buffer as a global-batch approximation. This is direct overlap with the original prefix-buffer motivation. It is not a mathematical proof that this project's particular estimator equals Qiu's, and its exact prefix/cross-term operator has not been matched line by line.
- Balles and Hennig, ICML 2018, Dissecting Adam: https://proceedings.mlr.press/v80/balles18a.html, Adam sign and relative gradient variance already studied. R004's exact first-step sign explanation is consistent with that known mechanism, and no new MoE-specific optimizer advantage has been isolated.
- Chen et al., ICML 2026, phi-Balancing: https://proceedings.mlr.press/v306/chen26br.html ; equations 7-11 and mirror-EMA estimator at https://arxiv.org/html/2605.15403v1 . Existing convex-dual/EMA population routing fixes further weaken broad optimizer novelty.
- Megatron Core latest API documentation (inspected for context, source pin remains the prior audited NVIDIA commit): https://docs.nvidia.com/megatron-core/developer-guide/latest/apidocs/core/core.transformer.moe.moe_utils.html, which describes local probability contributions and desired-level count statistics. Documentation version is NOT treated as equivalent to the pinned prior Megatron implementation.

## Alternative novelty searches rejected for now
- RLVR within-correct diversity: ICLR 2026 paper Diversity-Preserving Hybrid RL https://proceedings.iclr.cc/paper_files/paper/2026/hash/6a1b224b153e55c40a6359f9c9fb9d8c-Abstract-Conference.html ; Uniform-Correct Policy Optimization arXiv:2605.00365 https://arxiv.org/abs/2605.00365 ; recent solution mode collapse arXiv:2610.11064 https://arxiv.org/abs/2610.11064 . General correct-solution diversity collapse is not an unoccupied new-method topic.
- LoRA factorization gauge symmetry / optimization geometry: ICLR 2025 LoRA-RITE https://proceedings.iclr.cc/paper_files/paper/2025/hash/bcbc0f660d2dde42f9d1d0ecb14a6f9a-Abstract-Conference.html ; ICLR 2026 Riemannion https://proceedings.iclr.cc/paper_files/paper/2026/hash/8505a7e1da40320bf5692d7edec5aa45-Abstract-Conference.html ; Oct 2026 Riemannian geometry arXiv:2610.08049 https://arxiv.org/abs/2610.08049 . Gauge correction alone is not novel.

## A distinct test from pinned, separately frozen EventTune evidence
- External repository and frozen SHA (READ ONLY): Yunbo-max/EventTune commit 3150cae1eecf2ee82e508d32fe7f2e80913f8149.
- Reports: reports/task_subspace_diagnostics.md (blob d985c5bd800ffe83784a9a38077f037e2282efde) and reports/iclr2027_evidence_audit.md (blob f7299093731cf78d89ce6135e7b8b1b99c2f2b3e).
- Verified measurement: Camelyon support-to-query gradient energy overlap 0.9362 on KV, but KV Macro-F1 0.5994; RoboFail KV overlap 0.7441, F1 0.4389; ManipBench KV overlap 0.7242, F1 0.2193. These are not matched identical-protocol comparisons across tasks, and some are diagnostic oracle rows.
- ManipBench query-basis KV diagnostic increases F1 from 0.2193 to 0.2482, still below formal LoRA 0.4304. Query-basis used query labels and is not a permitted adaptation baseline.
- The EventTune evidence freeze prohibits rerunning large GPU matrices or changing its main method; no mutations are made to EventTune.

## Novelty and status
R004 mathematically shows that gradient sign explains almost all R002 first-step updates and higher gradient moments can affect finite-state Adam updates even at equal sign/mean/variance. The latter is a generic nonlinearity effect, not a new algorithm.
The MoE prefix-balancing branch is **parked for new-method novelty** (not deleted; full R001-R004 evidence retained). The transfer to VLM is a different causal mechanism: retaining a surrogate gradient subspace may not preserve the *reachable output decision margins* under a bounded actuator. Its linear toy counterexample is exact, but whether the idea is publishably distinct from existing actuation/expressivity work is unresolved.
Closest adjacent expressive-capacity papers to review before any method claim: ICLR 2024 The Expressive Power of Low-Rank Adaptation https://proceedings.iclr.cc/paper_files/paper/2024/hash/154926e0b66e2b2a8c1120852f31a12d-Abstract-Conference.html and arXiv:2601.13989 Linearized Subspace Refinement https://arxiv.org/abs/2601.13989 . Neither is an audited equivalence for this proposed reachability certificate.
