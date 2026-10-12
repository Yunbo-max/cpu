# Collaborate on one idea with native subagents

Use parallel agents when independent, bounded work can shorten the current
research question's critical path or improve its review. Keep **one active idea**
and one coordinating agent. Parallelism does not create additional research goals,
resource allocations or automatic approval. For a small or tightly dependent
task, continuing serially can be faster.

## Contents

- [Choose useful parallel work](#choose-useful-parallel-work)
- [Bind and scope each delegation](#bind-and-scope-each-delegation)
- [Launch through the host](#launch-through-the-host)
- [Integrate evidence and continue](#integrate-evidence-and-continue)
- [Recover interrupted work](#recover-interrupted-work)
- [Example: one method, several contributions](#example-one-method-several-contributions)

## Choose useful parallel work

Discover the capabilities and actual capacity exposed by the current host before
dispatch. Use an available native subagent facility; do not assume a particular
API, a fixed number of agents, a paid model service or persistent background
execution. When delegation is unavailable, perform the same work serially.

The coordinator retains the parent goal, current goal-contract version, active
idea/revision, scientific journal, runner decisions, integration and publication.
Only the coordinator writes shared state or calls the runner's `respond` for this
goal. A child returns a contribution to that goal; it cannot independently close
the idea, change its contract, replenish budgets or publish shared work.

Identify inputs and dependencies first. Delegate a task only when its required
inputs are available and accepted for that use. Paper extraction and a baseline
code audit can overlap; implementing a new formula must wait for its selected
definition. An exploratory draft with unresolved inputs must say so and cannot
be consumed as a finalized dependency.

For a proposed efficiency or quality improvement, move the most consequential
checks early enough to change implementation or experiment selection. Delegate
the applicable ready checks, not a mandatory team or another candidate pool:

| Assignment | Decision-changing deliverable |
| --- | --- |
| Baseline and protocol audit | Located primary protocol, strongest relevant simple/optimized comparator, fair inputs/tuning and missing comparisons |
| Metric audit | Formula/convention mapping, separately derived reference calculation and numerical edge cases that could invalidate a conclusion |
| Cost and counterexample audit | Measured or bounded cost components, scope of a possible speedup, and a discriminating counterexample or representative failure state |
| Closest-work audit | Concrete overlap/difference with cited mechanisms; whether the current idea adds a substantive change |

The coordinator states what each possible finding will change and chooses the
lowest-cost useful checks before a large sweep or prolonged micro-optimization.
Other ready work continues. A missing audit prevents only the conclusion that
depends on it; source gaps and numerical problems feed scoped repairs.

Choose as many agents as the ready work, host capacity and remaining project
budget justify. Do not fill every slot by default. Account for instruction,
integration and review overhead; do not duplicate completed work. Children do
not recursively fan out unless the coordinator explicitly assigns a bounded
delegation allowance within the same global limits.

Agent slots and experiment concurrency are separate. Several reading agents do
not authorize several simultaneous GPU jobs. Restore the project's configured
host, allocation and limits; use [simple-experiment-design.md](simple-experiment-design.md)
for measured CPU/GPU placement and [simple-runner.md](simple-runner.md) for jobs.
The coordinator accounts for all delegated effort and job reservations together;
child budgets partition existing authority and never multiply it. If native
model usage or price is not exposed, record it as unknown, not zero or free.
Track model/token usage separately from runner seconds and experiment resource
usage. Choose an observable finite work/deadline bound; do not claim exact cost
compliance without measurement. An agent with uncertain liveness still holds
its assigned capacity and write scope until reconciled.

Parallelize paper reading, derivation and disjoint implementation freely within
those limits, but isolate comparative performance timing on the actual configured
execution host. Reserve a quiet interval or demonstrably separate resources;
control competing CPU/GPU jobs, thread settings, warmup and run order. A process
CPU timer alone does not eliminate memory-bandwidth or cache contention. Retain
observed interference and repeat affected timings when needed. State when timings
were concurrent or uncontrolled instead of claiming fair speed measurements.

## Bind and scope each delegation

Use [simple-delegation.json](../assets/templates/simple-delegation.json) as an
editable project note. It is a draft template, not a runner configuration, new
CLI schema or evidence of a launch. Replace nulls only with observed identities
or deliberate project decisions. Keep the coordinator-owned ledger in durable
project storage with versioned entries; give children distinct output directories.

Record the following before launch:

| Record | Required meaning |
| --- | --- |
| Identity | Request ID, delegation ID and generation; a continuation/replacement gets a linked new generation |
| Parent binding | Current goal-contract version, active idea/revision, adopted source digest, actual plan and input references/hashes |
| Assignment | One question, concrete deliverable, exact read/write paths, output directory and completion requirements |
| Dependencies | Delegation/task/artifact identities and the specific accepted outputs this assignment consumes |
| Authority | Existing authorization source, deadline, effort/resource allowance and whether experiments or further delegation are permitted |
| Launch | Actual host capability, native agent ID and observed launch time; leave these null before a real launch |

For a runner-backed project, copy its observed goal and source identities. For a
project without that runtime, cite the actual versioned checkpoint/guidance and
mark inapplicable bindings explicitly; do not invent a runner digest or version.
Pin existing artifacts with hashes computed from their bytes. A nonexistent
future output has a target path, not an evidence hash. Reuse applicable design
and evidence records without silently assigning them to a new revision.

Provide the child only the context needed for its work: question, bindings,
selected sources, dependencies, authority, expected output and reporting format.
For independent review, use a fresh, minimal-context agent when available;
provide artifacts and the acceptance question without coaching the expected verdict.
Disclose any prior exposure that limits independence.
Fresh agent context, an independently derived implementation and an unseen
confirmation dataset are three different properties. A fresh reviewer inspecting
the producer's code is not an independent reference implementation; another agent
looking at already inspected results does not make them unseen. Record which
property actually holds and use the relevant evidence for the claim.

Assign disjoint file ownership. A read-only reviewer returns findings; a writer
changes only its named paths or supplies a patch proposal in its own output
directory. Shared paths, interfaces and generated exports belong to the
coordinator unless ownership is explicitly transferred. An assignment is an
instruction boundary, not a filesystem sandbox. Preserve others' changes and
check the actual diff before integrating. Never edit inputs used by an active
experiment; create a separate revision and transfer ownership only at a safe boundary.

Existing user authorization propagates only within its scope. A child cannot
infer permission for a new service, additional spending, external messages,
expanded resource access or a different publication destination. Resolve only
the genuinely missing authorization; continue independent authorized work.

## Launch through the host

Read the host's actual tool contracts. If tools such as `spawn_agent`,
`list_agents`, `send_message`, `followup_task`, `interrupt_agent` and `wait_agent`
are exposed, use their supported arguments and returned handles. Other hosts
may expose different operations. Never treat these names as a bundled skill API
or invent their presence, maximum capacity or successful execution.

Before spawning, retain an immutable assignment snapshot and persist a launch
intent with `lifecycle_state: dispatching` and `launch.intent_recorded_at_utc`.
Record the supported call correlation label (for example a unique `task_name`
derived from delegation ID/generation) or idempotency key before the call so a
lost acknowledgment can be matched against host inventory.
After a successful spawn, record the returned agent identity in `launch`.
A missing acknowledgment or ambiguous spawn error leaves an uncertain launch,
even with a null agent ID; a definitive host refusal proving no launch can be
recorded as not started. Reconcile the host inventory, messages, artifacts and jobs before
retrying; retain its capacity and write scope while existence remains uncertain.
Update the ledger when a contribution arrives, is superseded or becomes blocked.
Use messages for scoped clarifications and an idle-agent continuation facility
when supported. Keep ownership and revision bindings explicit across follow-ups.
The coordinator can perform useful local work while children run; wait for a
meaningful event only when no independent ready work remains.

This is cooperation above the existing runner. Native agents produce proposals,
code, readings or reviews; the coordinator submits concrete experiment tasks to
the existing execution protocol. Do not add invented subagent fields to runner
task JSON or bypass its attempt/source/evidence accounting. Prefer coordinator-
submitted runner tasks for diagnostics in a runner-backed project. Any directly
assigned child diagnostic requires a shared budget reservation, deadline and
attempt/resource allowance before launch; preserve its actual command, process/job,
receipts and usage in the same inventory before releasing that reservation.

## Integrate evidence and continue

Each child returns its request/delegation ID, generation and exact parent/input
binding in `result.binding`, plus status, artifact references, changed files,
commands/tests and observed results, limitations and a concrete next action.
Pin the retained immutable prelaunch snapshot in `assignment_ref`, not the mutable
aggregate ledger containing results. The coordinator copies the contribution into
its ledger without rewriting the child's binding.
Distinguish complete, partial, blocked and failed
contributions. Retain useful partial output; a timeout is not a scientific
negative result and a successful child response is not scientific verification.

Keep `result.status` separate from `acceptance.state`. Before accepting a result,
the coordinator checks its request/generation, current goal and idea binding,
source/input/plan identities, scoped file changes, real evidence and relevant
tests. Read consequential content, not only its summary or hashes. Material input
changes require targeted revalidation; changed goal/idea/source bindings require
explicit scoped reassessment. Unrelated journal/status events do not invalidate
unchanged inputs. Preserve valid unaffected work, old bindings and historical evidence.

Record which outputs were accepted and why, then update the shared journal or
runner once. Accepting a contribution does not mean accepting every scientific
claim in it. A code repair may be accepted while its method remains inconclusive.
Review disagreements through the relevant definition, proof, raw result or
additional check; agent count and majority vote do not establish truth.

Release downstream work as its own dependencies become accepted. There is no
global barrier requiring every child to finish, nor a new mandatory reviewer
PASS gate. Missing evidence returns a specific collection/analysis task; a bug
returns a scoped repair; valid negative evidence returns to the hypothesis.
Only consumers of the affected result wait. Apply the existing immutable task
replacement and downstream rebuild protocol when a submitted job needs repair.

## Recover interrupted work

Checkpoint the coordinator ledger, completed/partial artifacts, native handles,
running experiment identities, cumulative usage and next actions before context
or host limits. Resume from those records. Native conversations and handles may
not survive a host restart; a saved note does not keep an agent or job alive.
Restore the policy/executor/scheduler identities separately, as described in
[rsi-simple.md](rsi-simple.md#restore-the-scientific-policy-as-well-as-the-process).
Read new contributions since the last accepted checkpoint and targeted unresolved
artifacts first; do not ask every worker to reread the entire project after each
scheduled wake. Keep handoff, model and integration delays separate from actual
experiment CPU/wall time; unobserved native usage remains unknown.

For an unknown or lost handle, inspect the host's available status, artifacts and
actual job/attempt identities before replacing work. Do not launch duplicate
experiments merely because the child stopped replying. Interrupting a child does
not prove its subprocesses, SSH jobs or GPU work stopped. Reconcile those jobs
through their own execution receipts/status, preserving uncertain reservations.

At a deadline, collect partial work and diagnose the cause. Retry only within
the retained budget and per-issue bound, with a changed cause or a concrete
continuation checkpoint. A replacement receives a new generation linked to the
old one. Reconcile old writes/jobs before transferring ownership; late old
results remain history and cannot overwrite the accepted newer generation.
If delegation itself fails, continue useful serial work. If every remaining
action is genuinely blocked, record its resume condition without declaring the
research goal complete.

## Example: one method, several contributions

For one proposed method revision, the coordinator restores the goal and current
design. It may assign a paper reader to extract relevant published experimental
protocols and optimized baselines, while a separate auditor derives a stable
metric reference from its definition. Meanwhile it checks the derivation and
whether the targeted cost could change the overall result. Each contribution
names its actual sources and missing details; neither independently selects a
different research idea. A consequential mismatch redirects the affected work
before a large run, without holding unrelated work behind a group review barrier.

Once those inputs are accepted, code implementation and experiment/analysis
planning can overlap on disjoint paths with a shared, pinned method interface.
The coordinator integrates them, calibrates the configured execution host and
submits ready comparisons through the runner within the shared resource budget.
A separate reviewer can inspect consequential code or raw-to-table analysis
while other independent rows proceed. Result-driven repairs return to the owner
of the affected layer, and the coordinator records the next research decision.
