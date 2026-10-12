import collections
import datetime
import json
from pathlib import Path


ROOT = Path(".")
LANGS = ["en", "fr", "es"]
WINDOW = 100
ALPHA = 2


def load_dict(path):
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        token, count = line.rsplit(" ", 1)
        result.append((token, int(count)))
    return result


def load_codes(path):
    return [tuple(line.split(" ")) for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]


def encoded_length(token, rank):
    pieces = list(token)
    while len(pieces) > 1:
        available = [(rank[pair], idx, pair) for idx, pair in enumerate(zip(pieces, pieces[1:])) if pair in rank]
        if not available:
            break
        chosen = min(available)[2]
        merged = []
        i = 0
        while i < len(pieces):
            if i + 1 < len(pieces) and (pieces[i], pieces[i + 1]) == chosen:
                merged.append(pieces[i] + pieces[i + 1])
                i += 2
            else:
                merged.append(pieces[i])
                i += 1
        pieces = merged
    return len(pieces)


def gini(values):
    return sum(abs(a - b) for a in values for b in values) / (2 * len(values) * sum(values))


def selected_target(lengths, history):
    valid = set(range(3))
    threshold = ALPHA / 3
    while True:
        idx = max(valid, key=lambda j: (lengths[j], -j))
        if history.count(idx) / WINDOW <= threshold:
            return idx
        valid.remove(idx)


summary = json.loads((ROOT / "output/hybrid_window_summary.json").read_text(encoding="utf-8"))
trace = json.loads((ROOT / "output/hybrid_window_trace.json").read_text(encoding="utf-8"))["tail_steps"]
codes = load_codes(ROOT / "output/hybrid_window.codes")
classical = load_codes(ROOT / "inputs/classical.codes")
checks = {}
checks["merge_count_1000"] = len(codes) == 1000
checks["global_prefix_exact_500"] = codes[:500] == classical[:500]
rank = {pair: idx for idx, pair in enumerate(codes)}
totals = []
for lang in LANGS:
    total = sum(encoded_length(token, rank) * count for token, count in load_dict(ROOT / "inputs" / f"dev.{lang}.dict"))
    totals.append(total)
checks["direct_total_tokens_match"] = dict(zip(LANGS, totals)) == summary["candidate"]["final_total_tokens"]
means = [value / summary["rows"] for value in totals]
checks["direct_mean_tokens_match"] = all(abs(means[i] - summary["candidate"]["final_mean_tokens"][lang]) < 1e-12 for i, lang in enumerate(LANGS))
checks["direct_gini_match"] = abs(gini(means) - summary["candidate"]["gini"]) < 1e-15

history = collections.deque(maxlen=WINDOW)
targets = []
crossings = 0
prior_signs = None
for pos, step in enumerate(trace):
    expected_rank = 501 + pos
    checks[f"rank_{expected_rank}_identity"] = step["rank"] == expected_rank
    idx = selected_target(step["dev_lengths_before"], history)
    history.append(idx)
    targets.append(LANGS[idx])
    checks[f"rank_{expected_rank}_target"] = idx == step["selected_target_index"]
    after = step["dev_lengths_after"]
    signs = [0 if gap == 0 else (1 if gap > 0 else -1) for gap in (after[0] - after[1], after[0] - after[2], after[1] - after[2])]
    if prior_signs is None:
        before = step["dev_lengths_before"]
        prior_signs = [0 if gap == 0 else (1 if gap > 0 else -1) for gap in (before[0] - before[1], before[0] - before[2], before[1] - before[2])]
    crossings += sum(a != 0 and b != 0 and a != b for a, b in zip(prior_signs, signs))
    prior_signs = signs
switches = sum(a != b for a, b in zip(targets, targets[1:]))
checks["tail_target_count_500"] = len(targets) == 500
checks["tail_switches_match"] = switches == summary["candidate"]["tail_target_switches"]
checks["tail_crossings_match"] = crossings == summary["candidate"]["tail_pairwise_gap_sign_crossings"]
checks["target_counts_match"] = dict(collections.Counter(targets)) == summary["candidate"]["tail_target_counts"]

rules = summary["frozen_decision_rules"]
checks["fairness_rule_recomputed"] = rules["positive_fairness_gain_vs_classical"] == (summary["candidate"]["gini"] < summary["comparators"]["classical"]["gini"])
checks["cost_rule_recomputed"] = rules["total_cost_no_higher_than_hybrid"] == (summary["candidate"]["total_mean_cost"] <= summary["comparators"]["hybrid"]["total_mean_cost"] + 1e-12)
checks["crossing_rule_recomputed"] = rules["crossings_strictly_lower_than_hybrid"] == (crossings < summary["comparators"]["hybrid_tail_crossings"])
checks["switch_rule_recomputed"] = rules["switches_strictly_lower_than_hybrid"] == (switches < summary["comparators"]["hybrid_tail_target_switches"])
checks["promotion_rule_conjunction"] = rules["promote_to_fresh_confirmation"] == all(value for key, value in rules.items() if key != "promote_to_fresh_confirmation")

failed = [name for name, ok in checks.items() if not ok]
result = {
    "schema_version": 1,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "method": "Independent direct final-token encoding plus moving-window trace recomputation.",
    "checks_total": len(checks),
    "checks_passed": sum(checks.values()),
    "failed": failed,
    "direct_final_total_tokens": dict(zip(LANGS, totals)),
    "recomputed_tail_crossings": crossings,
    "recomputed_tail_switches": switches,
}
Path("output/hybrid_window_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
assert not failed, failed[:10]
print(json.dumps(result, indent=2))

