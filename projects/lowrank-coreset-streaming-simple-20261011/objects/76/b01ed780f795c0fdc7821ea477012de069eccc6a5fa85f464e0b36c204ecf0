"""Independent-command arithmetic and trajectory audit for the fixed B15 outputs."""
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REF = Path('/workspace/scratch/bb9f262965cf/b14_sources/b09/b09-rsi-20261010T1518/B09V2_baseline_eta0p1_r0.npz')


def load_json(name):
    return json.loads((HERE/name).read_text())


def main():
    exact = load_json('B15_exact_svd_eta0p1_r0.json')
    warm = load_json('B15_warm_lobpcg_eta0p1_r0.json')
    diag = load_json('B15_RANK_DEFICIENCY_DIAGNOSTIC.json')
    with np.load(HERE/'B15_exact_svd_eta0p1_r0.npz', allow_pickle=False) as z:
        eq, eu = z['query'].copy(), z['update'].copy()
        eviol = int(np.sum(z['endpoint_excess'] > z['endpoint_tol']))
    with np.load(HERE/'B15_warm_lobpcg_eta0p1_r0.npz', allow_pickle=False) as z:
        wq, wu = z['query'].copy(), z['update'].copy()
        wviol = int(np.sum(z['endpoint_excess'] > z['endpoint_tol']))
        fallback = int(z['endpoint_fallback'][(np.arange(512)+1)>=125].sum())
    with np.load(REF, allow_pickle=False) as z:
        rq, ru = z['query'].copy(), z['update'].copy()
    out = {
        'study': 'B15-fixed-output-audit',
        'exact_vs_reference_query_mismatches': int(np.sum(eq != rq)),
        'exact_vs_reference_update_mismatches': int(np.sum(eu != ru)),
        'warm_vs_reference_query_mismatches': int(np.sum(wq != rq)),
        'warm_vs_reference_update_mismatches': int(np.sum(wu != ru)),
        'exact_endpoint_tolerance_violations': eviol,
        'warm_endpoint_tolerance_violations_after_fallback': wviol,
        'warm_runtime_fallbacks_after_5k': fallback,
        'warm_solver_warning_count': int(warm['solver_warnings_total']),
        'exact_algorithm_cpu_seconds': exact['algorithm_cpu_seconds'],
        'warm_algorithm_cpu_seconds': warm['algorithm_cpu_seconds'],
        'exact_over_warm_cpu_ratio': exact['algorithm_cpu_seconds']/warm['algorithm_cpu_seconds'],
        'unperturbed_first_late_residual': diag['unperturbed']['final_max_residual'],
        'perturbed_excess_over_tolerance': diag['deterministic_perturbation']['excess_over_tolerance'],
        'pass': False,
        'failed_predicates': [
            '71/71 late refreshes triggered residual fallback, so the warm LOBPCG endpoint was never accepted',
            'the deterministic perturbation repair violated endpoint objective tolerance by more than 400x at the first late refresh',
            'the frozen hypothesis requires zero late fallback and both eta values; the eta=0.1 falsifier is sufficient for early stop'
        ],
        'route_decision': 'RETIRE_WARM_LOBPCG_UNDER_FROZEN_STRICT_TOLERANCE',
        'next_action': 'Freeze a randomized block-Krylov endpoint comparator with a declared iteration budget and the same endpoint objective/trajectory audit; do not run native5000 yet.',
        'input_hashes': {
            name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in [
                'B15_ROUND_CONTRACT.json','run_b15_policy.py',
                'B15_exact_svd_eta0p1_r0.json','B15_exact_svd_eta0p1_r0.npz',
                'B15_warm_lobpcg_eta0p1_r0.json','B15_warm_lobpcg_eta0p1_r0.npz',
                'B15_RANK_DEFICIENCY_DIAGNOSTIC.json']
        }
    }
    assert out['exact_vs_reference_query_mismatches'] == 0
    assert out['exact_vs_reference_update_mismatches'] == 0
    assert out['warm_vs_reference_query_mismatches'] == 0
    assert out['warm_vs_reference_update_mismatches'] == 0
    assert fallback == 71 and warm['runtime_fallbacks_after_5k'] == 71
    assert diag['deterministic_perturbation']['excess_over_tolerance'] > 400
    (HERE/'B15_AUDIT.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    print(json.dumps(out, allow_nan=False))


if __name__ == '__main__': main()
