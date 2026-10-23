# R014 nearest-neighbor audit: five independent ROOT hypotheses screened, none accepted

Frozen parent research commit: b896003e68b58a1bcf14dc671770204a587beb2f; date 2026-10-23. This is a scoped PRIOR SCREEN, not a proof that every possible related research question is occupied, and not a completed independent reviewer audit.

| Candidate mechanism | What would make the idea novel | Closest work and actual status | Decision |
|---|---|---|---|
| S1 Agent skill/library addition causes task degradation | An independently verified end-to-end mechanism beyond known negative transfer, mandatory procedures, skill selection and pre/postconditions | MSR *Agent Skills Can Be Harmful* (Aug 2026 **arXiv/preprint**, Microsoft Research page) analyzes 307 attributed failures; ACL 2026 SAGE demonstrates RL self-improving skill libraries; IEEE 2026 *Constraint-Consistent Skill Composition* already explicitly models preconditions/posteffects | broad claim collision; no active leaf |
| S2 More AI Scientist hypotheses/experiments produces worse reported truth | A genuinely new adaptive scientific inference failure not already covered by multiple testing, metric selection or post-hoc selection | 2026 *The more you automate, the less you see: Hidden pitfalls of autonomous AI scientists* (PMC) empirically tests benchmark choice, metric misuse and post-hoc bias in Agent Laboratory and AI Scientist v2; ICML 2026 FIRE-Bench measures actual rediscovery/evidence | classical and directly studied, no active leaf |
| S3 Better world-model pixel prediction hurts closed-loop control | A condition not captured by action conditioning, outcome fidelity or existing closed-loop tests, with new benchmark evidence | ICLR 2026 *World-In-World* directly reports visual quality insufficient for closed-loop success; Oct 20 2026 AMD technical article *Learning to Fail* explicitly tests same-state action-fork false successes (one-task industry technical report, NOT journal/conference). | broad claim collision, no active leaf |
| S4 More parallel masked-diffusion unmasking harms joint constraints | Higher-order dependency theorem or truly new correction beyond pairwise/factorization, actual model gains | ICML 2026 *Breaking the Factorization Barrier in Diffusion Language Models* (CoDD), *SPEED*, *DAPD* and ICLR 2026 *ParallelBench* directly analyze marginal independence / correlated tokens | direct math collision, no active leaf |
| S5 Stateful tool cache reuses valid output in wrong context | Distinct failure mechanism not matching state-key or replay misbinding | Feb 2026 TVCACHE preprint shows full tool history state key; Oct 2026 TRAP preprint defines tool-result misbinding; claims of first agent tool-cache state binding are unjustified | preprint collision, no active leaf |

**Citable original URLs (and scope):**
- https://www.microsoft.com/en-us/research/publication/agent-skills-can-be-harmful-an-empirical-study-of-skill-induced-failures-in-llm-agents/ (Microsoft Research, Aug 2026 arxiv publication page)
- https://aclanthology.org/2026.acl-long.69/ (peer-reviewed ACL 2026 SAGE)
- https://ieeexplore.ieee.org/document/11484408/ (IEEE 2026 explicit skill preconditions/posteffects)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13663820/ (2026 AI scientist workflow artifact and selection audit)
- https://proceedings.mlr.press/v306/wang26d.html (ICML 2026 FIRE-Bench)
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/5b4263be85820683d78675cc18d2efc7-Abstract-Conference.html (ICLR 2026 World-In-World)
- https://www.amd.com/en/developer/resources/technical-articles/2026/rl-inside-world-models.html (Oct 20 industry technical report; not peer reviewed here)
- https://proceedings.mlr.press/v306/li26fd.html (ICML 2026 CoDD)
- https://proceedings.mlr.press/v306/shen26z.html (ICML 2026 SPEED)
- https://proceedings.mlr.press/v306/kim26t.html (ICML 2026 DAPD)
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/9156b0f6dfa9bbd18c79cc459ef5d61c-Abstract-Conference.html (ICLR 2026 ParallelBench)
- https://arxiv.org/abs/2602.10986 (TVCACHE PREPRINT)
- https://arxiv.org/abs/2610.16333 (TRAP PREPRINT)

**Common failure reason:** All proposed high-level failures already have direct closest interventions/repairs and reproducible toy math. A model-free toy cannot establish an LLM/robot paper; arbitrary narrowing or renaming does not restore novelty. No code/GPU or original published implementation comparison was done. Future new leaf must name exact unsolved assumption, a source-pinned baseline not already addressing it, independently held-out benchmark, and falsifiable condition before active status. Missing approval, budget and reviewer gates remain intact.
