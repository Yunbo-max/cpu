import bz2, datetime, gzip, hashlib, json, resource, sqlite3, tempfile, unicodedata
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
manifest=json.loads(Path('source_manifest.json').read_text())
result={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_manifest_sha256':hashlib.sha256(Path('source_manifest.json').read_bytes()).hexdigest(),'tokenizer_scored':False,'selected_rows':None,'sentences':{},'links':{}}
for rec in manifest['files']:
    p=Path('output')/rec['spec']['url'].rsplit('/',1)[1]
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    assert h.hexdigest()==rec['sha256'] and p.stat().st_size==rec['bytes']

Path('temporary').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='source_audit_', dir='temporary') as td:
    db=sqlite3.connect(str(Path(td)/'links.sqlite3'))
    db.execute('pragma cache_size=-8192');db.execute('pragma temp_store=FILE');db.execute('pragma journal_mode=OFF')
    for lang,rec in zip(['eng','fra','spa'],manifest['files'][:3]):
        db.execute(f'create table {lang}(id integer primary key)')
        count=0;empty=0;short=0;batch=[];last=-1;ascending=True
        p=Path('output')/rec['spec']['url'].rsplit('/',1)[1]
        with bz2.open(p,'rt',encoding='utf-8',newline='') as f:
            for line in f:
                fields=line.rstrip('\r\n').split('\t',2)
                assert len(fields)==3 and fields[1]==lang, 'invalid language or TSV record'
                sid=int(fields[0]);assert sid>0 and fields[0]==str(sid)
                ascending &= sid>last;last=sid
                norm=' '.join(unicodedata.normalize('NFKC',fields[2]).casefold().split())
                empty+=not norm;short+=len(norm.split())<5
                batch.append((sid,));count+=1
                if len(batch)>=4096:
                    db.executemany(f'insert into {lang} values (?)',batch);batch=[]
            db.executemany(f'insert into {lang} values (?)',batch);db.commit()
        result['sentences'][lang]={'rows':count,'unique_ids':count,'strictly_ascending_ids':ascending,'normalization_empty':empty,'fewer_than_five_tokens':short}
    for table,left,right,rec in zip(['ef','es','fs'],['eng','eng','fra'],['fra','spa','spa'],manifest['files'][3:]):
        db.execute(f'create table {table}(a integer,b integer,primary key(a,b)) without rowid')
        batch=[];count=0
        p=Path('output')/rec['spec']['url'].rsplit('/',1)[1]
        with bz2.open(p,'rt',encoding='utf-8',newline='') as f:
            for line in f:
                fields=line.rstrip('\r\n').split('\t');assert len(fields)==2
                pair=tuple(map(int,fields));assert min(pair)>0
                batch.append(pair);count+=1
                if len(batch)>=4096:db.executemany(f'insert or ignore into {table} values (?,?)',batch);batch=[]
            db.executemany(f'insert or ignore into {table} values (?,?)',batch);db.commit()
        unique=db.execute(f'select count(*) from {table}').fetchone()[0]
        missing=db.execute(f'select count(*) from {table} t left join {left} l on t.a=l.id left join {right} r on t.b=r.id where l.id is null or r.id is null').fetchone()[0]
        result['links'][table]={'rows':count,'unique_edges':unique,'duplicate_edges':count-unique,'missing_or_wrong_language_endpoints':missing}
        assert missing==0,'link endpoint missing from frozen sentence exports'
    count=0
    with gzip.GzipFile('output/closed_triangles.tsv.gz','wb',mtime=0) as f:
        for triple in db.execute('select ef.a,ef.b,es.b from ef join es on ef.a=es.a join fs on ef.b=fs.a and es.b=fs.b order by ef.a,ef.b,es.b'):
            f.write(('\t'.join(map(str,triple))+'\n').encode());count+=1
    result['closed_triangles_before_exclusions']=count
    result['temporary_sqlite_bytes']=Path(td,'links.sqlite3').stat().st_size
    db.close()
triangle_digest=hashlib.sha256()
with Path('output/closed_triangles.tsv.gz').open('rb') as f:
    for block in iter(lambda:f.read(65536),b''):triangle_digest.update(block)
result['triangles_sha256']=triangle_digest.hexdigest()
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
result['status']='source_structure_verified_eligibility_and_contamination_pending'
Path('output/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
