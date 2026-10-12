import sys,json,collections,hashlib,datetime,runpy
from pathlib import Path as P
mode=sys.argv[1]
free=int(P('/sys/fs/cgroup/memory.max').read_text())-int(P('/sys/fs/cgroup/memory.current').read_text())
P('output/'+mode+'_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':536870912}))
assert free>=536870912,'memory_wait_required'
sys.path.insert(0,str(P('deps').resolve()))
from tokenizers import pre_tokenizers
pre=pre_tokenizers.Sequence([pre_tokenizers.Whitespace(),pre_tokenizers.ByteLevel(use_regex=False)])
if mode=='prepare':
 rows=json.loads(P('output/tico.trilingual.dev.json').read_text())
 for l in ['en','fr','es']:
  c=collections.Counter(x[0] for r in rows for x in pre.pre_tokenize_str(r[l]))
  P('output/dev.'+l+'.dict').write_text(''.join(f'{p} {c[p]}\n' for p in sorted(c)))
 c=collections.Counter()
 for l in ['en','fr','es']:
  d={}
  for line in P('inputs/'+l+'.dict').read_text().splitlines():
   p,n=line.rsplit(' ',1);d[p]=int(n)
  assert sum(d.values())==100000;c.update(d)
 P('output/pooled.dict').write_text(''.join(f'{p} {c[p]}\n' for p in sorted(c)))
 P('output/preparation.json').write_text(json.dumps({'n':len(rows),'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(P('inputs').glob('*.dict'))+list(P('output').glob('*.dict'))}}))
else:
 assert mode in ['classical','base','window','hybrid','ratio']
 source='inputs/learn_bpe.py' if mode=='classical' else 'inputs/parity_aware_learn_bpe.py'
 argv=[source,'--input']+(['output/pooled.dict'] if mode=='classical' else ['inputs/'+l+'.dict' for l in ['en','fr','es']])+['--output','output/'+mode+'.codes','--dict-input','--symbols','1000','--num-workers','1']
 if mode!='classical':
  argv+=['--variant','window' if mode=='window' else 'base']
  if mode=='ratio':argv+=['--ratio','1','1','1']
  else:argv+=['--dev']+['output/dev.'+l+'.dict' for l in ['en','fr','es']]
  if mode=='hybrid':argv+=['--global-merges','500']
  if mode=='window':argv+=['--window-size','100','--alpha','2']
 sys.argv=argv
 try:runpy.run_path(source,run_name='__main__')
 except SystemExit as e:
  if e.code not in (0,None):raise
 lines=P('output/'+mode+'.codes').read_text().splitlines();assert len(lines)==1001
 P('output/'+mode+'_result.json').write_text(json.dumps({'argv':argv,'merges':1000,'code_sha256':hashlib.sha256(P('output/'+mode+'.codes').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(P(source).read_bytes()).hexdigest(),'scope':'aligned TICO development; no confirmation access'},indent=2))
