import datetime, hashlib, json, urllib.request
from pathlib import Path

URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
out = Path("inputs/flores200_dataset.tar.gz")
free = int(Path('/sys/fs/cgroup/memory.max').read_text()) - int(Path('/sys/fs/cgroup/memory.current').read_text())
# The two pre-network attempts measured 14,155,776-byte peak RSS.  Streaming
# download has bounded buffers, so retain >9x that observation as the guard.
assert free >= 134217728, "memory_wait_required"
h = hashlib.sha256(); size = 0
request = urllib.request.Request(URL, headers={"User-Agent": "PA-BPE-research/1.0"})
with urllib.request.urlopen(request, timeout=30) as response, out.open("wb") as dst:
    headers = dict(response.headers.items())
    while True:
        chunk = response.read(1024*1024)
        if not chunk: break
        dst.write(chunk); h.update(chunk); size += len(chunk)
assert size == 25585843
receipt = {
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "url": URL,
    "sha256": h.hexdigest(), "bytes": size, "headers": headers,
    "text_inspected": False, "license_basis": "official archived repository README: FLORES-200 CC-BY-SA-4.0",
    "memory_guard_bytes": 134217728, "guard_basis": "two pre-network attempts peaked at 14155776 bytes; streaming transfer"
}
Path("output/flores_fetch.json").write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps({k: receipt[k] for k in ["url", "sha256", "bytes", "text_inspected"]}))
