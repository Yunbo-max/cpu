"""Bounded frozen-parameter CPU diagnostic, not model training or novelty proof.
Compares permutation-prefix gradient with its deterministic mean-equivalent mixture.
Uses unchanged definitions extracted from the already audited local harness.
"""
import ast,hashlib,itertools,json,time
from pathlib import Path
import torch
start=time.time();torch.set_num_threads(1)
root=Path(__file__).parent
src=root/'fresh_native_cpu_audit.py';raw=src.read_bytes()
expected='ff3fa89cef4b27f0ee7001b7c9c2ca71447e681b6ce243f23daa5102d78dce6a'
assert hashlib.sha256(raw).hexdigest()==expected
# Avoid executing the earlier audit again: retain only imports and definitions,
# source-blob verification and namespace initialization before its test runner.
tree=ast.parse(raw.decode());cut=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='start' for t in n.targets))
ns={'__file__':str(src)};exec(compile(ast.Module(body=tree.body[:cut],type_ignores=[]),str(src),'exec'),ns)
lr=1e-3;eps=1e-8;betas=(.9,.999)
def update(g,kind):
    p=torch.nn.Parameter(torch.zeros_like(g));p.grad=g.clone()
    opt=torch.optim.Adam([p],lr=lr,betas=betas,eps=eps) if kind=='adam' else torch.optim.SGD([p],lr=lr)
    opt.step()
    return p.detach().clone()
rows=[]
for seed in [101,102,103]:
    gen=torch.Generator().manual_seed(seed)
    W=torch.randn(3,2,generator=gen);batches=[torch.randn(3,2,generator=gen) for _ in range(4)]
    orders=list(itertools.permutations(range(4)))
    prefix=torch.stack([ns['native_gradient'](W,batches,o)[0] for o in orders])
    gg,_=ns['independent'](W,batches,orders[0],'global');gm,_=ns['independent'](W,batches,orders[0],'micro')
    lam=(sum(1/j for j in range(1,5))-1)/3;mix=(1-lam)*gg+lam*gm
    mean=prefix.mean(0);torch.testing.assert_close(mean,mix,atol=2e-7,rtol=2e-5)
    adam=torch.stack([update(g,'adam') for g in prefix]);adam_mix=update(mix,'adam')
    sgd=torch.stack([update(g,'sgd') for g in prefix]);sgd_mix=update(mix,'sgd')
    delta=adam.mean(0)-adam_mix;sgd_delta=sgd.mean(0)-sgd_mix
    sgd_error=float(sgd_delta.abs().max());assert sgd_error<1e-9
    # Population covariance of finite uniform permutation distribution (divide by24).
    flat=prefix.flatten(1);centered=flat-flat.mean(0);cov=centered.T@centered/len(orders)
    maxdelta=float(delta.abs().max())
    rows.append({'seed':seed,'orders':[list(o) for o in orders],
      'prefix_gradients':prefix.tolist(),'global_gradient':gg.tolist(),'micro_gradient':gm.tolist(),
      'explicit_mixture_gradient':mix.tolist(),'mean_prefix_gradient':mean.tolist(),
      'mean_gradient_max_abs_error':float((mean-mix).abs().max()),
      'prefix_gradient_population_covariance':cov.tolist(),'covariance_trace':float(cov.trace()),
      'adam_prefix_updates':adam.tolist(),'adam_mixture_update':adam_mix.tolist(),
      'mean_adam_prefix_update':adam.mean(0).tolist(),'adam_mean_minus_mixture':delta.tolist(),
      'adam_mean_difference_max_abs':maxdelta,'adam_mean_difference_l2':float(delta.norm()),
      'sgd_prefix_updates':sgd.tolist(),'sgd_mixture_update':sgd_mix.tolist(),
      'sgd_mean_difference_max_abs':sgd_error,
      'verdict':'different expected Adam update on this fixture' if maxdelta>1e-7 else 'not distinguished at prespecified 1e-7 update tolerance'})
result={'scope':'one optimizer update from identical zero moments, fixed routing parameters; no main task loss, no model training, no validation benefit claim',
 'source_harness_sha256':expected,'source_commit':'72d23540d0358ae24a41ff289d1461b094a770fa',
 'torch':torch.__version__,'threads':torch.get_num_threads(),'optimizer':{'lr':lr,'eps':eps,'betas':betas,'initial_m':0,'initial_v':0,'weight_decay':0,'step':1},
 'G':4,'lambda':lam,'seeds':[101,102,103],'total_permutations':72,
 'falsifier':'Mean-gradient mismatch > tolerance invalidates equivalence; SGD mismatch >=1e-9 indicates scaling/state issue; Adam difference <=1e-7 does not support distinction on that fixture.',
 'elapsed_seconds':time.time()-start,'rows':rows}
(root/'supervisor_adam_probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
print(json.dumps([{k:r[k] for k in ['seed','mean_gradient_max_abs_error','covariance_trace','adam_mean_difference_max_abs','adam_mean_difference_l2','sgd_mean_difference_max_abs','verdict']} for r in rows],indent=2))
