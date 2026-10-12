import hashlib, json
from pathlib import Path

result = json.loads(Path('output/cross_domain_frontier.json').read_text())
arms = ['classical', 'base', 'window', 'hybrid', 'ratio']
domains = ['GlobalVoices', 'FLORES']
checks = 0
for name in arms:
    gains = [result['table'][domain][name]['gain'] for domain in domains]
    total = [result['table'][domain][name]['total_cost_change'] for domain in domains]
    worst = [result['table'][domain][name]['worst_cost_change'] for domain in domains]
    robust = result['robust_summary'][name]
    assert robust['minimum_gain_across_domains'] == min(gains); checks += 1
    assert robust['maximum_total_cost_change_across_domains'] == max(total); checks += 1
    assert robust['maximum_worst_cost_change_across_domains'] == max(worst); checks += 1

def dominates(a, b):
    return (a['minimum_gain_across_domains'] >= b['minimum_gain_across_domains'] and
            a['maximum_total_cost_change_across_domains'] <= b['maximum_total_cost_change_across_domains'] and
            a['maximum_worst_cost_change_across_domains'] <= b['maximum_worst_cost_change_across_domains'] and a != b)
summary = result['robust_summary']
pairs = sorted([name + '>' + other for name in arms for other in arms if name != other and dominates(summary[name], summary[other])])
expected = sorted(['classical>ratio', 'base>window', 'hybrid>base', 'hybrid>window'])
assert pairs == expected; checks += 1
frontier = [name for name in arms if not any(dominates(summary[other], summary[name]) for other in arms if other != name)]
assert frontier == ['classical', 'hybrid']; checks += 1
assert result['per_domain']['GlobalVoices']['frontier'] == ['classical', 'hybrid']; checks += 1
assert result['per_domain']['FLORES']['frontier'] == ['classical', 'base', 'hybrid']; checks += 1
proof = {'status':'PASS','checks':checks,'result_sha256':hashlib.sha256(Path('output/cross_domain_frontier.json').read_bytes()).hexdigest(),'scope':'Independent robust-min/max and dominance reconstruction from retained domain summaries.'}
Path('output/cross_domain_frontier_verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
