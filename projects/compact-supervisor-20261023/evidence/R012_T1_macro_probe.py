#!/usr/bin/env python3
"""Pandas exact validator-expression probe for TabKG pinned revision.
Self-contained; DOES NOT import TabKG or run generator. Requires pandas/numpy.
"""
import json,time,numpy as np,pandas as pd
def main():
    started=time.process_time();K,M=100,10000
    X=np.concatenate([np.zeros(2*M,dtype=np.int64),np.arange(1,K,dtype=np.int64)])
    Y=np.concatenate([np.zeros(M,dtype=np.int64),np.ones(M,dtype=np.int64),np.arange(1,K,dtype=np.int64)+1])
    df=pd.DataFrame({"source":X,"target":Y})
    grouped=df.groupby("source")["target"].nunique()
    consistency=float((grouped==1).mean())  # exact pinned validator expression
    counts=df.groupby(["source","target"]).size()
    bayes_correct=int(counts.groupby(level=0).max().sum())
    row_error=1-bayes_correct/len(df)
    assert len(df)==20099 and consistency==0.99
    assert abs(row_error-10000/20099)<1e-12
    print(json.dumps({"rows":len(df),"groups":K,"macro_consistency":consistency,
      "accepted_at_threshold_0_9":consistency>=0.9,"best_reconstruction_error":row_error,
      "conditional_entropy_bits":20000/20099,"cpu_process_seconds":time.process_time()-started},indent=2))
if __name__=="__main__":main()
