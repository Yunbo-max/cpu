# Execute, observe, decide, continue

Use `scripts/simple_runner.py` for real current-host execution. It requires Linux
and Python 3.11+ with the standard library. Work CPU is sufficient for CPU tasks;
Local, SSH, a GPU and a model API are not prerequisites. Initialize a finite
budget appropriate to the user's existing authority. Installing the skill does
not start this process or create a platform lifecycle hook.

The runner handles task scheduling, detached workers, receipts, watched events
and decision delivery. The active agent handles research judgment and code
repair. An explicitly configured agent command can handle the same inbox on a
resident host. A command's exit code is not a scientific verdict.
For a disposable real-process check, use the
[CPU repair demo](../assets/examples/simple-runner-demo/README.md). Its scripted
adapter qualifies execution plumbing, not an LLM's research judgment.

## Native subagents and the execution runner

Follow [simple-collaboration.md](simple-collaboration.md) to delegate research and
implementation through tools actually exposed by the current host. The active
coordinator receives results, inspects artifacts and submits or responds to this
runner once. The runner does not automatically spawn platform agents, install a
provider or restore vanished native agent sessions.

Keep native assignment records outside the runner task/response schema. Native
agent IDs are not task receipts; child completion is not accepted input evidence.
Once outputs are reviewed, pin their actual hashes in dependent task `input_refs`.
Only the coordinator mutates the shared journal and runner decision state. Use
per-assignment waits; a waiting child need not put the whole idea into journal
`wait` or `uncertain_launch`. Preserve and reconcile any actual experiment run
identity separately from its supervising agent.

Runner `max_concurrency` limits command attempts, not native agents. All proposed
experiments share the project's existing resource and execution budgets. Keep
native model usage separately as measured or unknown; command seconds do not
measure its token bill. Children propose experiment commands to the coordinator,
which dispatches bounded runner tasks after inputs and resources are ready.
Shared performance timings need an isolated interval on the actual execution host;
agent availability or `max_concurrency` alone cannot ensure uncontended timings.
Record thread/device placement and competing work in the scientific plan/results.

## Declare the overall objective

Keep the user's overall `goal` distinct from the current hypothesis and next
command. Configure `goal_contract` with `mode` and `completion_criteria`, a list
of unique `{ "id": STRING, "description": STRING }` records. This controls final
closure, not admission to reading, code or experiments.

| Mode | Use and end condition |
| --- | --- |
| `bounded_task` | The user actually requested a finite check/repair/deliverable; assess those criteria when done |
| `research` | Carry hypotheses through tests, interpretation and next decisions; final closure needs declared criteria and an explicit research-cycle record |
| `continuous_research` | Keep advancing serial hypotheses while useful work and authorized resources remain; do not automatically complete the whole goal after a result |

For a request to research this paper/topic, a suitable contract could be:

```json
{
  "mode": "research",
  "completion_criteria": [
    {"id": "comparison", "description": "Evaluate a falsifiable improvement against appropriate baselines with the authentic task, metric and resources configured for this project"},
    {"id": "interpretation", "description": "Explain the measured outcome and resolve the checks necessary for the scoped conclusion, retaining negative evidence and limits"}
  ]
}
```

Bind these criteria to the actual user's request. Do not change them to “paper
found” or “code runs” merely because those milestones finished. `continuous_research`
does not grant infinite resources: explicit attempt, time and resource boundaries
still pause execution. No fixed count of candidates, seeds or cycles substitutes
for the scientific question.

## Connect scientific design to executable tasks

For research, read [simple-experiment-design.md](simple-experiment-design.md).
Use `assets/templates/simple-experiment-plan.json` and
`assets/templates/simple-experiment-results.json` as editable records, not completed
evidence. The scientific plan is distinct from the runner's task submission JSON:
the former explains comparisons and interpretation; the latter supplies argv,
dependencies, timeouts and artifact paths.

```bash
python3 SKILL_ROOT/scripts/simple_resources.py --output PROJECT/resources-v1.json --timeout-seconds 3
python3 SKILL_ROOT/scripts/simple_design.py check --root PROJECT --plan experiment-plan-v1.json --goal-contract-version N
python3 SKILL_ROOT/scripts/simple_design.py check --root PROJECT --plan experiment-plan-v1.json --results experiment-results-v1.json --goal-contract-version N
```

Use actual project paths and the observed goal version. Restore allocation and
execution-host settings from project setup and later authorized revisions; keep
them in the scientific plan's `resources.authorization`, not as unsupported
hardware fields in the runner config. Run the resource probe on that execution
host; it observes local hardware/constraints, not other hosts' capacity or
permission. Record allocation, remaining time and measured calibration separately.
The chat host's inventory is not a default project allocation. Missing GPU
tooling produces an unknown observation, not a mandate to
buy resources or abandon CPU work.

The design helper reports structural/evidence gaps and claim-scoped next actions.
It neither runs experiments nor changes journal state, and an empty gap list is
not scientific approval. Read the actual papers, metrics, raw outputs and analyses.
Review each affected claim's missing work while continuing independent useful work.
Do not add this checker as a universal task-admission gate.

Map each planned comparison to concrete task IDs and versioned outputs. Include
the actual immutable experiment-plan hash plus consequential code/data/configs in
task `input_refs`. For a changed design, retain the old plan, record whether results
had already been inspected, create new tasks and rebuild affected descendants.
After execution, bind results to the exact plan bytes and actual per-arm artifacts;
include analysis outputs and the complete run inventory, including failed and
excluded runs with reasons. Use these records as real `research_cycle` evidence.
Plan and result file hashes establish identity, not chronology or scientific truth.
Select tasks for their ability to change the next research decision relative to
cost: a strong comparator, independent numerical check, cost decomposition or
representative failure-state pilot can take priority over more configurations.
Keep correctness constraints separate from aggregate performance criteria and
account for unsuccessful attempts and fallback overhead. Preserve old frozen
criteria when a new hypothesis or metric correction creates a successor plan;
do not reinterpret old outcomes as if the new plan existed before them.

## Start with a concrete task

In examples, replace `SKILL_ROOT` and `PROJECT` with absolute existing paths.
Create `config.json` outside the runner's private state. This is an illustrative
engineering budget, not a universal research default:

```json
{
  "idea": "method-a",
  "goal": "Locate and repair the numerical instability in this method",
  "goal_contract": {
    "mode": "bounded_task",
    "completion_criteria": [{"id": "repair", "description": "Reproduce the instability, repair its diagnosed cause, and verify the affected behavior with retained evidence"}]
  },
  "limits": {
    "max_attempts": 12,
    "max_command_seconds": 600,
    "deadline_seconds": 1800,
    "max_concurrency": 1
  }
}
```

This example is an intentionally bounded repair goal. For research on a topic,
use the broader objective and research contract above; feasibility is only a
milestone within it. Missing legacy contracts are exposed as undeclared, not
silently inferred to mean a bounded task. Work may continue, but declare the goal
through `revise-goal` before making a new overall completion claim.

Use measured command bounds and the actual user's budget. A task reserves its
whole timeout plus three seconds of cleanup headroom before launch, then settles
actual elapsed command time from its
receipt. Unknown attempts retain their reservation. Agent-command invocations
also consume attempts and time. These are execution seconds, not token bills,
memory limits or scientific iterations. Set thread/process/device placement and
measure RAM/VRAM separately against the project's configured hardware allocation.
If a timeout plus cleanup cannot fit, the runner reports that specific resource
constraint so the decision-maker can reduce scope or cancel obsolete work. When
even the configured agent command cannot fit, a Work agent can still inspect and
respond directly. If `run` exited at that budget boundary, restart it after an
authorized, smaller task plan is submitted; the original counters and deadline
remain unchanged.

Write `plan.json` for a script that actually exists:

```json
{
  "submission_id": "initial-diagnostic-v1",
  "idea": "method-a",
  "revision": 1,
  "tasks": [{
    "task_id": "diagnostic-v1",
    "argv": ["python3", "diagnose.py"],
    "phase": "diagnostic",
    "purpose": "Reproduce the instability and preserve its diagnostic output",
    "timeout_seconds": 30,
    "cwd": ".",
    "depends_on": [],
    "input_refs": [],
    "outputs": []
  }]
}
```

Tasks use argv arrays with no implicit shell. Use project-relative working
directories, evidence paths and output paths; do not use symlinks or traversal.
Pin consequential code/data with `input_refs: [{"path": "diagnose.py",
"sha256": "ACTUAL_SHA256"}]`. Do not submit that placeholder as a hash. List files
the command must produce in `outputs`; stdout/stderr are retained independently.
Use versioned output paths so later work does not overwrite evidence. Unknown
dependencies, cycles and conflicting reuse of a task ID are rejected.

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT init --config config.json
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT submit --plan plan.json
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT run
```

`run` stays resident during ordinary idle or decision waits. In Work, keep it in
a live, resumable command session and retain that session identity. Do not wait
for `run` to exit before reading the inbox from another execution channel. One
supervisor lock prevents concurrent supervisors for the project.

## The active Work loop

1. Inspect `status` and `inbox`. Read the exact failed command, receipt, stdout,
   stderr, input/output references and budget before deciding what happened.
   Restore scientific-policy, executor/source and wake identities separately;
   a Simple command receipt does not imply a migrated scientific decision policy.
2. Do useful independent source, mathematics, code or analysis work. If a decision
   is open, repair the affected layer or choose a discriminating next experiment.
3. Write a response bound to that request's idea and revision; submit `respond`.
   Repair tasks use new IDs and `supersedes: OLD_TASK_ID`. A failed predecessor
   cannot satisfy a success dependency. Rebuild affected descendants explicitly
   with new IDs and replacement dependencies; retain the original failure.
4. When nothing independent is ready, use `wait --after LAST_SEQUENCE` with a
   bounded timeout. Read new events and repeat. A wait timeout is not goal failure
   or permission to announce completion. Do not end an active repair request just
   because a task is still running.
5. Mark the overall goal completed only when its actual criteria are answered.
   A user's stop, budget/access boundary or genuine block is a different state.
   Report a milestone without ending the active goal; perform its next action.

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT status
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT inbox
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT respond --response response.json
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT wait --after 0 --timeout-seconds 30
```

Use the numeric `sequence` from the last status/wait response instead of
repeatedly passing zero; this is not the string `event_id`. The inbox
snapshot contains `request_id`, `goal`, `goal_contract`, `goal_contract_version`,
the current question/idea state, `idea`, `revision`, `journal_version`,
unhandled `observations`, task/attempt state, remaining `budget` and `request_ref`.
There is one open request at a time. Results arriving while it is open remain
available for the next request rather than being silently discarded.
Full JSON snapshots retain history and can be large. Save command output to a
project log and inspect the relevant fields (`status`, `sequence`, `budget`, the
affected task/attempt and open request) instead of repeatedly copying the entire
history into the agent context. Retain the full file for recovery and review.
An hourly scheduler is a wake/recovery mechanism, not a limit of one task or batch
per activation. During the active session, keep handling eligible actions and
actual completions within its remaining authority and budget. Save the last
accepted checkpoint/sequence and read changed artifacts plus unresolved work on
the next wake; reread older evidence only when relevant to the current decision.
Do not infer background liveness between wakes or restart a user-paused project.

For end-to-end efficiency, preserve observed wake/scheduling delay, model and
integration latency alongside command CPU and wall time. Their scopes and clocks
must be explicit; sums of overlapping command durations are not elapsed project
time, and command accounting omits unexposed native model spend. Retain unknowns
in project telemetry notes rather than adding unsupported runner fields or claiming
exact total cost/speedup from command receipts alone.

## Exception reporting

The scientific decision inbox and a notification to the user are different
deliveries. Inspect new failures immediately and relay a concise user-visible
report through the active host, rather than only recording a repair task. A
configured decision adapter needs an actual permitted reporting channel; the
runner does not install email, webhooks or a model service.

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT alerts
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT health --max-age-seconds 30
```

These reads do not require SQLite and do not initialize, wake or mutate the
research project. They still require a usable Linux/Python host and this source
checkout; unavailable execution must be reported through the live host channel.
Alert records identify the incident, project, affected work,
observed reason, available evidence/log references and next action. The runner
exports committed exceptions, including failed/timed-out launches or commands,
invalid evidence, reconciliation, source and dependency problems, decision
errors, unusable external-wake records and budget conditions. DB/supervisor
exceptions have an independent persistence path with stderr fallback. Recording
failure must not hide the original error or block an otherwise usable task.

An alert's `delivery_state: local_pending_report` and `user_notified: false`
describe local recording only. A coordinator or externally configured reporter
must send it through the available authorized user channel, then retain the
observed delivery outcome and reported incident IDs in its own durable handoff.
No automatic sender or acknowledgement is supplied by these commands. Repeated
reads are not sends; unchanged incident IDs should not repeatedly notify the
user. Report a real recovery or changed condition as a linked update, preserving
the original record. Do not treat a sender timeout as proof of delivery or retry
unboundedly after an ambiguous send.

For an independently observed CPU/GPU/tool issue, retain the actual diagnostic
artifact and its SHA-256, then supply a nonempty evidence-ref array:

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT report-issue --issue-id cpu-window-1 --kind cpu_unavailable --reason 'Observed required execution capacity is unavailable; see diagnostic' --evidence resource-evidence.json --next-action 'Keep the affected experiment waiting; reconcile availability and continue authorized analysis'
```

Use an observed stable issue ID and true reason. This example does not probe the
host or establish CPU availability. Supported kinds include `cpu_unavailable`,
`gpu_unavailable`, `resource_unavailable` and `runtime_issue`; the label is the
caller's evidenced judgment, not an automatic diagnosis. An optional GPU missing
from a CPU-only task is not proof the task cannot run. Resource probes provide
observations, not allocations or leases. If tools/CPU cannot execute this command,
report directly through the still-working user/scheduler channel and preserve
what evidence is accessible; do not block reporting on creation of a local file.

`health` checks the recorded supervisor's actual Linux identity. Distinguish
last observed activity, live identity, stale activity, orderly exit and lost or
unknown identity; none by itself certifies scientific progress or the state of
every detached attempt. A live identity with activity older than the positive,
finite `--max-age-seconds` threshold is stale; the default is 30 seconds. Choose a
threshold appropriate to the actual polling and diagnostic duration. A lock
contender must not replace the owner's health
record. Inspect receipts and reconcile uncertain jobs before any restart.
An independent live watcher is required to observe SIGKILL, a hung supervisor or
host destruction. A local health file cannot send a message when its entire host
is unavailable. The existing scheduler's actual cadence limits discovery; never
promise instant alerts without an active transport and external monitor.

Every report should state: observation time and last successful progress when
known; project/task/attempt; symptom and evidence; affected and independent work;
attempted bounded repair and result; next action and genuinely required user
help. Keep cumulative budgets, failure history and user stops. A configured
background task must report access/execution failures on its next actual wake
instead of silently presenting stale running status. Updating its reporting
policy preserves its current enabled/paused state.

## Respond with work or a scoped conclusion

Every response requires `response_id`, `request_id`, `idea`, `revision`, `reason`
and the observed `goal_contract_version` for a declared goal,
and at least one concrete action. For example, after actually patching code,
submit a new diagnostic task:

```json
{
  "response_id": "repair-response-v1",
  "request_id": "COPY_THE_OPEN_REQUEST_ID",
  "idea": "method-a",
  "revision": 1,
  "goal_contract_version": 1,
  "reason": "The traceback localizes division by a zero norm; the code now handles that case, so rerun the diagnostic",
  "tasks": [{
    "task_id": "diagnostic-v2",
    "supersedes": "diagnostic-v1",
    "argv": ["python3", "diagnose.py"],
    "phase": "diagnostic",
    "purpose": "Check the concrete normalization repair after diagnostic-v1 failed",
    "timeout_seconds": 30
  }]
}
```

This example describes a repair that must really have occurred. Pin its actual
new code hash with `input_refs` and retain the old failure. The response may also
contain:

| Field | Meaning |
| --- | --- |
| `events` | Normal journal feedback, revisions, retirement/replacement or completion; each event has its own id and real evidence when required |
| `tasks` | New immutable tasks using the plan task schema |
| `continuation` | A partial result with checkpoint references and the next action; use alone as described below |
| `cancel_tasks` | IDs of obsolete queued/running tasks; cancellation retains history and must settle before goal completion |
| `await_tasks: true` | Wait for unfinished tasks, or refresh the inbox when newer observations arrived after this request |
| `wait` | `{ "identity": "external-result-v1", "event_path": "events/result-v1.json" }` |
| `goal_assessment` | Final criterion assessments `{criteria: [{id, conclusion, evidence}], remaining_work: [], reason}` bound to the current goal version; assessed evidence is not automatic scientific certification |
| `complete_goal: true` | Finalize a declared bounded/research goal with its goal assessment and journal completion, all attempts settled and no unhandled newer observations; never use for a mere milestone or continuous goal |

See [rsi-simple.md](rsi-simple.md#durable-journal-interface) for exact journal
events. `valid_negative_result` routes to analysis; it does not automatically end
the goal. `revision` advances the same idea. Replacement requires explicit prior
retirement/completion and preserves cumulative budget. A completion event needs
real evidence and `outcome` of `supported`, `not_supported`, `inconclusive` or
`repaired`; it reports the decision-maker's bounded judgment, never an automatic
science certification. For an intermediate bug fix, use progress or revision.

Use a `milestone` event with `label`, `next_phase`, reason and real evidence when
CPU feasibility or another intermediate deliverable finishes. It leaves the
same idea active. A `research_cycle` event records `hypothesis`, `prediction`,
`result`, `interpretation`, `next_action`, reason and the actual evidence for the
chain. It does not close the idea or goal and is not automatically created for
each command or seed. Records should link the real plan/results/analysis; the
runner checks their identity, not whether the scientific interpretation is true.
For runner decisions, a cycle is bound to the current `goal_contract_version`;
an omitted event-level version is supplied by `respond`, while an explicit stale
version refreshes the decision. Historical unbound cycles stay unbound. Reusing
old evidence for a revised goal requires an explicit current-version reassessment
with a new event ID; it does not turn an old run into a new experiment.

When an idea closes but the research objective remains, the next inbox includes
its closed state and asks for further work. Explicitly replace a retired/completed
idea with a substantively justified successor; do not submit ordinary tasks for
the closed identity. Decision-command receipts remain execution observations,
so they do not force a closed idea to accept new scientific progress.

For final closure, copy the current `goal_contract_version` and provide an
assessment for every declared criterion, with its exact `id`, a substantive
`conclusion`, and real `evidence` references. `remaining_work` must be empty only
when no work necessary for that scoped objective remains. A research contract
also needs an explicit research-cycle record for the current goal version; more cycles are required only by
the unresolved question/criteria, not a fixed quota. A missing assessment or
unfinished objective feeds a corrective decision, not a successful completion
or an automatic disabling of a healthy adapter. A continuous goal cannot be
closed by `complete_goal`; a real budget boundary remains a pause.

Responses cannot silently expand the execution budget. Replaying identical
submission/response IDs is idempotent; conflicting or stale responses fail before
partially adding work. Scientific journal feedback and task additions commit
together. Receipts remain retained even when their journal bridge needs repair.
An events-only response must lead to a new explicit decision request; writing a
next-action note without tasks, an observed wait, a terminal outcome or another
decision does not connect the execution loop.

## Correct a narrowed goal or premature completion

Do not delete a checkpoint, rerun an initial configuration to reset it, or change
old evidence from “feasibility” into “research complete”. At a quiet boundary,
adopt the intended source as described below, write the corrected contract to a
JSON file, and use the observed goal-contract version:

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT revise-goal --contract goal-contract.json --goal 'Investigate the method through hypotheses, comparisons and result-driven revisions within the existing budget' --reason 'Correct the earlier feasibility-only interpretation of the user request' --expected-version N --change-id goal-correction-v1 --reopen
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT run
```

The file uses the same `{mode, completion_criteria}` object as `goal_contract`.
Omit `--goal` when its text remains accurate. Use `--reopen` only to correct an
actual premature closure. This appends the earlier contract/closure and the
correction, retains the idea identity with a new revision when reopened, and
refreshes requests bound to the old goal version. It preserves attempts,
evidence, source history, cumulative usage and the original deadline. It cannot
silently undo the user's stop or authorize a fresh budget. Replaying an identical
change ID is idempotent; a conflicting change or stale expected version is refused.

Previously undeclared contracts remain historical facts, not retroactively
certified research goals. Inspect their actual scope before recording a new one.
The legacy journal `iterations` counter counts work observations; report explicit
research-cycle records separately from that field and from runner attempts.

## Automatic decisions on a resident host

Only when an agent command is already available and authorized, add this to the
initial config, substituting its real executable and arguments:

```json
{
  "agent_command": {
    "argv": ["configured-agent", "--request", "{request}", "--response", "{response}"],
    "timeout_seconds": 60
  }
}
```

`{request}` and `{response}` become absolute JSON file paths. The command reads
the immutable request and writes a response in the protocol above, preferably
by atomic file replacement, then exits. It may inspect artifacts and generate
concrete repairs within existing authority. The runner consumes and validates
the response. Install no backend or paid provider merely to fill this optional
field; active Work decisions use `inbox`/`respond` without it.

An adapter invocation is a real bounded, accounted attempt. It occurs for a new
decision, not on every polling tick. Failure or invalid output exposes a precise
error and leaves the request available for concrete correction; it must not
launch identical failed decision processes indefinitely. A host must remain
alive for unattended execution. This mechanism does not create a new ChatGPT Work
task after platform termination.
If new observations arrive while an adapter is preparing a completion, the
runner retains that attempt's receipt and accounting, rejects the stale closure,
and supplies a fresh decision request automatically. This is a snapshot refresh;
a malformed or unsupported decision still requires a concrete correction.

## Repair a dependency chain

If A failed and B depended on A, submit A2 with `supersedes: "A"`. The original
A retains its failed outcome and records `replaced_by: "A2"`. B's immutable
contract still depends on A. The runner emits a `downstream_rebuild` decision
with the affected task and required replacement dependencies; it does not leave
this work hidden behind a blocked queue entry.

Generate B2 with `supersedes: "B"`, its actual new command/input/output contract,
and `depends_on: ["A2"]`. The controller performs this repair through the normal
response loop, without a new human approval. Do not copy a stale metric, source
pin or old output path merely to reconnect the graph. If an input artifact does
not exist until A2 finishes, retain the dependency and register the corresponding
pinned downstream check after the real artifact arrives. An intentionally removed
downstream check needs an explicit scoped cancellation and reason.

Supersession is not a success flag: an uncertain or live predecessor must first
be reconciled, and successful historical work is not relabeled. New task IDs,
the old receipts, replacement links and cumulative budget remain visible.

## Continue saved partial work

An adapter can return a complete, atomic response containing only its usual
response/request/idea/revision/reason binding, the observed `goal_contract_version`
for a declared goal, and:

```json
{
  "continuation": {
    "reason": "max_tokens",
    "checkpoint_refs": [{"path": "checkpoints/design-part-1.md", "sha256": "ACTUAL_SHA256"}],
    "next_action": "Continue the saved experiment design with the remaining ablations",
    "session_id": "adapter-session-identifier-if-available"
  }
}
```

Save the actual partial code/design before computing its hashes. Do not use the
placeholder as evidence. `session_id` is optional backend context, not authority
to invent an external process or launch it again. A length/turn limit can preserve
a usable checkpoint even when the adapter exits nonzero; its failed execution
receipt stays recorded while an intact, evidence-backed continuation creates the
next bounded decision. Every invocation still consumes the same attempt/time
budget. A new label or session cannot reset it.

The next decision reads the checkpoint and performs `next_action`. Repeating
unchanged checkpoint content is not progress and cannot create a blind automatic
retry loop. A truncated JSON document or missing checkpoint stays an explicit
repair problem. This protocol requires the adapter to save a valid continuation;
it does not override ChatGPT platform limits or create a new Work task after host
destruction. The active Work agent likewise saves project checkpoints before
handoff and continues from them when the same project is resumed.

## Repair the agent command

A failed adapter version is retained and disabled from automatic retries. Fresh
experiment results still enter the scientific decision inbox for the Work agent.
After diagnosing the failure, write the corrected `{ "argv": [...],
"timeout_seconds": NUMBER }` object to a JSON file and use the observed adapter
version:

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT repair-agent --config agent-fixed.json --reason 'Corrected the diagnosed adapter configuration' --expected-version N --repair-id adapter-repair-v1
```

This records a new configuration version and preserves goal, original request
errors, tasks, deadline and all usage. The same repair ID with identical content
is idempotent; a conflicting repair or stale version is rejected. A JSON `null`
configuration selects direct Work decisions without a subprocess adapter. Do
not delete the project database or expand limits to fix a backend command.

## Source identity and adoption

Check the project's scientific-policy identity independently of its executor and
scheduler. Follow the versioned migration guidance in
[rsi-simple.md](rsi-simple.md#restore-the-scientific-policy-as-well-as-the-process)
only when adoption for that project is authorized. Installing or updating a skill
does not change old frozen contracts, lift a user pause or migrate a full-runtime
workspace. A material unresolved conflict blocks the dependent policy decision,
not independent reading/repair. Preserve history and record any affected-claim
reassessment; do not silently import full candidate-count gates into Simple.

The simple runner snapshots its execution scripts and the simple workflow
guidance, including executable content. Requests and future attempts record the
adopted digest; detached workers launch the pinned helper. This is separate from
the old declaration-only `SkillRegistry`.
New snapshots pin fourteen files: the original seven runner/journal/guidance files
plus the experiment-design reference, design checker, resource probe and two
plan/results templates, plus the collaboration reference and assignment template.
Historical exact seven-file and twelve-file snapshots remain valid for their
original attempts; they do not acquire newer guidance retroactively.
Any other inventory or changed content is rejected. Adopting a new snapshot is
still required before reserving new tasks from changed source.

An authorized source update is adopted at a quiet boundary: finish/reconcile
active attempts, interrupt the idle supervisor, then use the source-adoption
operation from the intended updated source and restart. History and budget remain;
old attempts keep their actual old pins. Existing pre-pin `.2` records must remain
explicitly unpinned rather than receiving a fabricated historical source digest.
A different file on disk cannot silently replace a live worker. The active agent
can perform this handoff within already granted update authority; it need not ask
for a new routine approval. No provider installation or automatic promotion of
untested self-edits follows from this interface.

```bash
python3 UPDATED_SKILL_ROOT/scripts/simple_runner.py --root PROJECT adopt-source --reason 'Adopt the reviewed authorized update for future tasks' --expected-digest CURRENT_SOURCE_DIGEST --adoption-id source-update-v1
python3 UPDATED_SKILL_ROOT/scripts/simple_runner.py --root PROJECT run
```

Use the observed source SHA-256 digest from status, not a Git commit SHA. For an
older project with no recorded source pin, the expected value is `unpinned`.
Adoption does not stop an active supervisor for you; interrupt its execution
session at the quiet boundary, without requesting a goal `stop`. Reusing an
adoption ID is idempotent only for the same update. A different installed source
must not dispatch new work under an old source identity. Keep the source snapshot
alongside the project for recovery.

## External wake, interruption and stop

An external wait watches its project-relative event file. The producer should
atomically write a JSON object with matching `identity` and preferably a unique
`event_id`. The matching event is consumed once and produces new decision work.
A prose promise such as “wait until ready” has no observable condition and cannot
serve as a watcher. Retain the event file as evidence.

If the supervisor is interrupted, restart `run` on the same preserved project.
Detached workers keep their identities and may finish while the supervisor is
absent; the new supervisor consumes their original receipts. PID, Linux start
ticks and boot identity distinguish a surviving process from a reused PID. On
hosts with an outer-namespace `/proc` mount, observed identities and signal PIDs
are translated separately; a cross-namespace cancellation uses the live worker's
event file rather than blindly signalling the observed outer PID.
A durable launch marker prevents a second command launch for the same attempt.

If a worker itself dies in an ambiguous window, the task becomes
`reconcile_required`; its budget stays reserved. Do not infer that an absent
receipt means the command never ran. Inspect the original attempt and preserve
evidence before using the CLI's reconciliation operation. It can explicitly
close an uncertain attempt as failed/cancelled, conservatively charge its
reservation and permit a separately identified replacement. It cannot invent a
successful receipt. Independent tasks may continue when dependencies and remaining
resources permit.
If an authentic terminal receipt arrives before manual reconciliation, it takes
precedence and is ingested with its actual outcome and elapsed time. The runner
does not replace it with a guessed failed/cancelled result.

```bash
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT stop --reason 'User requested stop'
python3 SKILL_ROOT/scripts/simple_runner.py --root PROJECT reconcile --help
```

`stop` is an explicit goal stop, unlike killing only the supervisor. A live
supervisor/worker processes cancellation and retains its real receipt. Timeout
and cancellation target the owned command process group, including descendants
that remain in that group. Processes deliberately escaping it are outside this
control contract. Do not claim memory enforcement or arbitrary remote-job
cancellation. Preserve the entire project, state directory and referenced files
for recovery; a destroyed scratch host cannot recover bytes that were not saved.
