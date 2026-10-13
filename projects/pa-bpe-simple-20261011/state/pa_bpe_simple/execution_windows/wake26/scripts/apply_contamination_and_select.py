import bz2
import csv
import gzip
import hashlib
import json
import shutil
import sqlite3
import tarfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "inputs"
OUT = ROOT / "output"
SCRATCH = ROOT / "scratch"
LANGS = ("en", "fr", "es")
TATOEBA = {"en": "eng", "fr": "fra", "es": "spa"}
TARGET = 1024


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def fingerprint(text):
    norm = normalize(text)
    tokens = norm.split()
    grams = Counter(
        hashlib.sha256("\0".join(tokens[i : i + 5]).encode()).digest()
        for i in range(max(0, len(tokens) - 4))
    )
    return norm, sha_bytes(norm.encode()), tokens, grams


def atomic_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
    tmp.replace(path)
    return sha_bytes(data)


class PriorIndex:
    def __init__(self, path):
        if path.exists():
            path.unlink()
        self.db = sqlite3.connect(path)
        self.db.executescript(
            """
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            PRAGMA temp_store=FILE;
            PRAGMA cache_size=-32768;
            CREATE TABLE prior(
              item TEXT NOT NULL, lang TEXT NOT NULL, source TEXT NOT NULL,
              exact TEXT NOT NULL, words INTEGER NOT NULL, mass INTEGER NOT NULL,
              PRIMARY KEY(item,lang)
            ) WITHOUT ROWID;
            CREATE INDEX prior_exact ON prior(lang,exact);
            CREATE TABLE grams(
              lang TEXT NOT NULL, gram BLOB NOT NULL, item TEXT NOT NULL,
              source TEXT NOT NULL, multiplicity INTEGER NOT NULL,
              PRIMARY KEY(lang,gram,item)
            ) WITHOUT ROWID;
            CREATE INDEX grams_item ON grams(lang,item);
            """
        )
        self.counts = defaultdict(lambda: defaultdict(int))

    def add(self, source, item, lang, text):
        norm, exact, tokens, grams = fingerprint(text)
        self.add_fingerprint(source, item, lang, exact, len(tokens), grams)

    def add_fingerprint(self, source, item, lang, exact, words, grams):
        if lang not in LANGS:
            raise ValueError((source, item, lang))
        self.db.execute(
            "INSERT INTO prior VALUES(?,?,?,?,?,?)",
            (item, lang, source, exact, words, sum(grams.values())),
        )
        self.db.executemany(
            "INSERT INTO grams VALUES(?,?,?,?,?)",
            ((lang, gram, item, source, n) for gram, n in grams.items()),
        )
        self.counts[source][lang] += 1

    def commit(self):
        self.db.commit()

    def match(self, lang, exact, grams):
        row = self.db.execute(
            "SELECT source,item FROM prior WHERE lang=? AND exact=? ORDER BY source,item LIMIT 1",
            (lang, exact),
        ).fetchone()
        if row:
            return "exact", row
        mass = sum(grams.values())
        if not mass:
            return None, None
        values = list(grams)
        totals = defaultdict(int)
        source_for = {}
        step = 200
        for start in range(0, len(values), step):
            part = values[start : start + step]
            sql = (
                "SELECT gram,item,source,multiplicity FROM grams WHERE lang=? AND gram IN ("
                + ",".join("?" for _ in part)
                + ")"
            )
            for gram, item, source, n in self.db.execute(sql, (lang, *part)):
                totals[item] += min(grams[gram], n)
                source_for[item] = source
        eligible = [(source_for[item], item) for item, inter in totals.items() if 5 * inter >= 4 * mass]
        if eligible:
            return "near", min(eligible)
        return None, None


def build_training(index):
    selection = json.loads((IN / "selected_rows.json").read_text())
    wanted = {
        (lang, row["row_id"]): row
        for lang, rows in selection["selected"].items()
        for row in rows
    }
    dbdir = SCRATCH / "selection_copy"
    dbdir.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        shutil.copy2(IN / ("selection.sqlite3" + suffix), dbdir / ("selection.sqlite3" + suffix))
    db = sqlite3.connect(dbdir / "selection.sqlite3")
    seen = set()
    for lang, sid, text, raw_hash in db.execute("SELECT lang,id,text,raw_hash FROM rows"):
        key = (lang, sid)
        if key not in wanted:
            continue
        if sha_bytes(text.encode()) != raw_hash or raw_hash != wanted[key]["raw_text_sha256"]:
            raise ValueError("training row hash mismatch")
        index.add("training", "training:" + sha_bytes((lang + "\0" + sid).encode()), lang, text)
        seen.add(key)
    db.close()
    if seen != set(wanted) or len(seen) != 515:
        raise ValueError((len(seen), len(wanted)))


def build_tico(index):
    rows = json.loads((IN / "tico_dev.json").read_text())
    if len(rows) != 970:
        raise ValueError(len(rows))
    for row in rows:
        for lang in LANGS:
            index.add("tico", f"tico:{row['id']}:{lang}", lang, row[lang])


def build_globalvoices(index):
    path = IN / "globalvoices_whitespace_fingerprints.sqlite3"
    db = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    meta = dict(db.execute("SELECT key,value FROM meta"))
    if meta.get("complete") != "true":
        raise ValueError("GlobalVoices index incomplete")
    count = 0
    for item, lang, _url_hash, exact, words, mass in db.execute(
        "SELECT blinded_unit_sha256,language,canonical_url_sha256,normalized_exact_sha256,word_count,shingle_mass FROM confirmation"
    ):
        grams = Counter(dict(db.execute(
            "SELECT shingle_sha256,multiplicity FROM shingles WHERE blinded_unit_sha256=? AND language=?",
            (item, lang),
        )))
        if sum(grams.values()) != mass:
            raise ValueError("GlobalVoices shingle mass mismatch")
        index.add_fingerprint("globalvoices", "globalvoices:" + item, lang, exact, words, grams)
        count += 1
    db.close()
    if count != 1536:
        raise ValueError(count)


def build_flores(index):
    members = {
        "en": "./flores200_dataset/devtest/eng_Latn.devtest",
        "fr": "./flores200_dataset/devtest/fra_Latn.devtest",
        "es": "./flores200_dataset/devtest/spa_Latn.devtest",
    }
    with tarfile.open(IN / "flores200_dataset.tar.gz", "r:gz") as tar:
        for lang, name in members.items():
            lines = tar.extractfile(name).read().decode("utf-8").splitlines()
            if len(lines) != 1012:
                raise ValueError((lang, len(lines)))
            for i, text in enumerate(lines):
                index.add("flores", f"flores:{lang}:{i}", lang, text)


def build_books(index):
    data = json.loads((IN / "multibook_raw_evaluation.json").read_text())
    sampled = 0
    for work, rec in sorted(data["sampling"].items()):
        if rec["sampled"] != len(rec["rows"]):
            raise ValueError(work)
        for row in rec["rows"]:
            if len(row["text"]) != 2:
                raise ValueError(work)
            for lang, text in zip(("en", "fr"), row["text"]):
                index.add("books_multibook", f"multibook:{work}:{row['sample_key']}:{lang}", lang, text)
            sampled += 1
    if sampled != 5120:
        raise ValueError(sampled)
    aligned = 0
    for split in ("dev", "confirm"):
        with (IN / f"books_{split}.tsv").open(newline="") as f:
            for i, row in enumerate(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)):
                for lang in LANGS:
                    index.add("books_alice_poe", f"books:{split}:{i}:{lang}", lang, row[lang])
                aligned += 1
    if aligned != 946:
        raise ValueError(aligned)


def build_prior_index(path):
    idx = PriorIndex(path)
    build_training(idx)
    build_tico(idx)
    build_globalvoices(idx)
    build_flores(idx)
    build_books(idx)
    idx.commit()
    return idx


def load_triangles():
    rows = []
    with gzip.open(IN / "eligible_closed_triangles.tsv.gz", "rt", encoding="utf-8") as f:
        for line in f:
            a, b, c = line.rstrip("\n").split("\t")
            ids = (int(a), int(b), int(c))
            key = hashlib.sha256(("pa-bpe-tatoeba-confirm-v1\0" + "\0".join(map(str, ids))).encode()).digest()
            rows.append((key, ids))
    if len(rows) != 38091:
        raise ValueError(len(rows))
    return rows


def load_candidate_texts(triangles):
    need = {lang: set() for lang in LANGS}
    for _key, ids in triangles:
        for lang, sid in zip(LANGS, ids):
            need[lang].add(sid)
    found = {lang: {} for lang in LANGS}
    for lang in LANGS:
        code = TATOEBA[lang]
        with bz2.open(IN / f"{code}_sentences.tsv.bz2", "rt", encoding="utf-8", newline="") as f:
            for line in f:
                sid, observed, text = line.rstrip("\r\n").split("\t", 2)
                sid = int(sid)
                if sid in need[lang]:
                    if observed != code or sid in found[lang]:
                        raise ValueError((lang, sid))
                    found[lang][sid] = text
        if set(found[lang]) != need[lang]:
            raise ValueError((lang, len(found[lang]), len(need[lang])))
    return found


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    triangles = load_triangles()
    texts = load_candidate_texts(triangles)
    idx = build_prior_index(SCRATCH / "prior.sqlite3")
    records = []
    exclusion_counts = Counter()
    exclusion_sources = Counter()
    for key, ids in triangles:
        per_lang = {}
        reasons = []
        for lang, sid in zip(LANGS, ids):
            text = texts[lang][sid]
            norm, exact, tokens, grams = fingerprint(text)
            item = {
                "id": sid,
                "normalized_exact_sha256": exact,
                "raw_text_sha256": sha_bytes(text.encode()),
                "tokens": len(tokens),
            }
            if not norm:
                reasons.append({"language": lang, "reason": "empty"})
            elif len(tokens) < 5:
                reasons.append({"language": lang, "reason": "short_lt5"})
            else:
                kind, prior = idx.match(lang, exact, grams)
                if kind:
                    source, prior_item = prior
                    reasons.append({
                        "language": lang,
                        "reason": kind + "_prior_content",
                        "prior_source": source,
                        "matched_prior_item_sha256": sha_bytes(prior_item.encode()),
                    })
            per_lang[lang] = item
        if reasons:
            for reason in reasons:
                exclusion_counts[reason["reason"]] += 1
                if "prior_source" in reason:
                    exclusion_sources[(reason["reason"], reason["prior_source"])] += 1
            status = "contaminated_or_ineligible"
        else:
            status = "content_eligible"
        records.append({
            "ordering_sha256": key.hex(),
            "ids": dict(zip(LANGS, ids)),
            "language_fingerprints": per_lang,
            "status": status,
            "reasons": reasons,
        })

    representatives = {}
    for rec in records:
        if rec["status"] != "content_eligible":
            continue
        key = bytes.fromhex(rec["ordering_sha256"])
        ids = tuple(rec["ids"][lang] for lang in LANGS)
        tie = (key, ids)
        for lang in LANGS:
            exact = rec["language_fingerprints"][lang]["normalized_exact_sha256"]
            old = representatives.get((lang, exact))
            if old is None or tie < old:
                representatives[(lang, exact)] = tie

    pool = []
    for rec in records:
        if rec["status"] != "content_eligible":
            continue
        key = bytes.fromhex(rec["ordering_sha256"])
        ids = tuple(rec["ids"][lang] for lang in LANGS)
        tie = (key, ids)
        if any(
            representatives[(lang, rec["language_fingerprints"][lang]["normalized_exact_sha256"])] != tie
            for lang in LANGS
        ):
            rec["status"] = "not_global_text_representative"
            exclusion_counts["not_global_text_representative"] += 1
        else:
            pool.append(rec)

    selected = []
    used = {lang: set() for lang in LANGS}
    for rec in sorted(pool, key=lambda x: (x["ordering_sha256"], *(x["ids"][l] for l in LANGS))):
        if any(rec["ids"][lang] in used[lang] for lang in LANGS):
            rec["status"] = "sentence_id_reuse"
            exclusion_counts["sentence_id_reuse"] += 1
            continue
        if len(selected) < TARGET:
            rec["status"] = "selected"
            selected.append(rec)
            for lang in LANGS:
                used[lang].add(rec["ids"][lang])
        else:
            rec["status"] = "eligible_after_target"

    if len(selected) < TARGET:
        raise RuntimeError(f"only {len(selected)} rows after frozen exclusions")

    decision_path = OUT / "candidate_decisions.jsonl.gz"
    with gzip.open(decision_path, "wt", encoding="utf-8", compresslevel=9) as f:
        for rec in sorted(records, key=lambda x: (x["ordering_sha256"], *(x["ids"][l] for l in LANGS))):
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")

    manifest = {
        "schema_version": 1,
        "protocol_sha256": sha_file(IN / "tatoeba_confirmation_protocol.json"),
        "implementation_addendum_sha256": sha_file(IN / "protocol_implementation_addendum.md"),
        "eligible_triangles_sha256": sha_file(IN / "eligible_closed_triangles.tsv.gz"),
        "target_rows": TARGET,
        "selection_rule": "content exclusions; global lowest ordering representative for every same-language normalized text; hash sort; greedy sentence-ID uniqueness",
        "rows": [
            {
                "ordering_sha256": rec["ordering_sha256"],
                "ids": rec["ids"],
                "language_fingerprints": rec["language_fingerprints"],
            }
            for rec in selected
        ],
    }
    manifest_sha = atomic_json(OUT / "tatoeba_development_1024.json", manifest)
    status_counts = Counter(rec["status"] for rec in records)
    summary = {
        "schema_version": 1,
        "status": "deterministic_development_selection_complete_pending_independent_verification",
        "candidate_triangles": len(records),
        "selected_rows": len(selected),
        "status_counts": dict(sorted(status_counts.items())),
        "language_level_exclusion_counts": dict(sorted(exclusion_counts.items())),
        "language_level_exclusion_sources": {
            f"{reason}:{source}": n for (reason, source), n in sorted(exclusion_sources.items())
        },
        "prior_inventory_counts": {
            source: dict(sorted(counts.items())) for source, counts in sorted(idx.counts.items())
        },
        "selected_manifest_sha256": manifest_sha,
        "candidate_decisions_sha256": sha_file(decision_path),
        "raw_text_persisted_in_outputs": False,
        "tokenizer_scored": False,
    }
    atomic_json(OUT / "selection_summary.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
