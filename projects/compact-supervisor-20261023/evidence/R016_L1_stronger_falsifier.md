# R016 controlled analytic negative result and correct full-horizon dependence

Original parent L1 (R015): current read gain can coexist with other fixed-probe loss under query-derived erase. New R016 evidence materially NARROWS it.

For p=P(current probe), rho=q^T k, beta in (0,1), lambda>=0, and Sbar=e2,k=e1,q=(rho,sqrt(1-rho²)), target output 0:
  R_QED - R_GDN2 = (1-rho²) lambda beta [-2 p rho + lambda beta (1-p+p rho²)].

For rho=.6,beta=.8, at real-paper-reported **mean** lambdas .101 and .120, threshold p_crit=lambda beta/[2 rho+lambda beta (1-rho²)] is respectively .06455 and .07610. Thus at p=.10, sign must be nonpositive for ALL beta<=1 if lambda is represented by those MEANS: threshold beta_crit=1.26936 / 1.06838. Actual tested delta risk with beta=.8 is -0.00229452 / -0.00185205. At rare p=.05 it turns positive (+0.000941903 / +0.002023096). The R015 p=.1/beta=.8 reversal used lambda=.25 (its MAX allowed, not the training means). CAUTION: mean lambda over heads is NOT actual per-head lambda; no empirical QED fault claim follows.

**Future recurrence matters:** If later operator matrices A_1,...,A_m and additive writes are held IDENTICAL across the compared streams, the delayed difference propagates exactly as
  Delta S_{t+m} = (A_m ... A_1) Delta S_t
              = -lambda (A_m...A_1 k) (Sbar^T d)^T.
For a read r: Delta o_{t+m}(r)=-lambda (r^T A_m...A_1 k) (Sbar^T d).
A future full overwrite along k, A_1=I-kk^T, annihilates the entire perturbation. Common alpha=.8 scalar decay attenuates its amplitude at lag five to .8^5=.32768. For truly trained QED trajectories, later k/q/gates, activations and writes can differ after the first intervention, invalidating this exact fixed-operator propagation. Such updates could erase OR amplify/cascade interference and must be measured, not assumed.

Executed CPU /mnt/data/r016_operator_audit.py SHA256 b7ba5c198d3e54429ed939e9676068ef0915e3d429c8841c5f81920c5907064c; raw JSON SHA256 71cbdc66cca21859906871a5891e6145210c0f799bd7738a5db4a3eac70a2176. 0.000712996 measured process CPU seconds, no model inference.

Consequence: Even the specific toy sign at p=.10 is not robust to trained reported strength. Combined with primary QED's future-read gate rationale and existing pretrained cross-fact interventions, L1 has insufficient distinct novelty and no actual learned-model evidence. Park standalone scientific-method claim, retain data/code and precise conditions to reopen.
