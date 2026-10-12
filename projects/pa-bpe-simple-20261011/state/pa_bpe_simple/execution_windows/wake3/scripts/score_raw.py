import csv, gzip, hashlib, importlib.util, json, math, random, sys
import xml.etree.ElementTree as ET
from pathlib import Path

spec=importlib.util.spec_from_file_location('verified_eval',Path('scripts/evaluator_reference.py'))
ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
LANGS=('en','fr')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def gini(x):
    assert len(x)>0 and all(v>=0 and math.isfinite(v) for v in x) and sum(x)>0
    n=len(x); ordered=sorted(x)
    v=sum((2*i-n-1)*a for i,a in enumerate(ordered,1))/(n*sum(ordered))
    assert abs(v-ev.gini(x))<1e-12
    return v

def stats(costs):
    n=len(costs);assert n>0
    means=[sum(c[i] for c in costs)/n for i in range(2)]
    return {'n':n,'mean_tokens':means,'gini':gini(means),
            'worst_language':LANGS[means.index(max(means))],
            'worst_cost':max(means),'sum_language_means':sum(means),
            'mean_sentence_gini':sum(gini(c) for c in costs)/n}

def texts(lang,work):
    m=json.loads(Path(f'output/raw_{lang}_manifest.json').read_text())['members'][work]
    assert sha(m['path'])==m['sha256']
    root=ET.parse(m['path']).getroot()
    assert not any(e.tag.rsplit('}',1)[-1]=='w' for e in root.iter())
    result={}
    for e in root.iter():
        if e.tag.rsplit('}',1)[-1]=='s':
            key=e.attrib['id'];assert key not in result
            result[key]=' '.join(''.join(e.itertext()).split())
    return result

def models():
    result={}
    for p in sorted(Path('inputs/models').glob('*.merges')):
        tok,merges,vocab=ev.tokenizer(p)
        assert len(merges)==1000 and len(vocab)==1256
        result[p.stem]=(tok,merges)
    assert len(result)==9
    return result

def paired():
    old=json.loads(Path('inputs/old_evaluation.json').read_text())
    workmap={'dev':'Carroll_Lewis-Alice_in_wonderland','confirm':'Poe_Edgar_Allan-Fall_of_the_House_of_Usher'}
    data={};summary={}
    for split,work in workmap.items():
        mapping={l:texts(l,work) for l in LANGS}
        with Path(f'inputs/{split}.tsv').open() as f:
            rows=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
        assert len({(r['en_id'],r['fr_id']) for r in rows})==len(rows)
        raw=[[mapping[l][r[l+'_id']] for l in LANGS] for r in rows]
        assert all(all(t for t in pair) for pair in raw)
        data[split]=(rows,raw)
        summary[split]={'work':work,'n':len(rows),'changed_texts':{l:sum(r[l]!=new[j] for r,new in zip(rows,raw)) for j,l in enumerate(LANGS)},'row_ids':[[r['en_id'],r['fr_id']] for r in rows]}
    output={'scope':'Same-ID raw versus annotation-derived text measurement repair; both works previously exposed','plan_sha256':sha('plan_wake3.json'),'datasets':summary,'arms':{}}
    for name,(tok,merges) in models().items():
        arm={}
        for split,(rows,raw) in data.items():
            costs=[[len(tok.encode(t).ids) for t in pair] for pair in raw]
            old_costs=[[len(tok.encode(r[l]).ids) for l in LANGS] for r in rows]
            assert old_costs==old['arms'][name]['datasets'][split]['paired_costs']
            for pair in raw[:3]:
                for text in pair: assert tok.encode(text).tokens==ev.replay(text,merges)
            a,b=stats(old_costs),stats(costs)
            arm[split]={'annotated':a,'raw':b,'raw_paired_costs':costs,'changed_cost_pairs':sum(x!=y for x,y in zip(old_costs,costs)),'gini_change':b['gini']-a['gini']}
        output['arms'][name]=arm
    Path('output/paired_raw_rescore.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({a:{s:{k:v[k] for k in ['annotated','raw','changed_cost_pairs']} for s,v in d.items()} for a,d in output['arms'].items()}))

def units():
    excluded={'Carroll_Lewis-Alice_in_wonderland','Poe_Edgar_Allan-Fall_of_the_House_of_Usher'}
    works=set(json.loads(Path('output/raw_en_manifest.json').read_text())['members'])-excluded
    source=ET.parse(gzip.open('inputs/en-fr.xml.gz','rb')).getroot()
    found={}
    for group in source.iter('linkGrp'):
        work=Path(group.attrib['fromDoc']).name.removesuffix('.gz').removesuffix('.xml')
        if work not in works:continue
        assert work==Path(group.attrib['toDoc']).name.removesuffix('.gz').removesuffix('.xml')
        assert work not in found
        mapping={l:texts(l,work) for l in LANGS};rows=[];excluded_empty=0;missing=[]
        for ordinal,link in enumerate(group.iter('link')):
            sides=link.attrib.get('xtargets','').split(';')
            assert len(sides)==2
            ids=[s.split() for s in sides]
            if not all(ids):excluded_empty+=1;continue
            if any(i not in mapping[l] for l,is_ in zip(LANGS,ids) for i in is_):missing.append(ids);continue
            pair=[' '.join(mapping[l][i] for i in is_).strip() for l,is_ in zip(LANGS,ids)]
            if not all(pair):excluded_empty+=1;continue
            key=f'pa-bpe-w3-v1|{work}|{ordinal}|{sides[0]}|{sides[1]}'
            rows.append({'ids':ids,'ordinal':ordinal,'text':pair,'sample_key':hashlib.sha256(key.encode()).hexdigest()})
        assert not missing,(work,missing[:3])
        selected=sorted(rows,key=lambda x:x['sample_key'])[:512]
        found[work]={'eligible':len(rows),'empty_links':excluded_empty,'missing_ids':len(missing),'sampled':len(selected),'rows':selected}
    assert set(found)==works,(set(found)^works)
    return found

def multi():
    data=units();output={'scope':'Frozen-model exploratory native raw-text generalization; 10 works, <=512 XCES units each; not pristine confirmation','plan_sha256':sha('plan_wake3.json'),'sampling':data,'arms':{}}
    for name,(tok,merges) in models().items():
        results={}
        for work,d in data.items():
            costs=[[len(tok.encode(t).ids) for t in r['text']] for r in d['rows']]
            assert all(all(n>0 for n in c) for c in costs)
            results[work]={**stats(costs),'paired_costs':costs}
        output['arms'][name]=results
    Path('output/multibook_raw_evaluation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    aggregate={}
    for name,books in output['arms'].items():
        means=[sum(d['mean_tokens'][i] for d in books.values())/len(books) for i in range(2)]
        aggregate[name]={'books':len(books),'rows':sum(d['n'] for d in books.values()),'mean_book_gini':sum(d['gini'] for d in books.values())/len(books),'gini_work_macro_language_means':gini(means),'work_macro_mean_tokens':means,'mean_book_worst':sum(d['worst_cost'] for d in books.values())/len(books),'mean_book_total':sum(d['sum_language_means'] for d in books.values())/len(books)}
    names=list(output['arms']);base=next(n for n in names if n.lower()=='classical');candidate=next(n for n in names if n.lower()=='robust_domain')
    contrasts={w:{k:output['arms'][candidate][w][k]-output['arms'][base][w][k] for k in ['gini','worst_cost','sum_language_means']} for w in data}
    rng=random.Random(20261011);values=list(contrasts.values());bootstrap={}
    for key in ['gini','worst_cost','sum_language_means']:
        samples=sorted(sum(rng.choice(values)[key] for _ in values)/len(values) for _ in range(5000))
        bootstrap[key]={'mean_difference':sum(v[key] for v in values)/len(values),'percentile95_sensitivity_interval':[samples[124],samples[4874]],'negative_books':sum(v[key]<0 for v in values),'positive_books':sum(v[key]>0 for v in values)}
    analysis={'aggregate':aggregate,'primary_candidate':candidate,'primary_baseline':base,'paired_work_contrasts':contrasts,'bootstrap':bootstrap,'uncertainty_scope':'Paired resampling of 10 observed books; repeated authors and incomplete exposure mapping prevent population-calibrated or pristine-confirmation interpretation. Other arm contrasts are descriptive.'}
    Path('output/multibook_analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    print(json.dumps(analysis))

assert gini([1,1])==0 and abs(gini([0,2])-.5)<1e-12
if sys.argv[1]=='paired':paired()
elif sys.argv[1]=='multi':multi()
else:raise ValueError(sys.argv[1])
