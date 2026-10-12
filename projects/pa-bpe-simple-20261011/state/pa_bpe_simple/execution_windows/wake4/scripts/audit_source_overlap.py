"""Exact long-shingle overlap audit between actual FineWeb2 train rows and raw Books rows."""
import hashlib,json,re,unicodedata
from pathlib import Path

def words(text):
    return re.findall(r"\w+",unicodedata.normalize('NFKC',text).casefold(),flags=re.UNICODE)

def shingles(tokens,n):
    for i in range(len(tokens)-n+1):
        phrase=' '.join(tokens[i:i+n])
        yield hashlib.sha256(phrase.encode()).digest(),phrase

training={}
for lang,name in [('en','fineweb_en_v1.json'),('fr','fineweb_fr.json')]:
    rows=json.loads(Path('inputs/'+name).read_text())['rows']
    assert len(rows)==40 and all(not r.get('truncated_cells') for r in rows)
    training[lang]=rows

evaluation=json.loads(Path('inputs/multibook_raw_evaluation.json').read_text())
result={'scope':json.loads(Path('source_overlap_plan.json').read_text())['scope'],
        'train_documents':{},'evaluation_rows':0,'thresholds':{}}
for lang,rows in training.items():
    result['train_documents'][lang]={'n':len(rows),'ids':[r['row']['id'] for r in rows],
        'urls':[r['row']['url'] for r in rows]}

for n in [15,30]:
    indices={}
    for lang,rows in training.items():
        idx={}
        for doc,r in enumerate(rows):
            for h,phrase in shingles(words(r['row']['text']),n):idx.setdefault(h,(doc,phrase))
        indices[lang]=idx
    matches=[];per_work={}
    for work,d in evaluation['sampling'].items():
        count=0
        for row_index,row in enumerate(d['rows']):
            if n==15:result['evaluation_rows']+=1
            for li,lang in enumerate(['en','fr']):
                for h,phrase in shingles(words(row['text'][li]),n):
                    if h in indices[lang]:
                        doc,train_phrase=indices[lang][h]
                        assert phrase==train_phrase
                        count+=1
                        if len(matches)<20:
                            tr=training[lang][doc]['row']
                            matches.append({'work':work,'row_index':row_index,'language':lang,
                                'train_id':tr['id'],'train_url':tr['url'],'phrase':phrase})
                        break
        per_work[work]=count
    result['thresholds'][str(n)]={'matching_language_rows':sum(per_work.values()),
        'works_with_matches':sum(v>0 for v in per_work.values()),'per_work':per_work,'examples':matches}
assert result['evaluation_rows']==5120
result['primary_30word_no_match']=result['thresholds']['30']['matching_language_rows']==0
Path('output/source_overlap_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['train_documents']},ensure_ascii=False))
