# CPU coreset continuation: all-center RCDA diagnostic

Owner: chat-20261013-lcs-a7d91c. Project: lowrank-coreset-streaming-simple-20261011. Procedure actually loaded: autonomous-rsi-chat 0.2.0-autonomous-chat.10, inquiry-v4. This participant adopts it prospectively; old Simple records and any old scheduled invocation are unchanged.

## Scope and ancestry
Continue the user's CPU-only low-rank/coreset/streaming-statistics research. No LLM output-pool work, GPU, API calls or paid compute. This host has a 4-CPU quota and a 4 GiB cgroup limit; numerical work is serial, single-threaded. Retain legacy w001-w010 and its 36 recorded cycles as historical counts, not newly reproduced evidence. In particular, do not reopen the retired Nyström/RFF, moment-notebook, rank-saturated LRA, hashing or FID families. The old finite-pool coreset results are not universal-space certificates.

## v4 inquiry / selected lead
Question: can the full-space relative cost-difference approximation (RCDA) of a fixed l1 coreset be computed on CPU without enumerating candidate centers? This changes the verification object from a finite candidate pool or one fitted median to a supremum over all x in R^d. It is not a renamed coreset sampler and does not claim a new coreset construction.

Source: Carmel and Krauthgamer, Stable coresets: Unleashing the power of uniform sampling, arXiv 2509.22189v2, Eq.(4), Theorem 3.1 and Sec.6. Author code: amircarmel-lab/StableCoresets@48f0233eb65269b8552eb163f275627e5447921d, l1_coresets.py (blob 0289c060914c9d62e2e846fe7931056a84d63f61), tests.ipynb (blob 53681b9efdc1f216593bb8c51eb95ea63892d2f0). Ratio-to-parametric optimization is classical, not our novelty: Dinkelbach 1967, DOI 10.1287/mnsc.13.7.492. Closest-work coverage remains incomplete.

## Mathematical work product (prospective; independent review pending)
Assume P is a nonempty finite point multiset, with uniform normalized mass, and Q is a nonempty nonnegatively weighted submultiset with total mass normalized to one. Let mu be a coordinatewise median of P. Write b_j(t)=E_P|P_j-t| and q_j(t)=E_Q|Q_j-t|, and h_j(t)=b_j(t)-q_j(t)-b_j(mu_j)+q_j(mu_j). Define C_P(x)=sum_j b_j(x_j), H(x)=sum_j h_j(x_j), and E=sup_x |H(x)|/C_P(x). Require opt(P)>0; the collapsed-support case is handled explicitly rather than divided by zero.

1. Separability of l1 gives these coordinate sums exactly.
2. Both distributions have unit mass. Outside the union of their coordinate supports, h_j is constant, while b_j grows linearly. Therefore for a nonnegative ratio threshold lambda, s*h_j-lambda*b_j cannot improve by moving beyond that support interval.
3. Between consecutive coordinate knots, s*h_j-lambda*b_j is affine. Its maximum lies at a knot (including either endpoint of a flat interval).
4. With T_j the union of P and Q coordinate values, for s in {-1,+1}, F_s(lambda)=sum_j max_{t in T_j}[s*h_j(t)-lambda*b_j(t)]. Consequently E<=lambda iff both F_s(lambda)<=0. Coordinate maximizers give an explicit witness. This eliminates the Cartesian product, not the need to read the original data.
5. Compute coordinate costs by sorting and weighted prefix sums. Bracket each ratio with parametric bisection. Sorting is O(d(n+m)log(n+m)); each threshold test is O(d(n+m)). Floating arithmetic produces a numerical bracket, not a formally outward-rounded certificate.

Connection to source theorem: c=max(1,C_Q(mu)/C_P(mu)); when E<1/5, the paper's theorem supplies a sufficient stable (E/c,4E) condition (with a conservative upper bound for E in floating implementation). A large RCDA value is NOT by itself a violation of stable-coreset ranking. Median-fit excess and RCDA are different endpoints, and one must not be reported as the other.

## Discriminating checks and falsifiers
- Engineering/mathematical tests before the numerical study: exhaustive Cartesian-knot enumeration on small instances, direct absolute-distance recomputation of the returned witness, full-data Q=P identity, weight-scale invariance, constant coordinates and collapsed support. Native author integer and seed-42 random fixtures are reused. These are algebra/software checks, not new benchmark datasets.
- Primary diagnostic: author fixture exactly uses np.random.seed(42), np.random.randn(1000,10), then an m=100 without-replacement sample. Compare original Eq.(6) median excess, the RCDA maximum on observed data-point centers plus mu, and the all-center RCDA bracket. Do not tune the fixture after inspecting results.
- Transfer diagnostics on the locally distributed public Wine, Breast Cancer Wisconsin and Digits point matrices, unscaled and without labels, using source-faithful uniform sampling WITH replacement at m=32,64,128 and seeds 0..4. These are public-data development investigations, NOT reproduction of the paper's Taxi/Twitter/SCGE main results. Equal seeds across widths are not presumed paired; each coreset gets its own endpoint comparison. No inferential generalization from 5 seeds.
- Strong verification comparator: brute-force knot enumeration on small supported native projections; direct independently coded cost evaluation for every reported maximizer. It is an algorithmic cross-check by the same participant, not an independent agent review.
- If a witness exceeds the supposed upper bound, brute-force disagreement exceeds 1e-9, or normalization/tail conditions fail, stop interpreting the verifier and repair that version. No large campaign before this check.
- If all-center and observed-center maxima coincide, record that negative observation; do not alter data to manufacture a gap. If the diagnostic passes, retain exact witnesses and investigate the actual stable pairwise condition and prior-art overlap before claiming an algorithmic contribution.

## Cost and claims
Record elapsed and CPU seconds, peak process RSS, cgroup snapshots, installed versions, raw rows, source and data hashes. Include preprocessing and full-data verification costs. No sublinear construction-speed or bounded-memory streaming claim follows from this offline diagnostic. No new-method superiority, full native-benchmark completion, independent acceptance or paper-readiness is claimed.

## Execution/coordination
Execution requires a SHA-conditional claim in the existing shared registry and readback. Only this owner writes this namespace. No current/CHECKPOINT.json, legacy ledger, other participant packet or scheduled task is overwritten. This finite active-turn run is not a new global budget or a background service. Publish raw evidence and a next action; refresh peers before selecting further work.
