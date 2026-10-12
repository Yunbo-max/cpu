import json
import math
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "inputs" / name).read_text())


def gini2(a, b):
    denominator = 2 * (a + b)
    return abs(a - b) / denominator if denominator else 0.0


def paired_metrics(pairs):
    if not pairs:
        raise RuntimeError("Empty paired-cost table")
    if any(len(row) != 2 or min(row) < 0 for row in pairs):
        raise RuntimeError("Invalid paired-cost row")
    left = [row[0] for row in pairs]
    right = [row[1] for row in pairs]
    gaps = [a - b for a, b in pairs]
    abs_gaps = [abs(value) for value in gaps]
    sentence = [gini2(a, b) for a, b in pairs]
    abs_sum = sum(abs_gaps)
    cancellation = 0.0 if abs_sum == 0 else 1 - abs(sum(gaps)) / abs_sum
    return {
        "n": len(pairs),
        "mean_tokens": [mean(left), mean(right)],
        "aggregate_gini": gini2(mean(left), mean(right)),
        "mean_sentence_gini": mean(sentence),
        "mean_absolute_token_gap": mean(abs_gaps),
        "signed_mean_token_gap": mean(gaps),
        "cancellation_ratio": cancellation,
        "left_longer": sum(value > 0 for value in gaps),
        "right_longer": sum(value < 0 for value in gaps),
        "ties": sum(value == 0 for value in gaps),
        "worst_language_cost": max(mean(left), mean(right)),
        "total_cost": mean(left) + mean(right),
    }


def check_stored(observed, stored, label, checks):
    mapping = {
        "mean_tokens": "mean_tokens",
        "aggregate_gini": "gini",
        "mean_sentence_gini": "mean_sentence_gini",
        "worst_language_cost": "worst_cost",
        "total_cost": "sum_language_means",
    }
    for ours, theirs in mapping.items():
        if theirs not in stored:
            continue
        left, right = observed[ours], stored[theirs]
        if isinstance(left, list):
            ok = len(left) == len(right) and all(abs(a - b) <= 1e-12 for a, b in zip(left, right))
        else:
            ok = abs(left - right) <= 1e-12
        checks.append({"table": label, "field": theirs, "passed": ok})
        if not ok:
            raise RuntimeError(f"Stored arithmetic mismatch: {label} {theirs}: {left} != {right}")


def rankdata(values):
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    offset = 0
    while offset < len(order):
        end = offset + 1
        while end < len(order) and values[order[end]] == values[order[offset]]:
            end += 1
        rank = (offset + 1 + end) / 2
        for position in range(offset, end):
            ranks[order[position]] = rank
        offset = end
    return ranks


def pearson(left, right):
    ml, mr = mean(left), mean(right)
    numerator = sum((a - ml) * (b - mr) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - ml) ** 2 for a in left) * sum((b - mr) ** 2 for b in right))
    return numerator / denominator if denominator else None


def spearman(rows, left_key, right_key):
    left = [row[left_key] for row in rows]
    right = [row[right_key] for row in rows]
    return pearson(rankdata(left), rankdata(right))


old = load("multibook_raw_evaluation.json")
pair = load("pair_candidate_evaluation.json")
full = load("full_candidate_evaluation.json")
eff = load("efficiency_candidate_evaluation.json")

if not (pair["source_sampling_sha256"] == full["source_sampling_sha256"] == eff["source_sampling_sha256"]):
    raise RuntimeError("Candidate evaluations do not bind the same Books sample")

arms = {}
for arm, works in old["arms"].items():
    arms[arm] = {"books": works, "tico": {}}
for source in (pair, full, eff):
    for arm, record in source["arms"].items():
        if arm in arms:
            raise RuntimeError(f"Duplicate arm identity: {arm}")
        arms[arm] = {"books": record["books"], "tico": record["tico"]}

old_tico = eff["old_tico_results"]
for arm in old["arms"]:
    arms[arm]["tico"]["tico.dev100"] = old_tico[arm]["datasets"]["tico.dev100"]

if len(arms) != 16:
    raise RuntimeError(f"Expected 16 arms, observed {len(arms)}")

arithmetic_checks = []
arm_results = {}
for arm in sorted(arms):
    record = arms[arm]
    tico_stored = record["tico"]["tico.dev100"]
    tico = paired_metrics(tico_stored["paired_costs"])
    check_stored(tico, tico_stored, f"{arm}/tico.dev100", arithmetic_checks)

    works = {}
    all_pairs = []
    for work, stored in sorted(record["books"].items()):
        observed = paired_metrics(stored["paired_costs"])
        check_stored(observed, stored, f"{arm}/books/{work}", arithmetic_checks)
        works[work] = observed
        all_pairs.extend(stored["paired_costs"])
    if len(works) != 10 or len(all_pairs) != 5120:
        raise RuntimeError(f"Unexpected Books coverage for {arm}")
    micro = paired_metrics(all_pairs)
    macro_fields = [
        "aggregate_gini",
        "mean_sentence_gini",
        "mean_absolute_token_gap",
        "cancellation_ratio",
        "worst_language_cost",
        "total_cost",
    ]
    macro = {field: mean([value[field] for value in works.values()]) for field in macro_fields}
    macro["works"] = len(works)
    macro["rows"] = len(all_pairs)
    arm_results[arm] = {"tico_dev100": tico, "books_micro": micro, "books_macro": macro, "books_by_work": works}


rows = []
for arm, result in arm_results.items():
    rows.append(
        {
            "arm": arm,
            "tico_aggregate_gini": result["tico_dev100"]["aggregate_gini"],
            "tico_sentence_gini": result["tico_dev100"]["mean_sentence_gini"],
            "tico_cancellation": result["tico_dev100"]["cancellation_ratio"],
            "tico_cost": result["tico_dev100"]["total_cost"],
            "books_aggregate_gini": result["books_macro"]["aggregate_gini"],
            "books_sentence_gini": result["books_macro"]["mean_sentence_gini"],
            "books_abs_gap": result["books_macro"]["mean_absolute_token_gap"],
            "books_cancellation": result["books_macro"]["cancellation_ratio"],
            "books_cost": result["books_macro"]["total_cost"],
        }
    )

correlations = {
    "tico_aggregate_vs_tico_sentence": spearman(rows, "tico_aggregate_gini", "tico_sentence_gini"),
    "tico_aggregate_vs_books_aggregate": spearman(rows, "tico_aggregate_gini", "books_aggregate_gini"),
    "tico_aggregate_vs_books_sentence": spearman(rows, "tico_aggregate_gini", "books_sentence_gini"),
    "tico_sentence_vs_books_sentence": spearman(rows, "tico_sentence_gini", "books_sentence_gini"),
    "books_aggregate_vs_books_sentence": spearman(rows, "books_aggregate_gini", "books_sentence_gini"),
    "tico_aggregate_vs_books_cost": spearman(rows, "tico_aggregate_gini", "books_cost"),
}

metric_keys = ["tico_aggregate_gini", "tico_sentence_gini", "books_aggregate_gini", "books_sentence_gini", "books_cost"]
for key in metric_keys:
    ranks = rankdata([row[key] for row in rows])
    for row, rank in zip(rows, ranks):
        row[key + "_rank"] = rank

classical = arm_results["classical"]
focus = {}
for arm in ("full_minmax", "eff_minmax", "exact_train", "full_pooled", "eff_pooled"):
    current = arm_results[arm]
    contrasts = {}
    for dataset, block in (("tico_dev100", "tico_dev100"), ("books_macro", "books_macro")):
        contrasts[dataset] = {
            field: current[block][field] - classical[block][field]
            for field in ("aggregate_gini", "mean_sentence_gini", "mean_absolute_token_gap", "cancellation_ratio", "total_cost")
        }
    focus[arm] = contrasts

classical_tico = classical["tico_dev100"]
full_tico = arm_results["full_minmax"]["tico_dev100"]
aggregate_reduction = 1 - full_tico["aggregate_gini"] / classical_tico["aggregate_gini"]
sentence_reduction = 1 - full_tico["mean_sentence_gini"] / classical_tico["mean_sentence_gini"]
full_minmax_gap = {
    "classical_tico_aggregate_gini": classical_tico["aggregate_gini"],
    "full_minmax_tico_aggregate_gini": full_tico["aggregate_gini"],
    "classical_tico_sentence_gini": classical_tico["mean_sentence_gini"],
    "full_minmax_tico_sentence_gini": full_tico["mean_sentence_gini"],
    "aggregate_relative_reduction": aggregate_reduction,
    "sentence_relative_reduction": sentence_reduction,
    "reduction_gap": aggregate_reduction - sentence_reduction,
    "full_minmax_cancellation_ratio": full_tico["cancellation_ratio"],
    "full_minmax_mean_absolute_token_gap": full_tico["mean_absolute_token_gap"],
}

simple_successors = []
for arm, result in arm_results.items():
    if arm == "classical":
        continue
    better_sentence = result["books_macro"]["mean_sentence_gini"] < classical["books_macro"]["mean_sentence_gini"]
    better_gap = result["books_macro"]["mean_absolute_token_gap"] < classical["books_macro"]["mean_absolute_token_gap"]
    no_cost_increase = result["books_macro"]["total_cost"] <= classical["books_macro"]["total_cost"]
    if (better_sentence or better_gap) and no_cost_increase:
        simple_successors.append(
            {
                "arm": arm,
                "better_sentence_gini": better_sentence,
                "better_mean_absolute_gap": better_gap,
                "no_total_cost_increase": no_cost_increase,
            }
        )

ranked = sorted(rows, key=lambda row: row["tico_aggregate_gini"])
result = {
    "scope": "Retrospective, exposed bilingual mechanism diagnostic; no confirmation or method-selection claim.",
    "input_identity": {
        "books_sampling_sha256": eff["source_sampling_sha256"],
        "arms": len(arms),
        "books_works_per_arm": 10,
        "books_rows_per_arm": 5120,
        "tico_rows_per_arm": 100,
    },
    "arithmetic_verification": {
        "field_checks": len(arithmetic_checks),
        "all_passed": all(item["passed"] for item in arithmetic_checks),
        "checks": arithmetic_checks,
    },
    "arm_results": arm_results,
    "cross_arm_rows": sorted(rows, key=lambda row: row["arm"]),
    "spearman_descriptive": correlations,
    "full_minmax_objective_gap": full_minmax_gap,
    "focus_contrasts_minus_classical": focus,
    "ranked_by_tico_aggregate_gini": [row["arm"] for row in ranked],
    "development_arms_meeting_sentence_or_gap_and_cost_rule": simple_successors,
    "interpretation_guard": "Correlations across 16 related arms are descriptive and non-independent; they are not p-values, causal evidence or population estimates.",
}

(ROOT / "output" / "objective_mismatch_diagnostic.json").write_text(json.dumps(result, indent=2) + "\n")

summary_lines = [
    "# Aggregate-versus-sentence fairness diagnostic",
    "",
    "All inputs are exposed English–French development diagnostics. Lower values are better; correlations are descriptive across related method variants.",
    "",
    "## Central decomposition",
    "",
    f"- Classical TICO dev100 aggregate Gini: {classical_tico['aggregate_gini']:.8f}",
    f"- full_minmax TICO dev100 aggregate Gini: {full_tico['aggregate_gini']:.8f}",
    f"- Classical mean sentence Gini: {classical_tico['mean_sentence_gini']:.8f}",
    f"- full_minmax mean sentence Gini: {full_tico['mean_sentence_gini']:.8f}",
    f"- Aggregate relative reduction: {aggregate_reduction:.4%}",
    f"- Sentence relative reduction: {sentence_reduction:.4%}",
    f"- full_minmax cancellation ratio: {full_tico['cancellation_ratio']:.8f}",
    f"- full_minmax mean absolute token gap: {full_tico['mean_absolute_token_gap']:.8f}",
    "",
    "## Descriptive rank correlations",
    "",
]
for key, value in correlations.items():
    summary_lines.append(f"- {key}: {value:.6f}" if value is not None else f"- {key}: undefined")
summary_lines += [
    "",
    "## Focus contrasts versus Classical",
    "",
    "| arm | TICO agg Δ | TICO sentence Δ | Books agg Δ | Books sentence Δ | Books cost Δ |",
    "|---|---:|---:|---:|---:|---:|",
]
for arm in focus:
    td = focus[arm]["tico_dev100"]
    bd = focus[arm]["books_macro"]
    summary_lines.append(
        f"| {arm} | {td['aggregate_gini']:.8f} | {td['mean_sentence_gini']:.8f} | "
        f"{bd['aggregate_gini']:.8f} | {bd['mean_sentence_gini']:.8f} | {bd['total_cost']:.8f} |"
    )
summary_lines += [
    "",
    "## Frozen simple decision rule",
    "",
    "Arms that improve Books mean sentence Gini or mean absolute token gap without increasing total token cost versus Classical:",
    "",
    json.dumps(simple_successors, ensure_ascii=False),
    "",
    f"Arithmetic checks passed: {len(arithmetic_checks)} / {len(arithmetic_checks)}.",
    "",
    "This diagnostic can motivate a new objective derivation, but it cannot select or confirm a method on these already inspected data.",
]
(ROOT / "output" / "objective_mismatch_summary.md").write_text("\n".join(summary_lines) + "\n")

print(
    json.dumps(
        {
            "arms": len(arms),
            "arithmetic_checks": len(arithmetic_checks),
            "full_minmax_objective_gap": full_minmax_gap,
            "spearman_descriptive": correlations,
            "simple_successors": simple_successors,
        },
        ensure_ascii=False,
    )
)
