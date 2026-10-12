import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text())


def F(record):
    return Fraction(record["numerator"], record["denominator"])


def sgn(value):
    return 1 if value > 0 else (-1 if value < 0 else 0)


result = load("output/conditional_shift_decomposition.json")
prior = load("inputs/mass_cancellation_audit.json")
checks = []


def check(label, passed):
    checks.append({"label": label, "passed": bool(passed)})
    if not passed:
        raise RuntimeError(f"verification failed: {label}")


check("15 arm contrasts", len(result["arm_results"]) == 15)
check("three frozen focus arms", sorted(result["focus_predeclared_arms"]) == ["eff_minmax", "exact_train", "full_minmax"])

author_work_counts = {
    "Bronte_Charlotte": 1,
    "Defoe_Daniel": 1,
    "Doyle_Arthur_Conan": 2,
    "Dumas_Alexandre": 1,
    "Verne_Jules": 4,
    "Voltaire": 1,
}

for arm, arm_record in sorted(result["arm_results"].items()):
    tico_expected = F(prior["arms"]["classical"]["tico_dev100"]["macro_sentence_gini"]) - F(
        prior["arms"][arm]["tico_dev100"]["macro_sentence_gini"]
    )
    books_expected = F(prior["arms"]["classical"]["books_macro"]["macro_sentence_gini"]) - F(
        prior["arms"][arm]["books_macro"]["macro_sentence_gini"]
    )
    for partition, partition_record in sorted(arm_record["partitions"].items()):
        check(f"{arm}/{partition}/tico group count", sum(g["tico_count"] for g in partition_record["groups"].values()) == 100)
        check(f"{arm}/{partition}/books group count", sum(g["books_count"] for g in partition_record["groups"].values()) == 5120)
        fairness = partition_record["outcomes"]["macro_row_gini_gain"]
        check(f"{arm}/{partition}/prior TICO macro cross-check", F(fairness["tico_mean"]) == tico_expected)
        check(f"{arm}/{partition}/prior Books macro cross-check", F(fairness["books_mean"]) == books_expected)
        for outcome, record in sorted(partition_record["outcomes"].items()):
            check(f"{arm}/{partition}/{outcome}/total identity", F(record["books_mean"]) - F(record["tico_mean"]) == F(record["total_shift"]))
            if record["estimable"]:
                check(
                    f"{arm}/{partition}/{outcome}/component identity",
                    F(record["composition_component"]) + F(record["conditional_component"]) == F(record["total_shift"]),
                )
    for omitted, loo in sorted(arm_record["leave_one_author_out"].items()):
        expected_rows = 5120 - author_work_counts[omitted] * 512
        for partition, partition_record in sorted(loo.items()):
            check(
                f"{arm}/omit-{omitted}/{partition}/books group count",
                sum(g["books_count"] for g in partition_record["groups"].values()) == expected_rows,
            )
            for outcome, record in sorted(partition_record["outcomes"].items()):
                check(
                    f"{arm}/omit-{omitted}/{partition}/{outcome}/total identity",
                    F(record["books_mean"]) - F(record["tico_mean"]) == F(record["total_shift"]),
                )
                if record["estimable"]:
                    check(
                        f"{arm}/omit-{omitted}/{partition}/{outcome}/component identity",
                        F(record["composition_component"]) + F(record["conditional_component"]) == F(record["total_shift"]),
                    )
    for partition, outcomes in sorted(arm_record["author_block_sign_stability"].items()):
        for outcome, stable in sorted(outcomes.items()):
            if not stable["estimable"]:
                continue
            full = arm_record["partitions"][partition]["outcomes"][outcome]
            loos = [arm_record["leave_one_author_out"][a][partition]["outcomes"][outcome] for a in result["identity"]["books_authors"]]
            check(
                f"{arm}/{partition}/{outcome}/total sign ledger",
                stable["total_signs_full_and_loo"] == [sgn(F(full["total_shift"]))] + [sgn(F(x["total_shift"])) for x in loos],
            )
            check(
                f"{arm}/{partition}/{outcome}/composition sign ledger",
                stable["composition_signs_full_and_loo"] == [sgn(F(full["composition_component"]))] + [sgn(F(x["composition_component"])) for x in loos],
            )
            check(
                f"{arm}/{partition}/{outcome}/conditional sign ledger",
                stable["conditional_signs_full_and_loo"] == [sgn(F(full["conditional_component"]))] + [sgn(F(x["conditional_component"])) for x in loos],
            )

output = {
    "scope": "Independent output-identity, coverage, exact-fraction and prior-macro cross-check; not a causal or statistical validation.",
    "checks": len(checks),
    "all_passed": all(item["passed"] for item in checks),
    "details": checks,
}
(ROOT / "output" / "conditional_shift_verification.json").write_text(json.dumps(output, indent=2) + "\n")
