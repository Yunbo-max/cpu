# R005 mathematics: actual EventTune actuator and joint feasibility
Date: 2026-10-23. Current stage: discovery; mathematical diagnostics only.
Inherited parent: Q-vlm-reachable-margin, commit 0404c8e177e9b8c8b406e623862ac717b82caa9d.

## 1. Actual KV-TTT control set
The pinned Full ResidualKVController uses, at each hooked K/V projection,
    Z' = Z + M * [(Z B) A B^T], A = alpha R / (1+||R||_F),
where M is the visual-token mask, B orthonormal covariance basis, rank r=16,
and alpha=3 in the frozen primary task config.
For any finite real R, ||A||_F < alpha. Conversely every A with ||A||_F<alpha
can be represented by R=A/(alpha-||A||_F), including A=0.
This is an exact open Frobenius ball in *effective A* per selected module.
The raw coefficient norm has no fixed upper bound: R can diverge.
For two layers (14,27) x K/V, the primary method has four distinct blocks,
so the concatenated Frobenius norm is < alpha*sqrt(4)=6.
The single arbitrary radius B=1 used in R004 was an illustrative toy, not
the constraint of the original EventTune controller.

## 2. Gradient coverage is not actuator excitation
For a fixed hook and masked token rows define H=M*(Z B), D=(G B), where
G=d(loss)/dZ evaluated at the base point. With fixed upstream Z,
    d(loss)/dA = H^T D .
The gradient-covariance energy overlap reported by EventTune,
    rho=tr(B^T C_G B)/tr(C_G),
only measures GB. It says nothing about H= M*(ZB), which multiplies GB
to produce an actual learnable controller gradient.
A local bound is
    ||d(loss)/dA||_F <= ||H||_F ||D||_F.
Under an effective Frobenius ball alpha, the largest first-order change
in a scalar candidate-score margin is alpha*||H^T D_margin||_F.
If H=0, then this hook's output is EXACTLY unchanged for all finite raw
controller parameters and every A in the admissible ball: Z'=Z.
If all selected hooks have zero projected activation under the base forward
and all earlier hooks are themselves zero, induction shows an exact model-wide
no-op for that sample. One dead hook alone does NOT imply that other hooks
cannot act.

Toy: B=e1, Z_dead=(0,1), Z_live=(1,0), and G=e1.
In both cases gradient energy overlap rho=1, and if support/query directions
match, signed kappa=1. The dead site cannot modify Z. The live site can.
With a label-score offset chosen so both initial margins are -0.5, an
effective scalar A>0.5 corrects the live case but cannot correct the dead.
This is a conditional single-hook counterexample, not a measured VLM outcome.

## 3. Same single-sample reachability, impossible joint shared controller
Take the scalar controller a with |a|<3 (actual alpha-compatible rank-1 slice).
Three linearized binary margins:
    m1(a)=-1/2+a, m2(a)=-1/2+a, m3(a)=-1/2-a.
Each item is separately correctable by some permissible a.
Every controller corrects at most two of the three items, with maximum 2/3
classification accuracy. Gradient subspace capture remains rho=1 (dimension
one), and if support and query use the same three items, their average signed
margin direction is +1/3 and aggregate cosine kappa=1.
Thus first-order coverage, aggregate signed alignment and *separate*
per-example reachability do NOT imply JOINT feasibility with shared params.

For sample-competitor constraints indexed by i, write
    m_i(A) = b_i + sum_s <G_{is}, A_s>,
with ||A_s||_F<=alpha_s (closed ball used for sup; actual open ball has
the same supremum). Define optimal minimum margin:
    t_star = max_{A in product of balls} min_i m_i(A).
Finite-dimensional minimax gives the exact linearized dual:
    t_star = min_{lambda in simplex}
        [sum_i lambda_i b_i + sum_s alpha_s * ||sum_i lambda_i G_{is}||_F].
If an explicit lambda produces a nonpositive right-hand side,
no shared controller makes ALL these margins strictly positive.
For the three-item toy, lambda=(1/2,0,1/2) yields weighted gradient zero
and dual value -1/2. This is an elementary convex-dual/Farkas-type
certificate, NOT a claim of a novel mathematical theorem.
Caution: it only certifies that all cannot be jointly corrected, not the
exact optimal accuracy on a general dataset (the 2/3 value is toy-specific).

## 4. Correct task score and nonlinear scope
EventTune's task scorer chooses the candidate with largest *sum of target
token log probabilities* (teacher-forced log-likelihood), not a single raw
last-token logit. Thus meaningful margins must be differences between these
candidate sequence scores. Different candidate tokenization is part of the
actual implemented function. Use derivatives of that true score margin.

For a nonlinear full model with Hessian spectral bound L_i on the effective
control ball, the weighted margin upper envelope has an added remainder at
most 0.5 * sum_i lambda_i L_i * sum_s alpha_s^2.
No L_i or per-item projected gradients have been observed in the tracked
repository. Do not promote the linearized condition to a global model
certificate without these inputs. alpha=3 is not automatically a small
perturbation for Taylor approximations.

## Scientific interpretation and limits
1) Gradient energy != activation excitation.
2) Per-example correctability != existence of a single feasible shared TTA.
3) Site expressivity and actuator placement already have strong ICML 2026
precedents; gradient conflict/imbalance likewise has established work.
The above math is a code-specific failure test; it is not yet a new method
or a unique publishable contribution.
