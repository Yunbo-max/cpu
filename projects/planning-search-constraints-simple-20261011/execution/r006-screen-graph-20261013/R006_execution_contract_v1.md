# R006 fixed-work generation attribution contract

Status: frozen before any R006 build or run. Parent evidence is the accepted R005
four-row diagnostic plus the separate R005L1 Depots budget supplement. R005 and
R005L1 files, binaries, denominators, and outcomes remain unchanged.

## Question and rival explanations

R005 found that transition generation, rather than transition removal, dominates
the measured rewiring prefix. R006 asks which work inside generation dominates:

1. applicability predicates;
2. reachability predicates;
3. removal-policy decisions;
4. transition/loop emission and vector growth; or
5. residual loop, indexing, and instrumentation overhead.

The candidate strong simple control is per-rewire reuse of the outgoing
applicability result for the same child and operator. The source audit proves that
this Boolean is invariant only for the frozen `NONE` policy and within one rewire
call. It is ordinary loop-invariant reuse, not a named new method. Reachability is
target dependent and is not cacheable under that key.

## Frozen first discriminator

- Public input: Autoscale21.11 optimal STRIPS Blocksworld p05, with the exact SAS
  identity already retained by R005.
- Configuration: the accepted `states_ops` configuration, seed 2011, one thread,
  `remove_spurious_transitions=NONE`.
- Fixed work: construction stops at `max_states=1000`; this is a diagnostic
  frontier, not the R005 full trajectory and not a native solve claim.
- Source: a new `scorpion_profile_v4_r006` tree derived from the accepted v3r2
  source. The accepted v3r2 tree and binary are read-only parents.
- Resources: one compiler thread; command RSS guard 2800 MB; address-space guard
  3500 MB; shared-cgroup abort 7.8 GB; project hard limit 8,000,000,000 bytes.
- Clock: one `steady_clock`, integer nanoseconds. Fine timers are inclusive only
  of the named predicate/policy/emission calls. Residual is the already measured
  enclosing generation duration minus the named durations when nonnegative.

The first source/build task may only add measurements. It must not cache a
predicate, reorder candidates, change a policy, or alter planner data structures.

## Required counters and arithmetic

For every rewire kind, accumulate incoming reachability calls/true values;
outgoing applicability calls/true values; outgoing reachability calls/true values;
policy decisions; emitted transitions; outgoing occurrence count `m`; and distinct
outgoing operator count `d` per rewire. Sum `m` and `d` across calls, while also
recording calls with zero outgoing work. Loops remain separately counted.

For outgoing generation define

`named = applicability + reachability + policy + emission`,

`residual = enclosing_outgoing_generation - named`.

Negative residual, lifecycle mismatch, unfinished scope, or counter identities
that fail makes the timing result invalid. Clock-call overhead is not subtracted
from a noisy aggregate. A later counter-only build is required before speed claims.

The ideal reuse ceiling is calculated only when `m>0`:

`saved_applicability_ceiling = T_app * max(0, 1 - d/m)`.

This assumes equal per-call cost and zero lookup/reset overhead, so it is an upper
bound rather than an expected speedup.

## Pre-registered decision

The applicability-reuse path remains worth implementing only if all are true on
the first fixed-work row:

1. the profile is valid and reaches exactly 1000 states;
2. `m/d >= 1.5`;
3. the ideal saved-applicability ceiling exceeds `1/11` of measured construction;
4. applicability is not displaced by reachability, emission, or residual after
   accounting for the enclosing phase.

Otherwise retire applicability reuse as a priority for this idea. This does not
reject constrained Cartesian abstractions; it rejects only this local optimization
priority. If the screen passes, the next required control is a counter-only versus
fine-clock matched-frontier pair, followed by an uninstrumented implementation.

## Correctness audit gate

Timing cannot establish correctness. Before accepting any implementation, use a
separate audit build to export canonical sorted `(source, operator, target)` tuples
with multiplicities and sorted `(state, operator)` loops at the same frontier.
Check outgoing/incoming mirror multisets, stored counts, state-domain identities,
and shortest-path distances including unreachable markers. Sorting is performed
only on exported copies; planner adjacency order is untouched. Baseline and any
candidate must match exactly. A final-frontier match is not a proof of every
intermediate split, so per-split incident-relation checks remain required before a
broader correctness claim.

No R006 scientific command had been run when this contract was frozen.
