import json, math, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])

def parse(path):
    text = path.read_text(errors="replace")
    rows = []
    pattern = re.compile(r"lengths \[([^\]]+)\]: picking best subword in corpus (\d+)")
    for match in pattern.finditer(text):
        lengths = [int(x) for x in match.group(1).split()]
        rows.append((lengths, int(match.group(2))))
    return rows

def summarize(name, rows):
    assert len(rows) == 1000, (name, len(rows))
    dims = len(rows[0][0])
    selected = [idx for _, idx in rows]
    zero_selected_gain = 0
    total_selected_gain = 0
    switches = sum(a != b for a, b in zip(selected, selected[1:]))
    for (cur, idx), (nxt, _) in zip(rows, rows[1:]):
        gain = cur[idx] - nxt[idx]
        assert gain >= 0, (name, gain)
        zero_selected_gain += gain == 0
        total_selected_gain += gain
    result = {
        "steps": len(rows), "dimensions": dims,
        "selected_language_counts": {str(i): selected.count(i) for i in sorted(set(selected))},
        "selection_switches": switches,
        "zero_selected_gain_steps_excluding_last": zero_selected_gain,
        "total_selected_dev_gain_excluding_last": total_selected_gain,
        "initial_lengths": rows[0][0], "final_premerge_lengths": rows[-1][0],
    }
    if dims == 4:
        domains = []
        inferred_languages = []
        mismatch = 0
        worst_gini = []
        for lengths, recorded in rows:
            matrix = [lengths[:2], lengths[2:]]
            rel = [[2*x/sum(pair) for x in pair] for pair in matrix]
            flat = [(rel[d][l], d, l) for d in range(2) for l in range(2)]
            _, d, l = max(flat, key=lambda x: x[0])
            domains.append(d); inferred_languages.append(l)
            mismatch += l != recorded
            worst_gini.append(max(abs(a-b)/(2*(a+b)) for a,b in matrix))
        result.update({
            "selected_domain_counts": {str(i): domains.count(i) for i in [0,1]},
            "selector_reconstruction_language_mismatches": mismatch,
            "initial_worst_domain_gini": worst_gini[0],
            "final_premerge_worst_domain_gini": worst_gini[-1],
            "worst_domain_switches": sum(a != b for a,b in zip(domains,domains[1:])),
        })
    return result

inventory = {
    "base": ROOT / "base.stderr.txt",
    "pooled": ROOT / "pooled.stderr.txt",
    "robust_domain": ROOT / "robust.stderr.txt",
}
result = {name: summarize(name, parse(path)) for name, path in inventory.items()}
OUT.write_text(json.dumps({"schema_version": 1, "scope": "retrospective verbose-log mechanism analysis; no confirmation eligibility", "results": result}, indent=2))
print(json.dumps(result, indent=2))
