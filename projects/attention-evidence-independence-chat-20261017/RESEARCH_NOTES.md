# T001 — Evidence identity and multiplicity in attention

Status: paper/code reading and mathematical analysis. NOT an empirical architecture paper or a qualified execution producer. 2026-10-17.

## Motivation
A copied document and an independent corroborating document can contain identical text, but their statistical evidence strength differs. Standard softmax may increase a repeated distractor's total mass because each copy contributes a term to the normalization denominator. Conversely, global deduplication can erase independent agreement.

## Closest primary work (novelty NOT established)
1. **LUCID** (Duvvuri et al., ICML 2026), https://proceedings.mlr.press/v306/duvvuri26a.html; official source https://github.com/saisuryadv/LUCID, examined modeling_lucid.py blob f1169971c91f372435b486cca54665cf36bc868f. Key-key lower triangular exponential preconditioner and value transform; serious baseline.
2. **The First Drop of Ink** (Gao et al., ICML 2026), https://proceedings.mlr.press/v306/gao26b.html, attention competition from hard distractors.
3. **RA-RAG** (Hwang et al., EMNLP 2025), https://aclanthology.org/2025.emnlp-main.1738/, source reliability and weighted majority vote.
4. **How retriever redundancy and diversity impact RAG effectiveness** (Ross et al., 2026), https://arxiv.org/abs/2608.13956, duplicate vs diverse sources.
5. **Counting Copies as Evidence** (Rahadi, Aug 2026 position preprint; not peer-reviewed), DOI 10.5281/zenodo.21923648, conceptual risk already identified.
6. **Set Transformer** (Lee et al., ICML 2019), https://proceedings.mlr.press/v97/lee19d.html, earlier set attention and invariance.

Actual nearest-equation/native benchmark comparison is still incomplete. No first-of-kind claim.

## Mathematical questions and conditional results

**F1 — Token multiplicity:** For one relevant target with logit a and m irrelevant exact-score copies each with logit b, standard softmax assigns target mass exp(a) / (exp(a) + m exp(b)). For a=2,b=0, m=1 gives 0.88079707798; m=20 gives 0.26978133428. This is not a claim that Softmax always changes when identical tokens are repeated: if all keys AND values coincide, weighted-average output can remain invariant.

**F2 — An identification impossibility:** Suppose Y is a fair binary class and a source emits a correct + vote with probability p=0.75 when Y=+, incorrect + with probability 0.25 when Y=-. In world A one source's + observation is copied ten times, implying P(Y=+|ten observed plus copies,world A)=0.75. In world B ten conditionally independent sources emit ten + votes, implying posterior p^10 / [p^10+(1-p)^10]=0.999983065198984. Without source/dependence metadata, visible sequences are exactly the same. Any deterministic map from this sequence to a confidence must output the same number in both worlds and cannot satisfy both condition-specific calibration values. For an equal two-world mixture of these two desired target numbers, minimum mean-squared deviation of one output is (0.999983065198984 - 0.75)^2/4=0.01562288322157. This is a constructed information-boundary theorem, not LLM evaluation.

**F3 — Candidate quotient-by-(source,evidence) attention:** Let c(i) group tokens with equal keys, values, and verified source identity. Suppose each member of group c has the same attention logit s_c, value v_c and count n_c within the current query's causal prefix. Set corrected logit s'_i=s_c - log n_c. Then sum_{i in c} exp(s'_i)=exp(s_c), and the attention output is precisely Softmax over one token per class, independent of how many repeats the same source produced. Different independent sources have different class IDs and preserve their additive mass. This elementary identity is NOT claimed as a novel architecture by itself.

**Restrictions:** accurate source/dependency metadata is an external information requirement; position/RoPE can make repeated-token logits differ; key-only groupings may merge contradictory values; a copied upstream article can appear under new sources; training a usable differentiable and causal grouping layer is unsolved. Source reliability and provenance-aware RAG are prior art. Models with identical visible inputs cannot solve the constructed two-world distinction through attention reshuffling.

## Falsifiable research routes
- H1 (algebra): standard softmax shifts target mass with duplicate distractors, while exact source-count correction preserves it if class logits and values coincide. Numerically test only after guarded admission.
- H2 (information): no input-only method can distinguish deliberately observationally identical dependent vs independent evidence worlds. A claimed exception needs additional information or a changed scoring target.
- H3 (empirical, open): source-aware attention can improve out-of-distribution copy-shift calibration under reliable provenance without degrading independent-source accumulation, relative to strong simple priors and capacity-matched models. It can fail; do not call success until native comparisons.
- H4 (boundary, open): mistaken/spoofed provenance or position-sensitive logits can erase or reverse benefits. Must test and retain negative findings.

## Decision
Confirmed only the conditional algebra/information boundary. Next scientific step: implement faithful controls and establish native evaluation. Do not expand experiments for a 90-minute quota. Revisit novelty only after comparison against LUCID, RA-RAG, explicit source dedup and source-conditioned vote aggregation.
