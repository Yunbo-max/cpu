import heapq,importlib.util,json,sys,time
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
import numpy as np

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=load('native_pa','scripts/native_pa_source.py')
ev=load('verified_eval','scripts/evaluator_reference.py');native.pre_tokenizer=ev.pre
mode=sys.argv[1];steps=int(sys.argv[2]);prefix=sys.argv[3]
assert mode in ['minmax','pooled','trainonly'] and steps in [100,1000]
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
train_lengths=sum((len(w)*f for w,f in train),np.zeros(2,dtype=np.int64))
produced=set(ev.ByteLevel.alphabet());trace=[];merges=[]

def objective(cost):
    v=cost.reshape(2,2).astype(float)
    if mode=='pooled':v=v.sum(axis=0,keepdims=True)
    return float((np.abs(v[:,0]-v[:,1])/(2*v.sum(axis=1))).max())

def nonoverlap_gains(pair,vocab,pair_stats,pair_indices,width):
    if pair[0]!=pair[1]:
        return np.asarray(pair_stats.get(pair,np.zeros(width,dtype=np.int64))).copy()
    total=np.zeros(width,dtype=np.int64)
    for idx,n in pair_indices.get(pair,{}).items():
        if n<1:continue
        word,freq=vocab[idx];i=0;count=0
        while i<len(word)-1:
            if word[i]==pair[0] and word[i+1]==pair[1]:count+=1;i+=2
            else:i+=1
        total+=count*freq
    return total

def dev_gains(pair):return nonoverlap_gains(pair,dev,ds,di,4)
def compression_gains(pair):return nonoverlap_gains(pair,train,ts,ti,2)

for step in range(steps):
    eligible=[p for p,f in ts.items() if int(sum(f))>=2 and ''.join(p) not in produced]
    assert eligible
    pairs=sorted(eligible)
    train_gain_matrix=np.asarray([compression_gains(pair) for pair in pairs])
    train_totals=train_gain_matrix.sum(axis=1)
    assert np.all(train_gain_matrix>=0) and np.all(train_totals>0)
    before=objective(lengths)
    gain_matrix=np.asarray([dev_gains(pair) for pair in pairs])
    after_costs=lengths[None,:]-gain_matrix
    assert np.all(gain_matrix>=0) and np.all(after_costs>0)
    domains=after_costs.reshape(-1,2,2).astype(float)
    if mode=='pooled':domains=domains.sum(axis=1,keepdims=True)
    objectives=(np.abs(domains[:,:,0]-domains[:,:,1])/(2*domains.sum(axis=2))).max(axis=1)
    improving=np.flatnonzero(objectives<before-1e-12)
    if mode!='trainonly' and len(improving):
        # Lexicographic constraint: first require strict fairness descent, then
        # maximize exact realized training compression. Remaining ties prefer
        # lower objective and lexicographically larger pair.
        chosen=max(improving,key=lambda j:(int(train_totals[j]),-float(objectives[j]),pairs[j]))
        fallback=False
    else:
        # Exact-compression control/fallback. A train-only arm always follows it.
        chosen=max(range(len(pairs)),key=lambda j:(int(train_totals[j]),-float(objectives[j]),pairs[j]))
        fallback=True
    pair=pairs[chosen];gain=gain_matrix[chosen];train_gain=train_gain_matrix[chosen]
    pred=float(objectives[chosen])
    tchanges=native.replace_pair(pair,train,ti)
    actual_train=sum(((len(old)-len(new))*freq for _,new,old,freq in tchanges),np.zeros(2,dtype=np.int64))
    assert np.array_equal(actual_train,train_gain),(step,pair,actual_train.tolist(),train_gain.tolist())
    native.update_pair_statistics(pair,tchanges,ts,ti);ts[pair]=np.zeros(2,dtype=np.int64)
    dchanges=native.replace_pair(pair,dev,di)
    actual=sum(((len(old)-len(new))*freq for _,new,old,freq in dchanges),np.zeros(4,dtype=np.int64))
    assert np.array_equal(actual,gain),(step,pair,actual.tolist(),gain.tolist())
    native.update_pair_statistics(pair,dchanges,ds,di);ds[pair]=np.zeros(4,dtype=np.int64)
    lengths-=actual;train_lengths-=actual_train;assert abs(objective(lengths)-pred)<1e-12
    trace.append({'step':step,'pair':pair,'eligible_pairs':len(pairs),'fallback':fallback,
                  'before':before,'after':pred,'dev_gains':actual.tolist(),
                  'train_gains':actual_train.tolist(),'train_gain_total':int(actual_train.sum()),
                  'dev_lengths':lengths.tolist(),'train_lengths':train_lengths.tolist()})
    produced.add(''.join(pair));merges.append(pair)
    if (step+1)%100==0:print(json.dumps({'step':step+1,'mode':mode,'objective':pred}),flush=True)

out=Path('output')/(prefix+'.merges');out.write_text('#version: 0.2\n'+''.join(a+' '+b+'\n' for a,b in merges))
tok,_,vocab=ev.tokenizer(out);assert len(vocab)==256+steps
independent=[sum(len(tok.encode(line).ids) for line in Path('inputs/'+f).read_text().splitlines()) for f in devfiles]
independent_train=[sum(len(tok.encode(line).ids) for line in Path('inputs/'+f).read_text().splitlines()) for f in trainfiles]
assert independent==lengths.tolist(),(independent,lengths.tolist())
assert independent_train==train_lengths.tolist(),(independent_train,train_lengths.tolist())
summary={'mode':mode,'steps':steps,'vocab_size':len(vocab),
         'fallbacks':sum(t['fallback'] for t in trace),
         'strict_descent_steps':sum(t['after']<t['before']-1e-12 for t in trace),
         'increase_steps':sum(t['after']>t['before']+1e-12 for t in trace),
         'final_objective':objective(lengths),'final_dev_costs':lengths.tolist(),
         'final_train_costs':train_lengths.tolist(),
         'realized_train_compression':int(sum(t['train_gain_total'] for t in trace)),
         'predicted_dev_gains_all_equal_actual':True,
         'predicted_train_gains_all_equal_actual':True,
         'independent_final_totals_agree':True}
(Path('output')/(prefix+'.trace.json')).write_text(json.dumps({'summary':summary,'trajectory':trace},indent=2)+'\n')
print(json.dumps(summary))
