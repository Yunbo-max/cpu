import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "inputs" / name).read_text())


def frac_json(value):
    return {"numerator": value.numerator, "denominator": value.denominator, "decimal": float(value)}


def nearest_rank(values, p):
    ordered = sorted(values)
    rank = max(1, (len(ordered) * p.numerator + p.denominator - 1) // p.denominator)
    return ordered[rank - 1]


def metrics(pairs):
    if not pairs or any(len(row) != 2 or min(row) < 0 for row in pairs):
        raise RuntimeError("invalid paired costs")
    n = len(pairs)
    sums = [a + b for a, b in pairs]
    gaps = [a - b for a, b in pairs]
    valid = [i for i, s in enumerate(sums) if s > 0]
    if not valid or sum(sums) == 0:
        raise RuntimeError("zero token mass")
    S = sum(sums)
    dsum = sum(gaps)
    P = sum(max(d, 0) for d in gaps)
    N = sum(max(-d, 0) for d in gaps)
    abs_mass = P + N
    aggregate = Fraction(abs(dsum), 2 * S)
    mass = Fraction(abs_mass, 2 * S)
    macro = sum((Fraction(abs(gaps[i]), 2 * sums[i]) for i in valid), Fraction()) / len(valid)
    cancellation_load = mass - aggregate
    cancellation_fraction = Fraction(0) if abs_mass == 0 else Fraction(2 * min(P, N), abs_mass)
    row_ginis = [Fraction(abs(gaps[i]), 2 * sums[i]) for i in valid]
    left = sum(a for a, _ in pairs)
    right = sum(b for _, b in pairs)
    result = {
        "n": n,
        "nonempty_rows": len(valid),
        "zero_mass_rows": n - len(valid),
        "token_mass": S,
        "positive_gap_count": sum(d > 0 for d in gaps),
        "zero_gap_count": sum(d == 0 for d in gaps),
        "negative_gap_count": sum(d < 0 for d in gaps),
        "positive_gap_mass": P,
        "negative_gap_mass": N,
        "aggregate_gini": frac_json(aggregate),
        "mass_weighted_sentence_gini": frac_json(mass),
        "macro_sentence_gini": frac_json(macro),
        "cancellation_load": frac_json(cancellation_load),
        "cancellation_fraction": frac_json(cancellation_fraction),
        "row_gini_quantiles": {
            "p50_nearest_rank": frac_json(nearest_rank(row_ginis, Fraction(1, 2))),
            "p90_nearest_rank": frac_json(nearest_rank(row_ginis, Fraction(9, 10))),
            "max": frac_json(max(row_ginis)),
        },
        "mean_language_costs": [float(Fraction(left, n)), float(Fraction(right, n))],
        "total_cost": frac_json(Fraction(S, n)),
        "worst_language_cost": frac_json(Fraction(max(left, right), n)),
    }
    if aggregate != mass - cancellation_load:
        raise RuntimeError("cancellation identity failed")
    return result


def F(record, key):
    item = record[key]
    return Fraction(item["numerator"], item["denominator"])


def macro(records):
    keys = [
        "aggregate_gini",
        "mass_weighted_sentence_gini",
        "macro_sentence_gini",
        "cancellation_load",
        "cancellation_fraction",
        "total_cost",
        "worst_language_cost",
    ]
    return {key: frac_json(sum((F(r, key) for r in records), Fraction()) / len(records)) for key in keys} | {
        "works": len(records)
    }


def author(work):
    return work.split("-", 1)[0]


def classify(candidate, reference):
    da = F(candidate, "aggregate_gini") - F(reference, "aggregate_gini")
    dm = F(candidate, "mass_weighted_sentence_gini") - F(reference, "mass_weighted_sentence_gini")
    dmacro = F(candidate, "macro_sentence_gini") - F(reference, "macro_sentence_gini")
    dc = F(candidate, "cancellation_load") - F(reference, "cancellation_load")
    return {
        "delta_aggregate_gini": frac_json(da),
        "delta_mass_weighted_sentence_gini": frac_json(dm),
        "delta_macro_sentence_gini": frac_json(dmacro),
        "delta_cancellation_load": frac_json(dc),
        "delta_total_cost": frac_json(F(candidate, "total_cost") - F(reference, "total_cost")),
        "delta_worst_language_cost": frac_json(F(candidate, "worst_language_cost") - F(reference, "worst_language_cost")),
        "cancellation_consistent_mismatch": da < 0 and dm >= 0 and dc > dm,
        "macro_row_mismatch": da < 0 and dmacro >= 0,
        "aligned_improvement": da < 0 and dm < 0,
    }


old = load("multibook_raw_evaluation.json")
pair = load("pair_candidate_evaluation.json")
full = load("full_candidate_evaluation.json")
eff = load("efficiency_candidate_evaluation.json")
if not (pair["source_sampling_sha256"] == full["source_sampling_sha256"] == eff["source_sampling_sha256"]):
    raise RuntimeError("candidate samples differ")

arms = {name: {"books": books, "tico": {}} for name, books in old["arms"].items()}
for source in (pair, full, eff):
    for name, record in source["arms"].items():
        if name in arms:
            raise RuntimeError("duplicate arm")
        arms[name] = {"books": record["books"], "tico": record["tico"]}
for name in old["arms"]:
    arms[name]["tico"]["tico.dev100"] = eff["old_tico_results"][name]["datasets"]["tico.dev100"]
if len(arms) != 16:
    raise RuntimeError("expected 16 arms")

checks = []
results = {}
for name in sorted(arms):
    record = arms[name]
    tico_stored = record["tico"]["tico.dev100"]
    tico = metrics(tico_stored["paired_costs"])
    works = {work: metrics(stored["paired_costs"]) for work, stored in sorted(record["books"].items())}
    pooled_pairs = [row for stored in record["books"].values() for row in stored["paired_costs"]]
    if len(works) != 10 or len(pooled_pairs) != 5120:
        raise RuntimeError("unexpected Books coverage")
    for label, observed, stored in [("tico.dev100", tico, tico_stored)] + [
        (work, works[work], record["books"][work]) for work in works
    ]:
        macro_present = "mean_sentence_gini" in stored
        checks.append({
            "arm": name,
            "unit": label,
            "stored_aggregate_matches": abs(observed["aggregate_gini"]["decimal"] - stored["gini"]) <= 1e-12,
            "stored_macro_present": macro_present,
            "stored_macro_matches": (
                abs(observed["macro_sentence_gini"]["decimal"] - stored["mean_sentence_gini"]) <= 1e-12
                if macro_present else None
            ),
        })
    results[name] = {
        "tico_dev100": tico,
        "books_by_work": works,
        "books_macro": macro(list(works.values())),
        "books_pooled": metrics(pooled_pairs),
    }

if not all(c["stored_aggregate_matches"] and (c["stored_macro_matches"] is not False) for c in checks):
    raise RuntimeError("stored metric mismatch")

authors = sorted({author(work) for work in results["classical"]["books_by_work"]})
contrasts = {}
for name in sorted(arms):
    if name == "classical":
        continue
    item = {
        "tico_dev100": classify(results[name]["tico_dev100"], results["classical"]["tico_dev100"]),
        "books_macro": classify(results[name]["books_macro"], results["classical"]["books_macro"]),
        "books_pooled": classify(results[name]["books_pooled"], results["classical"]["books_pooled"]),
        "books_leave_one_author_out": {},
    }
    for omitted in authors:
        candidate_units = [v for w, v in results[name]["books_by_work"].items() if author(w) != omitted]
        reference_units = [v for w, v in results["classical"]["books_by_work"].items() if author(w) != omitted]
        item["books_leave_one_author_out"][omitted] = classify(macro(candidate_units), macro(reference_units))
    item["stable_books_macro_cancellation_mismatch"] = item["books_macro"]["cancellation_consistent_mismatch"] and all(
        v["cancellation_consistent_mismatch"] for v in item["books_leave_one_author_out"].values()
    )
    item["stable_books_macro_aligned_improvement"] = item["books_macro"]["aligned_improvement"] and all(
        v["aligned_improvement"] for v in item["books_leave_one_author_out"].values()
    )
    contrasts[name] = item

output = {
    "scope": "Retrospective exposed bilingual diagnostic; no confirmation or method-selection claim.",
    "quantile_convention": "nearest-rank",
    "books_authors": authors,
    "verification": {
        "stored_fields_checked": len(checks) + sum(c["stored_macro_present"] for c in checks),
        "recomputed_macro_fields_without_stored_comparator": sum(not c["stored_macro_present"] for c in checks),
        "all_available_stored_fields_passed": True,
        "checks": checks
    },
    "arms": results,
    "all_arm_contrasts_minus_classical": contrasts,
    "arms_with_tico_cancellation_mismatch": [k for k, v in contrasts.items() if v["tico_dev100"]["cancellation_consistent_mismatch"]],
    "arms_with_stable_books_cancellation_mismatch": [k for k, v in contrasts.items() if v["stable_books_macro_cancellation_mismatch"]],
    "arms_with_stable_books_aligned_improvement": [k for k, v in contrasts.items() if v["stable_books_macro_aligned_improvement"]],
    "interpretation_guard": "All observations are deterministic and correlated across related arms on exposed English-French data."
}
(ROOT / "output" / "mass_cancellation_audit.json").write_text(json.dumps(output, indent=2) + "\n")

focus = ["full_minmax", "eff_minmax", "exact_train", "full_pooled", "eff_pooled"]
lines = [
    "# Exact token-mass cancellation audit",
    "",
    "Retrospective exposed English-French diagnostics only. Deltas are method minus Classical.",
    "",
    "| arm | TICO dGagg | TICO dGmass | TICO mismatch | Books dGagg | Books dGmass | Books stable mismatch | Books stable aligned improvement |",
    "|---|---:|---:|:---:|---:|---:|:---:|:---:|",
]
for name in focus:
    t = contrasts[name]["tico_dev100"]
    b = contrasts[name]["books_macro"]
    lines.append(
        f"| {name} | {t['delta_aggregate_gini']['decimal']:.8f} | {t['delta_mass_weighted_sentence_gini']['decimal']:.8f} | "
        f"{t['cancellation_consistent_mismatch']} | {b['delta_aggregate_gini']['decimal']:.8f} | "
        f"{b['delta_mass_weighted_sentence_gini']['decimal']:.8f} | {contrasts[name]['stable_books_macro_cancellation_mismatch']} | "
        f"{contrasts[name]['stable_books_macro_aligned_improvement']} |"
    )
lines += [
    "",
    f"TICO cancellation-mismatch arms: {output['arms_with_tico_cancellation_mismatch']}",
    f"Stable Books cancellation-mismatch arms: {output['arms_with_stable_books_cancellation_mismatch']}",
    f"Stable Books aligned-improvement arms: {output['arms_with_stable_books_aligned_improvement']}",
    "",
    "These are deterministic exposed-set signatures, not causal or prospective evidence.",
]
(ROOT / "output" / "mass_cancellation_summary.md").write_text("\n".join(lines) + "\n")
