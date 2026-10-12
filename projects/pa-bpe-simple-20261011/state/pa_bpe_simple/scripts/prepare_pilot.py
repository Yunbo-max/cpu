import csv,io,json,zipfile,hashlib,sys
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
from tokenizers.pre_tokenizers import Whitespace,ByteLevel,Sequence
from collections import Counter
import numpy as np
P=Path(__file__).resolve().parents[1]; E=P/'evidence'; D=P/'data'
pre=Sequence([Whitespace(),ByteLevel(use_regex=False)])
def save(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
meta={'languages':['en','fr'],'train':{},'splits':{},'licenses':{'FineWeb':'ODC-BY; original web text rights retained','TICO19':'Translations CC0; retain per-row source license and URL','OPUS Books':'personal educational research use; no commercial or mass redistribution; Andras Farkas / OPUS attribution'},'protocol':'New bilingual cross-domain pilot; NOT FLORES+ reproduction'}
counts={}
for lang,fn in [('en','fineweb_en_v1.json'),('fr','fineweb_fr.json')]:
 rows=json.loads((E/fn).read_text())['rows']; assert len(rows)==40
 assert all(not r.get('truncated_cells') for r in rows)
 texts=[r['row']['text'] for r in rows]; (D/f'train.{lang}').write_text('\n'.join(texts)+'\n')
 c=Counter(w for t in texts for w,_ in pre.pre_tokenize_str(t));counts[lang]=c
 meta['train'][lang]={'documents':40,'raw_bytes':sum(len(t.encode()) for t in texts),'pretokens':sum(c.values()),'ids':[r['row'].get('id',r['row_idx']) for r in rows]}
(D/'train.joint').write_bytes((D/'train.en').read_bytes()+(D/'train.fr').read_bytes())
# Equal numbers of pretoken occurrences, same TOTAL number as unbalanced baseline.
n=sum(sum(c.values()) for c in counts.values()); rng=np.random.default_rng(20261011);balanced=Counter()
for i,(lang,c) in enumerate(counts.items()):
 words=sorted(c); freq=np.array([c[w] for w in words],float); sample=rng.multinomial(n//2+(i==1)*(n%2),freq/freq.sum())
 balanced.update({w:int(v) for w,v in zip(words,sample) if v})
(D/'train.balanced.dict').write_text(''.join(f'{w} {v}\n' for w,v in sorted(balanced.items())))
z=zipfile.ZipFile(E/'tico_zip.zip')
(D/'TICO_README.md').write_bytes(z.read('tico19-testset/README.md'))
for split in ['dev','test']:
 rows=list(csv.DictReader(io.StringIO(z.read(f'tico19-testset/{split}/{split}.en-fr.tsv').decode()),delimiter='\t'))
 selected=sorted(rows,key=lambda r:hashlib.sha256(('pa-bpe-v1:'+r['stringID']).encode()).hexdigest())[:200]
 assert len({r['stringID'] for r in selected})==200
 selected=[dict(r,en=r['sourceString'].strip(),fr=r['targetString'].strip()) for r in selected]
 assert all(r['en'] and r['fr'] for r in selected)
 save(f'tico.{split}.json',selected);meta['splits']['tico.'+split]=[r['stringID'] for r in selected]
 if split=='dev':
  for l in ['en','fr']:(D/f'dev.{l}').write_text('\n'.join(r[l] for r in selected)+'\n')
assert not set(meta['splits']['tico.dev'])&set(meta['splits']['tico.test'])
rows=json.loads((E/'books_enfr.json').read_text())['rows']; assert all(not r.get('truncated_cells') for r in rows)
books=[dict(r['row']['translation'],id=r['row']['id']) for r in rows if all(r['row']['translation'].values())]
save('books.pilot.json',books);meta['splits']['books.pilot']=[r['id'] for r in books]
dev=json.loads((D/'tico.dev.json').read_text());lens=[sum(len(w) for r in dev for w,_ in pre.pre_tokenize_str(r[l])) for l in ['en','fr']]
meta['ratio_dev']=[v/lens[0] for v in lens];meta['pretokenizer']=json.loads(pre.__getstate__());meta['balanced_total_pretokens']=sum(balanced.values())
meta['hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()}
save('manifest.json',meta);print(json.dumps({k:v for k,v in meta.items() if k not in ['hashes','splits','train']},indent=2))
