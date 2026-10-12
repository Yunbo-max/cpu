import datetime
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path


ROOT = Path(".")
LANGS = ["en", "fr", "es"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"

memory_max = int(Path("/sys/fs/cgroup/memory.max").read_text())
memory_current = int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom = memory_max - memory_current
required = 512 * 1024 * 1024
capacity = {
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "memory_max_bytes": memory_max,
    "memory_current_bytes": memory_current,
    "headroom_bytes": headroom,
    "required_headroom_bytes": required,
    "basis": "Prior comparable 1000-merge author runs peaked below 115 MiB; 512 MiB retains more than 3x measured peak as shared-host safety margin.",
}
Path("output/hybrid_window_capacity.json").write_text(json.dumps(capacity, indent=2) + "\n")
assert headroom >= required, "memory_wait_required"

sys.path.insert(0, str((ROOT / "deps").resolve()))
source = "inputs/parity_aware_learn_bpe.py"
argv = [
    source,
    "--input",
    *[f"inputs/{lang}.dict" for lang in LANGS],
    "--output",
    "output/hybrid_window.codes",
    "--dict-input",
    "--symbols",
    "1000",
    "--num-workers",
    "1",
    "--variant",
    "window",
    "--dev",
    *[f"inputs/dev.{lang}.dict" for lang in LANGS],
    "--global-merges",
    "500",
    "--window-size",
    "100",
    "--alpha",
    "2",
]
sys.argv = argv
try:
    runpy.run_path(source, run_name="__main__")
except SystemExit as exc:
    if exc.code not in (0, None):
        raise

candidate = Path("output/hybrid_window.codes")
lines = candidate.read_text(encoding="utf-8").splitlines()
assert len(lines) == 1001
candidate_merges = lines[1:]
classical_merges = Path("inputs/classical.codes").read_text(encoding="utf-8").splitlines()[1:]
hybrid_merges = Path("inputs/hybrid.codes").read_text(encoding="utf-8").splitlines()[1:]
assert candidate_merges[:500] == classical_merges[:500] == hybrid_merges[:500]

result = {
    "schema_version": 1,
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "argv": argv,
    "merges": 1000,
    "global_prefix_merges": 500,
    "window_size": 100,
    "alpha": 2,
    "candidate_code_sha256": sha(candidate),
    "source_sha256": sha(Path(source)),
    "input_sha256": {p.name: sha(p) for p in sorted(Path("inputs").glob("*.dict"))},
    "scope": "TICO development only; candidate selection evidence, not independent confirmation.",
}
Path("output/hybrid_window_training.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

