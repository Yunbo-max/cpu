"""Matched chronological CREDO vs. source PTO/RO/SPO+ baselines (CPU, 1 thread)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = REPO / "runs/19-iclr26-credo"
sys.path.insert(0, str(RUN))
from model.conformal_dra import ConformalizedDecisionRiskAssessment
from model.opt import Optimization
from model.sampler import GaussianMixtureSampler
from model.ro import RobustOptimization
import model.spo as spo_module
from model.spo import SPO

# Keep the author's SPO+ implementation while restricting its per-iteration
# LP batch to one worker. Its source default is n_jobs=-1.
_parallel = spo_module.Parallel
spo_module.Parallel = lambda *args, **kwargs: _parallel(n_jobs=1)

DATA = RUN / "data/real_records.csv"
OUT = HERE / "credo_temporal_baseline_results.json"
torch_threads = 1


def transform(y: np.ndarray, tau: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y_ = -1.0 / (1.0 + np.exp(-0.5 * (y - tau)))
    cost = np.ones(4)
    A = np.concatenate([(-cost)[None, :], -np.eye(4), np.eye(4)], axis=0)
    b = np.concatenate([np.array([-2.0]), np.zeros(4), np.ones(4)])
    return y_, A, b


def rank(z: np.ndarray, optima: np.ndarray) -> int:
    decisions, counts = np.unique(optima, return_counts=True, axis=0)
    decisions = decisions[np.argsort(-counts)]
    hit = np.flatnonzero(np.all(decisions == z, axis=1))
    return int(hit[0] + 1) if len(hit) else int(len(decisions))


def main() -> None:
    import torch

    torch.set_num_threads(torch_threads)
    raw = pd.read_csv(DATA, index_col=0)
    dates = pd.to_datetime(raw.index)
    yall = raw.to_numpy(dtype=float)
    rows = []
    started = time.perf_counter()

    for block, start in enumerate((96, 120, 144)):
        fitcal_raw, test_raw = yall[:start], yall[start : start + 24]
        tau = fitcal_raw.mean(axis=0)
        fitcal, A, b = transform(fitcal_raw, tau)
        ytest, _, _ = transform(test_raw, tau)
        ncal = int(np.ceil(0.33 * len(fitcal)))
        ytr, ycal = fitcal[:-ncal], fitcal[-ncal:]
        seed = 2700 + block

        # PTO uses all pre-test observations, as in the source notebook.
        pto = Optimization(Y=fitcal.mean(axis=0), A=A, b=b).get_action()

        # Source RO: train mean plus an L-infinity split-conformal uncertainty set.
        ypred = ytr.mean(axis=0)
        scores = np.linalg.norm(ypred[None, :] - ycal, ord=np.inf, axis=1)
        q = float(np.quantile(scores, 0.95))
        directions = np.array([[1, 0, 0, 0], [-1, 0, 0, 0],
                               [0, 1, 0, 0], [0, -1, 0, 0],
                               [0, 0, 1, 0], [0, 0, -1, 0],
                               [0, 0, 0, 1], [0, 0, 0, -1]])
        # Keep source ordering: each axis contributes + and - bound.
        d = np.concatenate([[ypred[i] + q, -ypred[i] + q] for i in range(4)])
        ro = RobustOptimization(A=A, b=b, C=directions, d=d).get_action()

        # CREDO uses the same chronological fit/calibration split and seeds as
        # the already archived temporal audit; this is one fixed score draw.
        np.random.seed(seed)
        torch.manual_seed(seed)
        sampler = GaussianMixtureSampler(mu=np.zeros((3, 4)), scale=np.ones(3),
                                         weights=np.ones(3) / 3)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fitted = sampler.fit(ytr, n_iter=100, return_kwds=True)
        dra = ConformalizedDecisionRiskAssessment(A=A, b=b, kwds=fitted,
                                                   boundary_scale=10)
        np.random.seed(seed + 100)
        torch.manual_seed(seed + 100)
        dra.calibrate(ycal)
        decisions = dra.vertices
        qhat = np.asarray(dra.get_prob(K=10000), dtype=float)
        credo = decisions[int(np.argmax(qhat))]

        # Source SPO+ learns on all pre-test rows; fixed seeds make init stable.
        np.random.seed(seed)
        spo = SPO(A=A, b=b, verbose=False)
        spo.fit(Y=fitcal, lr=1e-1, niter=100)
        spo_action = spo.get_action()

        test_opt = np.array([Optimization(Y=y, A=A, b=b).get_action()
                             for y in ytest])
        actions = {"CREDO": credo, "PTO": pto, "RO": ro, "SPO+": spo_action}
        ranks = {name: rank(action, test_opt) for name, action in actions.items()}
        rows.append({
            "block": block,
            "train_end": dates[start - ncal - 1].date().isoformat(),
            "calibration_end": dates[start - 1].date().isoformat(),
            "test_start": dates[start].date().isoformat(),
            "test_end": dates[start + 23].date().isoformat(),
            "n_train": len(ytr), "n_calibration": len(ycal), "n_test": len(ytest),
            "actions": {k: v.tolist() for k, v in actions.items()},
            "ranks_lower_better": ranks,
            "credo_minus_baseline_rank": {k: ranks["CREDO"] - ranks[k]
                                           for k in ("PTO", "RO", "SPO+")},
            "credo_gmm_warnings": [f"{w.category.__name__}: {w.message}" for w in caught],
            "ro_calibration_radius_linf": q,
            "spo_iterations": 100,
        })

    summary = {name: [row["ranks_lower_better"][name] for row in rows]
               for name in ("CREDO", "PTO", "RO", "SPO+")}
    result = {
        "status": "developmental_chronological_baseline_comparison_not_confirmatory",
        "question": "Does CREDO's decision-rank tie with PTO persist against source RO and SPO+ on the same three chronological blocks?",
        "data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "source_commit": "19e884718599cd390564ddf93aff943a720f3e22",
        "design": {
            "blocks": "same three non-overlapping future 24-month blocks as credo_temporal_holdout_audit.py",
            "pretest_partition": "earliest 67% fit, latest 33% calibration",
            "CREDO": "source implementation, 3 components, K=10000, one fixed score draw per block",
            "PTO": "source implementation, mean of all pre-test data",
            "RO": "source implementation, L-infinity 95th-percentile calibration radius",
            "SPO+": "source implementation, lr=0.1, 100 iterations, single worker",
            "DFL": "not run; cvxpy and cvxpylayers are absent from the pinned Mac environment",
            "primary_metric": "source empirical decision rank over the 24-month test block; lower is better",
            "threads": 1,
            "random_seeds": "CREDO fit 2700+block, CREDO score 2800+block, SPO+ init 2700+block",
        },
        "ranks_by_block": rows,
        "rank_lists_by_method": summary,
        "elapsed_seconds": time.perf_counter() - started,
        "limitations": [
            "Only three blocks from one 168-month series; these do not support inferential claims.",
            "The chronological stress split does not satisfy a verified exchangeability assumption.",
            "A fixed stochastic seed is used per block; Monte Carlo score uncertainty was studied separately.",
            "DFL is unavailable in the pinned Mac environment, so the paper's full baseline table is not reproduced.",
            "All data were already inspected; this is developmental evidence, not confirmation.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "design", "rank_lists_by_method", "ranks_by_block", "elapsed_seconds", "limitations")}, indent=2))


if __name__ == "__main__":
    main()
