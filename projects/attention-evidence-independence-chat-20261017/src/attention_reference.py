"""Unexecuted, deterministic algebraic reference for source/evidence attention.

Not a trained LM, full LUCID implementation, or a qualified Auto Chat producer.
Requires official guarded binding before any claim-bearing experimental execution.
"""
from collections import Counter
from math import exp, log
from typing import Hashable, Sequence

import numpy as np


def softmax_pool(logits: Sequence[float], values: Sequence[float]) -> np.ndarray:
    s = np.asarray(logits, dtype=np.float64).reshape(-1)
    v = np.asarray(values, dtype=np.float64)
    if len(s) == 0 or v.shape[0] != len(s):
        raise ValueError("Expected non-empty matched logits and values")
    w = np.exp(s - s.max())
    w = w / w.sum()
    return np.tensordot(w, v, axes=(0, 0))


def quotient_pool(
    logits: Sequence[float],
    values: Sequence[float],
    class_ids: Sequence[Hashable],
) -> np.ndarray:
    """Subtract log class multiplicity.

    Exact copy invariance requires identical logits and values *within* each
    class; the function deliberately DOES NOT infer source IDs from content.
    It does not assert class consistency; a verifier must test it.
    """
    s = np.asarray(logits, dtype=np.float64).reshape(-1)
    if len(class_ids) != len(s):
        raise ValueError("Class ID length mismatch")
    counts = Counter(class_ids)
    adjusted = s - np.log([counts[c] for c in class_ids])
    return softmax_pool(adjusted, values)


def class_level_pool(
    logits: Sequence[float],
    values: Sequence[float],
    class_ids: Sequence[Hashable],
) -> np.ndarray:
    """Oracle one-per-class reference; fail on unequal member logits/values."""
    s = np.asarray(logits, dtype=np.float64).reshape(-1)
    v = np.asarray(values, dtype=np.float64)
    if len(class_ids) != len(s):
        raise ValueError("Class ID length mismatch")
    representatives = {}
    for i, group in enumerate(class_ids):
        if group not in representatives:
            representatives[group] = i
        else:
            j = representatives[group]
            if not np.allclose(s[i], s[j], atol=0, rtol=0) or not np.array_equal(v[i], v[j]):
                raise ValueError("Unequal key-score/value members; quotient premise violated")
    ix = list(representatives.values())
    return softmax_pool(s[ix], v[ix])


def posterior_from_unique_sources(votes_by_source: dict[Hashable, int], p: float = 0.75) -> float:
    """Bayesian posterior for independent source signs +/-1 and uniform prior."""
    if not (0.5 < p < 1):
        raise ValueError("This diagnostic requires 0.5 < source accuracy < 1")
    if any(v not in (-1, 1) for v in votes_by_source.values()):
        raise ValueError("Vote values must be +/-1")
    log_odds = sum(votes_by_source.values()) * log(p / (1 - p))
    if log_odds >= 0:
        return 1 / (1 + exp(-log_odds))
    t = exp(log_odds)
    return t / (1 + t)


def evidence_from_copies(copy_counts: dict[Hashable, tuple[int, int]]) -> dict[Hashable, int]:
    """Input source ID maps to (vote, copy_count); count cannot change posterior."""
    return {source: vote for source, (vote, n) in copy_counts.items()
            if n >= 1 and vote in (-1, 1)}
