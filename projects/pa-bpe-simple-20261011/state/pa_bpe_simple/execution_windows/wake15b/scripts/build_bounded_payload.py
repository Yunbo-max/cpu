import ast,collections,hashlib,io,json,pathlib,sys,warnings,os,datetime
P=pathlib.Path; out=P('output')
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
(out/'capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headroom':free,'required':536870912}))
assert free>=536870912,'memory_wait_required'
binding=json.loads(P('evidence/window_parent_binding.json').read_text());sys.path.insert(0,binding['dependency_directory'])
import pyarrow as pa
import pyarrow.parquet as pq
import tokenizers
from tokenizers import pre_tokenizers
import decontam_selector as ds
pa.set_cpu_count(1);pa.set_io_thread_count(1)
assert tokenizers.__version__=='0.22.1'
pre=pre_tokenizers.Sequence([pre_tokenizers.Whitespace(),pre_tokenizers.ByteLevel(use_regex=False)])
def digest(p):
    with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[];spec=json.loads(P('inputs/en_shard.json').read_text());assert digest('inputs/en.parquet')==spec['shard']['lfs_sha256']
for batch in pq.ParquetFile('inputs/en.parquet').iter_batches(batch_size=97,columns=['id','text','dump','language','url'],use_threads=False):
    for r in batch.to_pylist():
        r.update({'canonical_language':'en','dataset_repo':spec['repo'],'dataset_revision':spec['revision'],'dataset_shard_path':spec['shard']['path'],'dataset_shard_lfs_sha256':spec['shard']['lfs_sha256'],'shard_row_index':len(rows),'source_verification':'complete_file_LFS_SHA256_verified'});rows.append(r)
for lang in ('fr','es'):
    summary=json.loads(P('inputs',lang+'_rowgroup_summary.json').read_text());foot=json.loads(P('inputs',lang+'_footer_probe_v2.json').read_text());spec=summary['spec'];xet=spec['shard']['xet_hash']
    assert summary['source_range']['etag'].strip('"')==xet
    assert all(r['etag'].strip('"')==xet for r in foot['retrieval'])
    assert summary['spec']==foot['spec']
    path=P('inputs',lang+'_rowgroup0.jsonl');assert digest(path)==summary['row_output_sha256']
    rlist=[json.loads(x) for x in path.read_text().splitlines()];assert len(rlist)==summary['row_count']==1000
    for i,r in enumerate(rlist):
        assert r['shard_row_index']==i==r['row_within_group'] and r['row_group']==0
        for k,v in {'dataset_repo':spec['repo'],'dataset_revision':spec['revision'],'dataset_shard_path':spec['shard']['path'],'dataset_shard_lfs_sha256':spec['shard']['lfs_sha256']}.items():assert r[k]==v
        assert r['raw_text_sha256']==hashlib.sha256(r['text'].encode()).hexdigest()
    rows.extend(rlist)
assert len(rows)==2374
for r in rows:
    lang=r['canonical_language'];assert isinstance(r['id'],str) and r['id'];assert r['dump']=='CC-MAIN-2013-20'
    assert r['language'] in {'en':['en'],'fr':['fr','fra'],'es':['es','spa']}[lang]
    if lang!='en':assert r['language_script']=='Latn'
    r['lang']=lang
input_binding={'frame_protocol_sha256':digest('bounded_frame_protocol.json'),'files':{p.name:digest(p) for p in sorted(P('inputs').iterdir()) if p.is_file()}}
ds.atomic_json(out/'payload_input_binding.json',input_binding)
db=ds.open_db(out/'selection.sqlite3')
protocol_sha=digest('inputs/decontamination_selector_protocol.json');contract_sha=digest('inputs/adapter_contract.json')
assert digest('inputs/confirmation.sqlite3')=='26e99931e2379b281d697149f47e62c0edd51d8466acca8016561e369fa520d7'
ds.import_blinded_confirmation_index(db,'inputs/confirmation.sqlite3',protocol_sha,contract_sha)
ds.bind_run(db,protocol_sha,digest(out/'payload_input_binding.json'),True,digest('scripts/decontam_selector.py'))
ds.stage_rows(db,iter(rows),require_provenance=True)
by_id=collections.defaultdict(list)
for r in rows:by_id[(r['lang'],r['id'])].append(r)
counts={l:collections.Counter() for l in ['en','fr','es']};remaining={l:100000 for l in counts};selected={l:[] for l in counts};reject=collections.Counter();eligible=collections.Counter()
for accepted,item in ds.iter_decisions(db):
    if not accepted:reject[item['reason']]+=1;continue
    lang=item['language'];eligible[lang]+=1
    if remaining[lang]==0:continue
    matches=by_id[(lang,item['row_id'])];assert len(matches)==1;r=matches[0]
    pieces=[x[0] for x in pre.pre_tokenize_str(r['text'])]
    if not pieces:reject['zero_pretokens']+=1;continue
    n=min(remaining[lang],len(pieces));counts[lang].update(pieces[:n]);remaining[lang]-=n
    selected[lang].append({**item,'shard_row_index':r['shard_row_index'],'source_verification':r['source_verification'],'available_pretokens':len(pieces),'included_prefix_count':n,'raw_utf8_bytes':len(r['text'].encode()),'unicode_scalars':len(r['text'])})
summary={'frame_rows':dict(collections.Counter(r['lang'] for r in rows)),'accepted_after_decontamination':dict(eligible),'rejections':dict(reject),'remaining_pretokens':remaining,'confirmation_raw_accessed':False,'source_scope':'English whole file SHA verified; French/Spanish immutable HTTPS ranges checked against fixed Xet ETag, not whole-file LFS rehash','status':'INSUFFICIENT' if any(remaining.values()) else 'PAYLOAD_BUILT_NATIVE_CLI_PENDING','scope':'Convenience-frame development only; no tokenizer trained and no fairness measured'}
if any(remaining.values()):
    ds.atomic_json(out/'payload_summary.json',summary);db.close();print(json.dumps(summary));raise SystemExit(0)
parsers={}
for filename in ['learn_bpe.py','parity_aware_learn_bpe.py']:
    tree=ast.parse(P('inputs',filename).read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='get_vocabulary');ns={'Counter':collections.Counter,'sys':sys,'warnings':warnings};exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'),ns);parsers[filename]=ns['get_vocabulary']
summary['languages']={}
for lang,counter in counts.items():
    assert sum(counter.values())==100000
    assert not any(any(c in p for c in ' \r\n') for p in counter)
    content=''.join(f'{p} {counter[p]}\n' for p in sorted(counter))
    for parser in parsers.values():assert dict(parser(io.StringIO(content),True,1))==dict(counter)
    path=out/(lang+'.dict');tmp=path.with_suffix('.tmp');tmp.write_text(content);tmp.replace(path)
    summary['languages'][lang]={'documents':len(selected[lang]),'pretoken_occurrences':100000,'unique_pretokens':len(counter),'initial_symbol_mass':sum(len(p)*n for p,n in counter.items()),'raw_utf8_bytes_whole_selected_documents':sum(r['raw_utf8_bytes'] for r in selected[lang]),'unicode_scalars_whole_selected_documents':sum(r['unicode_scalars'] for r in selected[lang]),'dictionary_sha256':digest(path),'author_dictionary_parsers':'both exact roundtrip'}
manifest={'input_binding_sha256':digest(out/'payload_input_binding.json'),'protocol_sha256':digest('bounded_frame_protocol.json'),'selected':selected,'dictionary_sha256':{l:summary['languages'][l]['dictionary_sha256'] for l in counts},'scope':summary['scope']}
summary['selected_manifest_sha256']=ds.atomic_json(out/'selected_rows.json',manifest)
db.commit();db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.close();ds.atomic_json(out/'payload_summary.json',summary);print(json.dumps(summary))
