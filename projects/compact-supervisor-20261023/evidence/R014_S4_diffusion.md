# R014 S4 — perfect per-token posteriors can yield half invalid joint outputs

True two-token joint P(01)=P(10)=.5 and P(00)=P(11)=0: any valid sequence is alternating. Exact marginal predictions for each bit are P(X_i=1)=.5. Simultaneous INDEPENDENT sampling from these exact marginals yields P(01)=P(10)=.25 each, so P(valid)=.5. A learner can have perfect marginal prediction and still halve sequence validity when committing both positions independently. This is the *known factorization barrier*, not an original theorem.

Direct strongest accepted priors: ICML 2026 *Breaking the Factorization Barrier in Diffusion Language Models* (Coupled Discrete Diffusion / CoDD) explicitly represents joint interactions; ICML 2026 *SPEED*, *DAPD* and ICLR 2026 *ParallelBench* attack correlated parallel unmasking. General "make parallel decoding dependency aware" collides with these accepted results.

Decision: no ROOT leaf. A candidate higher-order dependence with verified failure beyond CoDD/DAPD/SPEED would require actual dLLM reproduction and a bounded new mechanism, which is not established by a two-bit CPU toy.
