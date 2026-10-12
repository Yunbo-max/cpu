import heapq,importlib.util,json,sys,time
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
import numpy as np

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=load('native_pa','scripts/native_pa_source.py')
ev=load('verified_eval','scripts/evaluator_reference.py');native.pre_tokenizer=ev.pre
mode='minmax';steps=1000;prefix='fallback_audit'
assert mode in ['minmax','pooled'] and steps in [100,1000]
trainfiles=['train.en','train.fr'];devfiles=['dev2.tico.en','dev2.tico.fr','dev2.books.en','dev2.books.fr']

def vocabulary(files):
    v=defaultdict(lambda:np.zeros(len(files),dtype=np.int64))
    for j,name in enumerate(files):
        with open('inputs/'+name) as f: counts=native.get_vocabulary(f,num_workers=1)
        for token,count in counts.items():v[tuple(token)][j]+=count
    return sorted(v.items(),key=lambda x:(int(sum(x[1])),x[0]),reverse=True)

train=vocabulary(trainfiles);dev=vocabulary(devfiles)
ts,ti=native.get_pair_statistics(train);ds,di=native.get_pair_statistics(dev)
lengths=sum((len(w)*f for w,f in dev),np.zeros(4,dtype=np.int64))
produced=set(ev.ByteLevel.alphabet());trace=[];merges=[]

def objective(cost):
    v=cost.reshape(2,2).astype(float)
    if mode=='pooled':v=v.sum(axis=0,keepdims=True)
    return float((np.abs(v[:,0]-v[:,1])/(2*v.sum(axis=1))).max())

def gains(pair):
    if pair[0]!=pair[1]:return np.asarray(ds.get(pair,np.zeros(4,dtype=np.int64))).copy()
    total=np.zeros(4,dtype=np.int64)
    for idx,n in di.get(pair,{}).items():
        if n<1:continue
        word,freq=dev[idx];i=0;count=0
        while i<len(word)-1:
            if word[i]==pair[0] and word[i+1]==pair[1]:count+=1;i+=2
            else:i+=1
        total+=count*freq
    return total


record=json.loads(Path('output/pair_minmax.trace.json').read_text())['trajectory']
selected=set(json.loads(Path('fallback_audit_plan.json').read_text())['selected_steps']);results=[]
for t in record:
    step=t['step'];pair=tuple(t['pair'])
    if step in selected:
        eligible=[p for p,f in ts.items() if int(sum(f))>=2 and ''.join(p) not in produced]
        before=objective(lengths);descent=[]
        for alt in eligible:
            gain=gains(alt);after=objective(lengths-gain)
            if after<before-1e-12:descent.append((after,-int(sum(ts[alt])),alt,gain))
        best=min(descent,key=lambda x:(x[0],x[1],x[2])) if descent else None
        row={'step':step,'eligible_pairs':len(eligible),'descending_pairs':len(descent),'before':before,'actual_fallback_after':t['after']}
        if best:
            after,_,alt,gain=best
            direct=np.zeros(4,dtype=np.int64)
            for word,freq in dev:
                i=0;n=0
                while i<len(word)-1:
                    if (word[i],word[i+1])==alt:n+=1;i+=2
                    else:i+=1
                direct+=n*freq
            assert np.array_equal(gain,direct)
            row.update(best_pair=alt,best_after=after,best_gain=gain.tolist(),direct_scan_matches=True)
        results.append(row)
    gain=gains(pair)
    tc=native.replace_pair(pair,train,ti);native.update_pair_statistics(pair,tc,ts,ti);ts[pair]=np.zeros(2,dtype=np.int64)
    dc=native.replace_pair(pair,dev,di);native.update_pair_statistics(pair,dc,ds,di);ds[pair]=np.zeros(4,dtype=np.int64)
    lengths-=gain;produced.add(''.join(pair))
    assert lengths.tolist()==t['lengths']
summary={'sampled_fallback_states':len(results),'states_with_missed_descent':sum(r['descending_pairs']>0 for r in results),'trajectory_all_costs_match':True,'counterfactuals':results,'scope':'fixed exposed development trajectory; full-eligible one-step alternatives only, not retrained or held-out improvement'}
Path('output/fallback_pool_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
