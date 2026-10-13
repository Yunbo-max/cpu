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
I = ROOT / "inputs"
O = ROOT / "output"
S = ROOT / "scratch"
LANGS = ("en", "fr", "es")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()


def fp(text):
    normalized = " ".join(unicodedata.normalize("NFKC", text).casefold().split())
    words = normalized.split()
    grams = Counter()
    for pos in range(len(words) - 4):
        grams[hashlib.sha256("\0".join(words[pos : pos + 5]).encode()).digest()] += 1
    return normalized, digest(normalized.encode()), len(words), grams


class Corpus:
    def __init__(self, path):
        if path.exists():
            path.unlink()
        self.con = sqlite3.connect(path)
        self.con.executescript(
            """
            PRAGMA journal_mode=DELETE; PRAGMA synchronous=OFF; PRAGMA temp_store=FILE; PRAGMA cache_size=-32768;
            CREATE TABLE docs(d INTEGER PRIMARY KEY, source TEXT, item TEXT, lang TEXT, exact TEXT, words INT, mass INT);
            CREATE INDEX docs_exact ON docs(lang,exact);
            CREATE TABLE gram(lang TEXT, h BLOB, d INT, n INT, PRIMARY KEY(lang,h,d)) WITHOUT ROWID;
            """
        )
        self.n = Counter()

    def put(self, source, item, lang, text=None, exact=None, words=None, grams=None):
        if text is not None:
            _norm, exact, words, grams = fp(text)
        mass = sum(grams.values())
        cur = self.con.execute("INSERT INTO docs(source,item,lang,exact,words,mass) VALUES(?,?,?,?,?,?)", (source,item,lang,exact,words,mass))
        doc = cur.lastrowid
        self.con.executemany("INSERT INTO gram VALUES(?,?,?,?)", ((lang,h,doc,n) for h,n in grams.items()))
        self.n[(source,lang)] += 1

    def contaminated(self, lang, exact, grams):
        row = self.con.execute("SELECT source,item FROM docs WHERE lang=? AND exact=? ORDER BY source,item LIMIT 1", (lang,exact)).fetchone()
        if row:
            return ("exact",) + row
        mass = sum(grams.values())
        if mass == 0:
            return None
        overlap = defaultdict(int)
        labels = {}
        hashes = list(grams)
        for start in range(0, len(hashes), 200):
            part = hashes[start:start+200]
            q = "SELECT g.h,g.d,g.n,d.source,d.item FROM gram g JOIN docs d ON d.d=g.d WHERE g.lang=? AND g.h IN (" + ",".join("?" for _ in part) + ")"
            for h, doc, n, source, item in self.con.execute(q, (lang,*part)):
                overlap[doc] += min(n, grams[h])
                labels[doc] = (source,item)
        hits = [labels[d] for d,v in overlap.items() if 5*v >= 4*mass]
        return ("near",) + min(hits) if hits else None


def add_training(c):
    selected = json.loads((I/"selected_rows.json").read_text())["selected"]
    wanted = {(lang,r["row_id"]):r["raw_text_sha256"] for lang,rows in selected.items() for r in rows}
    copy = S/"verify_selection.sqlite3"
    for suffix in ("","-wal","-shm"):
        shutil.copy2(I/("selection.sqlite3"+suffix), Path(str(copy)+suffix))
    db = sqlite3.connect(copy)
    got = set()
    for lang,sid,text,raw in db.execute("SELECT lang,id,text,raw_hash FROM rows"):
        if (lang,sid) in wanted:
            assert raw == wanted[(lang,sid)] == digest(text.encode())
            c.put("training", digest((lang+"\0"+sid).encode()), lang, text=text)
            got.add((lang,sid))
    db.close()
    assert got == set(wanted) and len(got) == 515


def add_tico(c):
    rows = json.loads((I/"tico_dev.json").read_text())
    assert len(rows) == 970
    for r in rows:
        for lang in LANGS:
            c.put("tico", r["id"]+":"+lang, lang, text=r[lang])


def add_gv(c):
    p = I/"globalvoices_whitespace_fingerprints.sqlite3"
    db = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
    assert dict(db.execute("SELECT key,value FROM meta"))["complete"] == "true"
    rows = db.execute("SELECT blinded_unit_sha256,language,normalized_exact_sha256,word_count,shingle_mass FROM confirmation").fetchall()
    assert len(rows) == 1536
    for item,lang,exact,words,mass in rows:
        grams = Counter(dict(db.execute("SELECT shingle_sha256,multiplicity FROM shingles WHERE blinded_unit_sha256=? AND language=?",(item,lang))))
        assert sum(grams.values()) == mass
        c.put("globalvoices", item, lang, exact=exact, words=words, grams=grams)
    db.close()


def add_flores(c):
    names={"en":"./flores200_dataset/devtest/eng_Latn.devtest","fr":"./flores200_dataset/devtest/fra_Latn.devtest","es":"./flores200_dataset/devtest/spa_Latn.devtest"}
    with tarfile.open(I/"flores200_dataset.tar.gz","r:gz") as t:
        for lang,name in names.items():
            lines=t.extractfile(name).read().decode().splitlines(); assert len(lines)==1012
            for n,text in enumerate(lines): c.put("flores",str(n),lang,text=text)


def add_books(c):
    sampling=json.loads((I/"multibook_raw_evaluation.json").read_text())["sampling"]
    total=0
    for work,rec in sorted(sampling.items()):
        assert len(rec["rows"])==rec["sampled"]
        for r in rec["rows"]:
            for lang,text in zip(("en","fr"),r["text"]): c.put("books_multibook",work+":"+r["sample_key"],lang,text=text)
            total+=1
    assert total==5120
    total=0
    for split in ("dev","confirm"):
        with (I/f"books_{split}.tsv").open(newline="") as f:
            for n,r in enumerate(csv.DictReader(f,delimiter="\t",quoting=csv.QUOTE_NONE)):
                for lang in LANGS: c.put("books_alice_poe",split+":"+str(n),lang,text=r[lang])
                total+=1
    assert total==946


def triangle_rows():
    out=[]
    with gzip.open(I/"eligible_closed_triangles.tsv.gz","rt") as f:
        for line in f:
            ids=tuple(map(int,line.rstrip().split("\t")))
            key=hashlib.sha256(("pa-bpe-tatoeba-confirm-v1\0"+"\0".join(map(str,ids))).encode()).digest()
            out.append((key,ids))
    assert len(out)==38091
    return sorted(out,key=lambda x:(x[0],x[1]))


def candidate_texts(rows):
    wanted={lang:set() for lang in LANGS}
    for _,ids in rows:
        for lang,sid in zip(LANGS,ids): wanted[lang].add(sid)
    found={lang:{} for lang in LANGS}
    for lang,code in zip(LANGS,("eng","fra","spa")):
        with bz2.open(I/f"{code}_sentences.tsv.bz2","rt",encoding="utf-8") as f:
            for line in f:
                sid,seen,text=line.rstrip("\r\n").split("\t",2); sid=int(sid)
                if sid in wanted[lang]:
                    assert seen==code and sid not in found[lang]
                    found[lang][sid]=text
        assert set(found[lang])==wanted[lang]
    return found


def verify():
    c=Corpus(S/"verify_prior.sqlite3")
    add_books(c); add_flores(c); add_gv(c); add_tico(c); add_training(c); c.con.commit()
    rows=triangle_rows(); texts=candidate_texts(rows)
    qdb=sqlite3.connect(S/"verify_candidates.sqlite3")
    qdb.executescript("CREATE TABLE eligible(seq INT PRIMARY KEY,key TEXT,en INT,fr INT,es INT,en_exact TEXT,fr_exact TEXT,es_exact TEXT,en_raw TEXT,fr_raw TEXT,es_raw TEXT,en_tokens INT,fr_tokens INT,es_tokens INT); CREATE TABLE rep(lang TEXT,exact TEXT,seq INT,PRIMARY KEY(lang,exact)) WITHOUT ROWID;")
    content_excluded=0; short=0; empty=0
    for seq,(key,ids) in enumerate(rows):
        values={}; bad=False
        for lang,sid in zip(LANGS,ids):
            text=texts[lang][sid]; norm,exact,nwords,grams=fp(text)
            values[lang]=(exact,digest(text.encode()),nwords)
            if not norm: empty+=1; bad=True
            elif nwords<5: short+=1; bad=True
            elif c.contaminated(lang,exact,grams): content_excluded+=1; bad=True
        if bad: continue
        qdb.execute("INSERT INTO eligible VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(seq,key.hex(),*ids,values['en'][0],values['fr'][0],values['es'][0],values['en'][1],values['fr'][1],values['es'][1],values['en'][2],values['fr'][2],values['es'][2]))
        for lang in LANGS:
            qdb.execute("INSERT OR IGNORE INTO rep VALUES(?,?,?)",(lang,values[lang][0],seq))
    qdb.commit()
    chosen=[]; used={lang:set() for lang in LANGS}; reps=0; reused=0
    sql="SELECT e.* FROM eligible e JOIN rep a ON a.lang='en' AND a.exact=e.en_exact AND a.seq=e.seq JOIN rep b ON b.lang='fr' AND b.exact=e.fr_exact AND b.seq=e.seq JOIN rep d ON d.lang='es' AND d.exact=e.es_exact AND d.seq=e.seq ORDER BY e.seq"
    for row in qdb.execute(sql):
        seq,key,en,fr,es,enx,frx,esx,enr,frr,esr,ent,frt,est=row; reps+=1
        ids={"en":en,"fr":fr,"es":es}
        if any(ids[l] in used[l] for l in LANGS): reused+=1; continue
        if len(chosen)<1024:
            chosen.append({"ordering_sha256":key,"ids":ids,"language_fingerprints":{"en":{"id":en,"normalized_exact_sha256":enx,"raw_text_sha256":enr,"tokens":ent},"fr":{"id":fr,"normalized_exact_sha256":frx,"raw_text_sha256":frr,"tokens":frt},"es":{"id":es,"normalized_exact_sha256":esx,"raw_text_sha256":esr,"tokens":est}}})
            for l in LANGS: used[l].add(ids[l])
    qdb.close(); c.con.close()
    observed=json.loads((O/"tatoeba_development_1024.json").read_text())
    assert len(chosen)==1024 and chosen==observed["rows"]
    summary=json.loads((O/"selection_summary.json").read_text())
    assert summary["selected_manifest_sha256"]==file_digest(O/"tatoeba_development_1024.json")
    result={"schema_version":1,"status":"independent_full_recomputation_pass","checked_candidates":len(rows),"selected_rows":len(chosen),"selected_manifest_sha256":summary["selected_manifest_sha256"],"content_excluded_language_instances":content_excluded,"short_language_instances":short,"empty_language_instances":empty,"global_representative_pool":reps,"sentence_id_reuse_before_target_and_tail":reused,"prior_inventory_counts":{f"{s}:{l}":n for (s,l),n in sorted(c.n.items())},"raw_text_persisted_in_output":False,"tokenizer_scored":False}
    data=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode(); (O/"selection_verification.json").write_bytes(data)
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__": verify()
