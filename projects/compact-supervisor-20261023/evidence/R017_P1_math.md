# R017 exact-k inclusion Jacobian audit (recovered original local work)

Original science Git parent 43b1dd770ce484a98f961591da4e3ea48411c4f2. Pinned ICML 2026 ProbMoE official repository HengHugoZhao/ProbMoE@3f0e538e8cab9b4b91f12479a0c0040c843723d2. Qwen Exact-k V1 source blob b06338fc66612f0e909c4b3fa954edabb662059a has log_q computed from detached log_p; OLMoE Exact-k V1 blob caa933e976bec9283e3ebac01adc347a1335cdf4 computes log_q from connected log_p and uses a separate probe in log_p+probe to differentiate exact marginals.

For fixed k and logits r, conditional selection P(z | sum z=k) is proportional to exp(sum_i z_i*r_i). It and softmax router weights do not change under r -> r+c*ones. With inclusion probability m_j=E[z_j], true derivative dm_j/dr_i=Cov(z_j,z_i).

The value of each computed m_j is exact for both implementations; however the Qwen V1 selected-logprob derivative, followed by the second derivative back through original logits, produces J_ji=(1-sigmoid(r_i))*Cov(z_j,z_i) because the nonselection factor is detached. OLMoE probe and connected nonselection term yields Cov(z_j,z_i). For r=(5,5), n2 k1: actual J00=.25; Qwen-path .001673212731, factor 149.41 smaller. Four experts k2 under global shifts -4,0,+4: Qwen J00=.23087643,.09518520,.00287668; correct and OLMoE J00=.23718483 invariant.

The PyTorch 2.10 CPU tests from R017 were re-executed and passed, but they were self-contained source-path mirrors, NOT the original imported classes or model checkpoints. Original executed file SHA256 8bbcd04a6a0d30a0ad911d7e886eba5c758dc3a82160955371ac311a546ce5d4; exact original receipt SHA256 9d0c8ff27b5604eb81b74c2a0d7b48db1a4b9ad8ab3903e875b4158cee9cbe5a (preserved in the R017/R018 conversation bundle).

ProbMoE Appendix F and AISTATS2026 Hooper/Shekhovtsov already study biased straight-through gradients. New-method originality is NOT established. Independent Work reviewer must confirm the intentionality of the source difference and model-level consequences. No GPU, paid API or training authorization.
