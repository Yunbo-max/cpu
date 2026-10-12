"""Investigational all-center L1 stability certificates.

Only exact_dual's rational witness decides admission. A positive bound means
UNKNOWN, never that a coreset is unstable. No strong-duality claim is made.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from bisect import bisect_right
from typing import Any
import math
import numpy as np
from scipy.optimize import minimize_scalar

F = Fraction

@dataclass
class Column:
    knots: list[int]
    full: list[int]
    sample: list[int]
    offset: int
    median_index: int
    f: np.ndarray
    g: np.ndarray

@dataclass
class State:
    n: int
    m: int
    exponent: int
    cols: list[Column]
    opt_int: int


def _costs(sorted_values: list[int], knots: list[int]) -> list[int]:
    prefix=[0]
    for v in sorted_values: prefix.append(prefix[-1]+v)
    n=len(sorted_values); total=prefix[-1]
    out=[]
    for t in knots:
        k=bisect_right(sorted_values,t)
        out.append((2*k-n)*t+total-2*prefix[k])
    return out


def prepare(P: np.ndarray, Q: np.ndarray) -> State:
    """Encode supplied binary64 values exactly, not rounded to decimal bins."""
    P=np.asarray(P,dtype=np.float64);Q=np.asarray(Q,dtype=np.float64)
    if P.ndim!=2 or Q.ndim!=2 or not len(P) or not len(Q) or not P.shape[1] or P.shape[1]!=Q.shape[1]:
        raise ValueError('Nonempty equally dimensional matrices required')
    if not np.isfinite(P).all() or not np.isfinite(Q).all():
        raise ValueError('Finite values required')
    pp=[[float(x).as_integer_ratio() for x in row] for row in P]
    qq=[[float(x).as_integer_ratio() for x in row] for row in Q]
    exponent=max(v[1].bit_length()-1 for rows in (pp,qq) for row in rows for v in row)
    scale=1<<exponent;n=len(P);m=len(Q);cols=[]
    for j in range(P.shape[1]):
        a=sorted(num*(scale//den) for num,den in (row[j] for row in pp))
        b=sorted(num*(scale//den) for num,den in (row[j] for row in qq))
        knots=sorted(set(a+b)); fc=_costs(a,knots);gc=_costs(b,knots)
        med=knots.index(a[(n-1)//2])
        cols.append(Column(knots,fc,gc,m*fc[med]-n*gc[med],med,
                           np.array([v/(n*scale) for v in fc]),
                           np.array([v/(m*scale) for v in gc])))
    opt=sum(c.full[c.median_index] for c in cols)
    if opt<=0:
        raise ValueError('Collapsed support: relative-cost denominator can vanish; handle separately')
    return State(n,m,exponent,cols,opt)


def _fractional_max(nums: list[list[int]], dens: list[list[int]], asymptote: F) -> dict[str,Any]:
    """Exact separable Dinkelbach iteration; asymptote controls the tails.

Each call's numerator/denominator functions are continuous piecewise affine
with common coordinate knots. All denominators sum to a strictly positive cost.
"""
    r=asymptote
    for iteration in range(256):
        p,q=r.numerator,r.denominator; chosen=[]; total=0
        for aa,bb in zip(nums,dens):
            idx=max(range(len(aa)),key=lambda i:q*aa[i]-p*bb[i])
            chosen.append(idx);total+=q*aa[idx]-p*bb[idx]
        if total<=0:
            return {'ratio':r,'indices':chosen,'iterations':iteration+1,'residual_numerator':total}
        a=sum(aa[i] for aa,i in zip(nums,chosen))
        b=sum(bb[i] for bb,i in zip(dens,chosen))
        if b<=0: raise ArithmeticError('Nonpositive joint denominator')
        new=F(a,b)
        if new<=r: raise ArithmeticError('Fractional iteration lost monotonicity')
        r=new
    raise RuntimeError('Exact fractional iteration exceeded diagnostic bound')


def exact_extremes(s: State) -> dict[str,Any]:
    dens=[[s.m*v for v in c.full] for c in s.cols]
    ng=[[s.n*v for v in c.sample] for c in s.cols]
    upper=_fractional_max(ng,dens,F(1))
    lowneg=_fractional_max([[-v for v in a] for a in ng],dens,F(-1))
    residual=[[s.m*f-s.n*g-c.offset for f,g in zip(c.full,c.sample)] for c in s.cols]
    plus=_fractional_max(residual,dens,F(0))
    minus=_fractional_max([[-v for v in a] for a in residual],dens,F(0))
    qmed=sum(c.sample[c.median_index] for c in s.cols)
    median_ratio=F(s.n*qmed,s.m*s.opt_int)
    return {'lower':-lowneg['ratio'],'upper':upper['ratio'],
            'rcda':max(plus['ratio'],minus['ratio']),
            'median_ratio':median_ratio,'details':{'upper':upper,'negative_lower':lowneg,'plus_rcda':plus,'minus_rcda':minus}}


def exact_dual(s: State, lam: F, alpha: F, beta: F) -> dict[str,Any]:
    lam=F(lam);alpha=F(alpha);beta=F(beta)
    if alpha<0 or beta<alpha or not F(1)<=lam<=(1+beta)/(1+alpha):
        raise ValueError('Multiplier outside the finite-tail domain')
    p,q=lam.numerator,lam.denominator
    a,A=alpha.numerator,alpha.denominator;b,B=beta.numerator,beta.denominator
    total=0;xx=[];yy=[]
    for c in s.cols:
        h1=[q*s.m*f-p*s.n*g for f,g in zip(c.full,c.sample)]
        h2=[p*(A+a)*B*s.n*g-(B+b)*A*q*s.m*f for f,g in zip(c.full,c.sample)]
        i=max(range(len(h1)),key=h1.__getitem__);j=max(range(len(h2)),key=h2.__getitem__)
        total+=A*B*h1[i]+h2[j];xx.append(i);yy.append(j)
    denominator=q*s.n*s.m*A*B*(1<<s.exponent)
    bound=F(total,denominator)
    # Check whether the separate maximizing centers themselves give a feasible violation.
    fx=F(sum(c.full[i] for c,i in zip(s.cols,xx)),s.n*(1<<s.exponent))
    fy=F(sum(c.full[i] for c,i in zip(s.cols,yy)),s.n*(1<<s.exponent))
    gx=F(sum(c.sample[i] for c,i in zip(s.cols,xx)),s.m*(1<<s.exponent))
    gy=F(sum(c.sample[i] for c,i in zip(s.cols,yy)),s.m*(1<<s.exponent))
    violation=gx<=(1+alpha)*gy and fx>(1+beta)*fy
    return {'bound':bound,'lambda':lam,'certified':bound<=0,'primal_violation':violation,
            'x_indices':xx,'y_indices':yy,'x_F':fx,'y_F':fy,'x_G':gx,'y_G':gy}


def propose_certificate(s:State,alpha:F,beta:F,extremes:dict[str,Any]|None=None)->dict[str,Any]:
    alpha=F(alpha);beta=F(beta)
    if alpha<0 or beta<alpha:raise ValueError('Require beta>=alpha>=0')
    hi=(1+beta)/(1+alpha)
    def objective(t:float)->float:
        return sum(float(np.max(c.f-t*c.g)+np.max(t*float(1+alpha)*c.g-float(1+beta)*c.f)) for c in s.cols)
    candidates=[F(1),hi]
    success=True
    if hi>1:
        opt=minimize_scalar(objective,bounds=(1.,float(hi)),method='bounded',options={'xatol':1e-11,'maxiter':160})
        success=bool(opt.success)
        if math.isfinite(opt.x):candidates.append(min(hi,max(F(1),F(float(opt.x)).limit_denominator(10**9))))
    if extremes is not None and extremes['lower']>0:
        candidates.append(min(hi,max(F(1),1/extremes['lower'])))
    # Every candidate is independently re-evaluated in exact arithmetic.
    answer=min((exact_dual(s,t,alpha,beta) for t in set(candidates)),key=lambda z:z['bound'])
    answer['proposal_success']=success
    answer['proposal_only_float_bound']=objective(float(answer['lambda']))
    return answer
