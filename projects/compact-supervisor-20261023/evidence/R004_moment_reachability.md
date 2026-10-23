# R004 mathematics: sign sufficiency, higher-moment counterexample and VLM reachability
Date: 2026-10-23. Internal designer derivation; not a formally independently reviewed theorem.

## Adam at its first step
Given zero m_0,v_0, the first bias-corrected Adam step in one coordinate is exactly:
U(g) = -alpha*g/(|g|+epsilon).
If g never equals 0 and |g|>>epsilon, U(g) is very close to -alpha*sgn(g).
Hence E[U(g)] approx -alpha*(P[g>0]-P[g<0]), regardless of gradient mean and variance.
On all original 72 pinned PyTorch prefix samples, the sign histogram predicts mean updates within 2.98e-9 maximum absolute coordinate error, with epsilon=1e-8 and alpha=.001. This is not a new optimization law.

## Mean, variance, and sign are not enough for finite-state Adam
Define two positive distributions:
A: g=2 or 4, each probability 1/2.
B: g=1 with probability 1/5, g=7/2 with probability 4/5.
Both have E[g]=3, Var(g)=1, P[g>0]=1. Their centered third moments are 0 versus -3/2.
Use common Adam hyperparameters beta1=.9, beta2=.999, alpha=.001, epsilon=1e-8 and t=100.
Condition on exactly the same feasible nonnegative previous moments:
m_99=(1-.9^99)*3, v_99=(1-.999^99)*(3^2+1).
For either distribution, define
U_t(g) = -alpha*((beta1*m_99+(1-beta1)*g)/(1-beta1^100))
         /(sqrt((beta2*v_99+(1-beta2)*g^2)/(1-beta2^100))+epsilon).
A high-precision Decimal scratch calculation produced:
E_A[U] = -0.00094859777588919409414...
E_B[U] = -0.00094861615462549457249...
E_B[U]-E_A[U] = -1.8378736300478346e-8 (not 0).
Therefore reducing a stochastic Adam gradient to just sign, mean and variance is NOT an exact equivalence theorem for arbitrary shared state.
This conclusion is generic for a nonlinear optimizer: it does NOT rescue a unique MoE method claim. For epsilon>0 and prior v>0, curvature/Taylor bounds from R003 apply. The context in which higher moments matter in practical training remains untested.

## Distinct mechanism transfer: bounded output reachability for frozen VLM editing
For task item i with correct label y, competitor j, frozen logit margin m0_ij=l0_i,y-l0_i,j,
and an editable subspace U with controller coefficients c obeying ||c||_2<=B,
linearize the output logits around c=0:
m_ij(c) = m0_ij + v_ij^T c + r_ij(c),
v_ij = U^T J_i^T(e_y-e_j).
If the margin-Hessian spectral norm is bounded by L_ij on the ball, then
r_ij(c) <= (L_ij/2)*||c||^2,
so max_{||c||<=B} m_ij(c) <= m0_ij + B*||v_ij|| + (L_ij/2)*B^2.
If this right-hand side is <= 0 for ANY competitor j, item i cannot be
corrected by this controller within the specified ball. Thus query
classification accuracy can never exceed 1 - N_certifiably_unreachable/N
within this bounded, fixed-model intervention class.
When L is unavailable, omit the remainder term but explicitly label the result
as a *linearized-model-only* upper bound; do not call it a certificate for the nonlinear VLM.

Exact 1D binary toy (L=0): margin m(c)=m0+c, |c|<=1.
Case A: m0=-2, max margin=-1, classification cannot be corrected.
Case B: m0=-0.5, max margin=+0.5, classification can be corrected.
Using identical support/query examples in each case, the 1D gradient-energy
projection ratio rho is 1 and the signed cosine kappa is +1 in both cases.
Yet achievable classification outcomes differ. Therefore rho and kappa alone
are insufficient statistics for bounded output-decision correction.

## Missing evidence and falsification
This is a geometry-vs-margin counterexample, not observed accuracy improvement.
A model-scale explanation requires actual frozen logits, action-site Jacobian
products, a justified control norm budget, and Hessian/remainder checks (if
claiming nonlinear validity), all with query labels used only as ORACLE DIAGNOSTICS.
If the controlled query margin bound flags no unreachable errors on the failing
frozen EventTune task, then limited linearized reachability alone does not
explain its recorded performance gap. If the budget or Jacobians are unavailable,
record that blocker and do not fabricate a certificate.
