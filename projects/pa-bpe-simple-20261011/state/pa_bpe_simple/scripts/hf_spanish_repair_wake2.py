import datetime, hashlib, json, sys, urllib.request
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
URLS = {
    "tree_spa": "https://huggingface.co/api/datasets/HuggingFaceFW/fineweb-2/tree/refs%2Fconvert%2Fparquet/spa_Latn?recursive=true&expand=false",
    "tree_spa_test": "https://huggingface.co/api/datasets/HuggingFaceFW/fineweb-2/tree/refs%2Fconvert%2Fparquet/spa_Latn/test?recursive=true&expand=false",
    "range_spa_test_0000": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/resolve/refs%2Fconvert%2Fparquet/spa_Latn/test/0000.parquet",
    "range_spa_train_0000": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/resolve/refs%2Fconvert%2Fparquet/spa_Latn/train/0000.parquet",
}
records=[]
for key,url in URLS.items():
    try:
        headers={"User-Agent":"PA-BPE-research/1.0"}
        if key.startswith("range_"): headers["Range"]="bytes=0-1023"
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=20) as resp:
            body=resp.read(1024 if key.startswith("range_") else -1)
            rec={"key":key,"requested_url":url,"final_url":resp.geturl(),"status":resp.status,
                 "headers":{k:v for k,v in resp.headers.items() if k.lower() in {"content-length","content-range","etag","x-repo-commit","location"}},
                 "bytes_read":len(body),"sha256_read":hashlib.sha256(body).hexdigest()}
        if not key.startswith("range_"):
            (OUT/f"{key}.json").write_bytes(body)
            data=json.loads(body);rec["entries"]=[{k:x.get(k) for k in ["path","size","type","oid"]} for x in data]
        records.append(rec)
    except Exception as exc:
        records.append({"key":key,"requested_url":url,"error_type":type(exc).__name__,"error":str(exc)})
result={"schema_version":1,"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"records":records}
(OUT/"hf_spanish_repair_wake2.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
