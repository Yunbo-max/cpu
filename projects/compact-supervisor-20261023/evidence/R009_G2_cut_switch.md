# R009 G2: ordinary mincut switching explains the four-fault toy
For any directed capacitated G, define lambda=min_{S:s in S,t notin S} c(delta+(S)).
Deleting F produces:
lambda(G-F)=min_S [c(delta+(S)) - c(F intersect delta+(S))]
and hence the exact identity
lambda(G)-lambda(G-F) =
  max_S [c(F intersect delta+(S)) - (c(delta+(S))-lambda(G))].
This is immediate from maxflow-mincut, not an original theorem.
The bracket is deleted cut capacity minus its original excess/slack.
In the R008 two-example construction with 4 monitored paths and
zero/one unmonitored backup, lambda after q monitored failures is
min(1,4-q) vs min(1,5-q). Both equal 1 for q=0,1,2,3.
For q=4, flow is 0 vs 1 because a second cut overtakes the original
source bottleneck: a standard cut switch, not a new independent
higher-order model parameter.
CPU actually checked equality on 16 seeded directed weighted graphs,
256 deletion queries, and all 4-edge toy masks: no mismatches.
Strong prior: ITCS 2026 k-fault mincut, arXiv:2609.01283 arbitrary-f
sensitivity, Nature Communications 2025 dynamic-cascade mechanisms
(related but separate scope).
DECISION: park original static toy as prospective new-method novelty.
This does not refute a future DIFFERENT dynamic-cascade hypothesis.
Reopen only with new data/conditions and genuinely distinct mechanism.
