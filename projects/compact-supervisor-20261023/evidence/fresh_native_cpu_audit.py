"""Execute unchanged AST-extracted Megatron functions on CPU, single-rank stubs.
Not a full TopKRouter/CUDA/distributed model test.
"""
import ast,hashlib,itertools,json,math,platform,time,types
from pathlib import Path
import torch

torch.set_num_threads(1)
ROOT=Path(__file__).parent
SOURCE_BLOBS={'evidence/megatron_router_72d2354.py':'8cb8936a785d4d02ed6e240a61912d3aa2b29cbf',
              'evidence/megatron_moe_utils_72d2354.py':'739283ee8b72cce835f94d6109e76169edfa0112'}
for name,expected in SOURCE_BLOBS.items():
    raw=(ROOT/name).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==expected
ns={'torch':torch,'HAVE_TE':False,'fused_moe_aux_loss':None,
    'fused_compute_score_for_moe_aux_loss':None,
    'reduce_from_tensor_model_parallel_region':lambda x,group:x}
logs=[]
ns['save_to_aux_losses_tracker']=lambda name,loss,*args,**kwargs:logs.append(float(loss.detach()))
extracted=[]
def extract(path,names,cls=None):
    raw=path.read_text();tree=ast.parse(raw)
    nodes=tree.body if cls is None else next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls).body
    for name in names:
        node=next(n for n in nodes if getattr(n,'name',None)==name)
        src=ast.get_source_segment(raw,node)
        extracted.append({'source':str(path.relative_to(ROOT)),'name':name,'start':node.lineno,'end':node.end_lineno,'sha256':hashlib.sha256(src.encode()).hexdigest()})
        # AST compilation retains exact source statements; no function body rewriting.
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
extract(ROOT/'evidence/megatron_moe_utils_72d2354.py',[
    'switch_load_balancing_loss_func','compute_routing_scores_for_aux_loss','MoEAuxLossAutoScaler'])
extract(ROOT/'evidence/megatron_router_72d2354.py',[
    '_apply_global_aux_loss','attach_and_log_load_balancing_loss','reset_global_aux_loss_tracker'],cls='TopKRouter')
class Group:
    def size(self):return 1

def make_router(K,token_scale=False):
    r=types.SimpleNamespace(topk=1,tp_dp_cp_group=Group(),
        global_tokens_per_expert=torch.zeros(K),ga_steps=torch.tensor(0.),
        config=types.SimpleNamespace(num_moe_experts=K,moe_router_fusion=False,num_layers=1,mtp_num_layers=None),
        layer_number=1,calculate_per_token_loss=token_scale,get_aux_loss_coeff=lambda x:1.)
    for name in ['_apply_global_aux_loss','attach_and_log_load_balancing_loss','reset_global_aux_loss_tracker']:
        setattr(r,name,types.MethodType(ns[name],r))
    return r

def native_gradient(W0,batches,order,token_scale=False,router=None):
    G=len(batches);W=W0.clone().requires_grad_();r=router or make_router(W.shape[0],token_scale)
    r.reset_global_aux_loss_tracker();assert r.ga_steps.item()==0 and r.global_tokens_per_expert.sum()==0
    logs.clear()
    # This replaces pipeline loss scaling explicitly. The native custom backward
    # does not obtain its aux scale from multiplying the dummy main loss by 1/G.
    ns['MoEAuxLossAutoScaler'].set_loss_scale(torch.tensor(1. if token_scale else 1./G))
    for i in order:
        logits=batches[i]@W.T
        routes,scores=ns['compute_routing_scores_for_aux_loss'](logits,1,'softmax',False)
        out=r._apply_global_aux_loss(scores,scores,routes)
        (out.sum()*0).backward()
    grad=W.grad.clone()
    if token_scale:
        # Source schedule uses scale 1; finalize divides total global token count.
        # Single rank and equal-sized batches only; finalize itself is not executed.
        grad/=G*len(batches[0])
    return grad,logs.copy(),r

def independent(W0,batches,order,mode):
    W=W0.clone().requires_grad_();G=len(batches);K=W.shape[0]
    ps=[torch.softmax(x@W.T,dim=-1) for x in batches]
    fs=[torch.nn.functional.one_hot(p.argmax(-1),K).float().mean(0).detach() for p in ps]
    qs=[p.mean(0) for p in ps]
    coeff=torch.zeros(K);terms=[]
    for j,i in enumerate(order):
        coeff+=fs[i]
        a=coeff/(j+1) if mode=='prefix' else (fs[i] if mode=='micro' else torch.stack(fs).mean(0))
        terms.append(K*(a*qs[i]).sum()/G)
    loss=sum(terms)
    return torch.autograd.grad(loss,W)[0],float(loss.detach())

def native_control(W0,batches,order,mode):
    """New estimator coefficients passed through unchanged native helper/backward."""
    W=W0.clone().requires_grad_();G=len(batches);K=W.shape[0]
    r=make_router(K);past=torch.zeros(K)
    ns['MoEAuxLossAutoScaler'].set_loss_scale(torch.tensor(1./G))
    for j,i in enumerate(order):
        routes,scores=ns['compute_routing_scores_for_aux_loss'](batches[i]@W.T,1,'softmax',False)
        n=len(batches[i]);f=routes.float().mean(0)
        if mode=='positive':a=f/G+(past/j if j else 0)
        elif mode=='pair_ht':a=(f+2*past)/G
        else:raise ValueError(mode)
        loss=ns['switch_load_balancing_loss_func'](scores,a*n,n,1,K,1.,False)
        out=r.attach_and_log_load_balancing_loss(scores,1.,loss,'control',r.tp_dp_cp_group)
        (out.sum()*0).backward()
        past+=f
    return W.grad.clone()

start=time.time();receipts=[]
cases=[('binary',torch.tensor([[math.log(4.)],[0.]]),[torch.tensor([[1.]]),torch.tensor([[-1.]])])]
for seed in [101,102,103]:
    gen=torch.Generator().manual_seed(seed)
    cases.append(('three_expert_'+str(seed),torch.randn(3,2,generator=gen),[torch.randn(3,2,generator=gen) for _ in range(4)]))
for name,W,batches in cases:
    G=len(batches);orders=list(itertools.permutations(range(G)))
    grads=[];maxerr=0.;maxloss=0.;tokenerr=0.
    controls={m:[] for m in ['positive','pair_ht']}
    for order in orders:
        got,losses,r=native_gradient(W,batches,order)
        ref,loss=independent(W,batches,order,'prefix')
        err=float((got-ref).abs().max());maxerr=max(maxerr,err)
        maxloss=max(maxloss,abs(sum(losses)/G-loss))
        torch.testing.assert_close(got,ref,atol=2e-7,rtol=2e-5)
        scaled,_,_=native_gradient(W,batches,order,True)
        tokenerr=max(tokenerr,float((got-scaled).abs().max()))
        torch.testing.assert_close(scaled,got,atol=2e-7,rtol=2e-5)
        again,_,_=native_gradient(W,batches,order,router=r)
        torch.testing.assert_close(again,got,atol=0,rtol=0)
        grads.append(got)
        for mode in controls:controls[mode].append(native_control(W,batches,order,mode))
    gg,_=independent(W,batches,orders[0],'global');gm,_=independent(W,batches,orders[0],'micro')
    lam=(sum(1/j for j in range(1,G+1))-1)/(G-1)
    mean=torch.stack(grads).mean(0);pred=(1-lam)*gg+lam*gm
    torch.testing.assert_close(mean,pred,atol=2e-7,rtol=2e-5)
    assert maxloss<3e-7
    for mode,values in controls.items():
        torch.testing.assert_close(torch.stack(values).mean(0),gg,atol=2e-7,rtol=2e-5)
    reverse_error=0.
    for idx,order in enumerate(orders):
        rev=orders.index(tuple(reversed(order)))
        paired=(controls['pair_ht'][idx]+controls['pair_ht'][rev])/2
        reverse_error=max(reverse_error,float((paired-gg).abs().max()))
        torch.testing.assert_close(paired,gg,atol=2e-7,rtol=2e-5)
    receipts.append({'name':name,'G':G,'permutations':len(orders),'lambda':lam,
      'native_vs_reference_max_abs_gradient_error':maxerr,'loss_max_abs_error':maxloss,
      'per_token_scaling_max_abs_error':tokenerr,'mean_vs_identity_max_abs_error':float((mean-pred).abs().max()),
      'prefix_coordinate_range_max':float((torch.stack(grads).max(0).values-torch.stack(grads).min(0).values).max()),
      'ht_reverse_pair_max_abs_error':reverse_error,
      'control_mean_max_abs_error':{m:float((torch.stack(v).mean(0)-gg).abs().max()) for m,v in controls.items()},
      'global_gradient':gg.tolist(),'native_mean_gradient':mean.tolist(),'reset_repeat_exact':True})
print(json.dumps({'scope':'unchanged extracted CPU functions with identity single-rank reduction and stub logging; manual pipeline scaling; no full CUDA router',
  'torch':torch.__version__,'python':platform.python_version(),'elapsed_seconds':time.time()-start,
  'source_commit':'72d23540d0358ae24a41ff289d1461b094a770fa','verified_source_blobs':SOURCE_BLOBS,'extracted':extracted,'receipts':receipts},indent=2))
