"""Differentiable CPU/GPU-agnostic reference, tested here on CPU only.

No fused GPU kernel, trained semantic gate, or differentiable FD/SVD controller
is claimed. Leading batch/head dimensions are supported by matrix operations.
"""
from __future__ import annotations
import torch


def block_from_precision(S, K, V, *, P=None, diag_precision=None, eta=1., Q=None):
    """Shapes: S (...,dv,d), K/Q (...,d,B), V (...,dv,B).

    Supply either SPD P=C^{-1} or its diagonal vector (...,d). The same
    gain controls erasure and writing. Y contains post-observation prefix
    readouts, NOT reads from the final block state for every position.
    """
    if (P is None) == (diag_precision is None):
        raise ValueError('supply exactly one of P and diag_precision')
    if eta <= 0 or K.shape[-1] < 1:
        raise ValueError('positive eta and nonempty block required')
    if S.shape[-1] != K.shape[-2] or V.shape[-2:] != (S.shape[-2],K.shape[-1]):
        raise ValueError('incompatible block shapes')
    if Q is not None and Q.shape != K.shape:
        raise ValueError('Q and K shapes must agree')
    PK = P @ K if P is not None else diag_precision.unsqueeze(-1)*K
    A = K.mT @ PK
    A = .5*(A+A.mT) + torch.eye(K.shape[-1],dtype=K.dtype,device=K.device)/eta
    L = torch.linalg.cholesky(A)
    E = V-S@K
    Gt = torch.cholesky_solve(PK.mT,L)
    Y = None
    if Q is not None:
        U = torch.linalg.solve_triangular(L,E.mT,upper=False).mT
        W = torch.linalg.solve_triangular(L,PK.mT@Q,upper=False)
        Y = S@Q + U@torch.triu(W)
    return S+E@Gt, Gt.mT, Y


def history_sequence(K,V,Q,*,method='full',block_sizes=(32,),ridge=1.,eta=1.):
    """Streams (...,time,dim), arbitrary known block sizes, differentiable reads.

    For full accumulated information and sum loss, partitioning does not
    alter the exact model. Diagonal/fixed-prior versions need not share this
    property. This is causal prefill, not buffered future-token decoding.
    """
    if method not in ('full','diag','scalar') or ridge <= 0 or eta <= 0:
        raise ValueError('invalid method/ridge/eta')
    sizes=tuple(block_sizes)
    if not sizes or any(not isinstance(b,int) or b < 1 for b in sizes):
        raise ValueError('positive integer block sizes required')
    if Q.shape != K.shape or V.shape[:-1] != K.shape[:-1] or K.shape[-2] == 0:
        raise ValueError('bad stream shapes')
    batch=K.shape[:-2]; n,d=K.shape[-2:]; dv=V.shape[-1]
    S=K.new_zeros((*batch,dv,d))
    P=torch.eye(d,dtype=K.dtype,device=K.device).expand(*batch,d,d)/ridge if method=='full' else None
    c=K.new_full((*batch,d),ridge)
    outputs=[]; start=0; idx=0
    while start<n:
        end=min(n,start+sizes[idx%len(sizes)])
        k=K[...,start:end,:].mT; v=V[...,start:end,:].mT; q=Q[...,start:end,:].mT
        S,G,Y=block_from_precision(S,k,v,P=P,diag_precision=None if P is not None else 1./c,eta=eta,Q=q)
        outputs.append(Y.mT)
        if method=='full':
            P=P-(P@k)@G.mT
            P=.5*(P+P.mT)
        elif method=='diag':
            c=c+eta*(k*k).sum(-1)
        start=end; idx+=1
    return torch.cat(outputs,dim=-2),S
