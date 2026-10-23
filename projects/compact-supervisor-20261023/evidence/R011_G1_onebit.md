# R011 G1 - Classical one-bit optimum (not a new theorem)
Parent: G1 at research coordination 56c7198d5c6f7bb12a1883ce81df1112652897be.
Let X=(X1,X2,X3) be iid unbiased bits, query index I drawn with p=(p1,p2,p3), and encoder E(X) only one bit. Decoder estimates X_I from E(X) and I. The globally optimal weighted 0/1 distortion over all 2^8 deterministic encoders is

D*(p)=min{1/4, (1-max_i p_i)/2}.

Proof: one-bit decoding selects two 3-bit reconstruction codewords a,b. Partition coordinates into S on which a,b differ and its complement. Matching coordinates cost their summed weight/2. For |S|=1 the best result is (1-max p_i)/2; for |S|=2 the cost is [min_{i,j in S} p_i + p_k]/2=(1-max_{i in S}p_i)/2, never better than caching the heaviest bit. For |S|=3, complements paired by symmetry yield D=(sum_i min(p_i,1-p_i))/4; that is 1/4 if pmax<=1/2 and (1-pmax)/2 otherwise. Taking minimum proves the formula.

Uniform p: optimum 0.25, best cached coordinate 1/3. Skewed (.8,.15,.05): both equal .1. Exhaustive enumeration over 256 encoders for 66 simplex grid points of step .1 in an actually run Python CPU script: max abs discrepancy 2.7755575615628914e-17. The script has no provider usage or GPU; no experimental graph win, originality, or method acceptance is claimed. This is classical rate-distortion/codebook behavior; code at evidence/R011_G1_onebit_enumerate.py.
