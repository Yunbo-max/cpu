import csv,io,zipfile,json,hashlib,collections,datetime
from pathlib import Path as P
z=P('inputs/tico.zip');assert hashlib.sha256(z.read_bytes()).hexdigest()=='0e82fc7ceaa877606c8934f32ead185716c9d2c54b3818f2a7ae655f5e7a08d8'
zf=zipfile.ZipFile(z);data={}
for l,s in [('fr','fr'),('es','es-LA')]:
 b=zf.read('tico19-testset/dev/dev.en-'+s+'.tsv');P('output/v3_dev.en-'+s+'.tsv').write_bytes(b)
 rows=list(csv.DictReader(io.StringIO(b.decode()),delimiter='\t'));assert len(rows)==971
 d={r['stringID']:r for r in rows};assert len(d)==971;data[l]=d
assert data['fr'].keys()==data['es'].keys()
rows=[];rejected=[]
for i in sorted(data['fr']):
 f=data['fr'][i];s=data['es'][i]
 if f['sourceString'].strip(' \t\r\n')!=s['sourceString'].strip(' \t\r\n') or f['url']!=s['url']:
  rejected.append({'id':i,'source_equal':f['sourceString']==s['sourceString'],'url_equal':f['url']==s['url'],'en_fr':f['sourceString'],'en_es':s['sourceString']});continue
 assert f['sourceLang']==s['sourceLang']=='en';assert f['targetLang']=='fr' and s['targetLang']=='es-419'
 rows.append({'id':i,'en':f['sourceString'].strip(' \t\r\n'),'fr':f['targetString'],'es':s['targetString'],'url':f['url'],'source_license':f['license'],'translators':{'fr':f['translator_ID'],'es':s['translator_ID']}})
assert all(r[l].strip() for r in rows for l in ['en','fr','es'])
P('output/v3_tico.trilingual.dev.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
P('output/v3_TICO_README.md').write_bytes(zf.read('tico19-testset/README.md'))
out={'n':len(rows),'rejected':rejected,'alignment':'shared stringID, ASCII boundary-whitespace-trimmed exact English and exact URL; no internal normalization or positional join','languages':['en','fr','es-LA'],'source_zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'dataset':'official TICO-19 dev, 971 sentences','licenses':dict(collections.Counter(r['source_license'] for r in rows)),'distinct_urls':len(set(r['url'] for r in rows)),'scope':'exposed development only; prior en/fr outcomes are known; no independent confirmation claim','confirmation_raw_opened':False,'output_sha256':hashlib.sha256(P('output/v3_tico.trilingual.dev.json').read_bytes()).hexdigest()}
P('output/v3_dev_alignment.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
