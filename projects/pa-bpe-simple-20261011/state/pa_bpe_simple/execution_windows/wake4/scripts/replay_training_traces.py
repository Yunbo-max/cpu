"""Explicit replay of every selected merge; does not rely on removable asserts."""
import importlib.util,json,sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
import numpy as np

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=load('native_pa','scripts/native_pa_source.py')
ev=load('verified_eval','scripts/evaluator_reference.py');native.pre_tokenizer=ev.pre
trainfiles=['train.en','train.fr'];devfiles=['dev2.tico.en','dev2.tico.fr','dev2.books.en','dev2.books.fr']

def fail(message):raise RuntimeError(message)
def vocabulary(files):
    v=defaultdict(lambda:np.zeros(len(files),dtype=np.int64))
    for j,name in enumerate(files):
        with open('inputs/'+name) as f:counts=native.get_vocabulary(f,num_workers=1)
        for token,count in counts.items():v[tuple(token)][j]+=count
    return sorted(v.items(),key=lambda x:(int(sum(x[1])),x[0]),reverse=True)
def exact_objective(cost,mode):
    c=[int(x) for x in cost]
    if mode=='pooled':return Fraction(abs((c[0]+c[2])-(c[1]+c[3])),2*sum(c))
    return max(Fraction(abs(c[0]-c[1]),2*(c[0]+c[1])),Fraction(abs(c[2]-c[3]),2*(c[2]+c[3])))

out={'arms':{},'verification':'All checks below are explicit RuntimeError conditions, not assert statements.'}
for arm in ['eff_minmax','eff_pooled','exact_train']:
    trace=json.loads(Path('output/'+arm+'.trace.json').read_text())
    rows=trace['trajectory'];summary=trace['summary'];mode=summary['mode']
    train=vocabulary(trainfiles);dev=vocabulary(devfiles)
    ts,ti=native.get_pair_statistics(train);ds,di=native.get_pair_statistics(dev)
    train_lengths=sum((len(w)*f for w,f in train),np.zeros(2,dtype=np.int64))
    dev_lengths=sum((len(w)*f for w,f in dev),np.zeros(4,dtype=np.int64))
    merges=[];positive_gaps=[]
    for step,row in enumerate(rows):
        if row['step']!=step:fail((arm,'step',step,row['step']))
        pair=tuple(row['pair']);before=exact_objective(dev_lengths,'pooled' if mode=='pooled' else 'minmax')
        if int(sum(ts.get(pair,np.zeros(2,dtype=np.int64))))<2:fail((arm,step,'ineligible'))
        tc=native.replace_pair(pair,train,ti)
        tg=sum(((len(old)-len(new))*freq for _,new,old,freq in tc),np.zeros(2,dtype=np.int64))
        native.update_pair_statistics(pair,tc,ts,ti);ts[pair]=np.zeros(2,dtype=np.int64)
        dc=native.replace_pair(pair,dev,di)
        dg=sum(((len(old)-len(new))*freq for _,new,old,freq in dc),np.zeros(4,dtype=np.int64))
        native.update_pair_statistics(pair,dc,ds,di);ds[pair]=np.zeros(4,dtype=np.int64)
        if tg.tolist()!=row['train_gains']:fail((arm,step,'train_gain',tg.tolist(),row['train_gains']))
        if dg.tolist()!=row['dev_gains']:fail((arm,step,'dev_gain',dg.tolist(),row['dev_gains']))
        train_lengths-=tg;dev_lengths-=dg
        if train_lengths.tolist()!=row['train_lengths']:fail((arm,step,'train_lengths'))
        if dev_lengths.tolist()!=row['dev_lengths']:fail((arm,step,'dev_lengths'))
        after=exact_objective(dev_lengths,'pooled' if mode=='pooled' else 'minmax')
        if abs(float(before)-row['before'])>1e-12 or abs(float(after)-row['after'])>1e-12:fail((arm,step,'objective'))
        if mode!='trainonly' and not row['fallback']:
            if not after<before:fail((arm,step,'non_descent_selected'))
            positive_gaps.append(before-after)
        merges.append(pair)
    merge_lines=[tuple(x.split(' ',1)) for x in Path('output/'+arm+'.merges').read_text().splitlines()[1:]]
    if merge_lines!=merges:fail((arm,'merge_file_trace_mismatch'))
    tok,actual_merges,vocab=ev.tokenizer(Path('output/'+arm+'.merges'))
    if actual_merges!=merges or len(vocab)!=1256:fail((arm,'tokenizer_structure'))
    ind_train=[sum(len(tok.encode(x).ids) for x in Path('inputs/'+f).read_text().splitlines()) for f in trainfiles]
    ind_dev=[sum(len(tok.encode(x).ids) for x in Path('inputs/'+f).read_text().splitlines()) for f in devfiles]
    if ind_train!=train_lengths.tolist() or ind_dev!=dev_lengths.tolist():fail((arm,'independent_totals'))
    if ind_train!=summary['final_train_costs'] or ind_dev!=summary['final_dev_costs']:fail((arm,'summary_totals'))
    out['arms'][arm]={'steps_replayed':len(rows),'all_selected_train_and_dev_gains_match':True,
      'all_trace_lengths_match':True,'merge_file_matches_trace':True,'independent_final_totals_match':True,
      'minimum_exact_positive_constrained_gap':float(min(positive_gaps)) if positive_gaps else None,
      'all_constrained_selected_steps_are_exact_rational_descents':all(x>0 for x in positive_gaps)}
Path('output/training_trace_replay.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
