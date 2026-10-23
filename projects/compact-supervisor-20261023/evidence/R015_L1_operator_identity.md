# R015 exact frozen-state collateral transfer and gate sign condition

Let Sbar = diag(alpha)S_prev be pre-update decayed state. Published GDN2 is S_GDN2=(I-k (b*k)^T)Sbar+k(w*v)^T and QED uses a=b*k+lambda*d, d=(I-kk^T)(b*q). The models share the same k,b,w,v,Sbar; only the erase vector differs.

Subtract recurrences:
  Delta S = -lambda*k*(Sbar.T@d).T
so the change for ANY held-state future read probe r is
  Delta o(r) = Delta S.T@r = -lambda*(r.T@k)*(Sbar.T@d).
The r=q special case is explicitly in QED preprint Eq.12; this generalization is elementary and NOT original.

For scalar value and b=beta 1, choose Sbar=e2, k=e1, q=(rho,sqrt(1-rho²)), r=e1, write=0, labels desired for both queries 0, let s=sqrt(1-rho²).
GDN2 reads: q -> s and r -> 0.
QED reads: q -> s(1-lambda beta rho) and r -> -lambda beta s.
Weighted read-probe squared risk is R = p error(q)^2 + (1-p) error(r)^2. Then

R_QED - R_GDN2 = s² * lambda*beta * [-2p rho + lambda beta(1-p+p rho²)].

For p=0.1, rho=.6, lambda=.25, sign changes at beta*=2p rho/[lambda(1-p+p rho²)]=0.5128205128. beta=.8 is STRICTLY INSIDE [0,1], and gives 0.064 vs 0.0726016, a 13.44% loss under the specified query distribution despite an improvement to current q. beta=.5 is below threshold and gives a slight gain. beta=1 limiting case gives 0.064 vs 0.08224 (+28.5%). At rho=0, current-query difference is 0, but r=k remains perturbed (no benefit to the orthogonal current query).

These held-state reads are NOT a complete model rollout: a genuine future token may perform another learned recurrent update, and attention projections/gates can depend on modified activations. All fixed-state claims must be downgraded if later learned dynamics erase the effect. The correct next experiment toggles online QED strength on the SAME trained checkpoint and measures immediate/future read errors, not simply compares two separately pretrained models.

Original private executed Python sources under /mnt/data: r015_qed_collateral_probe.py SHA256 2c62c8406e4654a09e6d06838baf4158e694344a8080988c3f827ed414b4907f and r015_threshold_probe.py SHA256 80b9c355a96b1b95d9889cd21cbbdfb251479e9b2b02ef688ac235b2f2066f20. Code in evidence/R015_L1_reproduce.py is a separate equivalent reproducer, NOT byte-identical. GDN2 source pin and QED v1 formulas checked. No GPU or real LM outcomes claimed.
