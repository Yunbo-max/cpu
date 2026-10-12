"""Classical exact L1 evaluators; no new-method or theorem claim.

Counts retain coordinate marginals, not cross-coordinate dependence. They are
sufficient only for additive losses such as L1, not general Euclidean distances.
"""
from __future__ import annotations
import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial.distance import cdist


def _matrix(x: ArrayLike) -> NDArray:
    a=np.asarray(x)
    if a.ndim != 2 or not a.shape[0] or not a.shape[1] or not np.all(np.isfinite(a)):
        raise ValueError('Expected a nonempty finite matrix')
    return a


def histogram_counts(x: ArrayLike, bins: int=17) -> NDArray[np.int64]:
    a=_matrix(x)
    if bins < 1 or np.any(a<0) or np.any(a>=bins) or np.any(a!=np.rint(a)):
        raise ValueError('Reference coordinates must be integers in [0,bins)')
    return np.stack([np.bincount(a[:,j].astype(np.int64),minlength=bins)
                     for j in range(a.shape[1])]).astype(np.int64,copy=False)


def histogram_costs(counts: ArrayLike, candidates: ArrayLike) -> NDArray[np.float64]:
    h=_matrix(counts); c=_matrix(candidates)
    if c.shape[1]!=h.shape[0] or np.any(h<0):
        raise ValueError('Invalid counts or candidate dimension')
    totals=h.sum(axis=1)
    if totals[0]<=0 or not np.all(totals==totals[0]):
        raise ValueError('Each coordinate must have the same positive count')
    b=h.shape[1]; v=np.arange(b,dtype=np.int64)
    if np.all(c>=0) and np.all(c<b) and np.all(c==np.rint(c)):
        table=h @ np.abs(v[:,None]-v[None,:])
        idx=c.astype(np.int64,copy=False)
        return table[np.arange(c.shape[1])[None,:],idx].sum(axis=1)/totals[0]
    out=np.zeros(c.shape[0],dtype=np.float64)
    for j in range(c.shape[1]):
        out += np.abs(c[:,j,None]-v[None,:]) @ h[j]
    return out/totals[0]


def sorted_costs(x: ArrayLike, candidates: ArrayLike) -> NDArray[np.float64]:
    a=_matrix(x).astype(np.float64,copy=False); c=_matrix(candidates)
    if a.shape[1]!=c.shape[1]: raise ValueError('Dimension mismatch')
    n=len(a); out=np.zeros(len(c),dtype=np.float64)
    for j in range(a.shape[1]):
        s=np.sort(a[:,j]); prefix=np.r_[0.,np.cumsum(s)]
        q=np.searchsorted(s,c[:,j],side='right')
        out+=c[:,j]*q-prefix[q]+prefix[-1]-prefix[q]-c[:,j]*(n-q)
    return out/n


def blocked_costs(x: ArrayLike, candidates: ArrayLike, block: int=64) -> NDArray[np.float64]:
    a=_matrix(x); c=_matrix(candidates)
    if a.shape[1]!=c.shape[1] or block<1: raise ValueError('Invalid dimensions or block')
    out=np.empty(len(c),dtype=np.float64)
    for i in range(0,len(c),block):
        out[i:i+block]=cdist(c[i:i+block],a,metric='cityblock').mean(axis=1)
    return out


class StreamingHistogram:
    def __init__(self, d: int, bins: int=17, window: int|None=None):
        if d<1 or bins<1 or (window is not None and window<1):
            raise ValueError('Invalid dimensions/window')
        self.d=d; self.bins=bins; self.window=window
        self.counts=np.zeros((d,bins),dtype=np.int64)
        self.seen=0; self.n=0
        dtype=np.uint8 if bins<=256 else np.uint32
        self.ring=None if window is None else np.empty((window,d),dtype=dtype)

    def update(self, row: ArrayLike) -> None:
        a=np.asarray(row)
        if a.shape!=(self.d,) or not np.all(np.isfinite(a)) or np.any(a<0) or np.any(a>=self.bins) or np.any(a!=np.rint(a)):
            raise ValueError('Invalid row')
        a=a.astype(np.int64,copy=False); j=np.arange(self.d)
        if self.window is not None:
            pos=self.seen%self.window
            if self.seen>=self.window:
                self.counts[j,self.ring[pos]]-=1
            else:
                self.n+=1
            self.ring[pos]=a
        else:
            self.n+=1
        self.counts[j,a]+=1; self.seen+=1

    def costs(self, candidates: ArrayLike) -> NDArray[np.float64]:
        return histogram_costs(self.counts,candidates)

    @property
    def state_bytes(self) -> int:
        # NumPy payload plus two logical int64 counters; Python overhead is
        # excluded here but included in process RSS. No free outgoing-row oracle.
        return self.counts.nbytes+(0 if self.ring is None else self.ring.nbytes)+16


def draw_sample(x, compact, rng, m):
    if m<1: raise ValueError('Sample size must be positive')
    idx=rng.choice(len(x),m,replace=True)
    return idx,x[idx],compact[idx]
