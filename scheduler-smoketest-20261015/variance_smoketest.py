#!/usr/bin/env python3
"""Bounded CPU-only variance numerical stability test, Python standard library."""
import argparse
import json
import math
import platform
import random
import resource
import time
import tracemalloc


def run(seed: int, n: int, offset: float, scale: float) -> dict:
    if not (1 <= n <= 100000) or not (scale > 0):
        raise ValueError("Expected 1<=n<=100000 and scale>0")
    start = time.perf_counter()
    tracemalloc.start()
    rng = random.Random(seed)
    values = [offset + rng.uniform(-scale, scale) for _ in range(n)]
    sx = sum(values)
    sx2 = sum(x * x for x in values)
    naive = sx2 / n - (sx / n) ** 2
    mean = 0.0
    m2 = 0.0
    for k, x in enumerate(values, 1):
        delta = x - mean
        mean += delta / k
        m2 += delta * (x - mean)
    welford = m2 / n
    centered = [x - offset for x in values]
    centered_mean = math.fsum(centered) / n
    reference = math.fsum((d - centered_mean) ** 2 for d in centered) / n
    elapsed = time.perf_counter() - start
    _current, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "parameters": {"seed": seed, "n": n, "offset": offset,
                       "noise_half_range": scale,
                       "noise_distribution": "uniform", "ddof": 0},
        "results": {
            "naive": naive,
            "welford": welford,
            "reference_centered_fsum": reference,
            "naive_absolute_error": abs(naive - reference),
            "welford_absolute_error": abs(welford - reference),
            "naive_relative_error": abs(naive - reference) / reference,
            "welford_relative_error": abs(welford - reference) / reference,
        },
        "runtime": {
            "python": platform.python_version(),
            "elapsed_s": elapsed,
            "tracemalloc_peak_bytes": traced_peak,
            "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "target_memory_budget_mib": 256,
            "hard_address_space_cap_enforced": False,
        },
        "reference_note": (
            "Two-pass centered math.fsum on actual representable float inputs; "
            "not theoretical variance."
        ),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261015)
    p.add_argument("--n", type=int, default=20000)
    p.add_argument("--offset", type=float, default=1e9)
    p.add_argument("--scale", type=float, default=1e-3)
    a = p.parse_args()
    print(json.dumps(run(a.seed, a.n, a.offset, a.scale), indent=2))
