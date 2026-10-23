# R016 original QED appendix and nearest-interference scope — source-based challenge

Parent research SHA 50990ec82d7684e1e44eb69279d3e78f1a5ba4b4; source inspection date 2026-10-23.

**QED original primary source:** Gupta, Das & Gupta, arXiv:2608.13668v1 (Aug 13 2026), https://arxiv.org/abs/2608.13668 .
- Section 3.1, Eq.6: a=b⊙k + lambda (I-kk^T)(b⊙q); the text explicitly says without the gate the layer could erase on every read and remove content that future reads still need. This anticipated future collateral is part of the ORIGINAL motivation, not discovered by L1.
- Eq.11 S_QED-S_GDN2=-lambda k (Sbar^T d)^T, Eq.12 current output projection via q. Any other fixed read r is a one-line projection, not new theory. All terms condition on unchanged Sbar, gates, k, q, v.
- Section 4.2 and Appendix A.1 Table 4: same-weight s-sweep (-1,0,.5,1,1.5,2) for two training seeds, scaling lambda at EVERY token, including prefill. Seed0 16K accuracy s0=41.4,s1=41.8, seed1 s0=55.0,s1=65.6; explicitly inconsistent. Table4 at s=1 gives lambda head MEANS .101 and .120, not the design maximum .25. Section 6.1 says this does not establish uniform reliance, and future training-time lambda_max sweep is necessary.
- The original authors did not report a fine-grained QED-specific multi-fact non-target break matrix conditioned on p, rho, beta that we could verify. That narrow empirical gap alone does not prove a new method.
- In Table 3, QED beats GDN2 on S-NIAH-1 extrapolation across both seeds (do not mischaracterize QED as a failed approach). Seed0 QED 16K 39.8 vs GDN2 21.8; seed1 59.8 vs 21.2. The lack of causal reliance of seed0 *online correction* is not equal to lack of trained-architecture benefit.

**Closest causal prior:** Lee, Park, Kim & Ko, *How Linear Attention Remembers*, arXiv:2609.33093v1 (Sep 27 2026), https://arxiv.org/abs/2609.33093 .
- Section 3.3 studies four facts and quantifies unintended non-target break 0.4%-1.4% after targeted pretrained-state edits; changes of a fact's state split into parallel/orthogonal components can change another fact's logit margin.
- Section 4.2 later key-aligned distractor writes lower original fact margin by approx 0.27-0.44 logits, with controlled norm-matched controls. This is direct evidence of recurrent cross-fact memory interference in GLA/GDN, but **NOT an experiment with QED itself**.
- Conclusions cannot imply all later QED effects are already quantified. The broad phenomenon and causal test design are nonetheless known; a standalone new-method claim would need novel model-specific measurement, corrective mechanism and independent strong comparison.

**Availability / use permissions:**
- GitHub connected search_repositories for exact title, "QED erase linear attention", authors and "query-derived erase" returned no matching repositories at the time checked.
- Web searches restricted to GitHub, Hugging Face and author/title did not verify official QED code / checkpoints; CatalyzeX marks "Request Code", which is weak evidence, not proof of global non-release.
- Hugging Face model_search and space_search connector calls failed with Tool not found; cannot assert HF-wide negative result.
- Public NVlabs/GatedDeltaNet-2 repository @de8476de0fecae08fc16f0bf3154900244c61c73 contains GDN2 code with NVIDIA source noncommercial license; not author QED code/weights.
- The How Linear Attention Remembers paper lists DIFFERENT existing GDN checkpoints (e.g., m-a-p/340M-20B-GatedDeltaNet-pure-baseline) and a complete GDN-only experiment. Not trained QED.

Formal separate Work reviewer verdict remains PENDING. No QED-trained full recurrence benchmark or multi-fact experiment executed.
