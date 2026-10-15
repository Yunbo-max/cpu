#!/usr/bin/env python3
"""Auto Chat scheduled smoke test r004; engineering numerical check (not a benchmark)."""
import datetime
import fractions
import json
import math
import platform
import random
import resource
import time

# Cap virtual address space before allocating; stay well under requested budget.
CAP = 256 * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (CAP, CAP))
START_WALL = time.perf_counter()
START_CPU = time.process_time()

SEED = 20261016
N = 20000
OFFSET = 1_000_000_000.0
STEP = 1 / 1024
rng = random.Random(SEED)
residual_ints = [rng.randint(-2, 2) for _ in range(N)]
values = [OFFSET + r * STEP for r in residual_ints]
assert len(values) == N
assert all((v - OFFSET) == r * STEP for v, r in zip(values, residual_ints))

# Independent exact population variance from the 5-point *integer* support.
s1 = sum(residual_ints)
s2 = sum(r * r for r in residual_ints)
exact_fraction = fractions.Fraction(N * s2 - s1 * s1, N * N * 1024 * 1024)
ref = float(exact_fraction)
assert ref > 0


def welford(seq, anchor=0.0):
    mean = 0.0
    m2 = 0.0
    for n, x in enumerate(seq, 1):
        z = x - anchor
        delta = z - mean
        mean += delta / n
        m2 += delta * (z - mean)
    return m2 / n


def fsum_twopass(seq):
    zs = [x - OFFSET for x in seq]
    mean = math.fsum(zs) / len(zs)
    return math.fsum((z - mean) ** 2 for z in zs) / len(zs)


def naive(seq):
    return sum(x * x for x in seq) / len(seq) - (sum(seq) / len(seq)) ** 2

# New held-out seed, new family; order varies within exactly same multiset.
sorted_asc = sorted(values)
sorted_desc = sorted_asc[::-1]
alt = []
i, j = 0, N - 1
while i <= j:
    alt.append(sorted_asc[i])
    i += 1
    if i <= j:
        alt.append(sorted_asc[j])
        j -= 1
orders = {"original": values, "ascending": sorted_asc,
          "descending": sorted_desc, "alternating_extremes": alt}
results = {}
for name, seq in orders.items():
    assert len(seq) == N and sum(x - OFFSET for x in seq) == sum(x - OFFSET for x in values)
    raw = welford(seq)
    anchored_first = welford(seq, anchor=seq[0])
    anchored_fixed = welford(seq, anchor=OFFSET)
    centered_fsum = fsum_twopass(seq)
    naive_result = naive(seq)
    results[name] = {
        "anchor_first_x0": seq[0],
        "naive": naive_result,
        "raw_welford": raw,
        "anchored_x0_welford": anchored_first,
        "anchored_offset_welford": anchored_fixed,
        "centered_two_pass_fsum": centered_fsum,
        "relative_error": {k: abs(v - ref) / ref for k, v in {
            "naive": naive_result,
            "raw_welford": raw,
            "anchored_x0_welford": anchored_first,
            "anchored_offset_welford": anchored_fixed,
            "centered_two_pass_fsum": centered_fsum,
        }.items()},
    }

record = {
    "schema": "autochat-smoketest-r004-numeric-v1",
    "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parameters": {
        "seed": SEED, "n": N, "offset": OFFSET, "step": STEP,
        "residual_int_support": [-2, -1, 0, 1, 2],
        "ddof": 0, "exact_float_input_identity_checked": True,
        "input_multiplicity_preserved_across_orders": True,
    },
    "reference": {
        "exact_rational_numerator": exact_fraction.numerator,
        "exact_rational_denominator": exact_fraction.denominator,
        "float_from_exact_rational": ref,
        "note": "Exact population variance from integer residual counts; float inputs at offset 1e9 preserve residuals exactly."
    },
    "residual_counts": {str(t): residual_ints.count(t) for t in range(-2, 3)},
    "results": results,
    "max_relative_error_by_method": {
        m: max(r["relative_error"][m] for r in results.values())
        for m in ("naive", "raw_welford", "anchored_x0_welford",
                  "anchored_offset_welford", "centered_two_pass_fsum")
    },
    "runtime": {
        "python": platform.python_version(),
        "hard_rlimit_as_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "wall_seconds": time.perf_counter() - START_WALL,
        "cpu_seconds": time.process_time() - START_CPU,
    },
    "scope": "engineering smoke test only; held-out deterministic sample, not a scientific/public benchmark"
}
print(json.dumps(record, sort_keys=True, indent=2))
