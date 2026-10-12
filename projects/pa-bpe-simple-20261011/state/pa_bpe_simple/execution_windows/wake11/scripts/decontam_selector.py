import hashlib, ipaddress, json, os, re, sqlite3, unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

WORD_RE = re.compile(r"\w+", re.UNICODE)
GV_HOST = "globalvoices.org"
REQUIRED_PROVENANCE = ("dataset_repo", "dataset_revision", "dataset_shard_path", "dataset_shard_lfs_sha256")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def normalize_text(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())

def canonical_url(value):
    if value is None:
        return None
    if not isinstance(value,str):
        raise TypeError("URL must be null or string")
    if not value:
        return None
    try:
        p = urlsplit(value)
        if p.scheme.lower() not in {"http", "https"} or not p.hostname:
            return None
        rawhost=p.hostname.lower()
        try:
            host=ipaddress.ip_address(rawhost).compressed
            host_render=f"[{host}]" if ":" in host else host
        except ValueError:
            if rawhost.endswith("."): rawhost=rawhost[:-1]
            if not rawhost or rawhost.endswith("."): return None
            host=rawhost.encode("idna").decode("ascii").lower(); host_render=host
        port = p.port
        netloc = host_render if port is None or (p.scheme.lower(), port) in {("http",80),("https",443)} else f"{host_render}:{port}"
        return urlunsplit((p.scheme.lower(), netloc, p.path or "/", p.query, ""))
    except (ValueError, UnicodeError):
        return None

def is_globalvoices(value):
    c = canonical_url(value)
    if not c: return False
    host = urlsplit(c).hostname
    return host == GV_HOST or host.endswith("." + GV_HOST)

def words(text):
    return WORD_RE.findall(normalize_text(text))

def shingle_counts(text, n=5):
    toks = words(text)
    out = {}
    for i in range(max(0, len(toks)-n+1)):
        h = hashlib.sha256("\0".join(toks[i:i+n]).encode()).digest()
        out[h] = out.get(h, 0) + 1
    return toks, out

def open_db(path):
    db = sqlite3.connect(path)
    db.executescript("""
      PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA temp_store=FILE;
      CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS conf(doc TEXT,lang TEXT,url TEXT,exact TEXT,words INT,mass INT,PRIMARY KEY(doc,lang));
      CREATE INDEX IF NOT EXISTS conf_exact ON conf(lang,exact);
      CREATE INDEX IF NOT EXISTS conf_url ON conf(url);
      CREATE TABLE IF NOT EXISTS grams(doc TEXT,lang TEXT,g BLOB,n INT,PRIMARY KEY(doc,lang,g));
      CREATE INDEX IF NOT EXISTS grams_inv ON grams(lang,g);
      CREATE TABLE IF NOT EXISTS rows(seq INTEGER PRIMARY KEY,lang TEXT,id TEXT,text TEXT,url TEXT,rank BLOB,raw_hash TEXT,prov TEXT);
      CREATE INDEX IF NOT EXISTS rows_id ON rows(lang,id);
      CREATE INDEX IF NOT EXISTS rows_rank ON rows(lang,rank,id);
      CREATE TEMP TABLE IF NOT EXISTS tg(g BLOB PRIMARY KEY,n INT);
    """)
    return db

def bind_run(db, protocol_sha, input_sha, require_provenance, implementation_sha):
    pair={"protocol_sha256":protocol_sha,"input_manifest_sha256":input_sha,
          "provenance_mode":"strict" if require_provenance else "diagnostic",
          "implementation_sha256":implementation_sha}
    old=dict(db.execute("SELECT k,v FROM meta"))
    if old and any(old.get(k)!=v for k,v in pair.items()):
        raise ValueError("resume binding mismatch")
    db.executemany("INSERT OR IGNORE INTO meta(k,v) VALUES(?,?)",pair.items()); db.commit()

def add_confirmation(db, docs, confirmation_sha):
    old=dict(db.execute("SELECT k,v FROM meta"))
    if old.get("confirmation_complete")=="1":
        if old.get("confirmation_manifest_sha256")!=confirmation_sha: raise ValueError("confirmation binding mismatch")
        return 0
    count=0
    with db:
        db.execute("INSERT OR REPLACE INTO meta VALUES('confirmation_manifest_sha256',?)",(confirmation_sha,))
        for d in docs:
            norm=normalize_text(d["text"]); toks,grams=shingle_counts(d["text"])
            blinded=sha((d["lang"]+"\0"+d["id"]).encode())
            supplied=d.get("url"); url=canonical_url(supplied)
            if supplied and not url: raise ValueError("invalid confirmation URL")
            db.execute("INSERT INTO conf VALUES(?,?,?,?,?,?)",(blinded,d["lang"],url,sha(norm.encode()),len(toks),sum(grams.values())))
            db.executemany("INSERT INTO grams VALUES(?,?,?,?)",((blinded,d["lang"],g,n) for g,n in grams.items()))
            count+=1
        db.execute("INSERT OR REPLACE INTO meta VALUES('confirmation_complete','1')")
    return count

def stage_rows(db, rows, require_provenance=False):
    expected="strict" if require_provenance else "diagnostic"
    if db.execute("SELECT v FROM meta WHERE k='provenance_mode'").fetchone()!=(expected,): raise ValueError("provenance mode binding mismatch")
    if db.execute("SELECT v FROM meta WHERE k='rows_complete'").fetchone()==('1',): return 0
    count=0
    with db:
      for seq,r in enumerate(rows):
        sid=r.get("id")
        if not isinstance(sid,str) or not sid: raise ValueError("missing stable id")
        if not isinstance(r.get("text"),str) or not r["text"]: raise ValueError("missing text")
        if require_provenance:
            if any(not isinstance(r.get(k),str) or not r[k] for k in REQUIRED_PROVENANCE): raise ValueError("missing formal provenance")
            if not re.fullmatch(r"[0-9a-f]{40,64}",r["dataset_revision"].lower()): raise ValueError("invalid dataset revision")
            if not re.fullmatch(r"[0-9a-f]{64}",r["dataset_shard_lfs_sha256"].lower()): raise ValueError("invalid shard LFS SHA256")
        lang=r["lang"]
        if lang not in {"en","fr","es"}: raise ValueError("invalid canonical language")
        supplied=r.get("url"); url=canonical_url(supplied)
        if supplied and not url: url="!invalid:"+sha(supplied.encode())
        rank=hashlib.sha256(("pa-bpe-train-v1\0"+lang+"\0"+sid).encode()).digest()
        prov={k:r.get(k) for k in REQUIRED_PROVENANCE}
        db.execute("INSERT INTO rows VALUES(?,?,?,?,?,?,?,?)",(seq,lang,sid,r["text"],url,rank,sha(r["text"].encode()),json.dumps(prov,sort_keys=True)))
        count+=1
      db.execute("INSERT OR REPLACE INTO meta VALUES('rows_complete','1')")
    return count

def content_reason(db, lang, text):
    norm=normalize_text(text); exact=sha(norm.encode())
    if db.execute("SELECT 1 FROM conf WHERE lang=? AND exact=? LIMIT 1",(lang,exact)).fetchone(): return "exact_content"
    toks,tgrams=shingle_counts(text)
    if len(toks)<20 or not tgrams: return None
    db.execute("DELETE FROM tg")
    db.executemany("INSERT INTO tg VALUES(?,?)",tgrams.items())
    q="""SELECT c.doc,c.mass,SUM(CASE WHEN tg.n<g.n THEN tg.n ELSE g.n END) inter
           FROM tg JOIN grams g ON g.lang=? AND g.g=tg.g JOIN conf c ON c.doc=g.doc AND c.lang=g.lang
           WHERE c.words>=20 GROUP BY c.doc,c.mass"""
    tmass=sum(tgrams.values())
    for _,cmass,inter in db.execute(q,(lang,)):
        if inter/min(tmass,cmass) >= .80: return "near_content"
    return None

def iter_decisions(db):
    meta=dict(db.execute("SELECT k,v FROM meta"))
    required={"protocol_sha256","input_manifest_sha256","implementation_sha256","provenance_mode","confirmation_manifest_sha256","confirmation_complete","rows_complete"}
    if not required <= set(meta) or meta.get("confirmation_complete")!="1" or meta.get("rows_complete")!="1": raise ValueError("incomplete selector bindings or stages")
    query="""SELECT r.lang,r.id,r.text,r.url,r.rank,r.raw_hash,r.prov,c.n
             FROM rows r JOIN (SELECT lang,id,COUNT(*) n FROM rows GROUP BY lang,id) c
             ON c.lang=r.lang AND c.id=r.id ORDER BY r.lang,r.rank,r.id"""
    for lang,sid,text,url,rank,raw_hash,prov,ncopies in db.execute(query):
        reason=None
        if ncopies>1: reason="duplicate_id_all_copies"
        elif url and url.startswith("!invalid:"): reason="invalid_url"
        elif is_globalvoices(url): reason="globalvoices_host"
        elif url and db.execute("SELECT 1 FROM conf WHERE url=? LIMIT 1",(url,)).fetchone(): reason="exact_url"
        else: reason=content_reason(db,lang,text)
        if reason: yield False,{"reason":reason}; continue
        yield True,{"language":lang,"row_id":sid,"rank_sha256":rank.hex(),"raw_text_sha256":raw_hash,"source":json.loads(prov)}

def select_small_for_tests_only(db):
    out=[]; rejected={}
    for accepted,item in iter_decisions(db):
        if accepted: out.append(item)
        else: rejected[item["reason"]]=rejected.get(item["reason"],0)+1
    return out,rejected

def atomic_json(path,obj):
    p=Path(path); tmp=p.with_name(p.name+".tmp")
    data=(json.dumps(obj,sort_keys=True,indent=2)+"\n").encode()
    with open(tmp,"wb") as f: f.write(data); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return sha(data)

def atomic_stream_manifest(path, metadata, decisions):
    p=Path(path); tmp=p.with_name(p.name+".tmp"); counts={}; selected=0
    with open(tmp,"wb") as f:
        f.write(b'{"metadata":'); f.write(json.dumps(metadata,sort_keys=True,separators=(",",":")).encode()); f.write(b',"selected":[')
        first=True
        for accepted,item in decisions:
            if not accepted:
                reason=item["reason"]; counts[reason]=counts.get(reason,0)+1; continue
            if not first: f.write(b',')
            f.write(json.dumps(item,sort_keys=True,separators=(",",":")).encode()); first=False; selected+=1
        f.write(b'],"rejections":'); f.write(json.dumps(counts,sort_keys=True,separators=(",",":")).encode()); f.write(b'}\n')
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp,p); fd=os.open(p.parent,os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return {"sha256":h.hexdigest(),"selected":selected,"rejections":counts}
