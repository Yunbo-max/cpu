"""Close the independent B15 REVISE items without changing frozen outputs."""
import hashlib
import inspect
import json
from pathlib import Path

import scipy
from scipy import version as scipy_version
from scipy.sparse.linalg import lobpcg

HERE = Path(__file__).resolve().parent
REF_ROOT = Path('/workspace/scratch/bb9f262965cf/b14_sources/b09/b09-rsi-20261010T1518')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    source = Path(inspect.getsourcefile(lobpcg))
    audit = json.loads((HERE/'B15_AUDIT.json').read_text())
    checks = {
        'scipy_version': scipy.__version__ == '1.17.0',
        'scipy_git_revision': scipy_version.git_revision == '8c75ae75176236f233824e9a0483c26a69e6dfec',
        'loaded_source_sha256': sha(source) == '2789d5f25416abeb27e3515e0948d7413b64e241f445b0a19ae3abb856cb4c38',
        'consumed_eta0p1_reference_sha256': sha(REF_ROOT/'B09V2_baseline_eta0p1_r0.npz') == 'b7ab2139b4f38289085d5ee2a10737330d68938ffe28ad939ad183d7c276d083',
        'unconsumed_eta0p01_reference_sha256': sha(REF_ROOT/'B09V2_baseline_eta0p01_r0.npz') == '66c6d97fed7983abc55c8ccf5b571f2613281a627a9993584e243632a76355e6',
        'fixed_comparator_falsified': audit['warm_runtime_fallbacks_after_5k'] == 71 and audit['pass'] is False,
        'revision_wording_narrowed': 'RETIRE_FROZEN_ZERO_EXTENDED_SCIPY_LOBPCG_COMPARATOR' in (HERE/'B15_REVISION_RECORD.md').read_text(),
    }
    assert all(checks.values()), checks
    out = {
        'study': 'B15-revision-closure-input-check',
        'checks': checks,
        'executed_solver': {
            'version': scipy.__version__,
            'git_revision': scipy_version.git_revision,
            'source_path': str(source),
            'source_sha256': sha(source),
        },
        'references': {
            'consumed_eta0p1_sha256': sha(REF_ROOT/'B09V2_baseline_eta0p1_r0.npz'),
            'unconsumed_eta0p01_sha256': sha(REF_ROOT/'B09V2_baseline_eta0p01_r0.npz'),
        },
        'decision': 'RETIRE_FROZEN_ZERO_EXTENDED_SCIPY_LOBPCG_COMPARATOR',
        'full_policy_rerun_required': False,
        'scope': 'versioned evidence identity and claim wording only; scientific negative outputs unchanged',
    }
    (HERE/'B15_REVISION_CLOSURE.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out))


if __name__ == '__main__': main()
