#!/usr/bin/env python3
"""Exact enumeration for the 3-bit/1-bit weighted Hamming toy only."""
from itertools import product

xs = list(product((0, 1), repeat=3))
num = 0
max_error = 0.0
for i in range(11):
    for j in range(11 - i):
        p = (i / 10, j / 10, (10 - i - j) / 10)
        optimal = 1.0
        for assignment in product((0, 1), repeat=8):
            risk = 0.0
            for message in (0, 1):
                group = [x for x, tag in zip(xs, assignment) if tag == message]
                for coordinate, weight in enumerate(p):
                    ones = sum(x[coordinate] for x in group)
                    risk += weight * min(ones, len(group) - ones) / 8
            optimal = min(optimal, risk)
        formula = min(0.25, (1 - max(p)) / 2)
        max_error = max(max_error, abs(optimal - formula))
        num += 1
assert num == 66
assert max_error < 1e-12
print({'probability_vectors': num, 'encoders_each': 256,
       'max_abs_error': max_error})
