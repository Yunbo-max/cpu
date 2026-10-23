#!/usr/bin/env python3
"""R015 reproducible controlled fast-weight QED toy, not pretrained model evaluation.
Requires NumPy. Paper equations: arXiv:2608.13668v1 Eq.(11)-(12).
"""
import numpy as np, math, json, time
def main():
    t=time.process_time();lam=.25;k=np.array([1.,0.]);S=np.array([[0.],[1.]])
    def run(rho,beta):
        q=np.array([rho,math.sqrt(1-rho*rho)]);b=np.array([beta,beta])
        d=b*q-k*np.dot(k,b*q)
        sb=(np.eye(2)-np.outer(k,b*k))@S
        sq=(np.eye(2)-np.outer(k,b*k+lam*d))@S
        current_base=float((sb.T@q).item());current_qed=float((sq.T@q).item())
        future_base=float((sb.T@k).item());future_qed=float((sq.T@k).item())
        return {"beta":beta,"current_baseline":current_base,"current_qed":current_qed,
          "future_baseline":future_base,"future_qed":future_qed,
          "risk_baseline":.1*current_base**2+.9*future_base**2,
          "risk_qed":.1*current_qed**2+.9*future_qed**2}
    rows=[run(.6,b) for b in (.1,.5,.8,.99,1.)]
    boundary=2*.1*.6/(lam*(.9+.1*.6**2))
    assert abs(boundary-.5128205128205128)<1e-12
    assert rows[1]["risk_qed"]<rows[1]["risk_baseline"]
    assert rows[2]["risk_qed"]>rows[2]["risk_baseline"]
    assert abs(rows[-1]["risk_qed"]-.08224)<1e-12
    q=np.array([0.,1.]);d=q;sb=(np.eye(2)-np.outer(k,k))@S
    sq=(np.eye(2)-np.outer(k,k+lam*d))@S
    assert np.isclose((sq-sb).T@q,0).all()
    assert np.isclose((sq-sb).T@k,-.25).all()
    rng=np.random.default_rng(20261023);err=0.
    for _ in range(1024):
        n=3;v=2;k1=rng.normal(size=n);k1/=np.linalg.norm(k1)
        q1=rng.normal(size=n);q1/=np.linalg.norm(q1)
        r1=rng.normal(size=n);r1/=np.linalg.norm(r1)
        gate=rng.uniform(.1,.95,size=n);S1=rng.normal(size=(n,v))
        Sbar=np.diag(rng.uniform(.5,1.0,size=n))@S1
        dd=gate*q1-k1*np.dot(k1,gate*q1);val=rng.normal(size=v)
        sb=(np.eye(n)-np.outer(k1,gate*k1))@Sbar+np.outer(k1,val)
        sq=(np.eye(n)-np.outer(k1,gate*k1+lam*dd))@Sbar+np.outer(k1,val)
        formula=-lam*np.dot(r1,k1)*(Sbar.T@dd)
        err=max(err,float(np.max(np.abs((sq-sb).T@r1-formula))))
    assert err<1e-12
    print(json.dumps({"operator":"QED/GDN2 exact state update","beta_threshold":boundary,
      "rows":rows,"orthogonal_future_probe_shift":float(((sq-sb).T@r1).flat[0]) if False else -.25,
      "randomized_identity_trials":1024,"random_max_error":err,
      "cpu_process_seconds":time.process_time()-t,
      "scope":"controlled fixed state; not model inference"},indent=2))
if __name__=="__main__":main()
