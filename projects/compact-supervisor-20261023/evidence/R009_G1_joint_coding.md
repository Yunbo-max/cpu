# R009 G1: joint fault-response coding versus hot-edge caching
Input X=(X1,X2,X3) uniform on {0,1}^3, independent.
For a one-bit encoder E:{0,1}^3->{0,1}, each requested edge i has
the Bayes-optimal decoder of Xi from the one-bit message.
For query probabilities (p1,p2,p3), the weighted risk is
D(E)=1/8 * sum_{message y} sum_{i=1}^3 p_i *
                     min(count_{E(x)=y}(Xi=0), count_{E(x)=y}(Xi=1)).
Exhaustively enumerated all 2^8=256 possible binary encoders.
Uniform queries p=(1/3,1/3,1/3): optimum weighted error 0.25;
caching any one coordinate loses two independent bits -> 1/3.
One optimal encoder is majority-of-three: code 0 for 000,001,010,100,
code 1 for 011,101,110,111; decoding all three bits to the code
produces 6/8 patterns with one bit error and 2/8 patterns with zero.
Skewed p=(0.8,0.15,0.05): optimum error 0.1; caching X1 has 0.1.
Thus joint coding can beat simplistic caching on one finite toy, but it
does not always beat it. This is classical one-shot rate distortion,
NOT a new theorem or achieved practical graph compression.

Why not claim novelty: ICALP 2024 handles weighted single-edge cut value,
ITCS 2026 handles unweighted single/dual maxflow sensitivity, and
arXiv 2609.01283 handles fixed susceptible sets in exact oracle work.
Existing sources do NOT yet provide a measured weighted, nonuniform,
probability-calibrated approximate fault-response coder.
Next question: after including query-index dictionary, offline encoding,
bits per graph, query latency and strong exact oracle/table baselines,
is any *empirically observed* low-entropy real-network regime left where
a probabilistic joint coder gives an actual useful advantage?
Falsifier: no held-out valid fault workload, no significant held-out
advantage over joint-codebook/table/oracle, or novelty collision with
a prior matching distributional objective.
CPU witness original: /mnt/data/r009_branching/r009_probe.py SHA256
9a4eeb3f79fd66a522085daf0a33d35f30d7f613bae364f404c701743229bd29
and raw receipt SHA256
75cc70e74b8fa48bc35f345efea18313a7a8548861cdd9ac06b1c729f4a902af.
No GPU or model training; no formal independent Work review.
