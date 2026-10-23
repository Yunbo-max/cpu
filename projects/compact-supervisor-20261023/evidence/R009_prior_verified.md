# R009 strongest-source collision audit for three previously active leaves
Research parent: 1d3ce273ae068ae122560d4d10956cb39b2f96c5. Inspected on October 23, 2026.

G1 nearest results:
- Baswana and Bhanja, ICALP 2024, Vital Edges for (s,t)-Mincut,
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2024.17
  gives an O(n)-space, O(1)-query directed WEIGHTED single-edge minimum-cut
  capacity oracle WHEN that edge's capacity is available, and a separate
  O(n^2)-space cut-reporting oracle. Thus weighted single-fault value
  retention is not an unstudied query interface.
- Ahi et al., ITCS 2026, https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.5
  gives O(lambda*n)-space single/dual directed UNWEIGHTED maxflow
  sensitivity oracles, and a multi-edge directed unweighted mincut oracle.
- Choudhary, Kumar, Saggi, arXiv:2609.01283 (September 1, 2026),
  https://arxiv.org/abs/2609.01283
  explicitly introduces subset sensitivity confined to a fixed susceptible
  edge set, with multi-update exact flow/cut applications and lower bounds.
  It is a preprint, not assumed to be a peer-reviewed accepted result.
  Fixed susceptible set is NOT the same as a nonuniform stochastic query
  distribution; G1's narrow question remains conditional on that difference.
- Raychaudhury et al., SIGMOD 2026, https://doi.org/10.1145/3801896
  exploits real workload query distributions to obtain query-specific
  coresets in query plan optimization (different mathematical target).
- Simple baseline on R008 independent-bit graph family: full response
  table needs eight bits plus any externally needed edge dictionary; if
  only two named failure edges can be queried, two response bits suffice.
  This is trivial and MUST be included before comparing learned sketches.

G2 nearest results:
- Ahi ITCS 2026 above already treats up to k edge failures for unweighted
  mincut (hence maxflow value by maxflow-mincut), and its own lower bounds.
- Choudhary et al. arXiv:2609.01283 tackles arbitrary f updates in the
  intended algebraic sensitivity setting; inspect its model, randomized
  guarantee and weight/parallel-edge limitations before claiming equivalence.
- Zhu et al., Nature Communications 2025,
  https://www.nature.com/articles/s41467-025-63001-4 studies dynamic
  flow network cascading failures through higher-order interactions,
  a related but NOT IDENTICAL outcome to static maxflow after edge removal.
- R009 exact algebra showed R008 four-fault construction is explained by a
  single alternative mincut activation, not a novel high-order operator.
  Park THIS static construction; dynamic cascades remain a separate
  untested research question, not an automatically accepted new leaf.

G3 nearest results:
- ICALP 2024 weighted vital-edge oracle explicitly takes a failing-edge
  query and known edge capacity. An original edge-index correspondence is
  a natural part of its input interface.
- Hashemi et al., IJCAI 2024 graph-reduction survey
  https://www.ijcai.org/proceedings/2024/891 covers sparsification,
  coarsening and condensation, not a universal impossibility of identity.
- R009 two-branch ambiguity disappears with one bit specifying the
  original p/q label swap; this was a missing query-map assumption rather
  than a new graph preservation theorem.
  Park G3's standalone novel-method direction.

Scope boundary: no implementation of the ITCS, ICALP, or arXiv oracles was
executed. These are comparison-theorem inspections and small exact proofs,
not a real network benchmark or performance win.
