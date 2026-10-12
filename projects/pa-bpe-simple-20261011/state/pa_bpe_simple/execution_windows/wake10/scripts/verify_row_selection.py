import copy
import ast
import hashlib
import io
import json
import random
import sys
import warnings
from collections import Counter
from pathlib import Path

MIN_HEADROOM = 384 * 1024 * 1024

def memory_headroom():
    current = int(Path('/sys/fs/cgroup/memory.current').read_text().strip())
    maximum = int(Path('/sys/fs/cgroup/memory.max').read_text().strip())
    return current, maximum, maximum-current

cur, mx, head = memory_headroom()
if head < MIN_HEADROOM:
    raise SystemExit(f'memory safety gate: {head} bytes headroom < {MIN_HEADROOM}')

import tokenizers
from tokenizers import pre_tokenizers

PRE = pre_tokenizers.Sequence([
    pre_tokenizers.Whitespace(),
    pre_tokenizers.ByteLevel(use_regex=False),
])
LANG_TAGS = {'en': {'en'}, 'fr': {'fr','fra'}, 'es': {'es','spa'}}
INPUTS = {'en': Path('inputs/en_probe.json'), 'fr': Path('inputs/fr_probe.json'), 'es': Path('inputs/es_probe.json')}
AUTHOR_SOURCES = {
    'classical': Path('inputs/learn_bpe.py'),
    'pa_bpe': Path('inputs/parity_aware_learn_bpe.py'),
}

def unwrap(path):
    doc=json.loads(path.read_text())
    return [x['row'] for x in doc['rows']]

def rank(lang, stable_id):
    return hashlib.sha256(('pa-bpe-train-v1\0'+lang+'\0'+stable_id).encode('utf-8')).digest()

def pretokens(text):
    return [piece for piece, _ in PRE.pre_tokenize_str(text)]

def eligible(lang, rows, fail_missing=True):
    ids=[]
    for r in rows:
        if not isinstance(r.get('id'),str) or not r['id']:
            if fail_missing: raise ValueError('missing stable id')
            continue
        ids.append(r['id'])
    duplicates={k for k,v in Counter(ids).items() if v>1}
    accepted=[]; rejected=Counter()
    for r in rows:
        sid=r.get('id')
        if not isinstance(sid,str) or not sid:
            rejected['missing_id']+=1; continue
        if sid in duplicates:
            rejected['duplicate_id_all_copies']+=1; continue
        text=r.get('text')
        if not isinstance(text,str) or not text:
            rejected['empty_text']+=1; continue
        if r.get('dump')!='CC-MAIN-2013-20':
            rejected['wrong_dump']+=1; continue
        if r.get('language') not in LANG_TAGS[lang]:
            rejected['wrong_language']+=1; continue
        if lang in {'fr','es'} and r.get('language_script')!='Latn':
            rejected['wrong_script']+=1; continue
        accepted.append(r)
    return sorted(accepted,key=lambda r:(rank(lang,r['id']),r['id'].encode('utf-8'))),dict(rejected)

def author_get_vocabulary(path):
    tree=ast.parse(path.read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='get_vocabulary')
    ns={'Counter':Counter,'sys':sys,'warnings':warnings}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    return ns['get_vocabulary']

def serialize_dictionary(counts):
    unsafe=[piece for piece in counts if any(ch in piece for ch in (' ','\r','\n'))]
    if unsafe: raise ValueError(f'{len(unsafe)} pretokens unsafe for author dict parser')
    return ''.join(f'{piece} {counts[piece]}\n' for piece in sorted(counts))

def select(lang, rows, budget):
    ordered,rejected=eligible(lang,rows)
    counts=Counter(); manifest=[]; remaining=budget
    for r in ordered:
        if remaining==0: break
        pieces=pretokens(r['text'])
        if not pieces:
            rejected['zero_pretokens'] = rejected.get('zero_pretokens',0)+1
            continue
        use=min(remaining,len(pieces))
        counts.update(pieces[:use])
        manifest.append({
            'id':r['id'],
            'rank_sha256':rank(lang,r['id']).hex(),
            'raw_text_sha256':hashlib.sha256(r['text'].encode('utf-8')).hexdigest(),
            'available_pretoken_count':len(pieces),
            'included_prefix_count':use,
            'source_file_path':r.get('file_path'),
            'source_dataset_shard_identity':'unavailable-in-probe; mandatory for formal selection'
        })
        remaining-=use
    if remaining:
        raise ValueError(f'insufficient probe pretokens for {lang}: missing {remaining}')
    dictionary=serialize_dictionary(counts)
    return {
        'language':lang,'budget':budget,'selected_rows':manifest,
        'selected_document_count':len(manifest),'unique_pretokens':len(counts),
        'dictionary_sha256':hashlib.sha256(dictionary.encode('utf-8')).hexdigest(),
        'dictionary':dictionary,
        'counter':dict(counts),
        'author_initial_symbol_mass':sum(len(piece)*count for piece,count in counts.items()),
        'rejections':rejected
    }

author_parsers={k:author_get_vocabulary(v) for k,v in AUTHOR_SOURCES.items()}
all_results={}; checks=[]
for lang,path in INPUTS.items():
    rows=unwrap(path)
    base=select(lang,rows,256)
    rev=select(lang,list(reversed(rows)),256)
    shuffled=list(rows); random.Random(20261012).shuffle(shuffled)
    shuf=select(lang,shuffled,256)
    invariant=(base==rev==shuf)
    checks.append({'language':lang,'check':'input_order_invariance','passed':invariant})
    if not invariant: raise AssertionError(f'order invariance failed: {lang}')

    dup=rows+[copy.deepcopy(rows[0])]
    accepted,rejections=eligible(lang,dup)
    dup_absent=all(r['id']!=rows[0]['id'] for r in accepted) and rejections.get('duplicate_id_all_copies')==2
    checks.append({'language':lang,'check':'all_copies_duplicate_rejection','passed':dup_absent})
    if not dup_absent: raise AssertionError(f'duplicate rejection failed: {lang}')

    missing=copy.deepcopy(rows); missing[0].pop('id',None)
    missing_raised=False
    try: eligible(lang,missing)
    except ValueError: missing_raised=True
    checks.append({'language':lang,'check':'missing_id_hard_failure','passed':missing_raised})
    if not missing_raised: raise AssertionError(f'missing ID did not fail: {lang}')

    exact=sum(x['included_prefix_count'] for x in base['selected_rows'])==256
    checks.append({'language':lang,'check':'exact_diagnostic_pretoken_budget','passed':exact,'observed':256})
    if not exact: raise AssertionError(f'exact budget failed: {lang}')
    counter_sum=sum(base['counter'].values())
    checks.append({'language':lang,'check':'serialized_counter_sum','passed':counter_sum==256,'observed':counter_sum})
    if counter_sum!=256: raise AssertionError(f'serialized counter mass failed: {lang}')
    for parser_name,parser in author_parsers.items():
        parsed=parser(io.StringIO(base['dictionary']),True,1)
        passed=dict(parsed)==base['counter']
        checks.append({'language':lang,'check':f'{parser_name}_author_parser_roundtrip','passed':passed})
        if not passed: raise AssertionError(f'{parser_name} parser roundtrip failed: {lang}')
    all_results[lang]=base

# Synthetic software-only fixture exercises multi-document boundary behavior; it is not research data.
synthetic=[]
for i,text in enumerate(['alpha beta','gamma delta epsilon','zeta eta theta iota']):
    synthetic.append({'id':f'<unit:{i}>','text':text,'dump':'CC-MAIN-2013-20','language':'en'})
ordered,_=eligible('en',synthetic)
first_n=len(pretokens(ordered[0]['text'])); second_n=len(pretokens(ordered[1]['text']))
synthetic_budget=first_n+max(1,second_n-1)
multi=select('en',synthetic,synthetic_budget)
multi_ok=len(multi['selected_rows'])==2 and multi['selected_rows'][0]['included_prefix_count']==first_n and 0<multi['selected_rows'][1]['included_prefix_count']<second_n
checks.append({'scope':'synthetic_software_unit','check':'multi_document_boundary_truncation','passed':multi_ok,'budget':synthetic_budget})
if not multi_ok: raise AssertionError('multi-document boundary test failed')

whitespace=synthetic+[{'id':'<unit:whitespace>','text':' \n\t ','dump':'CC-MAIN-2013-20','language':'en'}]
white_result=select('en',whitespace,synthetic_budget)
white_ok=white_result['rejections'].get('zero_pretokens')==1 and white_result['dictionary_sha256']==multi['dictionary_sha256']
checks.append({'scope':'synthetic_software_unit','check':'zero_pretoken_skip','passed':white_ok})
if not white_ok: raise AssertionError('zero-pretoken skip failed')

insufficient_failed=False
try: select('en',synthetic,10**6)
except ValueError: insufficient_failed=True
checks.append({'scope':'synthetic_software_unit','check':'insufficient_budget_hard_failure','passed':insufficient_failed})
if not insufficient_failed: raise AssertionError('insufficient budget did not fail')

pa_source=AUTHOR_SOURCES['pa_bpe'].read_text()
shared_dict_switch=(pa_source.count('get_vocabulary(f, is_dict, num_workers)')>=2)
checks.append({'scope':'fixed_author_source','check':'pa_bpe_shared_train_dev_dict_switch_detected','passed':shared_dict_switch})
if not shared_dict_switch: raise AssertionError('PA-BPE shared dict-input contract not detected')

for result in all_results.values():
    result.pop('dictionary')
    result.pop('counter')

result={
    'schema_version':1,
    'scope':'software/protocol diagnostic on already exposed first-row probes plus an explicitly synthetic boundary unit fixture; not formal training, benchmark, fairness evidence, or original-paper reproduction',
    'tokenizers_version':tokenizers.__version__,
    'pretokenizer':'Sequence([Whitespace(), ByteLevel(use_regex=False)])',
    'memory_at_start':{'current_bytes':cur,'max_bytes':mx,'headroom_bytes':head,'minimum_required_bytes':MIN_HEADROOM},
    'inputs':{k:{'path':str(v),'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'rows':len(unwrap(v))} for k,v in INPUTS.items()},
    'fixed_author_sources':{k:{'path':str(v),'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in AUTHOR_SOURCES.items()},
    'diagnostic_budget_per_language':256,
    'results':all_results,
    'checks':checks,
    'all_checks_passed':all(x['passed'] for x in checks),
    'formal_gates':{
        'decontamination':'HOLD','row_to_dataset_shard_provenance':'HOLD','payload_sampling':'HOLD','tokenizer_training':'HOLD','fairness_claims':'HOLD'
    }
}
Path('output/row_selection_verification_v2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'all_checks_passed':result['all_checks_passed'],'tokenizers_version':tokenizers.__version__,'languages':list(all_results),'formal_gate':'HOLD'},sort_keys=True))
