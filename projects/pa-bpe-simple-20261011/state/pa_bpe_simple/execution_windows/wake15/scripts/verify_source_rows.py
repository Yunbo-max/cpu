import collections,hashlib,json,pathlib,sys
assert int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())-int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())>=384*1024*1024,'memory_wait_required'
sys.path.insert(0,str(pathlib.Path('deps').resolve()))
import pyarrow as pa
import pyarrow.parquet as pq
pa.set_cpu_count(1);pa.set_io_thread_count(1)
checks=[]
for lang in ('en','fr','es'):
    spec=json.loads(pathlib.Path('inputs',lang+'_shard.json').read_text());f=pathlib.Path('cache',lang+'.parquet')
    with f.open('rb') as stream: actual=hashlib.file_digest(stream,'sha256').hexdigest()
    assert actual==spec['shard']['lfs_sha256'] and f.stat().st_size==spec['shard']['size_bytes']
    saved=json.loads(pathlib.Path('output',lang+'_extraction.json').read_text())
    rp=pathlib.Path('output',lang+'_diagnostic_rows.jsonl')
    assert hashlib.sha256(rp.read_bytes()).hexdigest()==saved['output_sha256']
    rows=[json.loads(x) for x in rp.read_text().splitlines()];by_offset={r['shard_row_index']:r for r in rows};assert len(by_offset)==len(rows)
    p=pq.ParquetFile(f); n=0;dumps=collections.Counter();ids=collections.Counter();eligible=[];matched=0
    columns=['id','text','dump','language','url']+(['language_script'] if lang!='en' else [])
    for batch in p.iter_batches(batch_size=97,columns=columns,use_threads=False):
        for row in batch.to_pylist():
            ids[row['id']]+=1;dumps[row['dump']]+=1
            assert isinstance(row['id'],str) and row['id']
            if n in by_offset:
                r=by_offset[n]
                assert all(r[k]==row[k] for k in columns)
                for k,v in {'dataset_repo':spec['repo'],'dataset_revision':spec['revision'],'dataset_shard_path':spec['shard']['path'],'dataset_shard_lfs_sha256':actual}.items():assert r[k]==v
                assert hashlib.sha256(row['text'].encode()).hexdigest()==r['raw_text_sha256']
                matched+=1
            ok=row['dump']=='CC-MAIN-2013-20' and row['language'] in {'en':('en',),'fr':('fr','fra'),'es':('es','spa')}[lang] and bool(row['text'])
            if lang!='en':ok=ok and row['language_script']=='Latn'
            if ok:
                digest=hashlib.sha256(b'pa-bpe-train-v1\x00'+lang.encode()+b'\x00'+row['id'].encode()).hexdigest()
                eligible.append((digest,row['id'],n))
            n+=1
    assert n==p.metadata.num_rows==saved['counts']['all_rows']
    assert dict(dumps)==saved['dump_counts']
    assert len(eligible)==saved['counts'].get('eligible_before_decontamination',0)
    duplicate_count=sum(v>1 for v in ids.values());assert duplicate_count==saved['duplicate_ids_in_scanned_shard']
    assert duplicate_count==0,'Independent exact top128 oracle requires no duplicates; diagnostic duplicate limitation must remain explicit'
    expected=sorted(eligible)[:128]
    assert [(r['rank_sha256'],r['id'],r['shard_row_index']) for r in rows]==expected
    assert matched==len(rows)==saved['retained_rows']
    checks.append({'language':lang,'full_lfs_hash_verified':True,'rows_scanned':n,'native_rows_matched':matched,'eligible_before_decontamination':len(eligible),'complete_shard_duplicates':duplicate_count,'exact_sorted_rank_oracle':True,'batch_size':97})
out={'status':'PASS','scope':'Independent local whole-file rehash, row-offset/native-field identity and no-duplicate exact full-sort oracle against diagnostic heap. Not production decontamination, representativeness, tokenizer or fairness qualification.','checks':checks,'confirmation_raw_accessed':False}
pathlib.Path('output/source_rows_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
