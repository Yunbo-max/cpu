# C001: All-center L1 coreset stability certificate

Procedure: actually loaded autonomous-rsi-chat 0.2.0-autonomous-chat.10 with inquiry-v4, goal-linked quality and GitHub-only cooperation. This participant does not migrate or resume the legacy Simple runner. Mode: ongoing research, first bounded investigation; not goal completion.

## Question, relevance and novelty limits
The parent goal is CPU-only low-rank, coreset and streaming-statistics research. Investigate whether a computable instance-wise certificate can cover ALL centers in R^d for L1 1-median, rather than the three-center finite-pool sampling procedure retired in legacy B002. This is an offline quality-certification problem, NOT a faster sampler, a streaming-memory claim, a new LLM output experiment or a proven new algorithm. Originality and genuinely independent mathematical review remain unresolved.

## Sources and transfer
Stable Coresets, arXiv:2509.22189v2, Definition 1.3, Theorem 3.1 and Sections 4/6. Author source amircarmel-lab/StableCoresets@48f0233eb65269b8552eb163f275627e5447921d, dimension_experiment.ipynb blob 503547cd6294e2ea4c9064680b113cb5184b0336: uniform WITH replacement; Gaussian generator centers randn*10, 5 clusters, randint assignments, randn noise*2. Use a declared reduced n=4096,d=16 version, not full paper replication. Real-data additional diagnostic: all sklearn packaged digits, raw 1797x64 integer features, no labels used. New paper arXiv:2606.30348 (Euclidean stable coresets) is recognized prior art, not claimed replicated or a certificate novelty clearance. No API/GPU/model generation.

## Public derivation (construction for investigation)
Let F(c)=mean_{x in P}||x-c||_1 and G(c)=mean_{x in Q}||x-c||_1. Both have unit mass; Q is a multiset of rows of P. Let alpha>=0,beta>=alpha. We want G(x)<=(1+alpha)G(y) => F(x)<=(1+beta)F(y), for ALL x,y in R^d.

Write g=G(x)-(1+alpha)G(y), h=F(x)-(1+beta)F(y). For any lambda>=0, g<=0 implies h<=h-lambda*g. Therefore
D(lambda)=sum_j max_z[F_j(z)-lambda G_j(z)] + sum_j max_z[lambda(1+alpha)G_j(z)-(1+beta)F_j(z)]
is an upper bound on every feasible h. D(lambda)<=0 is a sufficient stability certificate. D>0 is UNKNOWN, not evidence of instability. We do NOT assert strong duality or necessity.

Tail slopes make both maxima finite for lambda in [1,(1+beta)/(1+alpha)]. Within these bounds each 1D expression is piecewise affine, so its maximum occurs at a coordinate knot of P union Q (flat tails included at the end knots). L1 separability makes this an ALL-center bound, not a finite list of multidimensional centers. D is convex as a sum of maxima of affine functions. A floating scalar minimizer proposes a lambda only; acceptance must recompute D at a rational lambda with exact integer arithmetic. Encode every finite IEEE input using a common power-of-two scale; full/sample coordinate absolute-deviation sums are exact integers, divided by n and m. Do not rely on floating signs near zero.

DAG: normalized objective -> implication constrained maximization -> weak Lagrangian upper bound -> coordinate separability -> tail-domain bound -> finite knot maxima -> scalar proposal -> exact rational witness. Invalidating any assumption invalidates dependent certificate claims. No proof-length or operation quota.

## Strong baselines
1. Exact best multiplicative distortion: s=inf_c G(c)/F(c), t=sup_c G(c)/F(c), computed by exact separable fractional programming at coordinate knots plus asymptotic ratio 1. It certifies beta >= (1+alpha)t/s-1. This removes arbitrary multiplicative rescaling and is stronger than a fixed symmetric relative-error test.
2. Exact paper RCDA: median mu of P, e=sup_c |(F-G)(c)-(F-G)(mu)|/F(c). Set c0=max(1,G(mu)/F(mu)). Theorem 3.1 certifies when e0=max(e,alpha*c0)<1/5 and 4e0<=beta. Evaluate e by separable exact fractional programming. Never replace it with sampled centers.
3. P=Q identity control, exact coordinate median solution with its cost/timing, and direct finite-grid brute-force checks for small fixtures. Finite grids are implementation checks, not the all-center proof.

## Frozen first experiment
alpha=1/100. beta in {1/10,1/5,2/5}. Data: two independent author-generator datasets (data seeds 0,1, n4096,d16,kclusters5) and full packaged digits. Coreset sizes 16,64,256; independent sample seeds 40,41,42,43 using RandomState.choice replace=True. Thus 36 data/coreset cases and 108 tolerance settings. Identity controls separate. No new candidate tuning after outcomes. All data arrays, indices and source versions hashed before scoring. Full data access is permitted to ALL certificate methods and charged; this does not certify an unseen future stream.

Primary: exact certificate admission at identical (P,Q,alpha,beta). Guardrails: no false implication on exhaustive small checks; exact rational negativity, finite-input and unit-mass assumptions. Cost: full preprocessing plus proposal plus exact verification, peak RSS and full process wall; no kernel speed claims. Independent unit for sampled-Q variation is a sample drawn conditional on one dataset, not a new dataset; only two independent generated datasets and one real finite dataset. Report descriptive counts, not population confidence from repeated seeds.

## Predeclared decisions
If the dual admits settings rejected by BOTH strong baselines without validity defects, preserve the scoped gain and examine duality conservatism and closest prior art before expansion. If it is always equivalent/dominated, retire it as a new-method lead. If a verification bug occurs, retain failure and repair before interpreting. If it costs far more than computing the actual needed exact median, do not claim end-to-end practical speedup. No unrelated generic SVD/FD/FID/Nystrom/RFF reruns.

## Required unfinished obligations
Independent review unavailable in the current tool interface; no invented reviewer. Comprehensive prior-art clearance, large-scale native Taxi/scRNA/ranking comparisons, output-constrained use cases and full cost-benefit validation remain pending. The present experiment is a mathematical/protocol qualification and first bounded candidate comparison, not scientific acceptance.

## Resources and ownership
Current host observed 4 CPU quota, 4GiB hard RAM, numerical threads/concurrency1. Per command bounded timeout; no user lifetime research budget invented. Use owned local /mnt/data/lowrank_chat10 and this GitHub namespace only. Preserve legacy current/, snapshots and tasks. Direct container DNS failed; use connected GitHub for reads/writes. No new scheduler created.
