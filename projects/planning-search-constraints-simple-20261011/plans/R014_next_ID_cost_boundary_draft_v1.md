# R014 draft after actual R013 diagnostic (not selected/built/run)

R013 complete onlinecreation census was12.139181209CPU s/1764events of instrumented
98.353001CPU s (~12.34%), not dominant by itself. Its17154 ordinary sampled calls
have disjoint rawCPU ns15953454/24358206/7857590/7914743 across prefix/IDs/max/tail.
ID stage is largest within the descriptive sample, but includes allocation and
clockboundary overhead. No probabilitysample, epochstability or originalintrinsic
share/upperbound follows. Plan/work/VAL matched strongauthor baseline; no method
speed result. Do not target onlinecreation simply because author whole evaluation
timer is labeled 'diversification'.

## Next discriminating object

Read actual hierarchy traversal, task conversion and existing heuristic cache before
inventing a state-ID cache. Fresh source already refutes a tempting shortcut:
ModifiedGoalsTask changes only goals, but DelegatingTask::does_convert_ancestor_state_values
forwards to parent and returns false when ancestor reached; therefore the existing
RefinementHierarchy::needs_to_convert check already avoids conversion for pure goal
changes. Different task object identity does NOT imply repeated full state-copy here.
Do not claim conversion-removal savings without an actual event count.

For a fixed hierarchy mapping alpha_j and its actually tested coordinate support V_j,
two states agreeing on V_j map to the same leaf. A successor with genuinely changed
coordinates E disjoint from V_j can reuse its parent ID. This conditional elementary
invariance alone is not newalgorithm/CPUgain: existing estimate caches, ancestry and
search expansion/generation order, materializing parentIDs, memory traffic and
conditional effects all matter. Reachability still target-specific; no incorrect
cross-target/split reuse. Closest incrementalheuristic/decisiondiagram prior work must
be inspected before claiming novelty. A naive perstate28-ID array over17.6mstates is
~1.98GB just intstorage, not a free fit under frozen2.5GiB nativeAS, with cache and
search memory additional; do not implement that as default.

Prefer a bounded source/measurement discriminator of hierarchy decisions versus
allocation/prefix cost and actual parent-ID availability before an implementation
or more timing repeats. If measured opportunity is small or cache cost dominates,
park this route and inspect search quality/pruning instead. If a true construction
is chosen, preserve same idea but new mathtrace/quality/trajectory and real105+new
feedback ancestry; qualify semantics before observer-off complete-native performance.

Ordinary vectorreuse/constantgoal specialization are strong simple engineering
controls, not scientific novelty. Broader publicdomains/strongbaseline rawproperties/
closestprimary remain pending; no inactiveexactU timinggrid or Depots capescalation.
