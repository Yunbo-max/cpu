import importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
import numpy as np

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

native=load('native_pa','scripts/native_pa_source.py')
ev=load('verified_eval','scripts/evaluator_reference.py')
native.pre_tokenizer=ev.pre
files=['dev2.tico.en','dev2.tico.fr','dev2.books.en','dev2.books.fr']
initial=defaultdict(lambda:np.zeros(4,dtype=np.int64))
for j,name in enumerate(files):
    with open('inputs/'+name) as f:c=native.get_vocabulary(f,num_workers=1)
    for token,freq in c.items():initial[tuple(token)][j]+=freq

def objectives(lengths):
    a=lengths.reshape(2,2).astype(float)
    gin=np.abs(a[:,0]-a[:,1])/(2*a.sum(axis=1))
    relative=a/a.mean(axis=1,keepdims=True)
    d,l=np.unravel_index(np.argmax(relative),relative.shape)
    return gin,float(gin.max()),int(d),int(l)

output={'scope':'Retrospective deterministic replay of frozen trajectories, not retraining or causal proof of OOD failure','arms':{}}
for name in ['classical','pooled','robust_domain']:
    vocab={k:v.copy() for k,v in initial.items()}
    lengths=sum((len(k)*v for k,v in vocab.items()),np.zeros(4,dtype=np.int64))
    tok,merges,_=ev.tokenizer(Path('inputs/models')/(name+'.merges'))
    trajectory=[]
    for i,pair in enumerate(merges):
        before=lengths.copy();gin,oldmax,d,l=objectives(before)
        change=native.replace_pair_dict(pair,vocab)
        gains=np.asarray(change) if not np.isscalar(change) else np.zeros(4,dtype=np.int64)
        lengths-=gains
        newgin,newmax,_,_=objectives(lengths)
        assert np.all(gains>=0) and np.all(lengths>0)
        trajectory.append({'step':i,'pair':pair,'before':before.tolist(),'gains':gains.tolist(),'after':lengths.tolist(),'worst_domain_before':d,'costly_language_before':l,'target_gain':int(gains[2*d+l]),'max_gini_before':oldmax,'max_gini_after':newmax,'delta_max_gini':newmax-oldmax,'selected_domain_delta_gini':float(newgin[d]-gin[d])})
    independent=[sum(len(tok.encode(line).ids) for line in Path('inputs/'+f).read_text().splitlines()) for f in files]
    assert independent==lengths.tolist(),(name,independent,lengths.tolist())
    summary={'steps':len(merges),'initial_costs':trajectory[0]['before'],'final_costs':lengths.tolist(),'final_tokenizer_totals_agree':True,'increase_max_gini':sum(t['delta_max_gini']>1e-12 for t in trajectory),'decrease_max_gini':sum(t['delta_max_gini']<-1e-12 for t in trajectory),'unchanged_max_gini':sum(abs(t['delta_max_gini'])<=1e-12 for t in trajectory),'zero_worst_slice_gain':sum(t['target_gain']==0 for t in trajectory),'selected_domain_gini_increase':sum(t['selected_domain_delta_gini']>1e-12 for t in trajectory),'final_max_domain_gini':trajectory[-1]['max_gini_after'],'target_label':'actual selection rule for robust_domain; hypothetical diagnostic target for controls'}
    output['arms'][name]={'summary':summary,'trajectory':trajectory}
Path('output/merge_descent_audit.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({n:a['summary'] for n,a in output['arms'].items()}))
