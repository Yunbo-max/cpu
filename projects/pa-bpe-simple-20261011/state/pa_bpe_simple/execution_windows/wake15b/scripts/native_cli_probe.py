import collections,hashlib,json,pathlib,runpy,sys,datetime
P=pathlib.Path;mode=sys.argv[1];assert mode in ('classical','pa_ratio','pa_dev')
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output',mode+'_capacity.json').write_text(json.dumps({'headroom':free,'required':536870912,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}));assert free>=536870912,'memory_wait_required'
binding=json.loads(P('evidence/window_parent_binding.json').read_text());sys.path[:0]=[str(P('native_deps').resolve()),binding['dependency_directory']]
summary=json.loads(P('output/payload_summary.json').read_text());assert summary['status']=='PAYLOAD_BUILT_NATIVE_CLI_PENDING'
for lang in ('en','fr','es'):
    assert hashlib.sha256(P('output',lang+'.dict').read_bytes()).hexdigest()==summary['languages'][lang]['dictionary_sha256']
if mode=='classical':
    counter=collections.Counter()
    for l in ('en','fr','es'):
        for line in P('output',l+'.dict').read_text().splitlines():
            word,count=line.rsplit(' ',1);counter[word]+=int(count)
    assert sum(counter.values())==300000
    P('output/pooled.dict').write_text(''.join(f'{word} {counter[word]}\n' for word in sorted(counter)))
    source='inputs/learn_bpe.py';argv=[source,'--input','output/pooled.dict','--output','output/classical.codes','--dict-input','--symbols','32','--num-workers','1']
else:
    source='inputs/parity_aware_learn_bpe.py';argv=[source,'--input','output/en.dict','output/fr.dict','output/es.dict','--output','output/'+mode+'.codes','--dict-input','--symbols','32','--num-workers','1','--variant','base']
    if mode=='pa_ratio':argv+=['--ratio','1','1','1']
    else:argv+=['--dev','output/en.dict','output/fr.dict','output/es.dict']
sys.argv=argv
try:runpy.run_path(source,run_name='__main__')
except SystemExit as e:
    if e.code not in (0,None):raise
codepath=P('output',mode+'.codes');lines=codepath.read_text().splitlines();assert lines[0]=='#version: 0.2';assert len(lines)==33
result={'mode':mode,'argv':argv,'fixed_author_sha256':hashlib.sha256(P(source).read_bytes()).hexdigest(),'codes_sha256':hashlib.sha256(codepath.read_bytes()).hexdigest(),'merges':32,'train_pretoken_mass':300000,'status':'NATIVE_CLI_CONTRACT_PASS','scope':'32-merge CLI interface/resource diagnostic only, no evaluation or method comparison; pa_dev deliberately reuses nonparallel training dictionaries only to exercise shared dict-input parsing and is invalid as a fairness objective','confirmation_raw_accessed':False}
P('output',mode+'_cli_probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
