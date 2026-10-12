import hashlib,io,json,pathlib,sys,urllib.request,datetime
lang=sys.argv[1];assert lang in ('fr','es')
free=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())-int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
pathlib.Path('output',lang+'_rowgroup_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headroom':free,'required':536870912}))
assert free>=536870912,'memory_wait_required'
sys.path.insert(0,str(pathlib.Path('deps').resolve()))
import pyarrow as pa
import pyarrow.parquet as pq
pa.set_cpu_count(1);pa.set_io_thread_count(1)
spec=json.loads(pathlib.Path('inputs',lang+'_first_shard.json').read_text());shard=spec['shard'];size=shard['size_bytes']
footer_path=pathlib.Path('output',lang+'_footer_v2.parquet');footer_file=footer_path.read_bytes();md=pq.read_metadata(io.BytesIO(footer_file));group=md.row_group(0)
assert {'id','text','dump','language','language_script','url'}.issubset(md.schema.names)
dumpcol=next(group.column(i) for i in range(group.num_columns) if group.column(i).path_in_schema=='dump')
assert dumpcol.statistics.min==dumpcol.statistics.max=='CC-MAIN-2013-20'
starts=[min(x for x in (group.column(i).dictionary_page_offset,group.column(i).data_page_offset) if x is not None and x>=4) for i in range(group.num_columns)]
end=max(start+group.column(i).total_compressed_size for i,start in enumerate(starts));start=min(starts)
assert 0<end-start<=16777216
url='https://huggingface.co/datasets/'+spec['repo']+'/resolve/'+spec['revision']+'/'+shard['path']
req=urllib.request.Request(url+f'?download=true&pa_bpe_range={start}-{end-1}',headers={'Range':f'bytes={start}-{end-1}','Accept-Encoding':'identity','User-Agent':'pa-bpe-source-audit/1.0'})
with urllib.request.urlopen(req,timeout=40) as r:
    assert r.status==206 and r.headers.get('Content-Range')==f'bytes {start}-{end-1}/{size}'
    body=r.read(end-start+1);assert len(body)==end-start
    etag=r.headers.get('ETag')
body_path=pathlib.Path('output',lang+'_rowgroup0.bin');body_path.write_bytes(body)
parts=[(0,b'PAR1'),(start,body),(size-len(footer_file)+4,footer_file[4:])]
class Ranges(io.RawIOBase):
    def __init__(self):self.pos=0
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else (self.pos+offset if whence==1 else size+offset)
        if not 0<=self.pos<=size:raise ValueError('bad seek')
        return self.pos
    def read(self,n=-1):
        if n<0:n=size-self.pos
        for off,data in parts:
            if off<=self.pos and self.pos+n<=off+len(data):
                res=data[self.pos-off:self.pos-off+n];self.pos+=n;return res
        raise ValueError(f'Uncached read requested {self.pos}:{self.pos+n}')
reader=pq.ParquetFile(Ranges(),metadata=md,pre_buffer=False,buffer_size=0)
table=reader.read_row_group(0,columns=['id','text','dump','language','language_script','url'],use_threads=False)
assert len(table)==group.num_rows
rows_path=pathlib.Path('output',lang+'_rowgroup0.jsonl');tmp=rows_path.with_suffix('.tmp')
with tmp.open('x',encoding='utf-8') as out:
    for i,row in enumerate(table.to_pylist()):
        assert isinstance(row['id'],str) and row['id']
        assert row['dump']=='CC-MAIN-2013-20' and row['language_script']=='Latn' and row['language'] in {'fr':['fr','fra'],'es':['es','spa']}[lang]
        assert isinstance(row['text'],str) and row['text']
        row.update({'canonical_language':lang,'dataset_repo':spec['repo'],'dataset_revision':spec['revision'],'dataset_shard_path':shard['path'],'dataset_shard_lfs_sha256':shard['lfs_sha256'],'shard_row_index':i,'row_group':0,'row_within_group':i,'raw_text_sha256':hashlib.sha256(row['text'].encode()).hexdigest(),'source_verification':'immutable_https_byte_ranges_not_whole_lfs_rehash'})
        out.write(json.dumps(row,ensure_ascii=False)+'\n')
tmp.replace(rows_path)
summary={'spec':spec,'row_group':0,'row_count':len(table),'source_range':{'start':start,'end_inclusive':end-1,'total_file_bytes':size,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'etag':etag,'status':206},'footer_sha256':hashlib.sha256(footer_file).hexdigest(),'row_output_sha256':hashlib.sha256(rows_path.read_bytes()).hexdigest(),'full_lfs_rehash':False,'scope':'Frozen convenience-frame first row-group, provenance via pinned source HTTPS ranges; native labels verified against fixed eligibility; not decontaminated or training accepted yet'}
pathlib.Path('output',lang+'_rowgroup_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
