import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
old = json.loads((ROOT / "inputs" / "multibook_raw_evaluation.json").read_text())
eff = json.loads((ROOT / "inputs" / "efficiency_candidate_evaluation.json").read_text())
tico = eff["old_tico_results"]["classical"]["datasets"]["tico.dev100"]["paired_costs"]
books = [row for work in sorted(old["arms"]["classical"]) for row in old["arms"]["classical"][work]["paired_costs"]]
thresholds = [76, 120, 157]


def sign3(a, b):
    return "positive" if a > b else ("negative" if a < b else "zero")


def len4(a, b):
    total = a + b
    if total <= thresholds[0]: return "q1"
    if total <= thresholds[1]: return "q2"
    if total <= thresholds[2]: return "q3"
    return "q4"


def sign2(a, b):
    return "positive" if a > b else "nonpositive"


def len2(a, b):
    return "short" if a + b <= thresholds[1] else "long"


def table(rows, key):
    return Counter(key(a, b) for a, b in rows)


full_groups = [(s, q) for s in ["positive", "zero", "negative"] for q in ["q1", "q2", "q3", "q4"]]
coarse_groups = [(s, q) for s in ["positive", "nonpositive"] for q in ["short", "long"]]
tf = table(tico, lambda a, b: (sign3(a, b), len4(a, b)))
bf = table(books, lambda a, b: (sign3(a, b), len4(a, b)))
tc = table(tico, lambda a, b: (sign2(a, b), len2(a, b)))
bc = table(books, lambda a, b: (sign2(a, b), len2(a, b)))

def rows(groups, t, b):
    return [{"group": list(g), "tico_count": t[g], "books_count": b[g]} for g in groups]

result = {
    "scope": "Exposed Classical baseline support diagnostic only.",
    "full_3x4": {
        "cells": rows(full_groups, tf, bf),
        "books_positive_tico_empty": [list(g) for g in full_groups if bf[g] > 0 and tf[g] == 0],
        "estimable": not any(bf[g] > 0 and tf[g] == 0 for g in full_groups),
        "minimum_nonzero_tico_cell": min(v for v in tf.values() if v > 0),
    },
    "coarse_2x2": {
        "cells": rows(coarse_groups, tc, bc),
        "books_positive_tico_empty": [list(g) for g in coarse_groups if bc[g] > 0 and tc[g] == 0],
        "estimable": not any(bc[g] > 0 and tc[g] == 0 for g in coarse_groups),
        "minimum_tico_cell": min(tc[g] for g in coarse_groups),
    },
    "interpretation_guard": "Nonempty cells remove exact positivity failure but do not make 100 TICO rows sufficient for stable causal or population attribution."
}
(ROOT / "output" / "joint_support_diagnostic.json").write_text(json.dumps(result, indent=2) + "\n")
