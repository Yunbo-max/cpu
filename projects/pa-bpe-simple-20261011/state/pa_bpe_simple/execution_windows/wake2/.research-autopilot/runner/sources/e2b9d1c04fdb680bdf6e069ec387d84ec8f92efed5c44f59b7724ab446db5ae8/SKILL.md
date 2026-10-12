---
name: research-autopilot
description: "Use to research, verify and repair one method at a time from an idea, derivation, code or results. Coordinate available native subagents for independent work, learn experimental designs from papers, adapt comparisons to project CPU/GPU resources, and continue from evidence and failures. This is the rsi-simple edition; mathematical analysis is included."
---

# Research Autopilot Simple

Advance the user's research goal with **one active idea at a time**. Answer its
next important question, inspect the evidence, and continue the resulting work.
Keep revisions and negative results. This branch is `rsi-simple`, version
`0.3.0-simple.9`.

## Preserve the actual goal

Distinguish the **overall user goal**, the **current hypothesis/question**, and
the **next bounded task**. One active idea is a concurrency rule, not a one-cycle
limit. A command, seed batch, feasibility check, report or individual hypothesis
ending does not complete a broader research goal.
Multiple agents may work on that same active idea; the coordinator retains one
parent objective, one integration decision and shared resource accounting.

Select the runner's goal contract from the user's request without asking again
for an already clear intent:

- `bounded_task`: only when the request really ends at a named check, repair or
  deliverable, such as determining whether a paper fits the CPU budget.
- `research`: investigate/improve the method through hypotheses, actual evidence
  and interpretation; declare concrete criteria for answering that objective.
- `continuous_research`: the user explicitly wants open-ended research without
  an automatic completion endpoint; continue serial research
  within retained finite execution budgets. Do not turn a milestone into success
  of the whole goal or silently extend resources.

For empirical research on this paper/topic, CPU feasibility is an initial milestone.
Continue into source/baseline understanding, one falsifiable hypothesis, necessary
math, code and experiment design, actual comparison, interpretation and the next
decision. Reuse an existing method when supplied. Do not relabel “find a runnable
paper” as the user's whole goal.
For a theoretical objective, use the relevant proof, counterexample or mathematical
verification; do not impose unrelated experiments as a completion requirement.

After every batch, choose and perform the next useful action within scope and
budget. A valid negative result can revise or retire this idea and lead to a
substantively different successor. A positive pilot leads to the remaining
controls or confirmation required by the claim. Report progress without ending
an active goal. If all remaining work is genuinely blocked, preserve its exact
resume conditions and distinguish that pause from completion.

Count command attempts, journal observations and complete research cycles
separately. A full cycle records a hypothesis/prediction, a discriminating test,
observed result, interpretation and resulting decision. Three methods by three
seeds are nine runs, not automatically nine research cycles. A declared cycle is
still subject to scientific review; the runner does not certify its meaning.

## Start from what exists

1. Restore the user's goal, method, code, logs, prior decisions and active run
   identities. Do not restart discovery when a method already exists.
2. State the next uncertainty in one sentence: a derivation, implementation,
   metric, resource constraint or scientific prediction. Choose one active idea;
   revise it serially before considering a replacement.
3. Restore the project's resource settings from its initial setup and latest
   authorized updates: execution host, CPU/RAM, GPU devices/VRAM, availability
   window, concurrency and cumulative budget. There is no fixed hardware default.
   Code and design can be written in the current conversation; execute on the
   configured authorized host and check its actual capacity. This conversation's
   host, a previous project's allocation and a paper's hardware do not replace
   those settings. Reuse known settings without asking again. Do not require
   Work, a GPU, a new API key or a paid service.
4. Read [rsi-simple.md](references/rsi-simple.md) for the next action and feedback
   contract. Read `simple_runner.py --root PROJECT status` for an existing runner
   and `simple_loop.py --root PROJECT status` for its scientific journal before
   changing anything. Inspect the adopted source identity and its saved guidance
   before continuing an existing runner; use the source-adoption handoff for a
   new version. Reuse valid evidence instead of rerunning it.
5. For a research objective, also read
   [simple-experiment-design.md](references/simple-experiment-design.md) before
   designing or assessing its evidence. It is the default research contract,
   not an optional full-edition gate. For a bounded repair, use only the applicable
   diagnostics; for theory, design proof/counterexample checks appropriate to the
   claim rather than imposing empirical benchmarks.

On restore, identify the active **scientific policy**, command executor and wake
mechanism separately. A Simple runner does not silently replace a full-edition
candidate policy. Apply the user's latest authorized edition through a versioned
project handoff, retaining the old contract, evidence, usage and active identities.
Resolve stale conflicting instructions for their actual consumers; do not revive
20-to-15 quotas, previous deadlines or obsolete scorer prerequisites from history.
Updating this skill alone neither migrates nor resumes a paused research project.

## Choose work that can change the decision

Before expanding a batch, identify the current uncertainty, the outcomes that
would change the next action, and a cheaper discriminating check. Prefer useful
counterexamples, strong controls and measurement checks over larger grids or more
cards. Reuse accepted artifacts; scale surviving comparisons with their remaining
coverage visible. An unclear decision calls for focused analysis, not a project stop.

Keep the primary objective, protected quality constraints and secondary outcomes
separate. Lower recourse, lower error and faster execution do not establish one
another. Match the experiment to the current claim without changing the parent
goal after seeing results. Distinguish a common-start mechanism test from the
natural end-to-end trajectory; neither can overwrite the other's conclusion.

For efficiency work, measure the relevant strong baseline and component costs
early. Estimate the overall benefit even if the proposed component became free;
state assumptions and unknowns. Audit baselines, metric numerics and closest prior
mechanisms in parallel when useful, before expensive expansion. Preserve necessary
infrastructure repair as its own outcome, without counting it as an algorithm gain.

Before comparing outcomes, choose implementation equivalence or task-quality
evaluation and justify numerical tolerances. Keep correctness requirements distinct
from noisy performance decisions. Account for allowed fallback and failed attempts
in total cost; do not require every timing repeat to win or every solver attempt
to avoid fallback unless that is an actual declared task requirement. Preserve old
frozen failures; changed policies require a new design and suitable confirmation.

Use the design guide and optional `simple_design.py` decision-review advisories to
surface missing targeted work. They inspect declared structure and artifact hashes,
not scientific meaning, statistical validity or actual adoption of a project policy.
Old plans remain readable and unreviewed dimensions remain explicit; these notices
do not authorize experiments or become admission/continuation gates.

## Coordinate available subagents

When independent ready work can benefit, use the current host's native subagents
to parallelize it. Read [simple-collaboration.md](references/simple-collaboration.md)
before delegating; use its [assignment record](assets/templates/simple-delegation.json)
to retain the actual request, scope, native agent identity, result and acceptance.
This is part of the default Simple workflow when tools are available. Small or
dependent tasks can remain serial; missing subagent tools do not block the goal.

The coordinator owns the goal, journal, runner decisions, shared budget and final
integration. Delegate useful bounded work on the same idea: paper/protocol
extraction, mathematical analysis, implementation in disjoint files, or review of
available artifacts. Start dependent work only after its required artifacts have
been accepted. Never let several workers edit the same files, mutate project
state, reserve the same resource or launch competing supervisors.

Read current host capacity and project limits instead of fixing an agent count.
Agent slots and CPU/GPU experiment concurrency are different limits. Include
in-flight and uncertain assignments, coordinate any nested delegation, and record
model usage as observed or unknown rather than treating parallel work as free.
Continue useful work while children run; do not wait for the entire group when
the next independent action is ready.

Inspect actual artifacts and bindings before accepting a result. A child saying
“done” is not a scientific verdict. Use fresh, minimal-context review where useful;
preserve disagreements and resolve them with evidence. Failed or incomplete work
produces a scoped repair, continuation or reassignment. Reconcile uncertain agents
and jobs before reusing their write scope or launching replacements. Save partial
work and pending identities at handoff; native delegation requires a live host.

## Learn the design, then adapt it

Read the closest relevant published papers, their experimental sections,
appendices and available author/baseline code. Extract what each comparison
tests, its data/splits, baselines, controls, tuning, metrics, uncertainty and
compute. Record exact source locations, discrepancies and missing details.
An abstract, related-work list or copied hyperparameter table is not this work.
Explain which design is inherited, which must change for our hypothesis, and why;
do not inherit an untested assumption or an unaffordable budget silently.

Before inspecting new outcomes, version a plan mapping each claim to its needed
comparisons, predictions/falsifiers, artifacts, analysis and outcome decisions.
Cover the strong and simple baselines, fair information/tuning/compute, mechanism
controls, relevant generalization and uncertainty the claim needs. Plan the whole
evidence scope, then execute it in useful bounded batches. Keep deferred
requirements visible; a pilot does not erase the remaining matrix. Neither a
fixed number of seeds nor a full Cartesian product is universally appropriate.

Use `simple_resources.py` on the authorized execution host to record current
resource observations. Separately record the project's allocation, duration and
budget; visible/free GPUs are not authorization. Measure representative time,
peak memory and feasible concurrency before scaling. Keep CPU paths and preserve
comparison fairness when reducing scope. The probe does not reserve hardware or
enforce memory limits, and a local snapshot says nothing about a remote GPU host.

Use the plan/results templates and `simple_design.py check` from the design guide
to expose claim-specific omissions and next actions. Pin the actual plan in task
`input_refs`, preserve all runs, link results and analysis to it, and review the
scientific meaning independently when feasible. The helper checks records and
artifact identities; it does not certify a NeurIPS-level contribution, validate
statistics, or prove a plan preceded unseen results. Disclose retrospective
planning and prior holdout exposure, and freeze a separate confirmation when
the claim needs it. Missing evidence creates work for the affected claim.

## The working loop

**Understand the uncertainty → check the necessary mathematics → implement and
plan → run a useful diagnostic/comparison → verify what the result means → repair
or extend the same idea.** Enter at the stage supported by the existing artifacts.
Every stage produces both its actual output and an explicit next action.

- Keep mathematical assumptions, predicted effects and falsifiers concrete. A
  complete proof is needed only for a claim that depends on it.
- Generate code and the experiment design together: method, relevant baseline,
  original data/split, metric, controls, budget and interpretation of each outcome.
- Make the first check as small as the decision allows. A native subset is fine
  for a stated diagnostic; it is not a complete benchmark result. Do not impose
  a fixed sample count, runtime or number of experiments on every method.
- Execute only real commands within existing authorization. Preserve source and
  data identity, command, settings, logs, predictions/results and actual usage.
- Check evidence before drawing a conclusion. A recorded event, successful exit
  or model saying “verified” does not prove the method works.
- Interpret valid negative evidence and change the assumption, construction,
  experiment or scope that it challenges. Keep the old result and explain why
  the new check is informative. A positive pilot still needs confirmation before
  a broad superiority claim.

## Report exceptions to the user

Report observed failures promptly through the current host's user-visible output;
do not wait for the whole batch to finish or silently end the task. This includes
unavailable required CPU/GPU or execution tools, failed launches, timeouts,
resource errors, invalid data/evaluation, uncertain jobs, storage/sync failures
and conditions that prevent further work. Say what was actually observed: unknown
capacity is not zero capacity, a timeout is not proof of OOM, and a missing
heartbeat is not proof that a detached job has stopped.

Include the project/task/attempt when known, incident identity, observation time,
last successful progress, symptom and evidence, affected work, repair attempted
and outcome, next action and any necessary user intervention. Report recovery or
material escalation as an update. Deduplicate unchanged incidents across wakes;
keep historical failures. Continue scoped automatic repair and independent work
within existing authority instead of turning an alert into a global stop gate.

The runner's `alerts` and `health` commands expose local records independently of
SQLite; see [simple-runner.md](references/simple-runner.md#exception-reporting).
`report-issue` can retain evidenced resource/tool failures observed by the host.
Local persistence means pending report, not successful notification. The active
agent or configured notification-capable host must actually relay the report and
retain its delivery outcome separately; do not invent a webhook, email sender or
delivery receipt. If command execution is unavailable, report using the working
conversation/scheduler channel first and save evidence where access remains.

On each real background wake, inspect new alerts and the last health record
before claiming a project is running. A destroyed or CPU-starved host cannot
guarantee its own report: an independently live scheduler/monitor must observe
the missing or stale identity. State the actual observation cadence and delivery
limits. Skill installation does not activate that monitor. Preserve explicit
user pauses; adding a report rule never resumes research.

## Checks produce feedback

There is **no 20-to-15 candidate requirement and no Gate 0 PASS prerequisite** for
simple-mode reading, derivation, code generation, design or diagnostic execution.
These are explicit policy changes for this edition. Do not silently invoke the
full edition's admission checker, candidate ledger or native scorer checker as
prerequisites for this loop.

A failed check blocks only the action or claim that consumes it. The work needed
to repair that check must remain possible:

| Observation | Next useful work |
| --- | --- |
| Missing evidence or paper definition | Read or implement the specific missing part |
| Wrong derivation or assumption | Repair the mathematics; revise the prediction |
| Crash, shape error, numerical bug | Repair code, then rerun the affected check |
| Wrong or ambiguous evaluation | Repair/clarify the evaluator; withhold that comparison claim |
| Valid experiment contradicts the idea | Analyze the mechanism; revise or explicitly retire this idea |
| Uncertain result | Improve controls, precision or experiment design |
| Resource shortage | Reduce scope, optimize or wait for a known resource |
| Run still active / launch acknowledgment lost | Wait for its event / reconcile the same run identity |

Without an official scorer, implement the metric from the authentic published
mathematical definition and validate that implementation as described in the
reference. This is not an assertion of official scorer parity. Unqualified scores
may diagnose code; they cannot establish comparative scientific success.

## Continue without a blind retry loop

Within existing scope and budget, perform the next useful action without asking
for routine approval. Keep one active idea, cumulative effort and retained
failures. Materially change the cause of a failure before repeating the same
expensive run. At a per-issue repair limit, return to analysis and change strategy;
do not silently disable an entire project or its scheduler.

Wait only for a concrete external condition and retain its job/task identity.
An uncertain launch must be reconciled before retrying or replacing that task;
independent ready tasks may launch within unreserved budget. An actual resource
or permission boundary, exhausted agreed budget, user's stop, or completed goal
can pause/end this goal. Record the reason, what can resume it and any remaining
independent work. Do not invent infinite continuation after the host ends.

Use [simple_runner.py](scripts/simple_runner.py) to execute commands and continue
from their real receipts on a live Linux/Python host. Read
[the runner protocol](references/simple-runner.md) before initializing it. Submit
concrete argv tasks with dependencies and timeouts, then start `run`. The runner
keeps waiting when tasks or decisions are pending. It publishes failures, watches
external event files and schedules ready work; no model call occurs on an idle poll.

In Work, **stay with the active goal**: read `inbox`, inspect its real logs and
artifacts, repair code or revise the idea, then `respond` with concrete next tasks.
Use `milestone`/`progress` for preflight and intermediate repairs; `research_cycle`
records the hypothesis-to-decision chain. `completion` closes only the current
idea. For `bounded_task` or `research`, a whole-goal `complete_goal` needs the declared objective's
evidence-backed `goal_assessment`, no remaining scoped work, and the current
`goal_contract_version`. Do not use a local success to shrink that objective.
After an idea-only closure, handle the next decision and explicitly select a
successor when useful work remains. If a previous closure was premature, use the
versioned `revise-goal --reopen` correction at a quiet boundary; preserve its old
report, same idea lineage and all cumulative limits rather than deleting state.
Mark replacement tasks with `supersedes`. Rebuild affected downstream tasks with
new IDs and explicit dependencies on the repair; a successful A2 does not change
an immutable B that still depends on failed A. Address every `downstream_rebuild`
observation with useful work or an explicit scoped cancellation.
When no useful independent work is ready, use bounded `wait` to await a meaningful
event and repeat. Writing a next-action note or starting a supervisor alone does
not complete the user's request for continued verification and repair. An
explicitly configured agent command can handle this same decision protocol
unattended; it is a bounded, accounted command, not an automatically installed
provider. Never claim a new Work task will be created after the host disappears.

Before a model/context limit, save real partial work and a structured continuation
with checkpoint hashes and a concrete next action. Use the next bounded decision
to continue from those artifacts; do not restart the same completed segment.
Malformed or truncated output is retained for diagnosis, never invented into a
successful response. A broken agent command can be repaired with `repair-agent`
under the same accumulated budget; independent result intake continues meanwhile.

The runner records the executable and guidance source used for future work. When
updating an authorized skill revision, use the documented source adoption at a
quiet supervisor boundary, then restart from the adopted source. Keep existing
attempt pins and receipts. Neither changing a file in place nor the legacy
SkillRegistry's declaration-only promotion activates executable changes.

[simple_loop.py](scripts/simple_loop.py) retains the scientific journal: evidence
hashes, revisions, feedback and cumulative observations. New journals have no
implicit 20-observation cap; existing explicit limits remain. The runner owns
per-task waits and uncertainty so one affected task does not block independent
work. Neither helper certifies science. If Python is unavailable, preserve the
checkpoint and continue the useful work supported by that host.

## Deliver and hand off

Report: the question, what actually ran, what was learned, what changed and the
next action. Distinguish supported, not supported, inconclusive and implementation
repaired. A repaired bug is not a successful research claim. Link the actual
artifacts and carry source identities, pending runs and total budget forward.

The companion writing and figure skills remain available when requested. Full
workflow modules and the existing `research-autopilot` runtime remain in this
package for explicit full-edition use; their 20-to-15/Gate 0/G01/E04 policy is not
this default loop. Switching a live full-edition run requires a new explicit
project checkpoint, not relabeling old PASS flags. See the repository's
`docs/RSI_SIMPLE.zh-CN.md` for usage and `docs/RUNTIME.md` for the optional legacy
runtime. Publishing this skill edition targets the owner-selected `rsi-simple`
branch; scientific project delivery keeps its own authorized destination.
