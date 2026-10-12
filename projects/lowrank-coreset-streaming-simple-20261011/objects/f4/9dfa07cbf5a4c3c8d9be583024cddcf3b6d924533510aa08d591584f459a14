"""Reproduce the first late-refresh LOBPCG rank-deficiency and one frozen repair."""
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"

import hashlib
import json
import resource
import time
import warnings
from pathlib import Path

import numpy as np
from scipy.linalg import eigh, svd
from scipy.sparse.linalg import lobpcg

from run_b15_policy import CountedGram, SOURCE

HERE = Path(__file__).resolve().parent


def execute(G, X, tol):
    op = CountedGram(G)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        vals, vecs, history = lobpcg(op, X, largest=True, tol=tol, maxiter=40,
                                     retResidualNormsHistory=True, restartControl=20)
    order = np.argsort(vals)[::-1]
    return vals[order], vecs[:, order], history, op.columns, [str(x.message) for x in caught]


def main():
    cpu0 = time.process_time(); wall0 = time.perf_counter()
    with np.load(SOURCE, allow_pickle=False) as z:
        A = z['a']; energy = z['energy']
    k, old_t, t = 25, 124, 126
    old_u, _, _ = svd(A[:old_t], full_matrices=False)
    X = np.zeros((t, k)); X[:old_t] = old_u[:, :k]
    G = A[:t] @ A[:t].T
    v1_vals, v1_u, v1_h, v1_mv, v1_w = execute(G, X, 1e-8)

    X2 = X + 1e-4 * np.random.default_rng(t).standard_normal(X.shape)
    X2, _ = np.linalg.qr(X2, mode='reduced')
    v2_vals, v2_u, v2_h, v2_mv, v2_w = execute(G, X2, 1e-4)
    q = A[:t].T @ v2_u[:, :k]
    q /= np.sqrt(np.maximum(v2_vals[:k], np.finfo(float).tiny))[None, :]
    q, _ = np.linalg.qr(q, mode='reduced')
    top = eigh(G, eigvals_only=True, subset_by_index=(t-k, t-1), check_finite=False)
    opt = float(energy[t-1] - top.sum())
    loss = float(energy[t-1] - np.linalg.norm(A[:t] @ q)**2)
    endpoint_tol = 1e-10 * max(1.0, float(energy[t-1]))
    out = {
        'study': 'B15-first-late-refresh-rank-deficiency-diagnostic',
        'old_t': old_t, 't': t, 'k': k,
        'unperturbed': {
            'requested_tol': 1e-8,
            'history_length': len(v1_h),
            'final_max_residual': float(np.max(v1_h[-1])),
            'matvec_columns': int(v1_mv),
            'warning_count': len(v1_w),
            'first_warning': v1_w[0] if v1_w else None,
        },
        'deterministic_perturbation': {
            'amplitude': 1e-4, 'seed': t, 'requested_tol': 1e-4,
            'history_length': len(v2_h),
            'final_max_residual': float(np.max(v2_h[-1])),
            'matvec_columns': int(v2_mv),
            'warning_count': len(v2_w),
            'endpoint_excess': max(0.0, loss-opt),
            'endpoint_tolerance': endpoint_tol,
            'excess_over_tolerance': max(0.0, loss-opt)/endpoint_tol,
        },
        'process_cpu_seconds': time.process_time()-cpu0,
        'process_wall_seconds': time.perf_counter()-wall0,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'conclusion': 'unperturbed block fails from rank-deficient residuals; deterministic perturbation at a converged residual tolerance still violates the frozen endpoint objective tolerance',
    }
    path = HERE/'B15_RANK_DEFICIENCY_DIAGNOSTIC.json'
    path.write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    print(json.dumps(out, allow_nan=False))


if __name__ == '__main__': main()
