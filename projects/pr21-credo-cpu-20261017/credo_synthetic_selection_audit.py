"""Known-distribution diagnostic of fixed vs. same-calibration-selected CREDO scores."""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = REPO / "runs/19-iclr26-credo"
sys.path.insert(0, str(RUN))
from model.conformal_dra import ConformalizedDecisionRiskAssessment
from model.sampler import GaussianMixtureSampler

OUT = HERE / "credo_synthetic_selection_results.json"
N_REPLICATES = 200
N_REFERENCE = 1_000_000
N_TRAIN = 100
N_CAL = 100
K = 100


def truth_probabilities(vertices: np.ndarray, seed: int = 901771) -> np.ndarray:
    # The paper's Setting I: one Gaussian component with mean (-0.1,-0.1),
    # isotropic covariance 0.1 I, and the triangle x,y>=0, x+y<=1.
    true_sampler = GaussianMixtureSampler(
        mu=np.array([[-0.1, -0.1]]), scale=np.array([0.1]), weights=np.array([1.0])
    )
    np.random.seed(seed)
    samples = true_sampler.sample(N_REFERENCE)
    opt = np.zeros_like(samples)
    positive = samples.max(axis=1) > 0
    idx = np.flatnonzero(positive)
    winner = np.argmax(samples[idx], axis=1)
    opt[idx, winner] = 1.0
    return np.array([np.mean(np.all(opt == z, axis=1)) for z in vertices])


def interval_mean(values: np.ndarray) -> tuple[float, float, float]:
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(len(values)))
    return mean, mean - 1.96 * se, mean + 1.96 * se


def main() -> None:
    torch.set_num_threads(1)
    # Same simplex decision geometry as CREDO paper Setting I.
    A = np.array([[1, 1], [-1, 0], [0, -1]], dtype=float)
    b = np.array([1, 0, 0], dtype=float)
    scores_all = []
    selected_idx = []
    warnings_by_run = []
    started = time.perf_counter()

    for rep in range(N_REPLICATES):
        seed = 81000 + rep
        np.random.seed(seed)
        torch.manual_seed(seed)
        true_sampler = GaussianMixtureSampler(
            mu=np.array([[-0.1, -0.1]]), scale=np.array([0.1]), weights=np.array([1.0])
        )
        y_train = true_sampler.sample(N_TRAIN)
        y_cal = true_sampler.sample(N_CAL)

        # Match the source notebook: fit a 1-component GMM to training data,
        # calibrate on an independent, exchangeable sample, then score K draws.
        placeholder = GaussianMixtureSampler(
            mu=np.zeros((1, 2)), scale=np.ones(1), weights=np.ones(1)
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fitted = placeholder.fit(y_train, n_iter=100, return_kwds=True)
        dra = ConformalizedDecisionRiskAssessment(A=A, b=b, kwds=fitted,
                                                   boundary_scale=10)
        np.random.seed(seed + 1000)
        torch.manual_seed(seed + 1000)
        dra.calibrate(y_cal)
        np.random.seed(seed + 2000)
        torch.manual_seed(seed + 2000)
        s = np.asarray(dra.get_prob(K=K), dtype=float)
        scores_all.append(s)
        selected_idx.append(int(np.argmax(s)))
        warnings_by_run.append([f"{w.category.__name__}: {w.message}" for w in caught])

    scores = np.asarray(scores_all)
    selected_idx = np.asarray(selected_idx)
    vertices = dra.vertices
    truth = truth_probabilities(vertices)
    fixed_idx = int(np.flatnonzero(np.all(vertices == np.array([0.0, 0.0]), axis=1))[0])
    fixed_score = scores[:, fixed_idx]
    selected_score = scores[np.arange(N_REPLICATES), selected_idx]
    selected_truth = truth[selected_idx]
    pointwise = []
    for i, vertex in enumerate(vertices):
        mean, lo, hi = interval_mean(scores[:, i])
        pointwise.append({
            "decision": vertex.tolist(), "true_optimality_probability_mc": float(truth[i]),
            "mean_source_get_prob_score": mean,
            "score_mean_normal_95pct_interval": [lo, hi],
            "mean_score_minus_true_probability": float(mean - truth[i]),
        })
    fixed_m, fixed_lo, fixed_hi = interval_mean(fixed_score)
    selected_m, selected_lo, selected_hi = interval_mean(selected_score)
    selected_truth_m, selected_truth_lo, selected_truth_hi = interval_mean(selected_truth)
    gap = selected_score - selected_truth
    gap_m, gap_lo, gap_hi = interval_mean(gap)
    result = {
        "status": "developmental_known_distribution_selection_diagnostic_not_confirmatory",
        "question": "Does selecting the highest CREDO get_prob score from the same calibration sample inflate that score relative to the selected decision's true optimality probability?",
        "source_commit": "19e884718599cd390564ddf93aff943a720f3e22",
        "synthetic_setting": {
            "paper_setting": "CREDO Exp. 2, Setting I, sigma=0.1",
            "true_distribution": "N([-0.1,-0.1], 0.1 I)",
            "decision_region": "x>=0, y>=0, x+y<=1; optimal action is one of its three vertices",
            "train_n": N_TRAIN, "calibration_n": N_CAL,
            "fitted_gmm_components": 1,
            "replicates": N_REPLICATES, "K": K,
            "fixed_candidate": vertices[fixed_idx].tolist(),
            "selection_rule": "choose argmax of source get_prob scores using same calibration sample",
            "threads": 1,
            "true_probabilities": "Monte Carlo frequencies from an independent 1,000,000-draw reference sample; uncertainty is small but nonzero",
        },
        "pointwise_fixed_decision_scores": pointwise,
        "fixed_candidate_score_mean_ci": [fixed_m, fixed_lo, fixed_hi],
        "selected_candidate_score_mean_ci": [selected_m, selected_lo, selected_hi],
        "selected_candidate_true_probability_mean_ci_over_runs": [selected_truth_m, selected_truth_lo, selected_truth_hi],
        "selected_score_minus_selected_true_probability_mean_ci": [gap_m, gap_lo, gap_hi],
        "selected_vertex_counts": {str(v.tolist()): int(np.sum(selected_idx == i))
                                   for i, v in enumerate(vertices)},
        "gmm_warning_runs": int(sum(bool(x) for x in warnings_by_run)),
        "gmm_warning_examples": [w for run in warnings_by_run for w in run][:5],
        "elapsed_seconds": time.perf_counter() - started,
        "limitations": [
            "The true rates are Monte Carlo estimates, not analytic values.",
            "This is one small synthetic setting and cannot establish general selection bias or a new correction.",
            "The theoretical guarantee is pointwise for fixed decisions under exchangeability; this comparison is a diagnostic of reusing calibration for selection.",
            "The local solar time series remains nonexchangeable or of unverified exchangeability and is not evaluated by this synthetic experiment.",
            "All work is exploratory; no claim, Gate A, or paper conclusion follows from this run.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in (
        "status", "synthetic_setting", "pointwise_fixed_decision_scores",
        "fixed_candidate_score_mean_ci", "selected_candidate_score_mean_ci",
        "selected_candidate_true_probability_mean_ci_over_runs",
        "selected_score_minus_selected_true_probability_mean_ci",
        "selected_vertex_counts", "gmm_warning_runs", "elapsed_seconds", "limitations")}, indent=2))


if __name__ == "__main__":
    main()
