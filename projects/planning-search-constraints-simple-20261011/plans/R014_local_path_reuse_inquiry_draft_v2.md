# R014 v2 draft: conditional local-path opportunity before any reuse construction

Unselected inquiry/proof work product after true R013. Not an implementation,
native result, novelty claim, accepted methodtrace or replacement for v1's history.

## Source and object

Fixed hierarchy T_j maps a fixed-task state x to leaf alpha_j(x). During traversal
let P_j(x) be the variables actually tested on x's root-to-leaf path. For a real
successor y define Delta(x,y)={v:x[v]!=y[v]}, using actual state values, not only
syntactic effect variables (conditional effects/unchanged assignments matter).
Domain/task conversion must preserve these coordinates or be handled explicitly.

F03 sufficient-state move + G06 discrete path invariant: if Delta∩P_j(x)=empty,
every test taken by x sees the same coordinate in y. Induction from the root gives
the same child at each visited node and therefore alpha_j(y)=alpha_j(x). Fixed
hierarchy and same converted task are essential. This is a sufficient condition,
not necessary: a changed multi-valued variable can still choose the same side of
a node's equality test. It is elementary/classical incremental-evaluation logic,
not claimed novel; closest decisiondiagram/incrementalheuristic methods remain due.

No target-specific reachability cache is reused. Goal-only transformations preserve
state values here, but this is NOT a missing conversion optimization: fixed source
DelegatingTask::does_convert_ancestor_state_values forwards and returns false at
the ancestor; RefinementHierarchy already consults that predicate.

## Why a correct identity may still be a bad algorithm

Storing28 IDs at all17,639,567 evaluated states costs1,975,631,504 raw intbytes,
before metadata/lookup/path masks and search memory; not a free2.5GiB-AS fit.
One-parent scratch avoids that storage but may recompute all parent IDs per expansion.
Under the explicit equal-ID-cost approximation, N child evaluations, M parent
recomputations, reusable child fraction r, and added bookkeeping B≥0 give an
optimistic benefit condition r*N*C > M*C+B. Thus r>M/N even before bookkeeping.
Using only R013 coarse counts as a CONDITIONAL scale illustration, M=9,830,440
expanded and N=17,639,567 evaluated means r must exceed9830440/17639567 (~0.5573).
These counts are not measured parent recomputations/new-child cachemisses, costs
are heterogeneous, and this is not an empirical bound or predicted speedup.
The actual opportunity discriminator must measure those missing quantities.

## Exact source availability boundary

EagerSearch calls notify_state_transition(parent,op,successor) before dead-end/new
checks, BUT only for registered path_dependent_evaluators. Heuristic's default
get_path_dependent_evaluators is empty; SCP online currently does not override it.
Therefore the callback existing in Evaluator is not proof this heuristic already
gets notifications. Any observer/candidate must explicitly register or source-
isolate the eager hook, preserving all old source/binaries. If changing a header,
recompile the affected dependency closure; link success is not ABI qualification.
Notifications can include non-new or previously dead states, so their costs must
not be divided only by17.6m actual compute calls. Heuristic/EvaluationContext value
caches already exist and must remain part of the strong baseline.

## Concrete next falsifier, not a timing grid

Before selecting a reuse implementation, freeze one bounded source-bound read-only
opportunity counter: actual eligible new-child evaluations, changed coordinates,
parent-ID availability/fallbacks, path-mask reuse counts weighted by real traversal
work, and added bookkeeping. If the parent/fallback+maintenance cost cannot be
covered, park this route regardless of a high unweighted reuse percentage. If
opportunity survives, derive a complete state/quality-safe rule and strongest
simple comparator, qualify native work/plan/VAL before observer-off whole-native
performance. No cross-target/split cache, no assumed zero overhead, no benchmarks
or newmethods invented from a toy invariant. R013sample cost remains descriptive.

Source locations: eager_search.cc:195-225; evaluator.h:37-60; heuristic.h:79-81;
refinement_hierarchy.cc:60-88; task_proxy.h:717-729; delegating_task.cc:114-129;
all under fixed vendor/r010_author_uninstrumented_v1/src/search.
