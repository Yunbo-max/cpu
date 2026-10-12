import hashlib, ipaddress, json, os, re, sqlite3, unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

WORD_RE = re.compile(r"\w+", re.UNICODE)
GV_HOST = "globalvoices.org"
REQUIRED_PROVENANCE = ("dataset_repo", "dataset_revision", "dataset_shard_path", "dataset_shard_lfs_sha256")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def sha_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def is_sha256(value):
    return isinstance(value,str) and re.fullmatch(r"[0-9a-f]{64}",value) is not None

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
      CREATE TABLE IF NOT EXISTS conf_url_hash(url_hash TEXT PRIMARY KEY);
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
    if any(k in old and old[k]!=v for k,v in pair.items()):
        raise ValueError("resume binding mismatch")
    if old.get("confirmation_selector_protocol_sha256",protocol_sha)!=protocol_sha:
        raise ValueError("confirmation protocol binding mismatch")
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

def import_blinded_confirmation_index(db,source_path,protocol_sha,contract_sha):
    """Import only frozen hashes/counts; never read or reconstruct confirmation text."""
    source_path=Path(source_path).resolve(); source_sha=sha_file(source_path)
    old=dict(db.execute("SELECT k,v FROM meta"))
    if not is_sha256(protocol_sha) or not is_sha256(contract_sha): raise ValueError("invalid adapter binding hash")
    if old.get("protocol_sha256",protocol_sha)!=protocol_sha: raise ValueError("pre-bound selector protocol mismatch")
    source=sqlite3.connect(f"file:{source_path}?mode=ro",uri=True)
    try:
        if source.execute("PRAGMA integrity_check").fetchone()!=("ok",): raise ValueError("confirmation index integrity failure")
        if not {"meta","confirmation","shingles"}<={r[0] for r in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}: raise ValueError("confirmation index schema missing required tables")
        expected_columns={
          "confirmation":[("blinded_unit_sha256","TEXT"),("language","TEXT"),("canonical_url_sha256","TEXT"),("normalized_exact_sha256","TEXT"),("word_count","INTEGER"),("shingle_mass","INTEGER")],
          "shingles":[("blinded_unit_sha256","TEXT"),("language","TEXT"),("shingle_sha256","BLOB"),("multiplicity","INTEGER")]
        }
        for table,expected in expected_columns.items():
            if [(r[1],r[2].upper()) for r in source.execute(f"PRAGMA table_info({table})")]!=expected: raise ValueError(f"confirmation index column contract mismatch: {table}")
        smeta=dict(source.execute("SELECT key,value FROM meta"))
        required={"complete":"true","raw_text_stored":"false","tokenizer_or_fairness_output_computed":"false","selector_protocol_sha256":protocol_sha,"active_idea":"pa-bpe-domain-robustness","idea_revision":"1"}
        if any(smeta.get(k)!=v for k,v in required.items()): raise ValueError("confirmation index metadata binding mismatch")
        for key in ("source_manifest_sha256","units_sha256","builder_sha256"):
            if not is_sha256(smeta.get(key)): raise ValueError(f"invalid source metadata hash: {key}")
        bad=source.execute("""SELECT COUNT(*) FROM confirmation WHERE
          typeof(blinded_unit_sha256)!='text' OR typeof(language)!='text' OR typeof(normalized_exact_sha256)!='text'
          OR (canonical_url_sha256 IS NOT NULL AND typeof(canonical_url_sha256)!='text')
          OR typeof(word_count)!='integer' OR typeof(shingle_mass)!='integer' OR language NOT IN ('en','fr','es')
          OR length(blinded_unit_sha256)!=64 OR blinded_unit_sha256 GLOB '*[^0-9a-f]*'
          OR length(normalized_exact_sha256)!=64 OR normalized_exact_sha256 GLOB '*[^0-9a-f]*'
          OR (canonical_url_sha256 IS NOT NULL AND (length(canonical_url_sha256)!=64 OR canonical_url_sha256 GLOB '*[^0-9a-f]*'))
          OR word_count<0 OR shingle_mass<0 OR shingle_mass!=CASE WHEN word_count>=5 THEN word_count-4 ELSE 0 END""").fetchone()[0]
        if bad: raise ValueError("invalid confirmation hash/count record")
        langs=dict(source.execute("SELECT language,COUNT(*) FROM confirmation GROUP BY language"))
        if set(langs)!={"en","fr","es"} or min(langs.values())<=0 or len(set(langs.values()))!=1: raise ValueError("confirmation language balance mismatch")
        bad_grams=source.execute("""SELECT COUNT(*) FROM shingles s LEFT JOIN confirmation c USING(blinded_unit_sha256,language)
          WHERE c.blinded_unit_sha256 IS NULL OR typeof(s.blinded_unit_sha256)!='text' OR typeof(s.language)!='text'
          OR typeof(s.shingle_sha256)!='blob' OR typeof(s.multiplicity)!='integer' OR length(s.shingle_sha256)!=32 OR s.multiplicity<=0""").fetchone()[0]
        if bad_grams: raise ValueError("invalid or orphan confirmation shingle")
        bad_mass=source.execute("""SELECT COUNT(*) FROM confirmation c LEFT JOIN
          (SELECT blinded_unit_sha256,language,SUM(multiplicity) mass FROM shingles GROUP BY blinded_unit_sha256,language) s
          USING(blinded_unit_sha256,language) WHERE c.shingle_mass!=COALESCE(s.mass,0)""").fetchone()[0]
        if bad_mass: raise ValueError("confirmation shingle mass mismatch")
        expected={"confirmation_index_sha256":source_sha,"confirmation_manifest_sha256":smeta["source_manifest_sha256"],"confirmation_selector_protocol_sha256":protocol_sha,"confirmation_adapter_contract_sha256":contract_sha,"confirmation_representation":"blinded_hashes_v1"}
        if old.get("confirmation_complete")=="1":
            if any(old.get(k)!=v for k,v in expected.items()): raise ValueError("completed confirmation binding mismatch")
            return 0
        if sha_file(source_path)!=source_sha: raise ValueError("confirmation index changed while being read")
        count=0
        with db:
            for k,v in expected.items(): db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)",(k,v))
            for doc,lang,url_hash,exact,w,mass in source.execute("SELECT blinded_unit_sha256,language,canonical_url_sha256,normalized_exact_sha256,word_count,shingle_mass FROM confirmation ORDER BY blinded_unit_sha256,language"):
                db.execute("INSERT INTO conf VALUES(?,?,?,?,?,?)",(doc,lang,None,exact,w,mass))
                if url_hash is not None: db.execute("INSERT OR IGNORE INTO conf_url_hash VALUES(?)",(url_hash,))
                count+=1
            for row in source.execute("SELECT blinded_unit_sha256,language,shingle_sha256,multiplicity FROM shingles ORDER BY blinded_unit_sha256,language,shingle_sha256"):
                db.execute("INSERT INTO grams VALUES(?,?,?,?)",row)
            db.execute("INSERT OR REPLACE INTO meta VALUES('confirmation_complete','1')")
        return count
    finally: source.close()

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
    if meta.get("confirmation_representation")=="blinded_hashes_v1":
        needed={"confirmation_index_sha256","confirmation_selector_protocol_sha256","confirmation_adapter_contract_sha256"}
        if not needed<=set(meta) or meta["confirmation_selector_protocol_sha256"]!=meta["protocol_sha256"]: raise ValueError("inconsistent blinded confirmation bindings")
    query="""SELECT r.lang,r.id,r.text,r.url,r.rank,r.raw_hash,r.prov,c.n
             FROM rows r JOIN (SELECT lang,id,COUNT(*) n FROM rows GROUP BY lang,id) c
             ON c.lang=r.lang AND c.id=r.id ORDER BY r.lang,r.rank,r.id"""
    for lang,sid,text,url,rank,raw_hash,prov,ncopies in db.execute(query):
        reason=None
        if ncopies>1: reason="duplicate_id_all_copies"
        elif url and url.startswith("!invalid:"): reason="invalid_url"
        elif is_globalvoices(url): reason="globalvoices_host"
        elif url and (db.execute("SELECT 1 FROM conf WHERE url=? LIMIT 1",(url,)).fetchone() or db.execute("SELECT 1 FROM conf_url_hash WHERE url_hash=? LIMIT 1",(sha(url.encode()),)).fetchone()): reason="exact_url"
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
