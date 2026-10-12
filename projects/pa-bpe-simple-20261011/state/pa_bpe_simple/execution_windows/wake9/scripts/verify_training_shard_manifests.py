import hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
protocol=json.loads((root/'training_shard_protocol.json').read_text())
summary={'schema_version':1,'protocol_sha256':hashlib.sha256((root/'training_shard_protocol.json').read_bytes()).hexdigest(),'languages':{},'all_checks_passed':True,'payload_bytes_downloaded':0}
all_lfs=set()
for source in protocol['sources']:
    lang=source['language']; path=root/'output'/f'{lang}_training_shards.json'; manifest=json.loads(path.read_text()); files=manifest['files']
    checks={
      'repo_match':manifest['repo']==source['repo'],
      'revision_match':manifest['revision']==source['revision'],
      'tree_path_match':manifest['tree_path']==source['tree_path'],
      'count_match':len(files)==source['expected_parquet_files'],
      'paths_unique':len({x['path'] for x in files})==len(files),
      'lfs_sha256_valid':all(re.fullmatch(r'[0-9a-f]{64}',x['lfs_sha256']) is not None for x in files),
      'sizes_positive':all(x['size_bytes']>0 for x in files),
      'payload_zero':manifest['payload_bytes_downloaded']==0
    }
    overlap=len(all_lfs & {x['lfs_sha256'] for x in files}); all_lfs.update(x['lfs_sha256'] for x in files)
    checks['cross_language_lfs_overlap_zero']=overlap==0
    summary['languages'][lang]={'checks':checks,'file_count':len(files),'total_size_bytes':sum(x['size_bytes'] for x in files),'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cross_language_lfs_overlap_count':overlap}
    summary['all_checks_passed'] &= all(checks.values())
summary['total_files']=sum(x['file_count'] for x in summary['languages'].values())
summary['total_size_bytes']=sum(x['total_size_bytes'] for x in summary['languages'].values())
out=root/'output/training_shard_manifest_verification.json';out.write_text(json.dumps(summary,indent=2)+'\n')
if not summary['all_checks_passed']: raise SystemExit(1)
print(json.dumps(summary))
