import hashlib, json, math, random
from pathlib import Path

def gini3(values):
    a, _, c = sorted(values)
    return 2 * (c - a) / (3 * sum(values))
def quantile(values, p):
    s = sorted(values); x = (len(s)-1)*p; lo = int(math.floor(x)); hi = int(math.ceil(x))
    return s[lo] if lo == hi else s[lo]*(hi-x) + s[hi]*(x-lo)
result = json.loads(Path('output/flores_secondary.json').read_text())
assert result['rows'] == 1012 and result['raw_text_persisted'] is False
checks = 0
for name, arm in result['arms'].items():
    costs = arm['paired_costs']; assert len(costs) == 1012 and all(len(row) == 3 and all(isinstance(x, int) and x > 0 for x in row) for row in costs)
    means = [sum(row[j] for row in costs) / 1012 for j in range(3)]
    stored = [arm['mean_tokens'][lang] for lang in ['en', 'fr', 'es']]
    for actual, expected in zip(means, stored): assert abs(actual-expected) < 1e-12; checks += 1
    assert abs(gini3(means)-arm['gini']) < 1e-15; checks += 1
    assert abs(max(means)-arm['worst_cost']) < 1e-12; checks += 1
    assert abs(sum(means)-arm['total_cost']) < 1e-12; checks += 1
base = result['arms']['classical']; rng = random.Random(20261012)
boot = {name: {'gain': [], 'total': []} for name in ['base', 'window', 'ratio']}
for _ in range(2000):
    sums = {name: [0,0,0] for name in ['classical','base','window','ratio']}
    for _ in range(1012):
        i = rng.randrange(1012)
        for name in sums:
            for j, value in enumerate(result['arms'][name]['paired_costs'][i]): sums[name][j] += value
    for name in boot:
        boot[name]['gain'].append(gini3(sums['classical'])-gini3(sums[name]))
        boot[name]['total'].append(sum(sums[name])/sum(sums['classical'])-1)
for name in boot:
    arm = result['arms'][name]
    for actual, expected in zip([quantile(boot[name]['gain'],.025),quantile(boot[name]['gain'],.975)], arm['paired_gain_bootstrap95']): assert abs(actual-expected) < 1e-15; checks += 1
    for actual, expected in zip([quantile(boot[name]['total'],.025),quantile(boot[name]['total'],.975)], arm['total_cost_change_bootstrap95']): assert abs(actual-expected) < 1e-15; checks += 1
summary = {'status':'PASS','checks':checks,'arms':list(result['arms']),'result_sha256':hashlib.sha256(Path('output/flores_secondary.json').read_bytes()).hexdigest(),'independence':'Closed-form 3-value Gini and independently reconstructed paired bootstrap; no raw text needed.'}
Path('output/flores_secondary_verification.json').write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary))
