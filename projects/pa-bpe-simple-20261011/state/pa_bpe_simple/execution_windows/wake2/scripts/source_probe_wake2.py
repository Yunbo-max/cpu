import datetime, hashlib, json, sys, urllib.parse, urllib.request, zipfile
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
URLS = {
    "opus_books_en_fr_moses": "https://opus.nlpl.eu/opusapi/?corpus=Books&source=en&target=fr&preprocessing=moses",
    "opus_books_en_fr_xml": "https://opus.nlpl.eu/opusapi/?corpus=Books&source=en&target=fr&preprocessing=xml",
    "opus_books_en_es_xml": "https://opus.nlpl.eu/opusapi/?corpus=Books&source=en&target=es&preprocessing=xml",
    "opus_books_fr_es_xml": "https://opus.nlpl.eu/opusapi/?corpus=Books&source=fr&target=es&preprocessing=xml",
    "fineweb2_spa_parquet": "https://datasets-server.huggingface.co/parquet?dataset=HuggingFaceFW%2Ffineweb-2&config=spa_Latn",
    "fineweb2_spa_test_rows": "https://datasets-server.huggingface.co/rows?dataset=HuggingFaceFW%2Ffineweb-2&config=spa_Latn&split=test&offset=0&length=40",
    "fineweb2_spa_train_rows": "https://datasets-server.huggingface.co/rows?dataset=HuggingFaceFW%2Ffineweb-2&config=spa_Latn&split=train&offset=0&length=40",
}
records = []
for key, url in URLS.items():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PA-BPE-research/1.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read()
            status = resp.status
            final_url = resp.geturl()
        path = OUT / f"{key}.json"
        path.write_bytes(body)
        parsed = json.loads(body)
        summary = {}
        if isinstance(parsed, dict):
            summary["keys"] = sorted(parsed)[:30]
            if "rows" in parsed:
                summary["row_count"] = len(parsed["rows"])
            if "parquet_files" in parsed:
                summary["parquet_count"] = len(parsed["parquet_files"])
            if "corpora" in parsed:
                summary["corpora_count"] = len(parsed["corpora"])
        records.append({"key": key, "requested_url": url, "final_url": final_url,
                        "started_utc": started, "status": status, "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(), "summary": summary})
    except Exception as exc:
        records.append({"key": key, "requested_url": url, "started_utc": started,
                        "error_type": type(exc).__name__, "error": str(exc)})

tico = Path("evidence/tico_zip.zip")
if tico.is_file():
    with zipfile.ZipFile(tico) as zf:
        names = zf.namelist()
    records.append({"key": "tico_local_inventory", "sha256": hashlib.sha256(tico.read_bytes()).hexdigest(),
                    "members": len(names), "spanish_files": [n for n in names if "en-es" in n],
                    "french_files": [n for n in names if n.endswith("en-fr.tsv")]})

result = {"schema_version": 1, "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "records": records}
(OUT / "source_probe_wake2.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
