"""Paired same-calibration selection vs. independent recalibration diagnostic."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = REPO / "runs/19-iclr26-credo"
sys.path.insert(0, str(RUN))
from model.conformal_dra import ConformalizedDecisionRiskAssessment
from model.sampler import GaussianMixtureSampler

OUT = HERE / "credo_synthetic_selection_holdout_results.json"
N = 200
N_TRAIN = N_CAL = 100
K = 100
N_REFERENCE = 1_000_000


def mean_ci(x):
    x = np.asarray(x, dtype=float)
    mean = float(x.mean())
    se = float(x.std(ddof=1) / np.sqrt(len(x)))
    return [mean, mean - 1.96 * se, mean + 1.96 * se]


def main():
    torch.set_num_threads(1)
    A = np.array([[1, 1], [-1, 0], [0, -1]], dtype=float)
    b = np.array([1, 0, 0], dtype=float)
    true = GaussianMixtureSampler(mu=np.array([[-0.1, -0.1]]),
                                  scale=np.array([0.1]), weights=np.array([1.0]))
    np.random.seed(991771)
    reference = true.sample(N_REFERENCE)
    opt = np.zeros_like(reference)
    pos = reference.max(axis=1) > 0
    ix = np.flatnonzero(pos)
    opt[ix, np.argmax(reference[ix], axis=1)] = 1.0

    same_selected, fresh_selected = [], []
    same_origin, fresh_origin, selected_ids = [], [], []
    started = time.perf_counter()
    vertices = None

    for rep in range(N):
        seed = 91000 + rep
        np.random.seed(seed)
        torch.manual_seed(seed)
        ytrain = true.sample(N_TRAIN)
        yselect = true.sample(N_CAL)
        yeval = true.sample(N_CAL)
        predictor = GaussianMixtureSampler(mu=np.zeros((1, 2)),
                                            scale=np.ones(1), weights=np.ones(1))
        fitted = predictor.fit(ytrain, n_iter=100, return_kwds=True)

        select_dra = ConformalizedDecisionRiskAssessment(A=A, b=b, kwds=fitted,
                                                          boundary_scale=10)
        np.random.seed(seed + 1000)
        torch.manual_seed(seed + 1000)
        select_dra.calibrate(yselect)
        np.random.seed(seed + 2000)
        torch.manual_seed(seed + 2000)
        select_scores = np.asarray(select_dra.get_prob(K=K), dtype=float)
        selected = int(np.argmax(select_scores))

        eval_dra = ConformalizedDecisionRiskAssessment(A=A, b=b, kwds=fitted,
                                                       boundary_scale=10)
        np.random.seed(seed + 3000)
        torch.manual_seed(seed + 3000)
        eval_dra.calibrate(yeval)
        np.random.seed(seed + 4000)
        torch.manual_seed(seed + 4000)
        eval_scores = np.asarray(eval_dra.get_prob(K=K), dtype=float)

        vertices = select_dra.vertices
        origin = int(np.flatnonzero(np.all(vertices == np.array([0.0, 0.0]), axis=1))[0])
        same_selected.append(float(select_scores[selected]))
        fresh_selected.append(float(eval_scores[selected]))
        same_origin.append(float(select_scores[origin]))
        fresh_origin.append(float(eval_scores[origin]))
        selected_ids.append(selected)

    truth = np.array([np.mean(np.all(opt == z, axis=1)) for z in vertices])
    selected_ids = np.asarray(selected_ids)
    selected_true = truth[selected_ids]
    same_selected = np.asarray(same_selected)
    fresh_selected = np.asarray(fresh_selected)
    same_origin = np.asarray(same_origin)
    fresh_origin = np.asarray(fresh_origin)
    delta = same_selected - fresh_selected
    result = {
        "status": "developmental_paired_selection_recalibration_diagnostic_not_confirmatory",
        "protocol_path": "credo_selection_holdout_protocol.md",
        "source_commit": "19e884718599cd390564ddf93aff943a720f3e22",
        "design": {
            "setting": "published synthetic Setting I, sigma=0.1",
            "true_distribution": "N([-0.1,-0.1], 0.1 I)",
            "train_n": N_TRAIN, "selection_calibration_n": N_CAL,
            "independent_evaluation_calibration_n": N_CAL,
            "replicates": N, "K": K, "fitted_components": 1,
            "selection": "argmax source get_prob on selection calibration",
            "primary_endpoint": "same-calibration selected score minus independent-calibration score for that same selected decision",
            "control": "origin score on both calibration sets",
            "threads": 1,
        },
        "true_vertex_optimality_probabilities_mc": {
            str(z.tolist()): float(q) for z, q in zip(vertices, truth)
        },
        "same_calibration_selected_score_mean_ci": mean_ci(same_selected),
        "independent_calibration_selected_score_mean_ci": mean_ci(fresh_selected),
        "paired_selected_score_difference_mean_ci": mean_ci(delta),
        "selected_true_optimality_mean_ci_over_runs": mean_ci(selected_true),
        "same_score_minus_selected_true_probability_mean_ci": mean_ci(same_selected - selected_true),
        "fresh_score_minus_selected_true_probability_mean_ci": mean_ci(fresh_selected - selected_true),
        "fixed_origin_same_calibration_score_mean_ci": mean_ci(same_origin),
        "fixed_origin_independent_calibration_score_mean_ci": mean_ci(fresh_origin),
        "selected_vertex_counts": {str(z.tolist()): int(np.sum(selected_ids == i))
                                   for i, z in enumerate(vertices)},
        "elapsed_seconds": time.perf_counter() - started,
        "limitations": [
            "One two-dimensional synthetic distribution only; no general validity conclusion.",
            "Scores and reference truth have Monte Carlo error; intervals are descriptive normal intervals over replicates.",
            "Both calibration samples are exchangeable by construction; the real solar series was not tested here.",
            "This does not establish novelty or a new correction method.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
