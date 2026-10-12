import collections
import datetime
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(".")
LANGS = ["en", "fr", "es"]
WINDOW = 100
ALPHA = 2
GLOBAL = 500


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gini(values):
    values = [float(x) for x in values]
    return sum(abs(a - b) for a in values for b in values) / (2 * len(values) * sum(values))


def load_dict(path):
    counter = collections.Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        word, count = line.rsplit(" ", 1)
        counter[tuple(word)] += int(count)
    return counter


def load_codes(path):
    return [tuple(line.split(" ")) for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]


def apply_merge(seq, pair):
    a, b = pair
    out = []
    i = 0
    while i < len(seq):
        if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(seq[i])
            i += 1
    return tuple(out)


def merge_counter(counter, pair):
    out = collections.Counter()
    reduction = 0
    for seq, count in counter.items():
        merged = apply_merge(seq, pair)
        reduction += (len(seq) - len(merged)) * count
        out[merged] += count
    return out, reduction


def lengths(counters):
    return [sum(len(seq) * count for seq, count in counter.items()) for counter in counters]


def select_window_target(dev_lengths, history):
    threshold = ALPHA / len(LANGS)
    valid = set(range(len(LANGS)))
    while True:
        idx = max(valid, key=lambda j: (dev_lengths[j], -j))
        if history.count(idx) / WINDOW <= threshold:
            return idx
        valid.remove(idx)


train = [load_dict(ROOT / "inputs" / f"{lang}.dict") for lang in LANGS]
dev = [load_dict(ROOT / "inputs" / f"dev.{lang}.dict") for lang in LANGS]
codes = load_codes(ROOT / "output/hybrid_window.codes")
assert len(codes) == 1000
classical = load_codes(ROOT / "inputs/classical.codes")
hybrid = load_codes(ROOT / "inputs/hybrid.codes")
assert codes[:GLOBAL] == classical[:GLOBAL] == hybrid[:GLOBAL]

history = collections.deque(maxlen=WINDOW)
tail = []
prior_signs = None
all_crossings = 0
tail_crossings = 0
gini_worsening = 0
for rank, pair in enumerate(codes, start=1):
    before = lengths(dev)
    before_gini = gini(before)
    selected = None
    if rank > GLOBAL:
        selected = select_window_target(before, history)
        history.append(selected)
    train_reduction = []
    dev_reduction = []
    for j in range(3):
        train[j], red = merge_counter(train[j], pair)
        train_reduction.append(red)
        dev[j], red = merge_counter(dev[j], pair)
        dev_reduction.append(red)
    after = lengths(dev)
    signs = []
    for gap in (after[0] - after[1], after[0] - after[2], after[1] - after[2]):
        signs.append(0 if gap == 0 else (1 if gap > 0 else -1))
    crossings = 0 if prior_signs is None else sum(a != 0 and b != 0 and a != b for a, b in zip(prior_signs, signs))
    prior_signs = signs
    all_crossings += crossings
    if rank > GLOBAL:
        tail_crossings += crossings
        if gini(after) > before_gini + 1e-15:
            gini_worsening += 1
        tail.append(
            {
                "rank": rank,
                "pair": list(pair),
                "selected_target_index": selected,
                "selected_target": LANGS[selected],
                "dev_lengths_before": before,
                "dev_lengths_after": after,
                "dev_reduction": dev_reduction,
                "train_reduction": train_reduction,
                "pairwise_gap_sign_crossings": crossings,
                "gini_before": before_gini,
                "gini_after": gini(after),
            }
        )

final_lengths = lengths(dev)
rows = 970
means = [value / rows for value in final_lengths]
baseline = json.loads((ROOT / "inputs/wake19_mechanism_summary.json").read_text(encoding="utf-8"))["arms"]
classical_final = baseline["classical"]["checkpoints"]["1000"]
hybrid_final = baseline["hybrid"]["checkpoints"]["1000"]
targets = [step["selected_target"] for step in tail]
switches = sum(a != b for a, b in zip(targets, targets[1:]))

rules = {
    "crossings_strictly_lower_than_hybrid": tail_crossings < baseline["hybrid"]["phases"]["tail_501_1000"]["pairwise_gap_sign_crossings"],
    "switches_strictly_lower_than_hybrid": switches < baseline["hybrid"]["phases"]["tail_501_1000"]["target_switches"],
    "positive_fairness_gain_vs_classical": gini(means) < classical_final["gini"],
    "total_cost_no_higher_than_hybrid": sum(means) <= hybrid_final["total_mean_cost"] + 1e-12,
}
rules["promote_to_fresh_confirmation"] = all(rules.values())
summary = {
    "schema_version": 1,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "TICO development-only mechanism and selection check; no new confirmation data accessed.",
    "rows": rows,
    "languages": LANGS,
    "candidate": {
        "code_sha256": sha(ROOT / "output/hybrid_window.codes"),
        "global_prefix_merges": GLOBAL,
        "window_size": WINDOW,
        "alpha": ALPHA,
        "final_total_tokens": dict(zip(LANGS, final_lengths)),
        "final_mean_tokens": dict(zip(LANGS, means)),
        "gini": gini(means),
        "total_mean_cost": sum(means),
        "worst_language": LANGS[means.index(max(means))],
        "worst_mean_cost": max(means),
        "tail_pairwise_gap_sign_crossings": tail_crossings,
        "tail_target_switches": switches,
        "tail_target_counts": dict(collections.Counter(targets)),
        "tail_gini_worsening_steps": gini_worsening,
    },
    "comparators": {
        "classical": classical_final,
        "hybrid": hybrid_final,
        "hybrid_tail_crossings": baseline["hybrid"]["phases"]["tail_501_1000"]["pairwise_gap_sign_crossings"],
        "hybrid_tail_target_switches": baseline["hybrid"]["phases"]["tail_501_1000"]["target_switches"],
    },
    "contrasts": {
        "gini_change_vs_classical": gini(means) - classical_final["gini"],
        "gini_change_vs_hybrid": gini(means) - hybrid_final["gini"],
        "total_cost_pct_vs_classical": 100 * (sum(means) / classical_final["total_mean_cost"] - 1),
        "total_cost_pct_vs_hybrid": 100 * (sum(means) / hybrid_final["total_mean_cost"] - 1),
        "crossing_change_vs_hybrid": tail_crossings - baseline["hybrid"]["phases"]["tail_501_1000"]["pairwise_gap_sign_crossings"],
        "switch_change_vs_hybrid": switches - baseline["hybrid"]["phases"]["tail_501_1000"]["target_switches"],
    },
    "frozen_decision_rules": rules,
}
(ROOT / "output/hybrid_window_trace.json").write_text(json.dumps({"schema_version": 1, "tail_steps": tail}, separators=(",", ":")) + "\n")
(ROOT / "output/hybrid_window_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

