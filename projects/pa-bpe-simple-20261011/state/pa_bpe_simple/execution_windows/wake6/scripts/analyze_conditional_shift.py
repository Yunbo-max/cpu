import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "inputs" / name).read_text())


def fj(value):
    return {"numerator": value.numerator, "denominator": value.denominator, "decimal": float(value)}


def meanf(values):
    values = list(values)
    if not values:
        return None
    return sum(values, Fraction()) / len(values)


def sign(value):
    return 1 if value > 0 else (-1 if value < 0 else 0)


def row_gini(a, b):
    total = a + b
    if total <= 0:
        raise RuntimeError("zero-mass aligned row")
    return Fraction(abs(a - b), 2 * total)


def paired_rows(reference_pairs, arm_pairs):
    if len(reference_pairs) != len(arm_pairs):
        raise RuntimeError("paired row-count mismatch")
    rows = []
    for index, ((a0, b0), (a1, b1)) in enumerate(zip(reference_pairs, arm_pairs)):
        if min(a0, b0, a1, b1) < 0:
            raise RuntimeError("negative token cost")
        d0, d1 = a0 - b0, a1 - b1
        s0, s1 = a0 + b0, a1 + b1
        rows.append({
            "index": index,
            "baseline_gap": d0,
            "baseline_total": s0,
            "macro_row_gini_gain": row_gini(a0, b0) - row_gini(a1, b1),
            "absolute_gap_reduction": Fraction(abs(d0) - abs(d1)),
            "total_cost_delta": Fraction(s1 - s0),
            "worst_language_cost_delta": Fraction(max(a1, b1) - max(a0, b0)),
        })
    return rows


OUTCOMES = [
    "macro_row_gini_gain",
    "absolute_gap_reduction",
    "total_cost_delta",
    "worst_language_cost_delta",
]


def decompose(tico_rows, books_rows, group_fn, groups):
    output = {"groups": {}, "outcomes": {}}
    for group in groups:
        trows = [row for row in tico_rows if group_fn(row) == group]
        brows = [row for row in books_rows if group_fn(row) == group]
        output["groups"][group] = {
            "tico_count": len(trows),
            "books_count": len(brows),
            "tico_proportion": fj(Fraction(len(trows), len(tico_rows))),
            "books_proportion": fj(Fraction(len(brows), len(books_rows))),
            "tico_conditional_means": {key: (fj(meanf(row[key] for row in trows)) if trows else None) for key in OUTCOMES},
            "books_conditional_means": {key: (fj(meanf(row[key] for row in brows)) if brows else None) for key in OUTCOMES},
        }
    for key in OUTCOMES:
        missing = [
            group for group in groups
            if output["groups"][group]["books_count"] > 0 and output["groups"][group]["tico_count"] == 0
        ]
        tmean = meanf(row[key] for row in tico_rows)
        bmean = meanf(row[key] for row in books_rows)
        if missing:
            output["outcomes"][key] = {
                "estimable": False,
                "missing_tico_conditionals": missing,
                "tico_mean": fj(tmean),
                "books_mean": fj(bmean),
                "total_shift": fj(bmean - tmean),
            }
            continue
        reweighted = sum(
            Fraction(output["groups"][group]["books_count"], len(books_rows))
            * meanf(row[key] for row in tico_rows if group_fn(row) == group)
            for group in groups
            if output["groups"][group]["books_count"] > 0
        )
        composition = reweighted - tmean
        conditional = bmean - reweighted
        total = bmean - tmean
        if composition + conditional != total:
            raise RuntimeError("exact decomposition identity failed")
        output["outcomes"][key] = {
            "estimable": True,
            "tico_mean": fj(tmean),
            "books_mean": fj(bmean),
            "reweighted_tico_mean_at_books_composition": fj(reweighted),
            "total_shift": fj(total),
            "composition_component": fj(composition),
            "conditional_component": fj(conditional),
            "component_with_larger_absolute_magnitude": (
                "composition" if abs(composition) > abs(conditional)
                else "conditional" if abs(conditional) > abs(composition)
                else "equal"
            ),
            "signs": {
                "total": sign(total),
                "composition": sign(composition),
                "conditional": sign(conditional),
            },
        }
    return output


def nearest_rank(values, numerator, denominator):
    ordered = sorted(values)
    rank = max(1, (len(ordered) * numerator + denominator - 1) // denominator)
    return ordered[rank - 1]


def author(work):
    return work.split("-", 1)[0]


old = load("multibook_raw_evaluation.json")
pair = load("pair_candidate_evaluation.json")
full = load("full_candidate_evaluation.json")
eff = load("efficiency_candidate_evaluation.json")
if not (pair["source_sampling_sha256"] == full["source_sampling_sha256"] == eff["source_sampling_sha256"]):
    raise RuntimeError("candidate Books samples differ")

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

reference = arms["classical"]
reference_tico = reference["tico"]["tico.dev100"]["paired_costs"]
works = sorted(reference["books"])
reference_books_by_work = {work: reference["books"][work]["paired_costs"] for work in works}
authors = sorted({author(work) for work in works})
thresholds = [
    nearest_rank([a + b for a, b in reference_tico], 1, 4),
    nearest_rank([a + b for a, b in reference_tico], 1, 2),
    nearest_rank([a + b for a, b in reference_tico], 3, 4),
]


def sign_group(row):
    return "positive" if row["baseline_gap"] > 0 else ("negative" if row["baseline_gap"] < 0 else "zero")


def length_group(row):
    value = row["baseline_total"]
    if value <= thresholds[0]:
        return "q1"
    if value <= thresholds[1]:
        return "q2"
    if value <= thresholds[2]:
        return "q3"
    return "q4"


partitions = {
    "baseline_gap_sign": (sign_group, ["positive", "zero", "negative"]),
    "baseline_length": (length_group, ["q1", "q2", "q3", "q4"]),
}

arm_results = {}
for name in sorted(arms):
    if name == "classical":
        continue
    arm_tico = arms[name]["tico"]["tico.dev100"]["paired_costs"]
    tico_rows = paired_rows(reference_tico, arm_tico)
    books_rows_by_work = {}
    for work in works:
        if work not in arms[name]["books"]:
            raise RuntimeError(f"missing work for {name}: {work}")
        books_rows_by_work[work] = paired_rows(reference_books_by_work[work], arms[name]["books"][work]["paired_costs"])
    books_rows = [row for work in works for row in books_rows_by_work[work]]
    if len(tico_rows) != 100 or len(books_rows) != 5120:
        raise RuntimeError("unexpected coverage")
    result = {"partitions": {}, "leave_one_author_out": {}}
    for partition, (group_fn, groups) in partitions.items():
        result["partitions"][partition] = decompose(tico_rows, books_rows, group_fn, groups)
    for omitted in authors:
        subset = [row for work in works if author(work) != omitted for row in books_rows_by_work[work]]
        result["leave_one_author_out"][omitted] = {
            partition: decompose(tico_rows, subset, group_fn, groups)
            for partition, (group_fn, groups) in partitions.items()
        }
    stability = {}
    for partition in partitions:
        stability[partition] = {}
        for outcome in OUTCOMES:
            full_record = result["partitions"][partition]["outcomes"][outcome]
            loo_records = [result["leave_one_author_out"][a][partition]["outcomes"][outcome] for a in authors]
            if not full_record["estimable"] or not all(record["estimable"] for record in loo_records):
                stability[partition][outcome] = {"estimable": False}
                continue
            stability[partition][outcome] = {
                "estimable": True,
                "total_signs_full_and_loo": [full_record["signs"]["total"]] + [record["signs"]["total"] for record in loo_records],
                "composition_signs_full_and_loo": [full_record["signs"]["composition"]] + [record["signs"]["composition"] for record in loo_records],
                "conditional_signs_full_and_loo": [full_record["signs"]["conditional"]] + [record["signs"]["conditional"] for record in loo_records],
            }
    result["author_block_sign_stability"] = stability
    arm_results[name] = result

focus = {}
for name in ["full_minmax", "eff_minmax", "exact_train"]:
    focus[name] = {}
    for partition in partitions:
        focus[name][partition] = {
            outcome: arm_results[name]["partitions"][partition]["outcomes"][outcome]
            for outcome in ["macro_row_gini_gain", "absolute_gap_reduction", "total_cost_delta"]
        }

result = {
    "scope": "Retrospective exposed English-French descriptive decomposition; not confirmation, causal identification, or method selection.",
    "identity": {
        "arms": len(arms),
        "contrasts": len(arm_results),
        "tico_rows_per_arm": 100,
        "books_works_per_arm": len(works),
        "books_rows_per_arm": 5120,
        "books_authors": authors,
        "books_sampling_sha256": eff["source_sampling_sha256"],
    },
    "tico_classical_length_thresholds_nearest_rank": {"q25": thresholds[0], "q50": thresholds[1], "q75": thresholds[2]},
    "outcome_conventions": {
        "macro_row_gini_gain": "positive is fairness improvement",
        "absolute_gap_reduction": "positive is smaller absolute language token gap",
        "total_cost_delta": "negative is lower total token cost",
        "worst_language_cost_delta": "negative is lower worst-language token cost",
    },
    "arm_results": arm_results,
    "focus_predeclared_arms": focus,
    "interpretation_guard": "Exact decomposition is descriptive on exposed deterministic related arms. Components depend on the chosen partition and do not establish causality or transportability."
}
(ROOT / "output" / "conditional_shift_decomposition.json").write_text(json.dumps(result, indent=2) + "\n")

lines = [
    "# Conditional domain-shift decomposition",
    "",
    "Retrospective exposed English-French diagnostics. Values below decompose Books mean minus TICO mean for each arm-vs-Classical row outcome.",
    "",
    f"Classical TICO length thresholds (nearest rank): q25={thresholds[0]}, q50={thresholds[1]}, q75={thresholds[2]} total tokens.",
    "",
    "| arm | partition | outcome | TICO mean | Books mean | total shift | composition | conditional | larger |",
    "|---|---|---|---:|---:|---:|---:|---:|---|",
]
for name in ["full_minmax", "eff_minmax", "exact_train"]:
    for partition in partitions:
        for outcome in ["macro_row_gini_gain", "absolute_gap_reduction", "total_cost_delta"]:
            row = focus[name][partition][outcome]
            if not row["estimable"]:
                lines.append(f"| {name} | {partition} | {outcome} | NA | NA | NA | NA | NA | non-estimable |")
            else:
                lines.append(
                    f"| {name} | {partition} | {outcome} | {row['tico_mean']['decimal']:.8f} | "
                    f"{row['books_mean']['decimal']:.8f} | {row['total_shift']['decimal']:.8f} | "
                    f"{row['composition_component']['decimal']:.8f} | {row['conditional_component']['decimal']:.8f} | "
                    f"{row['component_with_larger_absolute_magnitude']} |"
                )
lines += [
    "",
    "Component size is not a causal attribution. Author-block sign checks and all 15 contrasts are retained in the JSON.",
]
(ROOT / "output" / "conditional_shift_summary.md").write_text("\n".join(lines) + "\n")
