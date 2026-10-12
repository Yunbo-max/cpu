import argparse, datetime, hashlib, json, pathlib, re, urllib.parse, urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--language',required=True)
parser.add_argument('--repo',required=True)
parser.add_argument('--revision',required=True)
parser.add_argument('--tree-path',required=True)
parser.add_argument('--expected-count',required=True,type=int)
parser.add_argument('--output',required=True)
args=parser.parse_args()
base='https://huggingface.co/api/datasets/'+args.repo+'/tree/'+args.revision+'/'+urllib.parse.quote(args.tree_path,safe='/')
url=base+'?'+urllib.parse.urlencode({'recursive':'true','expand':'true','limit':100})
pages=[]; entries=[]; seen_urls=set()
while url:
    if url in seen_urls: raise RuntimeError('pagination cycle')
    seen_urls.add(url)
    req=urllib.request.Request(url,headers={'User-Agent':'pa-bpe-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=45) as response:
        raw=response.read(); status=response.status; link=response.headers.get('Link')
    if status!=200: raise RuntimeError(f'HTTP {status}')
    page=json.loads(raw)
    if not isinstance(page,list): raise RuntimeError('tree response is not a list')
    pages.append({'url':url,'http_status':status,'response_bytes':len(raw),'response_sha256':hashlib.sha256(raw).hexdigest(),'entry_count':len(page)})
    entries.extend(page)
    url=None
    if link:
        for part in link.split(','):
            if 'rel="next"' in part:
                match=re.search(r'<([^>]+)>',part)
                if match: url=match.group(1)
files=[entry for entry in entries if entry.get('type')=='file' and entry.get('path','').endswith('.parquet')]
if len(files)!=args.expected_count: raise RuntimeError(f'expected {args.expected_count} parquet files, observed {len(files)}')
paths=[entry['path'] for entry in files]
if len(paths)!=len(set(paths)): raise RuntimeError('duplicate paths')
for entry in files:
    lfs=entry.get('lfs') or {}; oid=lfs.get('oid','')
    if not re.fullmatch(r'[0-9a-f]{64}',oid): raise RuntimeError('missing/invalid LFS oid for '+entry['path'])
    if entry.get('size')!=lfs.get('size') or not isinstance(entry.get('size'),int) or entry['size']<=0: raise RuntimeError('size mismatch for '+entry['path'])
clean=[{'path':e['path'],'git_oid':e.get('oid'),'lfs_sha256':e['lfs']['oid'],'size_bytes':e['size'],'xet_hash':e.get('xetHash'),'last_commit_id':(e.get('lastCommit') or {}).get('id')} for e in files]
out={'schema_version':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'language':args.language,'repo':args.repo,'revision':args.revision,'tree_path':args.tree_path,'api_pages':pages,'parquet_file_count':len(clean),'total_size_bytes':sum(e['size_bytes'] for e in clean),'files':clean,'payload_bytes_downloaded':0,'scope':'immutable source identities only'}
path=pathlib.Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'language':args.language,'pages':len(pages),'files':len(clean),'total_size_bytes':out['total_size_bytes'],'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
