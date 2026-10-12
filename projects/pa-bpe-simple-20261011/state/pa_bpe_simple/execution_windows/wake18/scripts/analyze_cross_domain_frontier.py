import hashlib, json
from pathlib import Path

ARMS = ['classical', 'base', 'window', 'hybrid', 'ratio']
gv = json.loads(Path('inputs/globalvoices_confirmation.json').read_text())
fl = json.loads(Path('output/flores_secondary.json').read_text())
domains = {'GlobalVoices': gv['arms'], 'FLORES': fl['arms']}

def point(arm):
    return {
        'gini': arm['gini'],
        'gain': arm['gini_improvement_vs_classical'],
        'total_cost_change': arm['total_cost_relative_change'],
        'worst_cost_change': arm['worst_cost_relative_change'],
        'worst_language': arm['worst_language'],
        'mean_sentence_gini': arm['mean_sentence_gini'],
    }

def dominates(a, b):
    weak = a['gini'] <= b['gini'] and a['total_cost_change'] <= b['total_cost_change'] and a['worst_cost_change'] <= b['worst_cost_change']
    strict = a['gini'] < b['gini'] or a['total_cost_change'] < b['total_cost_change'] or a['worst_cost_change'] < b['worst_cost_change']
    return weak and strict

table = {domain: {name: point(arms[name]) for name in ARMS} for domain, arms in domains.items()}
per_domain = {}
for domain, points in table.items():
    pairs = []
    for left in ARMS:
        for right in ARMS:
            if left != right and dominates(points[left], points[right]): pairs.append([left, right])
    frontier = [name for name in ARMS if not any(dominates(points[other], points[name]) for other in ARMS if other != name)]
    per_domain[domain] = {'dominance_pairs': pairs, 'frontier': frontier}

robust = {}
for name in ARMS:
    robust[name] = {
        'minimum_gain_across_domains': min(table[d][name]['gain'] for d in table),
        'maximum_total_cost_change_across_domains': max(table[d][name]['total_cost_change'] for d in table),
        'maximum_worst_cost_change_across_domains': max(table[d][name]['worst_cost_change'] for d in table),
    }
def robust_dominates(a, b):
    weak = a['minimum_gain_across_domains'] >= b['minimum_gain_across_domains'] and a['maximum_total_cost_change_across_domains'] <= b['maximum_total_cost_change_across_domains'] and a['maximum_worst_cost_change_across_domains'] <= b['maximum_worst_cost_change_across_domains']
    strict = a != b
    return weak and strict
robust_pairs = [[a,b] for a in ARMS for b in ARMS if a != b and robust_dominates(robust[a], robust[b])]
robust_frontier = [name for name in ARMS if not any(robust_dominates(robust[other], robust[name]) for other in ARMS if other != name)]

crossovers = {}
for name in ['base','window']:
    h = table['FLORES']['hybrid']; other = table['FLORES'][name]
    crossovers[name] = (h['gini'] - other['gini']) / (other['total_cost_change'] - h['total_cost_change'])

result = {
    'inputs': {
        'globalvoices_sha256': hashlib.sha256(Path('inputs/globalvoices_confirmation.json').read_bytes()).hexdigest(),
        'flores_sha256': hashlib.sha256(Path('output/flores_secondary.json').read_bytes()).hexdigest(),
    },
    'table': table,
    'per_domain': per_domain,
    'robust_summary': robust,
    'robust_dominance_pairs': robust_pairs,
    'robust_frontier': robust_frontier,
    'flores_gini_vs_total_cost_scalarization_breakpoint': crossovers,
    'interpretation': 'Among these frozen arms, hybrid robustly dominates base and window across the two exposed domains when comparing minimum fairness gain and maximum total/worst cost. Classical robustly dominates ratio. The robust frontier is Classical versus hybrid: accepting hybrid means trading a bounded token-cost increase for a positive fairness gain in both domains. This is descriptive mechanism evidence, not causal proof or fresh confirmation.',
    'scope': 'Post-exposure cross-domain analysis of two retained aligned datasets; no tuning, no new tokenizer, and no general multilingual claim.'
}
Path('output/cross_domain_frontier.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'per_domain': per_domain, 'robust_summary': robust, 'robust_frontier': robust_frontier, 'breakpoints': crossovers}, indent=2))
