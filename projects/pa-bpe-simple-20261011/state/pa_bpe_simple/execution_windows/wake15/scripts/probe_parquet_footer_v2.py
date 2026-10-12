import datetime,hashlib,io,json,pathlib,struct,sys,time,urllib.request
lang=sys.argv[1]; spec=json.loads(pathlib.Path('inputs',lang+'_first_shard.json').read_text()); shard=spec['shard']; total=shard['size_bytes']
assert int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())-int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())>=384*1024*1024,'memory_wait_required'
url='https://huggingface.co/datasets/'+spec['repo']+'/resolve/'+spec['revision']+'/'+shard['path']
records=[]
def get(start,end):
    assert end-start+1<=4*1024*1024
    req=urllib.request.Request(url+'?download=true&pa_bpe_range='+str(start)+'-'+str(end),headers={'Range':f'bytes={start}-{end}','User-Agent':'pa-bpe-source-audit/1.0','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=30) as r:
        assert r.status==206, f'Range refused {r.status}'
        assert r.headers.get('Content-Range')==f'bytes {start}-{end}/{total}',r.headers.get('Content-Range')
        data=r.read(end-start+2);assert len(data)==end-start+1
        records.append({'range':[start,end],'status':r.status,'content_range':r.headers.get('Content-Range'),'etag':r.headers.get('ETag'),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        return data
tail=get(total-8,total-1)
assert tail[4:]==b'PAR1'
footer_size=struct.unpack('<I',tail[:4])[0]
pathlib.Path('output',lang+'_footer_length_v2.json').write_text(json.dumps({'footer_size':footer_size,'retrieval':records,'source':spec},indent=2))
assert 0<footer_size<=64*1024*1024, str(footer_size)
footer=b''.join(get(start,min(start+4*1024*1024-1,total-9)) for start in range(total-8-footer_size,total-8,4*1024*1024))
pathlib.Path('output',lang+'_footer_v2.parquet').write_bytes(b'PAR1'+footer+tail)
sys.path.insert(0,str(pathlib.Path('deps').resolve()))
import pyarrow as pa
import pyarrow.parquet as pq
pa.set_cpu_count(1);pa.set_io_thread_count(1)
metadata=pq.read_metadata(io.BytesIO(b'PAR1'+footer+tail))
groups=[]
for i in range(metadata.num_row_groups):
    rg=metadata.row_group(i); cols=[]
    for j in range(rg.num_columns):
        col=rg.column(j);st=col.statistics
        if col.path_in_schema in ('dump','language','language_script'):
            cols.append({'column':col.path_in_schema,'statistics':None if st is None else {'has_min_max':st.has_min_max,'min':str(st.min),'max':str(st.max),'null_count':st.null_count},'compressed_bytes':col.total_compressed_size,'data_page_offset':col.data_page_offset,'dictionary_page_offset':col.dictionary_page_offset})
    groups.append({'row_group':i,'num_rows':rg.num_rows,'columns':cols})
result={'spec':spec,'retrieval':records,'footer_length':footer_size,'num_rows':metadata.num_rows,'row_groups':groups,'schema':str(metadata.schema),'full_file_hash_verified':False,'scope':'Metadata-only range probe at immutable revision, byte ranges validated against frozen file size. Does not independently verify entire LFS object or authorize training rows.','payload_text_read':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
pathlib.Path('output',lang+'_footer_probe_v2.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'language':lang,'row_groups':metadata.num_row_groups,'rows':metadata.num_rows,'bytes_read':sum(r['bytes'] for r in records),'dump_ranges':[c['statistics'] for g in groups for c in g['columns'] if c['column']=='dump'][:10]}))
