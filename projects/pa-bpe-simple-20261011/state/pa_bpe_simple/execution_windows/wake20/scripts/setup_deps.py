import json
import resource
import subprocess
import sys
import time
from pathlib import Path


start = time.monotonic()
cmd = [
    sys.executable,
    "-m",
    "pip",
    "install",
    "--target",
    "deps",
    "--no-cache-dir",
    "--disable-pip-version-check",
    "--report",
    "output/install_report.json",
    "tokenizers==0.22.1",
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=100)
Path("output/install.stdout").write_text(result.stdout, encoding="utf-8")
Path("output/install.stderr").write_text(result.stderr, encoding="utf-8")
Path("output/setup.json").write_text(
    json.dumps(
        {
            "argv": cmd,
            "exit_code": result.returncode,
            "wall_seconds": time.monotonic() - start,
            "child_usage": list(resource.getrusage(resource.RUSAGE_CHILDREN)),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
result.check_returncode()

