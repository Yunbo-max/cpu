import json
import statistics
from pathlib import Path

ROOT = Path('.')
LANGS = ['en', 'fr', 'es']
PAIRS = [('en-fr', 0, 1), ('en-es', 0, 2), ('fr-es', 1, 2)]
summary = json.loads((ROOT / 'output/mechanism_summary.json').read_text())
raw = json.loads((ROOT / 'output/mechanism_raw.json').read_text())


def crossings(steps):
    out = {}
    for label, i, j in PAIRS:
        after_magnitudes = []
        ranks = []
        for s in steps:
            before = s['dev_lengths_before'][i] - s['dev_lengths_before'][j]
            after = s['dev_lengths_after'][i] - s['dev_lengths_after'][j]
            if before and after and ((before > 0) != (after > 0)):
                after_magnitudes.append(abs(after))
                ranks.append(s['rank'])
        out[label] = {
            'count': len(ranks),
            'first_rank': min(ranks) if ranks else None,
            'last_rank': max(ranks) if ranks else None,
            'median_absolute_gap_after_crossing_tokens': statistics.median(after_magnitudes) if after_magnitudes else None,
            'max_absolute_gap_after_crossing_tokens': max(after_magnitudes, default=None),
        }
    return out


arms = {}
for name in ['classical', 'hybrid', 'base']:
    tail = raw['arms'][name][500:]
    cp = summary['arms'][name]['checkpoints']
    arms[name] = {
        'tail_gini_change': cp['1000']['gini'] - cp['500']['gini'],
        'tail_total_mean_cost_change': cp['1000']['total_mean_cost'] - cp['500']['total_mean_cost'],
        'tail_crossings_by_pair': crossings(tail),
        'tail_gini_worsening_steps': sum(s['gini_after'] > s['gini_before'] + 1e-15 for s in tail),
        'tail_selected_target_counts': summary['arms'][name]['phases']['tail_501_1000']['selected_target_counts'],
        'tail_target_switches': summary['arms'][name]['phases']['tail_501_1000']['target_switches'],
    }

hc = summary['arms']['hybrid']['phases']['tail_501_1000']['dev_reduction']
cc = summary['arms']['classical']['phases']['tail_501_1000']['dev_reduction']
reallocation = {lang: hc[lang] - cc[lang] for lang in LANGS}
hybrid_tail = summary['arms']['hybrid']['phases']['tail_501_1000']
base_tail = summary['arms']['base']['phases']['tail_501_1000']
result = {
    'schema_version': 1,
    'scope': 'Post hoc arithmetic decomposition of the frozen wake19 mechanism audit; no new threshold or method selection.',
    'arms': arms,
    'hybrid_vs_classical_tail_reduction_delta_tokens': reallocation,
    'hybrid_vs_classical_tail_net_reduction_delta_tokens': sum(reallocation.values()),
    'hybrid_tail_selector_alignment': {
        'selected_target_is_effect_owner': hybrid_tail['selected_target_is_dev_effect_owner'],
        'targeted_merges': hybrid_tail['targeted_merges'],
        'fraction': hybrid_tail['selected_target_is_dev_effect_owner'] / hybrid_tail['targeted_merges'],
        'selected_target_has_positive_effect': hybrid_tail['selected_target_has_positive_dev_effect'],
    },
    'frozen_prediction_tests': {
        'exact_global_prefix': summary['hybrid_classical_common_prefix_merges'] == 500,
        'endpoint_replay': all(max(abs(v) for v in x['differences'].values()) < 1e-12 for x in summary['pretokenization_validation'].values()),
        'hybrid_tail_reduces_gini': arms['hybrid']['tail_gini_change'] < 0,
        'hybrid_selector_usually_owns_effect': hybrid_tail['selected_target_is_dev_effect_owner'] > hybrid_tail['targeted_merges'] / 2,
        'hybrid_has_fewer_exact_sign_crossings_than_base': sum(v['count'] for v in arms['hybrid']['tail_crossings_by_pair'].values()) < sum(v['count'] for v in arms['base']['tail_crossings_by_pair'].values()),
        'hybrid_has_fewer_target_switches_than_base': hybrid_tail['target_switches'] < base_tail['target_switches'],
    },
    'interpretation': "Hybrid's fixed global prefix preserves efficient shared compression, while its tail redirects reductions toward the highest-cost French/Spanish development stream. The exact-crossing and target-switch falsifiers fail: the tail controller is not smoother than base. The supported account is delayed/limited exposure to the same reactive parity controller, not suppression of local chattering.",
    'claim_limit': 'This mechanism is reconstructed on exposed TICO development data. It explains the fixed-code behavior but does not prove causal transfer to confirmation domains.',
}
(ROOT / 'output/mechanism_interpretation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
