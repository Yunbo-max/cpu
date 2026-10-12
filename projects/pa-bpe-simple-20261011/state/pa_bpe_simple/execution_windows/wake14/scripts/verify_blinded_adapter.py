import json,resource,shutil,sqlite3,tempfile
from pathlib import Path
from decontam_selector import *

cur=int(Path('/sys/fs/cgroup/memory.current').read_text()); mx=int(Path('/sys/fs/cgroup/memory.max').read_text())
if mx-cur < 384*1024*1024: raise SystemExit('memory safety gate: less than 384 MiB cgroup headroom')
checks=[]
def check(name,value,**extra):
    checks.append({'check':name,'passed':bool(value),**extra})
    if not value: raise AssertionError(name)
def make_source(path,psha):
    docs=[('en','a','https://independent.example:443/a#fragment','one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo'),('fr','a','https://fr.example/a','bonjour monde court'),('es','a','https://es.example/a','hola mundo corto')]
    db=sqlite3.connect(path); db.executescript('''CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID; CREATE TABLE confirmation(blinded_unit_sha256 TEXT NOT NULL,language TEXT NOT NULL,canonical_url_sha256 TEXT,normalized_exact_sha256 TEXT NOT NULL,word_count INTEGER NOT NULL,shingle_mass INTEGER NOT NULL,PRIMARY KEY(blinded_unit_sha256,language)) WITHOUT ROWID; CREATE TABLE shingles(blinded_unit_sha256 TEXT NOT NULL,language TEXT NOT NULL,shingle_sha256 BLOB NOT NULL,multiplicity INTEGER NOT NULL,PRIMARY KEY(blinded_unit_sha256,language,shingle_sha256)) WITHOUT ROWID;''')
    meta={'complete':'true','raw_text_stored':'false','tokenizer_or_fairness_output_computed':'false','selector_protocol_sha256':psha,'active_idea':'pa-bpe-domain-robustness','idea_revision':'1','source_manifest_sha256':'1'*64,'units_sha256':'2'*64,'builder_sha256':'3'*64}; db.executemany('INSERT INTO meta VALUES(?,?)',meta.items())
    for lang,sid,url,text in docs:
        doc=sha((lang+'\0'+sid).encode()); toks,grams=shingle_counts(text); db.execute('INSERT INTO confirmation VALUES(?,?,?,?,?,?)',(doc,lang,sha(canonical_url(url).encode()),sha(normalize_text(text).encode()),len(toks),sum(grams.values()))); db.executemany('INSERT INTO shingles VALUES(?,?,?,?)',((doc,lang,g,n) for g,n in grams.items()))
    db.commit(); db.close(); return docs

psha=sha_file('decontamination_selector_protocol.json'); csha=sha_file('adapter_contract.json'); isha=sha_file('scripts/decontam_selector.py'); actual_source=Path('inputs/globalvoices_blinded_fingerprints_v2.sqlite3')
check('oracle_normalization_sha256',sha(normalize_text('  ONE\tTWO three four five six  ').encode())=='bab7fd6e5bd624f4ea0c33f7e7219262a6fa93a945a8964d9f110148286b7b37')
u=canonical_url('HTTPS://Example.COM:443/a?q=1#frag'); check('oracle_url_default_port_query_fragment',u=='https://example.com/a?q=1' and sha(u.encode())=='e644b002bae6e8a77466d56f39a165e2d4ad0fb3072cbd4e96356cabc762be6b')
u=canonical_url('https://[2001:0db8::1]:443/a#f'); check('oracle_url_ipv6',u=='https://[2001:db8::1]/a' and sha(u.encode())=='0de259d5e13b2260244a3bd6ad3495da076336b29d47aaf3ad601594915c34c5')
t,g=shingle_counts('one two three four five six'); check('oracle_shingle_sha256',t==['one','two','three','four','five','six'] and {x.hex():n for x,n in g.items()}=={'dee0e5db76efdc53e5c53b7f3de69421b273809a95d1b0247c32dfc38e41bce4':1,'0d99b1352cd334db25a218c24cbe8b0adadbedd33cac089922e7acb0f8c81e3b':1})
with tempfile.TemporaryDirectory(dir='output') as tdname:
    td=Path(tdname); src=td/'fixture.sqlite3'; docs=make_source(src,psha); target=open_db(td/'selector.sqlite3')
    check('fixture_hash_only_import',import_blinded_confirmation_index(target,src,psha,csha)==3 and target.execute('SELECT COUNT(*) FROM conf').fetchone()[0]==3)
    check('fixture_no_plaintext_confirmation_url',target.execute('SELECT COUNT(*) FROM conf WHERE url IS NOT NULL').fetchone()[0]==0)
    check('fixture_reopen_idempotence',import_blinded_confirmation_index(target,src,psha,csha)==0)
    bind_run(target,psha,'fixture',False,isha); mismatch=False
    try: bind_run(target,'f'*64,'fixture',False,isha)
    except ValueError: mismatch=True
    check('late_bind_and_protocol_mismatch_guard',mismatch)
    badp=False
    try: import_blinded_confirmation_index(target,src,'f'*64,csha)
    except ValueError: badp=True
    check('completed_reimport_wrong_protocol_guard',badp)
    badc=False
    try: import_blinded_confirmation_index(target,src,psha,'e'*64)
    except ValueError: badc=True
    check('completed_reimport_wrong_contract_guard',badc)
    base=docs[0][3]; rows=[{'id':'url','lang':'es','url':'https://independent.example/a','text':'unrelated'},{'id':'exact','lang':'en','url':'https://clean.example/a','text':'  '+base.upper()+'  '},{'id':'near','lang':'en','url':'https://clean.example/b','text':'zero '+base+' twenty-three'},{'id':'clean','lang':'fr','url':'https://clean.example/c','text':'texte sans rapport'}]
    stage_rows(target,rows,False); ds=list(iter_decisions(target)); accepted={x['row_id'] for ok,x in ds if ok}; rejected=[x['reason'] for ok,x in ds if not ok]
    check('hash_url_exact_semantics',rejected.count('exact_url')==1,rejected=rejected); check('hash_exact_content_semantics',rejected.count('exact_content')==1); check('hash_shingle_near_semantics',rejected.count('near_content')==1); check('clean_row_survives',accepted=={'clean'},accepted=sorted(accepted)); target.close()
    corrupt=td/'corrupt.sqlite3'; shutil.copyfile(src,corrupt); b=sqlite3.connect(corrupt); b.execute("UPDATE confirmation SET shingle_mass=shingle_mass+1 WHERE language='en'"); b.commit(); b.close(); tdb=open_db(td/'bad.sqlite3'); failed=False
    try: import_blinded_confirmation_index(tdb,corrupt,psha,csha)
    except ValueError: failed=True
    check('corrupt_mass_fails_before_import',failed and tdb.execute('SELECT COUNT(*) FROM conf').fetchone()[0]==0); tdb.close()
    early=open_db(td/'early.sqlite3'); bind_run(early,'f'*64,'early',False,isha); ef=False
    try: import_blinded_confirmation_index(early,src,psha,csha)
    except ValueError: ef=True
    check('early_bind_protocol_mismatch_guard',ef and early.execute('SELECT COUNT(*) FROM conf').fetchone()[0]==0); early.close()
    actual=open_db(td/'actual.sqlite3'); imported=import_blinded_confirmation_index(actual,actual_source,psha,csha); source=sqlite3.connect(f'file:{actual_source.resolve()}?mode=ro',uri=True); actual.execute('ATTACH DATABASE ? AS src',(str(actual_source.resolve()),))
    sc={'confirmation':source.execute('SELECT COUNT(*) FROM confirmation').fetchone()[0],'url_hash':source.execute('SELECT COUNT(DISTINCT canonical_url_sha256) FROM confirmation WHERE canonical_url_sha256 IS NOT NULL').fetchone()[0],'grams':source.execute('SELECT COUNT(*) FROM shingles').fetchone()[0],'mass':source.execute('SELECT SUM(multiplicity) FROM shingles').fetchone()[0]}; tc={'confirmation':actual.execute('SELECT COUNT(*) FROM conf').fetchone()[0],'url_hash':actual.execute('SELECT COUNT(*) FROM conf_url_hash').fetchone()[0],'grams':actual.execute('SELECT COUNT(*) FROM grams').fetchone()[0],'mass':actual.execute('SELECT SUM(n) FROM grams').fetchone()[0]}
    check('actual_index_count_preservation',imported==1536 and sc==tc,source=sc,target=tc)
    ed=actual.execute('SELECT COUNT(*) FROM conf t LEFT JOIN src.confirmation s ON t.doc=s.blinded_unit_sha256 AND t.lang=s.language AND t.exact=s.normalized_exact_sha256 AND t.words=s.word_count AND t.mass=s.shingle_mass WHERE s.blinded_unit_sha256 IS NULL').fetchone()[0]; gd=actual.execute('SELECT COUNT(*) FROM grams t LEFT JOIN src.shingles s ON t.doc=s.blinded_unit_sha256 AND t.lang=s.language AND t.g=s.shingle_sha256 AND t.n=s.multiplicity WHERE s.blinded_unit_sha256 IS NULL').fetchone()[0]
    check('actual_exact_and_shingle_record_preservation',ed==0 and gd==0,exact_delta=ed,gram_delta=gd)
    sm=actual.execute('SELECT COUNT(*) FROM (SELECT canonical_url_sha256 FROM src.confirmation WHERE canonical_url_sha256 IS NOT NULL EXCEPT SELECT url_hash FROM conf_url_hash)').fetchone()[0]; tm=actual.execute('SELECT COUNT(*) FROM (SELECT url_hash FROM conf_url_hash EXCEPT SELECT canonical_url_sha256 FROM src.confirmation WHERE canonical_url_sha256 IS NOT NULL)').fetchone()[0]
    check('actual_url_hash_set_preservation',sm==0 and tm==0,source_minus_target=sm,target_minus_source=tm); check('actual_target_contains_no_staged_development_text',actual.execute('SELECT COUNT(*) FROM rows').fetchone()[0]==0); source.close(); actual.close()
result={'schema_version':1,'scope':'adapter mechanics and frozen confirmation-index preservation only; no real development selection, tokenizer, or fairness output','source_index_sha256':sha_file(actual_source),'protocol_sha256':psha,'implementation_sha256':isha,'memory_at_start':{'current_bytes':cur,'limit_bytes':mx,'headroom_bytes':mx-cur},'checks':checks,'all_checks_passed':all(x['passed'] for x in checks),'actual_counts':tc,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'formal_gates':{'blinded_confirmation_adapter':'PASS','row_to_fixed_shard_provenance':'HOLD','production_development_selection':'HOLD','tokenizer_training':'HOLD','fairness_claims':'HOLD'}}
Path('output/blinded_adapter_verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); print(json.dumps({'checks':len(checks),'all_checks_passed':result['all_checks_passed'],'actual_counts':tc},sort_keys=True))
