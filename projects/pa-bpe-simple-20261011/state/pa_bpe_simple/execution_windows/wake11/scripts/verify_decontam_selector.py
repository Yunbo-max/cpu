import hashlib, json, resource, sqlite3, tempfile
from pathlib import Path
from decontam_selector import *

MIN_HEADROOM=384*1024*1024
cur=int(Path('/sys/fs/cgroup/memory.current').read_text()); mx=int(Path('/sys/fs/cgroup/memory.max').read_text())
if mx-cur < MIN_HEADROOM: raise SystemExit('memory safety gate')
protocol=Path('decontamination_selector_protocol.json')
psha=hashlib.sha256(protocol.read_bytes()).hexdigest()
isha=hashlib.sha256(Path('scripts/decontam_selector.py').read_bytes()).hexdigest()
empty_conf_sha=hashlib.sha256(b'empty-confirmation-index').hexdigest()
checks=[]
def check(name,value,**extra):
    checks.append({'check':name,'passed':bool(value),**extra})
    if not value: raise AssertionError(name)

base="one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo"
near="zero "+base+" twentythree"
conf=[
 {'id':'secret-en-a','lang':'en','url':'https://globalvoices.org:443/story?a=1#x','text':base},
 {'id':'secret-fr-a','lang':'fr','url':'https://fr.globalvoices.org/histoire','text':'Bonjour le monde ceci est un texte court mais unique.'},
 {'id':'secret-en-b','lang':'en','url':'https://independent.example:443/canonical#fragment','text':'another short confirmation document'}
 ,{'id':'secret-ipv6','lang':'en','url':'https://[2001:0db8::1]:443/a#fragment','text':'ipv6 confirmation document'}
]
rows=[
 {'id':'domain','lang':'es','url':'HTTP://ES.GLOBALVOICES.ORG.:80/x#f','text':'clean spanish words'},
 {'id':'invalid-url','lang':'en','url':'https://example.org:bad/x','text':'clean invalid URL row'},
 {'id':'exact-url','lang':'es','url':'https://independent.example/canonical','text':'different'},
 {'id':'ipv6-url','lang':'es','url':'https://[2001:db8::1]/a','text':'different ipv6'},
 {'id':'exact','lang':'en','url':'https://example/a','text':'  ONE\tTWO three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo  '},
 {'id':'near','lang':'en','url':'https://example/b','text':near},
 {'id':'short','lang':'en','url':'https://example/c','text':'one two three'},
 {'id':'cross','lang':'fr','url':'https://example/d','text':base},
 {'id':'clean','lang':'en','url':'https://example/e','text':'completely unrelated short development record'},
 {'id':'dup','lang':'en','url':'https://example/f','text':'first duplicate'},
 {'id':'dup','lang':'en','url':'https://example/g','text':'second duplicate'}
]
for r in rows:
 r.update({'dataset_repo':'fixture','dataset_revision':'a'*40,'dataset_shard_path':'fixture.jsonl','dataset_shard_lfs_sha256':'0'*64})

conf_sha=hashlib.sha256(json.dumps([{'id':x['id'],'lang':x['lang'],'url':x['url'],'raw_text_sha256':hashlib.sha256(x['text'].encode()).hexdigest()} for x in conf],sort_keys=True).encode()).hexdigest()

with tempfile.TemporaryDirectory(dir='output') as td:
    td=Path(td); dbpath=td/'selector.sqlite3'
    db=open_db(dbpath); bind_run(db,psha,'fixture-input-sha',True,isha); add_confirmation(db,conf,conf_sha); stage_rows(db,rows,True)
    selected,rejected=select_small_for_tests_only(db)
    ids={x['row_id'] for x in selected}
    fixture_rejections=dict(rejected)
    check('publisher_domain_block',rejected.get('globalvoices_host')==1,observed=rejected)
    check('invalid_supplied_url_rejected',rejected.get('invalid_url')==1)
    check('canonical_exact_and_ipv6_url_block',rejected.get('exact_url')==2)
    check('exact_normalized_content',rejected.get('exact_content')==1)
    check('near_multiset_containment',rejected.get('near_content')==1)
    check('short_and_cross_language_survive',{'short','cross'} <= ids,selected=sorted(ids))
    check('all_duplicate_copies_rejected',rejected.get('duplicate_id_all_copies')==2 and 'dup' not in ids)
    check('full_sha256_shingles',db.execute('SELECT MIN(length(g)),MAX(length(g)) FROM grams').fetchone()==(32,32))
    check('confirmation_raw_text_not_emitted',all(d['text'] not in json.dumps({'selected':selected,'rejected':rejected}) for d in conf))
    db.close(); db=open_db(dbpath); bind_run(db,psha,'fixture-input-sha',True,isha)
    rows_before=db.execute('SELECT COUNT(*) FROM rows').fetchone()[0]
    idem=(add_confirmation(db,conf,conf_sha)==0 and stage_rows(db,rows,True)==0 and db.execute('SELECT COUNT(*) FROM rows').fetchone()[0]==rows_before)
    check('close_reopen_stage_idempotence',idem)
    mismatch=False
    try: bind_run(db,psha,'different',True,isha)
    except ValueError: mismatch=True
    check('restart_binding_and_mismatch_guard',mismatch)
    mode_mismatch=False
    try: bind_run(db,psha,'fixture-input-sha',False,isha)
    except ValueError: mode_mismatch=True
    check('provenance_mode_binding_guard',mode_mismatch)
    streamed=atomic_stream_manifest(td/'selected_manifest.json',{'protocol_sha256':psha},iter_decisions(db))
    manifest=json.loads((td/'selected_manifest.json').read_text())
    check('atomic_stream_manifest_hash',streamed['sha256']==hashlib.sha256((td/'selected_manifest.json').read_bytes()).hexdigest() and not (td/'selected_manifest.json.tmp').exists() and len(manifest['selected'])==len(selected))
    db.close()

# Already-exposed probes: exact SQLite ordering must match direct reference. Formal provenance must fail.
def unwrap(path,lang):
    doc=json.loads(path.read_text()); out=[]
    aliases={'en':{'en'},'fr':{'fr','fra'},'es':{'es','spa'}}[lang]
    for x in doc['rows']:
        r=x['row']
        if r.get('language') not in aliases or r.get('dump')!='CC-MAIN-2013-20': continue
        if lang in {'fr','es'} and r.get('language_script')!='Latn': continue
        out.append({'id':r.get('id'),'lang':lang,'text':r.get('text'),'url':r.get('url')})
    return out

probe_summary={}
with tempfile.TemporaryDirectory(dir='output') as td:
    td=Path(td)
    for lang in ('en','fr','es'):
        rs=unwrap(Path(f'inputs/{lang}_probe.json'),lang)
        db=open_db(td/f'{lang}.sqlite3'); bind_run(db,psha,lang,False,isha); add_confirmation(db,[],empty_conf_sha); stage_rows(db,rs,False)
        selected,rejected=select_small_for_tests_only(db); got=[x['row_id'] for x in selected]
        counts={x['id']:sum(y['id']==x['id'] for y in rs) for x in rs}
        want=[x['id'] for x in sorted(rs,key=lambda x:(hashlib.sha256((f'pa-bpe-train-v1\0{lang}\0'+x['id']).encode()).digest(),x['id'].encode())) if counts[x['id']]==1]
        check(f'{lang}_sqlite_rank_equivalence',got==want,rows=len(rs))
        failed=False
        try:
            db2=open_db(td/f'{lang}-formal.sqlite3'); bind_run(db2,psha,lang,True,isha); add_confirmation(db2,[],empty_conf_sha); stage_rows(db2,rs,True)
        except ValueError: failed=True
        finally:
            if 'db2' in locals(): db2.close()
        check(f'{lang}_formal_provenance_hard_failure',failed)
        probe_summary[lang]={'input_rows':len(rs),'selected':len(got),'rejected':rejected}
        db.close()

missing=False
try:
    with tempfile.TemporaryDirectory(dir='output') as td:
        db=open_db(Path(td)/'missing.sqlite3'); bind_run(db,psha,'missing',False,isha); stage_rows(db,[{'id':'','lang':'en','text':'x'}])
except ValueError: missing=True
check('missing_id_dataset_hard_failure',missing)

# A late formal-provenance error must roll back earlier staged rows in the same transaction.
with tempfile.TemporaryDirectory(dir='output') as td:
    db=open_db(Path(td)/'rollback.sqlite3'); bind_run(db,psha,'rollback',True,isha)
    good={'id':'good','lang':'en','text':'valid','dataset_repo':'fixture','dataset_revision':'b'*40,'dataset_shard_path':'x','dataset_shard_lfs_sha256':'1'*64}
    bad=dict(good,id='bad',dataset_revision='not-a-revision')
    failed=False
    try: stage_rows(db,[good,bad],True)
    except ValueError: failed=True
    check('late_provenance_failure_rolls_back',failed and db.execute('SELECT COUNT(*) FROM rows').fetchone()[0]==0)

# Emission before confirmation completion must be impossible.
with tempfile.TemporaryDirectory(dir='output') as td:
    db=open_db(Path(td)/'incomplete.sqlite3'); bind_run(db,psha,'incomplete',False,isha)
    stage_rows(db,[{'id':'x','lang':'en','text':'x'}],False)
    blocked=False
    try: next(iter_decisions(db))
    except ValueError: blocked=True
    check('incomplete_stage_emission_guard',blocked)

# Non-string URL must fail transactionally.
with tempfile.TemporaryDirectory(dir='output') as td:
    db=open_db(Path(td)/'urltype.sqlite3'); bind_run(db,psha,'urltype',False,isha)
    failed=False
    try: stage_rows(db,[{'id':'x','lang':'en','text':'x','url':123}],False)
    except TypeError: failed=True
    check('url_type_guard_and_rollback',failed and db.execute('SELECT COUNT(*) FROM rows').fetchone()[0]==0)

falsey_guards=[]
for value in (0,False,b''):
    with tempfile.TemporaryDirectory(dir='output') as td:
        db=open_db(Path(td)/'falsey.sqlite3'); bind_run(db,psha,'falsey-'+type(value).__name__,False,isha)
        failed=False
        try: stage_rows(db,[{'id':'x','lang':'en','text':'x','url':value}],False)
        except TypeError: failed=True
        falsey_guards.append(failed and db.execute('SELECT COUNT(*) FROM rows').fetchone()[0]==0)
check('falsey_nonstring_url_guards',all(falsey_guards),cases=len(falsey_guards))

# Moderate generator-only scale probe: validates streaming behavior, not production scale.
with tempfile.TemporaryDirectory(dir='output') as td:
    td=Path(td); db=open_db(td/'scale.sqlite3'); bind_run(db,psha,'scale-20000',True,isha); add_confirmation(db,[],empty_conf_sha)
    def scale_rows():
        for i in range(20000):
            yield {'id':f'scale-{i:06d}','lang':('en','fr','es')[i%3],'text':f'clean short scale row {i}',
                   'dataset_repo':'fixture','dataset_revision':'c'*40,'dataset_shard_path':'scale.jsonl','dataset_shard_lfs_sha256':'2'*64}
    before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    staged=stage_rows(db,scale_rows(),True)
    scale_stream=atomic_stream_manifest(td/'scale_manifest.json',{'scope':'software-scale-probe'},iter_decisions(db))
    after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    check('moderate_streaming_scale_probe',staged==20000 and scale_stream['selected']==20000 and not scale_stream['rejections'],peak_rss_kib=after,baseline_peak_rss_kib=before)

result={
 'schema_version':1,
 'scope':'software verification only; synthetic decontamination fixture plus already exposed source probes; no confirmation raw text, formal payload, tokenizer, or fairness outcome',
 'protocol_sha256':psha,
 'memory_at_start':{'current_bytes':cur,'max_bytes':mx,'headroom_bytes':mx-cur},
 'sqlite_version':sqlite3.sqlite_version,
 'checks':checks,'all_checks_passed':all(x['passed'] for x in checks),'probe_summary':probe_summary,
 'fixture_rejections':fixture_rejections,
 'moderate_scale_probe':{'rows':20000,'peak_rss_kib':after,'baseline_peak_rss_kib':before,'claim':'software scale probe only; not production qualification'},
 'formal_gates':{'decontamination_on_real_confirmation':'HOLD','row_to_fixed_shard_provenance':'HOLD','production_scale':'HOLD','payload_sampling':'HOLD','tokenizer_training':'HOLD','fairness_claims':'HOLD'}
}
Path('output/decontam_selector_verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'checks':len(checks),'all_checks_passed':result['all_checks_passed'],'formal_gate':'HOLD'},sort_keys=True))
