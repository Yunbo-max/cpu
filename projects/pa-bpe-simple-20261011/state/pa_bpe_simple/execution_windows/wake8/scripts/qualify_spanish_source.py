import collections, datetime, hashlib, json, pathlib, urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
protocol = json.loads((root / "spanish_source_protocol.json").read_text())
request = urllib.request.Request(protocol["endpoint"], headers={"User-Agent": "pa-bpe-research-source-audit/1.0"})
with urllib.request.urlopen(request, timeout=60) as response:
    raw = response.read()
    status = response.status
assert status == 200
payload = json.loads(raw)
assert payload["dataset"] == protocol["repo"]
assert payload["config"] == protocol["config"]
assert payload["split"] == protocol["split"]
rows = payload.get("rows", [])
assert rows
records = [item["row"] for item in rows]
required = ("id", "text", "url", "file_path")
assert any(all(record.get(key) for key in required) for record in records)
(root / "inputs").mkdir(exist_ok=True)
(root / "output").mkdir(exist_ok=True)
(root / "inputs" / "fineweb2_spa_first_rows.json").write_bytes(raw)
summary = {
    "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "qualification_only_not_training_sample": True,
    "endpoint": protocol["endpoint"],
    "repo_revision_from_frozen_hub_metadata": protocol["repo_revision"],
    "http_status": status,
    "response_bytes": len(raw),
    "response_sha256": hashlib.sha256(raw).hexdigest(),
    "row_count": len(records),
    "truncated": payload.get("truncated"),
    "feature_names": [feature["name"] for feature in payload.get("features", [])],
    "dump_counts": dict(sorted(collections.Counter(record.get("dump") for record in records).items())),
    "unique_ids": len({record.get("id") for record in records}),
    "globalvoices_url_hits": sum("globalvoices" in str(record.get("url", "")).lower() for record in records),
    "formal_training_gate": "HOLD pending immutable-shard identities, hash-ranked sampling, and frozen URL/text decontamination"
}
(root / "output" / "spanish_source_qualification.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary, ensure_ascii=False))
