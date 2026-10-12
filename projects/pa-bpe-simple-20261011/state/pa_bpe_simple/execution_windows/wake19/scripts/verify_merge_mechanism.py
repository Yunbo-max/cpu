import hashlib
import json
from pathlib import Path

ROOT = Path('.')
LANGS = ['en', 'fr', 'es']


def gini(x):
    x = [float(v) for v in x]
    return sum(abs(a-b) for a in x for b in x) / (2 * len(x) * sum(x))


summary = json.loads((ROOT / 'output/mechanism_summary.json').read_text())
raw = json.loads((ROOT / 'output/mechanism_raw.json').read_text())
checks = []


def check(name, ok, detail=None):
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
    assert ok, (name, detail)


def codes(name):
    return [tuple(x.split(' ')) for x in (ROOT / 'inputs' / f'{name}.codes').read_text().splitlines() if x and not x.startswith('#')]


c = codes('classical')
h = codes('hybrid')
prefix = next((i for i, (a, b) in enumerate(zip(c, h)) if a != b), min(len(c), len(h)))
check('exact 500 merge common prefix', prefix == 500, prefix)
check('summary prefix agrees', summary['hybrid_classical_common_prefix_merges'] == prefix)

for arm_name in ['classical', 'hybrid', 'base']:
    steps = raw['arms'][arm_name]
    arm = summary['arms'][arm_name]
    check(f'{arm_name} 1000 raw steps', len(steps) == 1000)
    check(f'{arm_name} ranks consecutive', [x['rank'] for x in steps] == list(range(1, 1001)))
    for phase, lo, hi in [('prefix_1_500', 0, 500), ('tail_501_1000', 500, 1000)]:
        subset = steps[lo:hi]
        ps = arm['phases'][phase]
        for key in ['train_reduction', 'dev_reduction']:
            rebuilt = {lang: sum(s[key][j] for s in subset) for j, lang in enumerate(LANGS)}
            check(f'{arm_name} {phase} {key} sum', rebuilt == ps[key], {'got': rebuilt, 'saved': ps[key]})
        check(f'{arm_name} {phase} gini worsen count',
              sum(s['gini_after'] > s['gini_before'] + 1e-15 for s in subset) == ps['gini_worsening_steps'])
    first = arm['checkpoints']['0']['dev_total_tokens']
    final = arm['checkpoints']['1000']['dev_total_tokens']
    red = arm['phases']['all_1_1000']['dev_reduction']
    check(f'{arm_name} dev mass conservation', all(first[l] - red[l] == final[l] for l in LANGS))
    means = [arm['checkpoints']['1000']['dev_mean_tokens'][l] for l in LANGS]
    check(f'{arm_name} final gini', abs(gini(means) - arm['checkpoints']['1000']['gini']) < 1e-15)
    expected = json.loads((ROOT / 'inputs/wake16b_evaluation.json').read_text())['arms'][arm_name]['mean_tokens']
    check(f'{arm_name} frozen final means', all(abs(means[j] - expected[l]) < 1e-12 for j, l in enumerate(LANGS)))

check('shared rank500 checkpoint', summary['arms']['classical']['checkpoints']['500'] == summary['arms']['hybrid']['checkpoints']['500'])
out = {
    'schema_version': 1,
    'status': 'PASS',
    'checks_passed': len(checks),
    'checks': checks,
    'summary_sha256': hashlib.sha256((ROOT / 'output/mechanism_summary.json').read_bytes()).hexdigest(),
    'raw_sha256': hashlib.sha256((ROOT / 'output/mechanism_raw.json').read_bytes()).hexdigest(),
}
(ROOT / 'output/mechanism_verification.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
