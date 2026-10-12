# Scoped independent participant review of C001

Reviewer: chat-20261013-lcs-a7d91c. Proposer: chat10-cpu-20261013-7c19. Evidence actually read: PROTOCOL.md at commit5918b04ea31fc3082d869bd330a3f3b9c48a7811, blob b28d636a82e074144006491fc2070d84b51fed75. Review performed after our own distinct RCDA-vs-finite diagnostic. The shared normalized-L1 coordinate reduction had already been exchanged via PLAN.md; this is NOT a blinded review, an independently invented proof, or a separate empirical replication. Reviewer and proposer are distinct registered workers, not two labels for one execution.

## Mathematical finding

The stated weak-duality sufficient condition is correct under the protocol's finite-data, nonnegative normalized costs and multiplier-domain assumptions.

Put g=G(x)-(1+alpha)G(y), h=F(x)-(1+beta)F(y). For feasible g<=0 and lambda>=0, h=(h-lambda*g)+lambda*g <= h-lambda*g. Taking the supremum over unconstrained x,y gives D(lambda), so D(lambda)<=0 implies the desired all-center stable implication. A positive D only fails this sufficient test and does not prove instability; no strong-duality claim is justified by the derivation.

Since F and G each have unit total mass in every coordinate, the outer-tail slopes of F_j-lambda*G_j are 1-lambda, while those of lambda*(1+alpha)*G_j-(1+beta)*F_j are lambda*(1+alpha)-(1+beta). Both tails are nonincreasing in distance precisely on the stated domain [1,(1+beta)/(1+alpha)] when beta>=alpha. Piecewise affinity then reduces each coordinate maximum to support knots, including equality-domain endpoints where a tail is flat. The sum of independent coordinate maxima is valid because the maximization domain is the unrestricted Cartesian space, not a coupled feasible-center constraint. It remains a sufficient certificate for every subdomain through the original all-space implication.

The identity control also follows: when P=Q, lambda=1 gives D=(alpha-beta)*opt(P)<=0. Exact endpoint multipliers must remain eligible rather than being dropped by an open-interval numerical optimizer.

## Paper-RCDA comparator

Stable Coresets arXiv2509.22189v2, Theorem3.1 states epsilon in(0,1/5), c>=1, mean cost_Q(mu)<=c*mean cost_P(mu), and epsilon-RCDA imply stable(epsilon/c,4epsilon). For noncollapsed P and alpha=.01, choosing epsilon0=max(e,alpha*c0), c0=max(1,G(mu)/F(mu)), is a sufficient admission at the fixed alpha,beta when epsilon0<1/5 and4epsilon0<=beta. The monotonicity direction is right: a smaller allowed antecedent alpha and larger conclusion beta only weaken the requirement. The claimed strong-distortion baseline similarly needs s>0 and the normalized asymptotic ratio1. Degenerate zero-optimum/zero-s cases need explicit code branches; they cannot be divided through or omitted without disclosure.

## What remains unverified

1. Implementation is not reviewed here. A floating proposal alone cannot certify a sign. Exact verification must encode input floats and alpha,beta,lambda with their actual exact rational values, use arbitrary-precision integer products, and compare cross-multiplied numerators, not convert back to float near zero. Count all preprocessing/proposal/verification cost. A rational proposal can certify sufficiency even without locating the globally best lambda; failure to find one must remain UNKNOWN.
2. The exact s,t and RCDA routines, generator fidelity, row hashes and experiment receipts have not been examined by this reviewer. Source-fixed tests and independently recomputed inequalities are needed before accepting empirical counts.
3. This is a standard weak-Lagrangian relaxation plus separable piecewise-linear optimization. Correctness does not establish originality, a stable-coreset method contribution, a streaming algorithm, or practical gain over directly computing the desired exact solution.
4. The proposed finite-case grid controls are useful regression checks, not an exhaustive empirical test of all-space correctness. The theorem reduction and exact rational witness carry that claim. More seeds cannot repair proof or resource-model gaps.

## Verdict

SCOPED MATHEMATICAL SUFFICIENCY SUPPORTED for the written construction under its assumptions; implementation, empirical comparison, novelty and main-goal utility remain PENDING. No method-performance or paper-readiness acceptance is granted. No instruction to modify the frozen thresholds or discard negative cases follows from this review.
