import sys,json,hashlib,csv,io,zipfile,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data';E=P/'evidence'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((D/'manifest.json').read_text());plan=json.loads((P/'experiment_plan_v1.json').read_text());r=json.loads((P/'runs/evaluation_v1.json').read_text())
assert set(r['arms'])==set(plan['arms'])
for name,digest in m['hashes'].items():assert h(D/name)==digest,name
assert all(a['merges']==1000 and a['vocab']==1256 for a in r['arms'].values())
dev=json.loads((D/'tico.dev.json').read_text())[:100]
books={}
for name in ['dev','confirm']:
 raw=json.loads((E/f'books_{name}_v2.json').read_text())['rows'];assert all(not x.get('truncated_cells') for x in raw)
 books[name]=[dict(x['row']['translation'],id=x['row']['id']) for x in raw]
z=zipfile.ZipFile(E/'tico_zip.zip');raw=list(csv.DictReader(io.StringIO(z.read('tico19-testset/test/test.en-fr.tsv').decode()),delimiter='\t'))
test=sorted(raw,key=lambda r:hashlib.sha256(('pa-bpe-v1:'+r['stringID']).encode()).hexdigest())[200:400]
test=[dict(r,en=r['sourceString'].strip(),fr=r['targetString'].strip()) for r in test]
datasets={'tico.dev100':dev,'books.dev100':books['dev'],'tico.confirm':test,'books.confirm':books['confirm']}
overlaps={}
for lang in ['en','fr']:
 train=(D/f'train.{lang}').read_text()
 prior=[x for name in ['tico.dev','tico.test','books.pilot'] for x in json.loads((D/f'{name}.json').read_text())]
 devtexts={x[lang].strip() for split in ['tico.dev100','books.dev100'] for x in datasets[split]}|{x[lang].strip() for x in prior}
 for split in ['tico.confirm','books.confirm']:
  overlap=[x.get('stringID',x.get('id')) for x in datasets[split] if x[lang].strip() in devtexts or x[lang].strip() in train]
  overlaps[split+'.'+lang]=overlap
# Exclude exact confirmation strings shared with development/training in EITHER language.
for split in ['tico.confirm','books.confirm']:
 excluded=set(overlaps[split+'.en']+overlaps[split+'.fr']);datasets[split]=[x for x in datasets[split] if x.get('stringID',x.get('id')) not in excluded]
 assert len(datasets[split])>=90
for name,rows in datasets.items():(D/f'{name}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for lang in ['en','fr']:
 for domain,rows in [('tico',dev),('books',books['dev'])]:(D/f'dev2.{domain}.{lang}').write_text('\n'.join(r[lang].strip() for r in rows)+'\n')
 (D/f'dev2.pooled.{lang}').write_text('\n'.join(r[lang].strip() for r in dev+books['dev'])+'\n')
assert not {r['id'] for r in books['dev']}&{r['id'] for r in books['confirm']}
audit={'v1_acceptance':True,'expected_arms':plan['arms'],'actual_vocab':1256,'exact_match_exclusions':overlaps,'split_counts':{k:len(v) for k,v in datasets.items()},'hashes':{p.name:h(p) for p in D.glob('*') if p.name.startswith(('dev2.','tico.confirm','books.confirm','tico.dev100','books.dev100'))}}
(D/'manifest_v2.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
