import hashlib,importlib.util,json,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('verified_eval','scripts/evaluator_reference.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
data=json.loads(Path('output/multibook_raw_evaluation.json').read_text())
old=json.loads(Path('inputs/old_candidate_evaluation.json').read_text())
def stats(costs):
    n=len(costs);mean=[sum(x[i] for x in costs)/n for i in [0,1]]
    g=ev.gini(mean);assert abs(g-ev.gini_sorted(mean))<1e-12
    return {'n':n,'mean_tokens':mean,'gini':g,'worst_cost':max(mean),'sum_language_means':sum(mean),'mean_sentence_gini':sum(ev.gini(x) for x in costs)/n,'paired_costs':costs}
result={'scope':'Development-exposed comparison; no independent confirmation or novelty claim','source_sampling_sha256':hashlib.sha256(Path('output/multibook_raw_evaluation.json').read_bytes()).hexdigest(),'arms':{},'existing_books_summary':json.loads(Path('output/multibook_analysis.json').read_text())['aggregate']}
for name in ['pair_minmax','pair_pooled']:
    tok,merges,vocab=ev.tokenizer(Path('output')/(name+'.merges'));assert len(merges)==1000 and len(vocab)==1256
    books={}
    for work,d in data['sampling'].items():
        books[work]=stats([[len(tok.encode(t).ids) for t in row['text']] for row in d['rows']])
    tico={}
    for split in ['tico.dev100','tico.confirm']:
        rows=json.loads(Path('inputs/'+split+'.json').read_text())
        tico[split]=stats([[len(tok.encode(row[l]).ids) for l in ['en','fr']] for row in rows])
        for row in rows[:2]:
            for l in ['en','fr']:assert tok.encode(row[l]).tokens==ev.replay(row[l],merges)
    aggregate={'mean_book_gini':sum(b['gini'] for b in books.values())/len(books),'mean_book_worst':sum(b['worst_cost'] for b in books.values())/len(books),'mean_book_total':sum(b['sum_language_means'] for b in books.values())/len(books)}
    contrasts={}
    for base in ['classical','pooled','robust_domain']:
        contrasts[base]={k:{'mean_delta':sum(books[w][k]-data['arms'][base][w][k] for w in books)/len(books),'better_books':sum(books[w][k]<data['arms'][base][w][k] for w in books),'worse_books':sum(books[w][k]>data['arms'][base][w][k] for w in books)} for k in ['gini','worst_cost','sum_language_means']}
    result['arms'][name]={'books':books,'tico':tico,'aggregate':aggregate,'contrasts':contrasts,'training':json.loads(Path('output/'+name+'.trace.json').read_text())['summary']}
result['old_tico_results']=old['arms']
Path('output/pair_candidate_evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
compact={a:{'aggregate':d['aggregate'],'contrasts':d['contrasts'],'training':d['training'],'tico':{s:{k:v for k,v in values.items() if k!='paired_costs'} for s,values in d['tico'].items()}} for a,d in result['arms'].items()}
Path('output/pair_candidate_summary.json').write_text(json.dumps(compact,indent=2)+'\n');print(json.dumps(compact))
