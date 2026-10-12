import collections, datetime, hashlib, heapq, json, os, pathlib, sys, time, urllib.request

lang=sys.argv[1]
spec_path=pathlib.Path('inputs')/(lang+'_shard.json')
spec=json.loads(spec_path.read_text()); shard=spec['shard']
assert lang==spec['language'] and lang in ('en','fr','es')
resource={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'memory_max':int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text()), 'memory_current':int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())}
pathlib.Path('output',lang+'_capacity.json').write_text(json.dumps(resource,indent=2))
assert resource['memory_max']-resource['memory_current']>=536870912, 'memory_wait_required'
assert shard['size_bytes']<=60000000
cache=pathlib.Path('cache');cache.mkdir(exist_ok=True)
target=cache/(lang+'.parquet'); tmp=target.with_suffix('.part')
url='https://huggingface.co/datasets/'+spec['repo']+'/resolve/'+spec['revision']+'/'+shard['path']
started=time.monotonic();digest=hashlib.sha256();size=0
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'pa-bpe-source-audit/1.0'}), timeout=40) as response, tmp.open('xb') as out:
    assert response.status==200
    status=response.status
    while block:=response.read(1024*1024):
        size+=len(block)
        assert size<=shard['size_bytes']
        out.write(block);digest.update(block)
        assert time.monotonic()-started<95,'download internal deadline'
assert size==shard['size_bytes'] and digest.hexdigest()==shard['lfs_sha256'], 'source hash or size mismatch'
tmp.replace(target)
sys.path.insert(0,str(pathlib.Path('deps').resolve()))
import pyarrow as pa
import pyarrow.parquet as pq
pa.set_cpu_count(1);pa.set_io_thread_count(1)
pf=pq.ParquetFile(target)
columns=pf.schema_arrow.names
required={'id','text','dump','language','url'}
assert required.issubset(columns),str(columns)
if lang!='en': assert 'language_script' in columns, str(columns)
columns_to_read=sorted(required | ({'language_script'} if lang!='en' else set()))
counts=collections.Counter();dumps=collections.Counter();languages=collections.Counter();scripts=collections.Counter()
# Keep at most 128 smallest eligible ID hashes from this diagnostic file only.
# This is not the full-universe selector and makes no decontamination claim.
heap=[]; seen=set(); duplicates=set();row_offset=0
for batch in pf.iter_batches(batch_size=128,columns=columns_to_read,use_threads=False):
    for row in batch.to_pylist():
        index=row_offset;row_offset+=1;counts['all_rows']+=1
        for counter,key in [(dumps,'dump'),(languages,'language'),(scripts,'language_script')]:counter[str(row.get(key))]+=1
        stable=row['id'];text=row['text']
        if not isinstance(stable,str) or not stable:counts['missing_id']+=1;continue
        if stable in seen:duplicates.add(stable)
        seen.add(stable)
        if row['dump']!='CC-MAIN-2013-20':counts['wrong_dump']+=1;continue
        if row['language'] not in {'en':['en'],'fr':['fr','fra'],'es':['es','spa']}[lang]:counts['wrong_language']+=1;continue
        if lang!='en' and row['language_script']!='Latn':counts['wrong_script']+=1;continue
        if not isinstance(text,str) or not text:counts['empty_text']+=1;continue
        counts['eligible_before_decontamination']+=1
        rank=hashlib.sha256(('pa-bpe-train-v1\0'+lang+'\0'+stable).encode()).hexdigest()
        enriched={**row,'canonical_language':lang,'dataset_repo':spec['repo'],'dataset_revision':spec['revision'],'dataset_shard_path':shard['path'],'dataset_shard_lfs_sha256':shard['lfs_sha256'],'shard_row_index':index,'raw_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'rank_sha256':rank}
        item=(-int(rank,16),-index,enriched)
        if len(heap)<128:heapq.heappushush(heap,item) if False else heapq.heappush(heap,item)
        elif item[:2]>heap[0][:2]:heapq.heapreplace(heap,item)
assert row_offset==pf.metadata.num_rows
assert counts['missing_id']==0,'missing stable ID in scanned shard'
retained=sorted((item[2] for item in heap if item[2]['id'] not in duplicates),key=lambda x:(x['rank_sha256'],x['id']))
outpath=pathlib.Path('output',lang+'_diagnostic_rows.jsonl')
with outpath.with_suffix('.tmp').open('x',encoding='utf-8') as out:
    for row in retained:out.write(json.dumps(row,ensure_ascii=False)+'\n')
outpath.with_suffix('.tmp').replace(outpath)
summary={'language':lang,'scope':'smallest whole fixed shard diagnostic, not representative or production selected','source':spec,'source_spec_sha256':hashlib.sha256(spec_path.read_bytes()).hexdigest(),'retrieval':{'url':url,'http_status':status,'bytes':size,'sha256':digest.hexdigest(),'full_file_verified':True},'schema':str(pf.schema_arrow),'row_groups':pf.metadata.num_row_groups,'counts':dict(counts),'dump_counts':dict(dumps),'language_counts':dict(languages),'script_counts':dict(scripts),'duplicate_ids_in_scanned_shard':len(duplicates),'retained_rows':len(retained),'output_sha256':hashlib.sha256(outpath.read_bytes()).hexdigest(),'pyarrow':pa.__version__,'threads':1,'confirmation_raw_accessed':False,'training_eligible':False,'duplicate_scope':'complete scanned shard only, no claim about the full dataset'}
pathlib.Path('output',lang+'_extraction.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['language','counts','retained_rows','duplicate_ids_in_scanned_shard','output_sha256']}))
