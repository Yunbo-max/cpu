# Depots R005-L1: prospective longer-budget supplement

User steering on 2026-10-13 16:27:45 Europe/London authorizes continuing the
two censored Depots rows while CPU capacity is available. Both original stdout
logs report SIGXCPU / search exit23, not OOM; visible current CPU use is near idle.

Execute states_ops first, then none after inspecting the first terminal receipt.
Native overall CPU limit is 600 seconds; outer wall guard650; runner675.
Retain one solver thread, seed2011, max_states10000/max_transitions1000000,
CEGAR max_time30, identical search strings, data, v3r2 source and binary.
Retain native2500M, group RSS2.8e9B, per-process AS3.5e9B and shared guard7.8e9B.
No change to the original frozen R005 four-row matrix, baselines or failures.
New run IDs and directories are an explicit budget sensitivity supplement;
longer budget is not algorithmic improvement or independent confirmation.

Question: does increasing the outer native CPU budget make these public tasks
complete under unchanged search and memory settings? Rival: search frontier growth
still exceeds 600CPU seconds or memory cap. A valid plan and native successful
exit, followed by independent VAL on original PDDL, establishes only that row's
native outcome under the larger budget. Timeout/memory refusal remains censored;
invalid input/identity/validator execution is not a mathematical refutation.
Inspect raw exit, logs, CPU/wall/RSS before the next arm. Missing fields stay null.
This does not resolve R006 graph witnesses or predicate/emission attribution.
If both remain censored, retain that cost boundary and choose a source-informed
next action; do not endlessly escalate identical runs or erase previous outcomes.
