import hashlib
import json
from pathlib import Path

ROOT = Path('.')
LANGS = ['en', 'fr', 'es']
PAIRS = [('en-fr', 0, 1), ('en-es', 0, 2), ('fr-es', 1, 2)]
raw = json.loads((ROOT / 'output/mechanism_raw.json').read_text())
saved = json.loads((ROOT / 'output/mechanism_interpretation.json').read_text())
checks = []


def check(name, ok, detail=None):
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
    assert ok, (name, detail)


totals = {}
for arm in ['classical', 'hybrid', 'base']:
    steps = raw['arms'][arm][500:]
    total = 0
    for label, i, j in PAIRS:
        count = 0
        for s in steps:
            a = s['dev_lengths_before'][i] - s['dev_lengths_before'][j]
            b = s['dev_lengths_after'][i] - s['dev_lengths_after'][j]
            count += bool(a and b and ((a > 0) != (b > 0)))
        got = saved['arms'][arm]['tail_crossings_by_pair'][label]['count']
        check(f'{arm} {label} crossing count', count == got, {'recomputed': count, 'saved': got})
        total += count
    totals[arm] = total
    check(f'{arm} tail length', len(steps) == 500)

hyb = raw['arms']['hybrid'][500:]
align = sum(s['selected_target'] == s['dev_effect_owner'] for s in hyb)
positive = sum(s['dev_reduction'][LANGS.index(s['selected_target'])] > 0 for s in hyb)
check('hybrid selector alignment', align == saved['hybrid_tail_selector_alignment']['selected_target_is_effect_owner'])
check('hybrid selected effect positive', positive == saved['hybrid_tail_selector_alignment']['selected_target_has_positive_effect'])
check('crossing falsifier value', saved['frozen_prediction_tests']['hybrid_has_fewer_exact_sign_crossings_than_base'] == (totals['hybrid'] < totals['base']), totals)
check('negative result retained', saved['frozen_prediction_tests']['hybrid_has_fewer_exact_sign_crossings_than_base'] is False)
out = {
    'schema_version': 1,
    'status': 'PASS',
    'checks_passed': len(checks),
    'checks': checks,
    'interpretation_sha256': hashlib.sha256((ROOT / 'output/mechanism_interpretation.json').read_bytes()).hexdigest(),
}
(ROOT / 'output/mechanism_interpretation_verification.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
