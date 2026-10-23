# Internal mathematical audit: prefix Horvitz–Thompson variance

Date: 2026-10-23. Scope: bounded internal algebra verification requested by the integration owner. No literature search, novelty claim, model-performance claim, native model experiment, recursive delegation, or formal independent Work gate. Exact rational enumeration is mathematical diagnostic evidence.

## Verdict

Both requested statements are correct for fixed contributions and a uniform permutation:

E ||g_hat-T||^2 = [sum_i ||b_i||^2 + sum_(i<j) ||A_ij||^2]/(3 G^4),

and, for every individual permutation pi,

[g_hat(pi)+g_hat(reverse(pi))]/2 = T.

The variance formula holds for G>=1; at G=1 all antisymmetric sums are empty and both sides are zero. G=0 is undefined.

## Definitions and shapes

Let C_ij=f_i J_j be a fixed vector in R^d. For example, f_i can be a detached K-dimensional row vector and J_j a K-by-d router Jacobian. The result uses only the values C_ij, so it does not require their particular factorization, iid data, or probability normalization.

Define

T=G^-2 sum_(i,j) C_ij,
g_hat(pi)=G^-2 [sum_i C_ii+2 sum_(i precedes j in pi) C_ij],
A_ij=C_ij-C_ji, A_ji=-A_ij, A_ii=0,
b_i=sum_(j != i) A_ij.

For i<j write s_ij(pi)=+1 if i precedes j, and -1 otherwise. Extend it by s_ji=-s_ij. The product s_ij A_ij is invariant to reversing the labeling of the edge.

## Exact error representation and unbiasedness

For an unordered pair {i,j}, the full target includes C_ij+C_ji. The estimate includes either 2 C_ij or 2 C_ji. Their difference is therefore s_ij A_ij. Diagonal terms cancel exactly, giving

g_hat-T=G^-2 sum_(i<j) s_ij A_ij.

Under a uniform permutation E[s_ij]=0, hence E[g_hat]=T. This is the Horvitz–Thompson inclusion correction for directed off-diagonal contributions with inclusion probability 1/2. The edge-inclusion events are dependent, and their dependence is essential for the variance formula.

## Permutation sign moments

1. E[s_ij^2]=1.
2. If edges {i,j} and {k,l} are disjoint, E[s_ij s_kl]=0. The two relative orders are uniformly distributed; swapping the positions of i and j flips the first sign without changing the second.
3. For distinct i,j,k, orient both edges outward from their common vertex i. Then E[s_ij s_ik]=1/3. Among the six relative orders of these three indices, i is first or last with total probability 2/3, giving sign product +1; i is in the middle with probability 1/3, giving sign product -1.

The third identity must be used with the corresponding orientation of A. In an increasing-index convention, a chain-shaped pairing can have sign covariance -1/3; pretending every shared-edge covariance is +1/3 without reorienting A is an error.

## Vector mean squared error proof

Set S=sum_(i<j)||A_ij||^2. Let

U=sum_i sum_(j<k; j,k != i) <A_ij,A_ik>,

where each term uses edges oriented outward from the common vertex i. Each pair of distinct edges sharing one vertex occurs exactly once in U. Expanding the squared error and applying the sign moments gives

G^4 E||g_hat-T||^2 = S+(2/3)U.

On the other hand,

sum_i ||b_i||^2
 = sum_i sum_(j != i)||A_ij||^2 + 2U
 = 2S+2U.

Eliminating U yields

S+(2/3)U = [S+sum_i||b_i||^2]/3,

which proves the requested expression.

A stronger matrix version also follows by replacing inner products with symmetrized outer products:

Cov(g_hat)=[sum_i b_i b_i^T+sum_(i<j)A_ij A_ij^T]/(3G^4).

The stated MSE is its trace. In particular, zero permutation variance requires every A_ij=0; cancellation of the b_i alone is insufficient in the general C_ij setting. This criterion concerns the estimator at fixed records, not properties of a trained model.

## Exact forward/reverse cancellation

Reversing a permutation flips every pairwise order: s_ij(reverse(pi))=-s_ij(pi). Therefore the reverse error is exactly the negative forward error:

g_hat(reverse(pi))-T=-(g_hat(pi)-T).

Averaging gives T identically, without needing to randomize pi or average over additional permutations. Equivalently, the two passes include both orientations of every off-diagonal pair once after averaging, while preserving the diagonal contribution.

This exact identity does not imply a free computational gain: an implementation must obtain the relevant gradients for both orders or otherwise reproduce their algebraic sum. Runtime, graph retention, repeated forwards, memory, and random-number coupling require separate implementation accounting.

## Implementation and gradient assumptions

- Hold parameters fixed throughout the estimator and any paired reverse pass; update only after the intended accumulation. Sequential optimizer updates alter J_j and invalidate the fixed-record cancellation.
- Preserve f_i and J_i for each microbatch under reordering. Capacity-dependent routing, batch-dependent operations, sequence repacking or changed attention context can break this condition.
- With dropout, exact cancellation requires the same per-microbatch random realization across both passes, or cached contributions. The same global seed alone need not associate the same masks with a microbatch after reversing order.
- Treat f_i as detached if this is the intended applied gradient. The audit concerns the resulting vectors f_i J_j and does not add gradients through routing frequencies.
- Uniform permutations are required for the displayed unbiasedness/variance law. Exact forward/reverse averaging is valid for ANY initial order, provided its fixed records are preserved.
- Equal microbatch means and the 1/G^2 normalization must match the real implementation. Token-count weighting, masked denominators and distributed reduction require a weighted derivation if they differ.
- These are raw-gradient identities. Nonlinear clipping or adaptive updates performed separately on the forward and reverse estimates generally do not preserve their cancellation at the parameter-update level. Average the raw vectors first to use the exact identity.

## Exact rational enumeration

A Python Fraction calculation enumerated all permutations for G=1,...,6 (873 permutations total). For each order it checked exact forward/reverse cancellation, then checked unbiasedness and the proposed vector MSE formula. No tolerance or floating-point arithmetic was used. Exit code 0; tool-reported wall time 0.181795978 seconds.

| G | Permutations | Exact vector MSE | Formula | Unbiased | Every reverse pair exact |
|---|---:|---|---|---|---|
| 1 | 1 | 0 | true | true | true |
| 2 | 2 | 365369645/41699273616 | true | true | true |
| 3 | 6 | 3252475295/562940193816 | true | true | true |
| 4 | 24 | 25133517/3206403200 | true | true | true |
| 5 | 120 | 265175083/57829983750 | true | true | true |
| 6 | 720 | 464743165/140735048454 | true | true | true |

This finite diagnostic checks representative inputs and the arithmetic implementation. The argument above proves the general fixed-record result.

Reproduction code:

```python
from fractions import Fraction as F
from itertools import permutations

def plus(a,b): return tuple(x+y for x,y in zip(a,b))
def minus(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(c,a): return tuple(c*x for x in a)
def norm2(a): return sum((x*x for x in a),F(0))
def product(f,J):
    return tuple(sum((f[k]*J[k][r] for k in range(2)),F(0))
                 for r in range(2))

for G in range(1,7):
    fs=[(F(i+1,G+1),F(G-i,G+1)) for i in range(G)]
    Js=[((F((3*i+2)%7,7),F((5*i+1)%11,11)),
         (F((2*i+3)%13,13),F((4*i+1)%17,17))) for i in range(G)]
    pairs=[[product(fs[i],Js[j]) for j in range(G)] for i in range(G)]
    zero=(F(0),F(0))
    T=scale(F(1,G*G),tuple(
        sum((pairs[i][j][r] for i in range(G) for j in range(G)),F(0))
        for r in range(2)))
    A=[[minus(pairs[i][j],pairs[j][i]) for j in range(G)]
       for i in range(G)]
    bs=[tuple(sum((A[i][j][r] for j in range(G)),F(0))
              for r in range(2)) for i in range(G)]
    rhs=(sum((norm2(b) for b in bs),F(0))+
         sum((norm2(A[i][j]) for i in range(G)
              for j in range(i+1,G)),F(0)))/(3*G**4)
    def est(perm):
        z=zero
        for pos,j in enumerate(perm):
            z=plus(z,pairs[j][j])
            for i in perm[:pos]: z=plus(z,scale(F(2),pairs[i][j]))
        return scale(F(1,G*G),z)
    mse=F(0); avg=zero; count=0
    for perm in permutations(range(G)):
        h=est(perm); hr=est(perm[::-1])
        assert scale(F(1,2),plus(h,hr))==T
        avg=plus(avg,h)
        mse+=norm2(minus(h,T)); count+=1
    mse/=count; avg=scale(F(1,count),avg)
    assert avg==T and mse==rhs
```

## Claim boundary

Established: exact fixed-record expectation, covariance/MSE, and deterministic antithetic order cancellation.

Not established: originality, applicability to a particular codebase, improved model learning, computational advantage, distributed-system correctness, or a formal review gate.
