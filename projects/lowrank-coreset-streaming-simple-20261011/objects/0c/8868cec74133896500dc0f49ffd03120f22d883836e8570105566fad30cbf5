"""B15: exact-SVD versus attributed warm-start LOBPCG endpoint refresh."""
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"

import argparse
import hashlib
import json
import resource
import time
import warnings
from pathlib import Path

import numpy as np
from scipy.linalg import eigh
from scipy.sparse.linalg import LinearOperator, lobpcg

HERE = Path(__file__).resolve().parent
SOURCE = Path('/workspace/scratch/bb9f262965cf/b14_sources/b09/b09-rsi-20261010T1518/LANDMARK512_FD_RAW.npz')
INPUT_SHA256 = 'd0de6bb598161e85557321a309e9d720cb1c398b722140725e47d8365e3ec68a'
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def exact_opt_from_gram(G, t, k, energy):
    if t <= k:
        return 0.0
    vals = eigh(G[:t, :t], eigvals_only=True, subset_by_index=(t-k, t-1),
                driver='evr', check_finite=False, overwrite_a=False)
    return max(0.0, float(energy - np.maximum(vals, 0.0).sum()))


class CountedGram(LinearOperator):
    def __init__(self, gram):
        self.gram = gram
        self.columns = 0
        super().__init__(dtype=gram.dtype, shape=gram.shape)

    def _matvec(self, x):
        self.columns += 1
        return self.gram @ x

    def _matmat(self, X):
        self.columns += X.shape[1]
        return self.gram @ X


def exact_endpoint(Aprefix, k):
    U, _, right = np.linalg.svd(Aprefix, full_matrices=False)
    q = right[:min(k, len(Aprefix))].T.copy()
    return q, U[:, :min(k, len(Aprefix))].copy(), 0, False, 0.0, 0


def warm_endpoint(Aprefix, gram, k, prior_u):
    t = len(Aprefix)
    if t < 5*k:
        return exact_endpoint(Aprefix, k)
    X = np.zeros((t, k), dtype=np.float64)
    rows = min(prior_u.shape[0], t)
    X[:rows, :] = prior_u[:rows, :k]
    op = CountedGram(gram)
    caught = []
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')
        vals, U, residual_history = lobpcg(
            op, X, largest=True, tol=1e-8, maxiter=40,
            retResidualNormsHistory=True, restartControl=20)
        caught = [str(w.message) for w in ws]
    order = np.argsort(vals)[::-1]
    vals = np.asarray(vals)[order]
    U = np.asarray(U)[:, order]
    final_residual = float(np.max(np.asarray(residual_history[-1])))
    fallback = (not np.isfinite(vals).all() or not np.isfinite(U).all()
                or not np.isfinite(final_residual) or final_residual > 1e-8)
    if fallback:
        q, U2, _, _, _, _ = exact_endpoint(Aprefix, k)
        return q, U2, op.columns, True, final_residual, len(caught)
    positive = np.maximum(vals[:k], np.finfo(np.float64).tiny)
    q = Aprefix.T @ U[:, :k]
    q /= np.sqrt(positive)[None, :]
    q, _ = np.linalg.qr(q, mode='reduced')
    return q[:, :k], U[:, :k].copy(), op.columns, False, final_residual, len(caught)


def save_npz_atomic(path, arrays):
    temp = path.with_name(path.name + '.partial.npz')
    np.savez_compressed(temp, **arrays)
    with np.load(temp, allow_pickle=False) as z:
        for key in arrays:
            _ = z[key].shape
    os.replace(temp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--solver', choices=('exact_svd', 'warm_lobpcg'), required=True)
    ap.add_argument('--eta', choices=('0.01', '0.1'), required=True)
    ap.add_argument('--repeat', type=int, choices=range(3), required=True)
    args = ap.parse_args()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == INPUT_SHA256
    with np.load(SOURCE, allow_pickle=False) as z:
        A = z['a'].copy(); energy = z['energy'].copy()
    assert A.shape == (512, 2704)
    eta = float(args.eta); n, _ = A.shape; k = 25
    tol = 1e-10 * np.maximum(1.0, energy)
    G = np.zeros((n, n), dtype=np.float64)
    Q = None; Ustate = None; cached = 0.0
    query = np.zeros(n, bool); update = np.zeros(n, bool)
    loss = np.zeros(n); queried_opt = np.full(n, np.nan)
    endpoint_excess = np.full(n, np.nan); endpoint_tol = np.full(n, np.nan)
    endpoint_cpu = np.zeros(n); endpoint_matvec_columns = np.zeros(n, np.int64)
    endpoint_final_residual = np.full(n, np.nan); endpoint_fallback = np.zeros(n, bool)
    endpoint_warning_count = np.zeros(n, np.int64)
    component = {'gram_update':0.0, 'residual':0.0, 'exact_eigvals':0.0,
                 'endpoint':0.0, 'bookkeeping':0.0}
    wall0 = time.perf_counter(); cpu0 = time.process_time()
    for i, x in enumerate(A):
        t = i + 1
        c = time.process_time(); g = A[:t] @ x; G[i,:t]=g; G[:t,i]=g
        component['gram_update'] += time.process_time()-c
        c = time.process_time()
        residual = 0.0 if Q is None else float(np.linalg.norm(A[:t]-(A[:t]@Q)@Q.T)**2)
        component['residual'] += time.process_time()-c; loss[i]=residual
        qflag = Q is None or t <= k or residual > (1.0+eta)*cached + tol[i]
        uflag = Q is None or t <= k; query[i]=qflag
        if qflag:
            c=time.process_time(); opt=exact_opt_from_gram(G,t,k,energy[i]); component['exact_eigvals']+=time.process_time()-c
            queried_opt[i]=opt; cached=max(cached,opt-tol[i],0.0)
            if residual > (1.0+eta)*opt + tol[i]: uflag=True
            if uflag:
                c=time.process_time()
                if args.solver=='exact_svd':
                    Q,Ustate,mv,fb,fr,wc=exact_endpoint(A[:t],k)
                else:
                    if Ustate is None:
                        Q,Ustate,mv,fb,fr,wc=exact_endpoint(A[:t],k)
                    else:
                        Q,Ustate,mv,fb,fr,wc=warm_endpoint(A[:t],G[:t,:t],k,Ustate)
                dt=time.process_time()-c; component['endpoint']+=dt; endpoint_cpu[i]=dt
                endpoint_matvec_columns[i]=mv; endpoint_fallback[i]=fb
                endpoint_final_residual[i]=fr; endpoint_warning_count[i]=wc
                captured=float(np.linalg.norm(A[:t]@Q)**2)
                endpoint_excess[i]=max(0.0,float(energy[i]-captured-opt)); endpoint_tol[i]=tol[i]
        update[i]=uflag
    algorithm_cpu=time.process_time()-cpu0; algorithm_wall=time.perf_counter()-wall0
    component['bookkeeping']=algorithm_cpu-sum(component.values())
    stem=f"B15_{args.solver}_eta{args.eta.replace('.','p')}_r{args.repeat}"
    arrays={'query':query,'update':update,'loss':loss,'queried_opt':queried_opt,
            'endpoint_excess':endpoint_excess,'endpoint_tol':endpoint_tol,
            'endpoint_cpu':endpoint_cpu,'endpoint_matvec_columns':endpoint_matvec_columns,
            'endpoint_final_residual':endpoint_final_residual,
            'endpoint_fallback':endpoint_fallback,'endpoint_warning_count':endpoint_warning_count}
    raw=HERE/f'{stem}.npz'; save_npz_atomic(raw,arrays)
    out={'study':'B15-native512-warm-lobpcg-endpoint-comparator','solver':args.solver,
         'eta':eta,'repeat':args.repeat,'rows':n,'dimension':A.shape[1],'rank':k,
         'queries_after_growth':int(query[k:].sum()),'refreshes_after_growth':int(update[k:].sum()),
         'algorithm_cpu_seconds':algorithm_cpu,'algorithm_wall_seconds':algorithm_wall,
         'component_cpu_seconds':component,'endpoint_matvec_columns_total':int(endpoint_matvec_columns.sum()),
         'runtime_fallbacks_after_5k':int(endpoint_fallback[(np.arange(n)+1)>=5*k].sum()),
         'solver_warnings_total':int(endpoint_warning_count.sum()),
         'max_endpoint_excess_over_tol':float(np.nanmax(endpoint_excess/endpoint_tol)),
         'endpoint_tolerance_violations':int(np.nansum(endpoint_excess>endpoint_tol)),
         'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
         'input_sha256':INPUT_SHA256,'raw_file':raw.name,
         'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
         'development_only':True,'new_method':False,'native5000':False}
    (HERE/f'{stem}.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps(out,allow_nan=False))


if __name__=='__main__': main()
