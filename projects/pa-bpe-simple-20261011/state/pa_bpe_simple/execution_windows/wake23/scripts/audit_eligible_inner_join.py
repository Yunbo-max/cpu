import bz2
import datetime
import gzip
import hashlib
import json
import resource
import sqlite3
import sys
import tempfile
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

FILES = {
    "eng": ("eng_sentences.tsv.bz2", "0eabb52f54350bbb39807190920bfddaf9fee2ba50ca75af67e11a22ec475c29"),
    "fra": ("fra_sentences.tsv.bz2", "fac31d82b216c95affee7dffcee6c0ae59c45f254ebbfbbf8abb9e66da86ee8f"),
    "spa": ("spa_sentences.tsv.bz2", "d1f7aa997368571e8bbba341ab60f9145fefe14970f21065bd97be8e03c8e6fb"),
    "ef": ("eng-fra_links.tsv.bz2", "fc05adc4b3bc78871c6809d979d754e41b67ed10477d8ba6b877bc16f036c2bc"),
    "es": ("eng-spa_links.tsv.bz2", "3009b84ae398f39f21ce27e2d012d456c9ee8732a201ae5523f1ab2f8d5658f3"),
    "fs": ("fra-spa_links.tsv.bz2", "e869ab6b17355bc94e6a607ab361fd1cd27af4b09e1cc321e05913402b243df6"),
}

def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

result = {
    "protocol_revision": "tatoeba-eligible-inner-join-v2",
    "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source_sha256": {},
    "sentences": {},
    "links": {},
    "tokenizer_scored": False,
    "development_selected": False,
    "strict_v1_status": "retained_as_failed_missing_exported_endpoints",
}
for role, (name, expected) in FILES.items():
    actual = sha256(INPUT / name)
    if actual != expected:
        raise ValueError(f"source hash mismatch for {role}: {actual}")
    result["source_sha256"][name] = actual

with tempfile.TemporaryDirectory(prefix="eligible_join_", dir=ROOT) as temp:
    db_path = Path(temp) / "audit.sqlite3"
    db = sqlite3.connect(db_path)
    db.execute("pragma cache_size=-16384")
    db.execute("pragma temp_store=FILE")
    db.execute("pragma journal_mode=OFF")
    db.execute("pragma synchronous=OFF")

    for lang in ("eng", "fra", "spa"):
        db.execute(f"create table {lang}(id integer primary key)")
        rows = 0
        duplicates = 0
        batch = []
        with bz2.open(INPUT / FILES[lang][0], "rt", encoding="utf-8", newline="") as stream:
            for line in stream:
                fields = line.rstrip("\r\n").split("\t", 2)
                if len(fields) != 3 or fields[1] != lang:
                    raise ValueError(f"invalid {lang} sentence row {rows + 1}")
                sid = int(fields[0])
                if sid <= 0 or fields[0] != str(sid):
                    raise ValueError(f"invalid {lang} sentence id")
                batch.append((sid,))
                rows += 1
                if len(batch) == 8192:
                    before = db.total_changes
                    db.executemany(f"insert or ignore into {lang} values (?)", batch)
                    duplicates += len(batch) - (db.total_changes - before)
                    batch.clear()
            before = db.total_changes
            db.executemany(f"insert or ignore into {lang} values (?)", batch)
            duplicates += len(batch) - (db.total_changes - before)
            db.commit()
        result["sentences"][lang] = {
            "rows": rows,
            "unique_ids": rows - duplicates,
            "duplicate_ids": duplicates,
        }

    specs = {
        "ef": ("eng", "fra"),
        "es": ("eng", "spa"),
        "fs": ("fra", "spa"),
    }
    for table, (left, right) in specs.items():
        db.execute(f"create table {table}(a integer,b integer,primary key(a,b)) without rowid")
        rows = 0
        batch = []
        with bz2.open(INPUT / FILES[table][0], "rt", encoding="utf-8", newline="") as stream:
            for line in stream:
                fields = line.rstrip("\r\n").split("\t")
                if len(fields) != 2:
                    raise ValueError(f"invalid {table} link row {rows + 1}")
                pair = tuple(map(int, fields))
                if min(pair) <= 0:
                    raise ValueError(f"invalid {table} endpoint")
                batch.append(pair)
                rows += 1
                if len(batch) == 8192:
                    db.executemany(f"insert or ignore into {table} values (?,?)", batch)
                    batch.clear()
            db.executemany(f"insert or ignore into {table} values (?,?)", batch)
            db.commit()
        unique = db.execute(f"select count(*) from {table}").fetchone()[0]
        counts = db.execute(f"""
            select
              sum(case when l.id is not null and r.id is not null then 1 else 0 end),
              sum(case when l.id is null and r.id is not null then 1 else 0 end),
              sum(case when l.id is not null and r.id is null then 1 else 0 end),
              sum(case when l.id is null and r.id is null then 1 else 0 end)
            from {table} t
            left join {left} l on t.a=l.id
            left join {right} r on t.b=r.id
        """).fetchone()
        retained, left_only_missing, right_only_missing, both_missing = map(int, counts)
        eligible = table + "_eligible"
        db.execute(f"create table {eligible}(a integer,b integer,primary key(a,b)) without rowid")
        db.execute(f"insert into {eligible} select t.a,t.b from {table} t join {left} l on t.a=l.id join {right} r on t.b=r.id")
        db.commit()
        result["links"][table] = {
            "rows": rows,
            "unique_edges": unique,
            "duplicate_edges": rows - unique,
            "retained_edges": retained,
            "excluded_edges": unique - retained,
            "left_only_missing": left_only_missing,
            "right_only_missing": right_only_missing,
            "both_missing": both_missing,
        }
        if retained + left_only_missing + right_only_missing + both_missing != unique:
            raise AssertionError(f"partition mismatch for {table}")

    triangles_path = OUTPUT / "eligible_closed_triangles.tsv.gz"
    triangle_count = 0
    with gzip.GzipFile(filename=str(triangles_path), mode="wb", mtime=0) as out:
        query = """
            select ef.a,ef.b,es.b
            from ef_eligible ef
            join es_eligible es on ef.a=es.a
            join fs_eligible fs on ef.b=fs.a and es.b=fs.b
            order by ef.a,ef.b,es.b
        """
        for triple in db.execute(query):
            out.write(("\t".join(map(str, triple)) + "\n").encode())
            triangle_count += 1
    result["closed_triangles"] = triangle_count
    result["triangles_sha256"] = sha256(triangles_path)
    result["temporary_sqlite_bytes"] = db_path.stat().st_size
    db.close()

result["total_retained_edges"] = sum(item["retained_edges"] for item in result["links"].values())
result["total_excluded_edges"] = sum(item["excluded_edges"] for item in result["links"].values())
result["status"] = "eligible_inner_join_verified_selection_still_hold"
result["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUTPUT / "eligible_inner_join_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
