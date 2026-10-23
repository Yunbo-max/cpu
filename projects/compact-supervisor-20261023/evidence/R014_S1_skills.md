# R014 S1 — skill library monotonicity is an oracle policy-class bound, not a new agent discovery

Let Pi(L) be the admissible policies with a set of callable skills L. If skills can be ignored and adding a skill has no mandatory overhead or hidden change to old skills, Pi(L) subset Pi(L'). By definition V*(L') = sup_{pi in Pi(L')} E[R(pi)] >= sup_{pi in Pi(L)} E[R(pi)] = V*(L). Therefore a broad claim that *giving an optimal agent free additional callable skills always reduces attainable success* is mathematically false.

Observed loss can happen for a particular learned router with mistaken selection, nonzero context/execution cost, constraints of skill-only mode, or non-stationary side effects; these assumptions must be specified before attribution. Simple numerical sanity check: base task success utility 0.8; new skill local success 0.9 but adds compulsory cost .3, so forced-use net = .6, optional-use best net remains .8. This is a utility/cost toy, NOT actual observed LLM failure.

Literature: Microsoft Research 2026 arXiv *Agent Skills Can Be Harmful* studies 307 skill-induced failures, notably excessive verification and heavy implementation pipelines. ACL 2026 SAGE trained skill library use; IEEE 2026 Constraint-Consistent Skill Composition already includes conditions, effects and task transfer. Thus "skills sometimes harmful", "more skills cause more verification", "use pre/postcondition contracts" are too close for novelty.

Scientific decision: screening NEGATIVE for broad S1; do not create an active ROOT child. Next genuine candidate would require a new assumption-specific effect surviving direct strong prior AND tests on actual agent skill-execution traces, not only this superset identity.
