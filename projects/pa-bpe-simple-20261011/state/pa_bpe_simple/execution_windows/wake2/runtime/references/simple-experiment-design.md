# Simple research: from published experiments to executable evidence

## Contents

- [Scope and starting point](#scope-and-starting-point)
- [Read and extract published experiments](#read-and-extract-published-experiments)
- [Turn questions into an experiment matrix](#turn-questions-into-an-experiment-matrix)
- [Order work by the decision it can change](#order-work-by-the-decision-it-can-change)
- [Choose strong comparisons and decisive controls](#choose-strong-comparisons-and-decisive-controls)
- [Check measurement before explaining discrepancies](#check-measurement-before-explaining-discrepancies)
- [Plan statistics before interpreting results](#plan-statistics-before-interpreting-results)
- [Bind the design to authorized hardware and budget](#bind-the-design-to-authorized-hardware-and-budget)
- [Separate development from independent confirmation](#separate-development-from-independent-confirmation)
- [Connect the matrix to execution and collection](#connect-the-matrix-to-execution-and-collection)
- [Recompute raw results into tables and claims](#recompute-raw-results-into-tables-and-claims)
- [Choose the next action from the evidence](#choose-the-next-action-from-the-evidence)
- [Official reporting and review references](#official-reporting-and-review-references)

## Scope and starting point

Use this reference when designing or extending empirical research in Simple mode. Preserve the user's overall
objective and work on one active idea at a time. Read existing plans, source notes, results and pending tasks
before adding work. A useful experiment answers a question and changes a decision; a list of commands or
benchmark names alone is not a complete experimental design.

For a bounded repair, use only the checks needed to establish the repair's scope. For theory, organize
assumptions, proof obligations, counterexamples and verification; add empirical work only when it answers a
relevant question. This reference adds no Gate 0, 20-to-15 candidate quota, fixed seed count or compulsory
human review. Missing design evidence creates a task. It withholds only the affected scientific conclusion;
reading, implementation, diagnostics and independent work can continue.

## Read and extract published experiments

Start with the supplied paper and its closest relevant published alternatives. Read the full experimental
section, tables/figures, appendices and limitations, then inspect the actual repository files for loaders,
training, inference, scoring, configuration, aggregation and reproduction commands. An abstract, README or
search snippet does not establish how an experiment was conducted. Pin paper version, section/table/appendix
locators, repository commit and inspected file paths.

Create an extraction record for each relevant experiment, including negative or incomplete comparisons. Group
genuinely identical settings without losing their individual conditions. When details are absent or code
contradicts the paper, record that specific uncertainty and resolve it before relying on the comparison.

| Extract from the source | Adapt to our question |
| --- | --- |
| Question, claim and rival explanation | Which of our claims does this test, and what could refute it? |
| Treatment, published/simple baselines, controls and varied factors | Which arms are necessary here, and which source choices do not transfer? |
| Dataset revision, split, sample IDs/selection, preprocessing and leakage controls | What population and conditions will our conclusion cover? |
| Metric, denominator, scorer, aggregation and selection rule | What exactly will our commands measure and compare? |
| Independent unit, repetitions, uncertainty, exclusions and stopping | Which statistical assumptions remain defensible for our design? |
| Hardware, training/tuning/inference effort, time and memory | What requires a measured pilot on our authorized host? |
| Observed result, limitation and failed/omitted conditions | What evidence remains missing and what should we test next? |

Distinguish published claims from our observed reproductions. Reported numbers remain literature evidence
until comparability is established; do not insert them as if our runner produced them. Reuse valid existing
runs with their exact scope. Adapt the experiment's reasoning, not just its table layout or convenient
settings. Published practice can contain weaknesses; justify changes that address them.
Compare closest work by objectives, assumptions, information, computation and outcomes. Record the material
limitation our change addresses, its value for the user's task, and the distinct predictions of our explanation
and its closest rival. A renamed component or extra compute alone is not evidence of new scientific value.
Do this mechanism and counterexample audit while developing the active idea, before expanding its experiment
grid. Record whether the contribution is a new mechanism, a justified adaptation, a boundary or an implementation
improvement. A failed novelty claim need not erase useful engineering or negative evidence; revise the claim
and next question. Do not generate a quota of candidate cards to compensate for unresolved novelty.

## Turn questions into an experiment matrix

For each proposed claim, state its scope, falsifiable prediction, strongest rival explanation and smallest
decision-changing comparison. Keep broad aspirations separate from the claim currently testable with available
evidence and resources. Link claim IDs to the parent goal's criteria without shrinking that goal to a pilot.
Separate task quality, output stability/change, computational work and elapsed time. Choose a primary objective
and declare any quality constraints or cost tradeoff; lower movement does not by itself establish lower compute
or faster execution. If the target changes after results, retain the original question and version the new one.

Keep a versioned matrix beside the code. Each required row contains the following:

| Matrix item | Concrete content |
| --- | --- |
| Identity and purpose | Stable row ID, claim IDs, question, prediction and why this comparison changes a decision |
| Experimental arms | Method revisions, strong published/simple comparators and necessary controls |
| Conditions | Dataset/split/sample policy, model/task/scale conditions, factors and repetitions |
| Measurement | Metric/direction/denominator, scorer and analysis versions, independent unit and uncertainty |
| Execution | Actual commands/configs, task IDs/dependencies, pinned inputs, raw outputs and analysis outputs |
| Resources | Authorized host/device placement, measured or explicitly estimated cost, memory and total allocation |
| Decision and state | Outcome interpretations, required/optional status, observed state, result locator and remaining obligation |

Use claim-driven coverage: main comparison for effectiveness; component/replacement tests for mechanism;
independent conditions for generalization; sensitivity and failure regimes for material robustness boundaries;
quality versus cost when efficiency is claimed. Explain why a category is unnecessary for the actual claim. Do
not require all categories or an arbitrary Cartesian product for every question.

Distinguish designed, implemented, software-checked, executed, analyzed and supported. A required row that
lacks code, resources or results stays visible with its cause and next action. Preserve it across scheduling
windows. Optional showcase runs cannot replace a missing decisive comparison. A small pilot may establish only
feasibility while the method comparison and the parent research goal remain active.

## Order work by the decision it can change

Before a new batch, name the remaining uncertainty, competing explanations, and what each plausible outcome
would change. Prefer the least costly credible discriminator of that uncertainty. Cost includes implementation,
model/reviewer effort, experimental compute and waiting when observed; unknown costs remain unknown. Do not
run another broad grid merely because the last batch finished or a queue has spare capacity.

Use this ordering when it fits the claim, with independent work overlapping:

1. Audit the proposed mechanism against closest work and a counterexample or limiting case. Clarify whether the
   target is correctness, quality, stability or speed, and which evidence can distinguish the explanations.
2. Check the consequential evaluator and run a representative small comparison against a credible strong
   baseline. Develop an optimized exact/simple comparator alongside an efficiency method, before interpreting
   wins over a weak implementation. Missing comparator evidence limits the speed claim, not all development.
3. Profile the complete competing paths before investing in a local optimization. Retain raw component times
   and work counts, the workload and any unmeasured remainder. If a nonoverlapping component accounts for a
   measured fraction `p` of elapsed cost, removing it gives the optimistic ceiling `1 / (1 - p)` only when the
   remaining work is unchanged and `p < 1`. Account for added maintenance, transfers and fallback; do not invent
   fractions, add overlapping timers, or treat this ceiling as an observed speedup. With no profile, propose a
   bounded measurement rather than declaring the direction futile.
4. Use representative development cases to test whether the mechanism can work and expose failure causes.
   Include consequential difficult regimes, not only the easiest successful example. Recalibrate both arms
   across claim-relevant dimensions, ranks, sizes or devices before extending a small-scale performance verdict.
5. Expand promising comparisons to justified coverage, then freeze fresh confirmation. Stop or reduce a local
   optimization when its measured opportunity is too small for the declared objective; retain infrastructure
   repairs that are independently necessary and explain their separate value.

This is a scheduling policy, not a sequence of global approvals. Missing evidence generates a bounded next
action with an owner, dependency and expected decision. A failed implementation returns to repair; a valid
negative result challenges the scoped hypothesis; neither automatically ends the parent research objective.
Predeclare pilot continuation/futility rules appropriate to its purpose, retaining all attempted cases. A
selected pilot remains development even if its metric later improves.

## Choose strong comparisons and decisive controls

For an effectiveness claim, include the strongest relevant published alternative that addresses the same task
and a credible simple or training-free alternative. Inspect actual compatible implementations and explain
excluded competitors. Record reproduction status, settings and any material deviation from the source. Missing
access or an unaffordable baseline leaves the corresponding superiority claim unresolved; it does not make a
weaker comparator equivalent. If one comparator fills both roles, record that fact instead of duplicating runs.

Match information access, data/splits, supervision, preprocessing, model capacity where consequential, tuning
opportunity, inference/search/selection budget and evaluation protocol. Record total tuning and failed-run
cost as well as the chosen configuration. When budgets differ intentionally, compare quality against cost and
state that estimand; do not attribute the entire difference to the method itself.

For mechanism claims, name the competing explanation each control can distinguish. Remove or replace the
proposed component while preserving other consequential settings. Test a budget/information-matched simpler
substitute when extra compute, parameters or labels could explain the gain. A versus A+B alone does not
establish B's independent effect or an A-by-B interaction; a complementarity claim needs the appropriate
component and interaction contrasts. Retain null and adverse results.
For stateful/online methods, distinguish a matched-start comparison (same input state, testing the local update)
from complete natural trajectories (each method's actual evolving history). Both may be needed. Shared seeds or
inputs alone do not establish shared state; retain state identities and initialization/warmup rules. A corrected
matched-start experiment cannot overwrite the original trajectory result or substitute for end-to-end evidence.

Choose sensitivity ranges on development evidence and justify their task relevance. Test generalization on
independent conditions tied to the stated scope; more seeds of one condition do not establish a new domain.
Inspect important worst groups, natural failure cases, drift or long tails with a denominator and sampling
rule. Keep failure taxonomy and causal explanation separate: an association is a clue, not proof of the
mechanism. Unknown boundaries limit the wording of the claim.
Align any proxy or predictor with the actual downstream decision: predicting whether an event occurs is not
necessarily predicting its solve cost or the best action. Name the label, decision time, cost of acquiring each
feature and baseline policy. Features requiring the result being predicted cannot establish a cheap predecision
policy. Evaluate decision benefit including feature acquisition and errors, and confine a negative proxy result
to the tested label, settings and use; it does not refute every alternative use of the feature.

## Check measurement before explaining discrepancies

When a numerical discrepancy could change the scientific interpretation, first verify the measurement layer
independently of the proposed mechanism. Derive the metric from its stated definition; where possible compare
with a mathematically equivalent stable formulation or separately written reference. Copying the same formula
into a second function is not independent verification. Check units, denominator, invariances, identical and
nearly identical inputs, degenerate/extreme cases and relevant precision/scaling. Bound tolerances from numerical
reasoning and observations rather than choosing them to hide a disagreement. Small constructed cases diagnose
software/math; they are not a substitute benchmark for a real-data performance claim.

Verify write/read round trips for consequential state, predictions and trajectories; compare shape, identity,
finite values and declared numerical tolerance. Preserve corrupt artifacts, logs and the versions needed to
diagnose them. Hashes prove byte identity, not that the saved values or scoring formula are correct. Correcting
an evaluator requires revisiting affected scores, explanations and eligibility, not merely relabeling old tables.

Choose the acceptance contract that matches the intended change. An implementation replacement may need
output/trajectory equivalence. A new algorithm generally needs task-quality constraints and declared stability
or cost objectives; different valid trajectories do not by themselves prove failure. Define hard correctness
constraints separately from soft performance targets and statistical uncertainty. If fallback is allowed by
the task, include attempted solver cost, fallback frequency, final quality and full end-to-end cost; do not
require zero fallback by default. A run that always falls back establishes no accepted endpoint benefit for
that implementation, not impossibility of all methods in its family.

Retain historical contracts and verdicts even if their thresholds were stronger than the useful research
question. A revised tolerance, fallback policy or objective creates a linked new design; it cannot retroactively
turn a failed frozen test into a success. Continue unrelated useful work while resolving measurement uncertainty.

## Plan statistics before interpreting results

Specify the estimand: effect/contrast, eligible population, metric direction, practically meaningful magnitude
and what outcome would change the decision. Identify the independent experimental unit and any pairing,
clustering or repeated measurement. Examples from the same trained model, correlated folds or repeated
decodings are not automatically independent model replications.

Record sample selection, randomness sources, seed policy, repetition count and its precision/budget rationale.
Use pilot variability to plan development work; label an underpowered or narrow experiment accordingly. There
is no universal number of seeds, sample-size threshold, confidence level or significance requirement. Avoid
promising a precise conclusion before measuring variability and cost.
For speed, define the paired whole-workload effect and practical margin with an uncertainty/repetition policy.
Do not make every individual noisy timing pair a required win unless a justified per-case requirement truly
belongs to the task. Report adverse cases and variability even when the aggregate meets its target; correctness
violations remain separate from a merely uncertain performance difference.

Choose an uncertainty method appropriate to the units and assumptions; distinguish standard deviation,
standard error and confidence interval. Preserve paired units where relevant. Account for dependence in
analysis rather than increasing the reported sample size with correlated observations. A point estimate is
valid as a declared exploratory summary, not an invented interval or significance test.

Declare primary outcomes and the family of comparisons. Specify multiplicity handling when selecting among
several tests, or clearly retain exploratory status. Record missing/unscored cases, invalid runs and exclusion
rules with denominators. Define finite stopping for precision, futility or resources before confirmation; if
inspecting results sequentially affects stopping, use an appropriate declared analysis or treat the result as
exploratory and arrange fresh confirmation.

Implement the analysis beside the experiment. Preserve its input inventory, configuration and outputs so
another pass can recompute the reported quantities. [statistics-and-claims.md](statistics-and-claims.md)
offers further techniques; using one does not import the full edition's admission or evaluator contracts.

## Bind the design to authorized hardware and budget

Start from the resource settings established for this project and their latest authorized revision. Record the
execution host, CPU/RAM allocation, GPU identities/count/VRAM where applicable, availability window, concurrency
and budget. Reuse them on resume; no fixed CPU, RAM or GPU allocation is built into this workflow. Missing
settings remain unknown rather than inheriting another project's limits, paper hardware or the chat host.
Copy the applicable allocation into each comparison's `resources.authorization` with its configuration source.

Keep three distinct records: the user's authorized allocation, a current host observation, and a measured
workload pilot. Use the actual authorized CPU/GPU host; do not impose CPU-only execution when GPUs are
authorized or add GPUs to a CPU-only allocation. A visible GPU model/count/UUID, idle utilization or free VRAM
is an observation, not permission, a scheduler allocation or an exclusive resource lease.
Observe the configured execution host. A CPU-only chat host does not restrict a project configured for remote
GPUs, and a local `unknown` GPU result says nothing about that remote host. Transient shortages adjust batch
placement without rewriting the allocation. Authorized setting changes require a retained configuration
revision and affected-cost recalibration; accumulated usage, failed attempts and existing run identities remain.

Record CPU affinity/quota, RAM limits, device identity and relevant available VRAM, alongside the environment
and data/cache/storage constraints. Respect the user's device selection and any scheduler or container
restrictions. Device indices can be remapped; resolve UUID/MIG visibility when needed instead of guessing a
device. Unknown inventory limits only work that depends on it, not unrelated ready tasks.

Collect an observation with the read-only resource helper:

```bash
python3 SKILL_ROOT/scripts/simple_resources.py --output PROJECT/resources-before.json --timeout-seconds 3
```

The snapshot reports observations and diagnostics; it does not reserve resources, configure thread counts, cap
memory or benchmark a workload. Preserve its time and host identity. Recheck transient capacity before
placement; a stale free-memory reading cannot guarantee a later command fits. Set actual CPU/thread/device
bounds in the workload or authorized host scheduler; runner concurrency alone is insufficient.

Run a bounded pilot for consequential method and baseline paths. Measure startup, training/inference/scoring
speed, peak RAM/VRAM, I/O and sustained throughput with real settings and representative native inputs. State
warmup/cache/batch conditions. Estimate full row and total matrix cost from measured work units with headroom;
unmeasured extrapolation remains an estimate. Include preprocessing, tuning, repeats, baselines, controls,
aggregation, confirmation, retries and failed attempts.
For performance measurements, control competing compute, thread/BLAS settings, device placement and run order;
record unavoidable contention. Pair arms under comparable cache/warmup conditions and repeat as justified.
Native subagents may read, derive or implement in parallel, but coordinate their numerical diagnostics and
experiments so they do not contaminate timed comparisons. Agent slots are not permission for competing timed
jobs. Process CPU time, wall time and GPU time answer different questions; none alone removes all interference.

Dispatch batches that fit both simultaneous capacity and cumulative authorization. Reserve room for essential
controls and confirmation; prioritize decision-changing work before expensive showcases. Serialize
memory-heavy arms or reduce justified development scope when useful. Never silently remove required
comparisons, change the scientific task or extend resources to make the current window appear complete. Keep
running/queued/blocked rows and their residual costs across batches. If the required comparison cannot fit the
total budget, report the exact unresolved claim and continue useful independent work; a smaller diagnostic
answers a narrower question.

## Separate development from independent confirmation

Label evidence as development, prospective confirmation or retrospective analysis. Maintain an exposure
record: which results, cases and conditions informed design, tuning, selection or exclusions, and when. Hashes
and timestamps establish identity, not that a person or model had never inspected the results.

Before confirmation, freeze the method/configuration, comparator policy, data and sample eligibility, metric,
analysis, comparison family, budgets and decision rules. Choose fresh evidence appropriate to the claim: new
independent units or conditions as required, not merely a new filename for inspected results. Keep the frozen
design and source pins. Broader claims need their own justified confirmation and coverage.
If selection used the test cases, new seeds alone do not make those cases unexposed.

If a result-affecting choice changes after exposure, retain the old design/results, record why, and create a
linked revision with new task IDs and valid fresh confirmation. Old results may inform development or an
explicitly retrospective analysis; they do not become evidence for a newly prespecified test. An evaluator bug
can require rescoring preserved predictions, but record the exposure and altered claim eligibility. Keep
infrastructure retry policy and every attempt visible; never select the most favorable rerun as confirmation
or replace failed units without a declared policy.

## Connect the matrix to execution and collection

Use [simple-collaboration.md](simple-collaboration.md) to parallelize ready source,
derivation, implementation or review work around this matrix. Keep one coordinator
for claim decisions and compute dispatch. Agent capacity does not multiply the
GPU/RAM allocation or remove experiment dependencies; accept and pin each worker's
actual artifacts before using them as inputs to a comparison.
Delegate early baseline inspection, independent metric checks, mechanism/counterexample review and cost
profiling when independent and useful. Give each assignment a decision it should inform and actual evidence
to inspect. A reviewer need not wait for an entire batch, and the coordinator need not wait for every reviewer
before doing work that does not depend on their findings.

Adapt [the plan template](../assets/templates/simple-experiment-plan.json) to the actual project. Its
`paper_designs` records feed `comparisons`; each `claim` names its `required_comparison_ids`. Record `scope`,
`exposure`, goal-contract version, idea and revision. Each comparison carries arms, data, metric, statistics,
execution and resource records. Use `not_applicable_reason` where appropriate; formal claims need a specific
explanation for having no empirical comparisons.
Record allocation in `resources.authorization`, observations in `inventory_refs`, and pilots in `calibration`.
Keep parent-goal comparisons outside this batch visible in `scope.residual_required_coverage`.
When useful, retain `workflow_binding` with the scientific and executor editions and evidence references.
An executor upgrade does not silently adopt a different scientific policy; resolve applicable guidance on
resume, keep history, and migrate only at the source-adoption boundary described in the runner guide.

The optional comparison `decision_review` records `next_decision`, distinct `objectives`, and a
`comparison_basis` of `implementation_equivalence` or `task_quality`. Its `baseline`, `metric`, `efficiency`,
`novelty` and `proxy` blocks track `unreviewed`, `planned`, `executed` or a justified `not_applicable`, with
evidence references. Use them selectively for the actual claim: identify the independent metric check,
measured profile/opportunity/full cost/timing isolation, mechanism difference and closest collision, or
prediction target and feature availability cost. Preserve unknowns; filling fields is not executing the checks.
The optional `outcome_rules.performance_policy` records whether every timing repeat must win or any fallback
must cause rejection, together with the task-specific reasons for those unusually strong requirements.

Run the read-only design check before consuming a plan or result for a claim:

```bash
python3 SKILL_ROOT/scripts/simple_design.py check --root PROJECT --plan plans/design.json
python3 SKILL_ROOT/scripts/simple_design.py check --root PROJECT --plan plans/design.json --results results/design.json --claim-id CLAIM --goal-contract-version N
```

Use the actual claim ID and current goal-contract version. The optional results file follows [the results
template](../assets/templates/simple-experiment-results.json), pins `plan_ref` and maps comparison/arm IDs to
real task/run IDs, artifact hashes and analysis references. Keep `not_run`/`partial` rows honest; do not
manufacture future receipts to fill a template. The helper returns gaps and scoped next actions; it does not
dispatch, verify resource authority or grant scientific certification. `documented` means planned arms have referenced
artifacts and analysis, not that they prove a claim.
Use result `conclusion` values `supported`, `not_supported` or `inconclusive`;
describe contradiction and narrower scope in the analysis/limitations, and record
repairs as journal events. An honest `not_run` row still reports missing evidence.
The helper's separate `decision_review.advisories` identify missing/unreviewed declarations and questionable
declared policies, with scoped next actions. They neither alter coverage/status nor fail the command merely
because review is pending. References may be checked for identity; the helper cannot establish baseline
strength, numerical independence, valid statistics, a truthful profile or originality from prose/hash alone.
Older plans remain usable without these optional fields; the coordinator still reasons about the relevant
questions and records useful follow-up instead of treating an empty advisory list as scientific acceptance.

Translate each ready matrix row into concrete runner tasks using [simple-runner.md](simple-runner.md). Keep
row-to-task mapping in the design artifact; task purpose should state the scientific question or engineering
dependency. Pin consequential code, data manifests, configuration, evaluator and design with `input_refs`. Use
versioned `outputs`; do not overwrite files referenced by old runs. Make collection/scoring/analysis depend on
the actual required experiment tasks. An incomplete comparison can yield a labeled partial analysis, not full
coverage.

For example, one comparison row maps to method and baseline run tasks, then a scoring task and an aggregation
task. The aggregation consumes both arms' raw inventories and emits a versioned result table plus its input
manifest. Its table cell records the row/claim, run IDs, denominator and analysis revision. Additional
necessary controls become explicit dependencies, not an unchecked paragraph.

Read receipts and logs after every batch. Successful process exit establishes execution status, not metric
correctness, fairness or support for a claim. Verify sample coverage, configuration and output identity before
consuming results. For repairs, retain failed attempts, submit replacement tasks with `supersedes`, and
rebuild affected downstream tasks with new IDs and dependencies. Reconcile uncertain attempts before replacing
them; independent ready work may proceed.

## Recompute raw results into tables and claims

Retain the complete inventory: successful, failed, invalid, negative, unselected and development runs, with
their role and eligibility. Count missing and unscored units explicitly. Keep raw predictions/measurements,
sample IDs, scorer outputs, commands, source/environment identities, logs, usage and analysis code together.
Distinguish elapsed time, CPU core-seconds, GPU/device time, command counts and model/agent usage. Include
setup, maintenance, rejected attempts, fallback and analysis costs appropriate to the claim; preserve both
component and complete-path measurements. Missing model usage or incomplete CPU telemetry stays explicitly
unknown or a lower bound. Neither numbered batches nor several seeds are separate scientific discoveries.

Recompute each reported table/figure from retained inputs. Trace every aggregate to its own comparison arms,
units, denominators, exclusions and uncertainty method. Check direction, units, joins, duplicate samples and
treatment/baseline pairing. Do not borrow another claim's evidence or reuse incompatible protocol totals.
Review at least the consequential raw-to-table transformations independently of the original interpretation; a
separate reviewer is useful when available, not a required service or approval gate. State any remaining
review limitations.

For each claim, record supported, partial, unsupported, contradicted or inconclusive, its tested scope,
adverse evidence, allowed wording and remaining work. A repaired implementation is a repair result. Software
tests and helper validation establish their stated engineering properties; neither certifies an empirical
claim. When source, data, scoring or analysis changes, re-evaluate affected conclusions and derived
figures/tables instead of retaining an old scientific verdict by label.

## Choose the next action from the evidence

| Observation | Next work |
| --- | --- |
| Invalid implementation or evaluation | Repair that layer and rerun/rescore affected evidence |
| Valid negative result | Test the challenged assumption or competing mechanism; revise or retire the idea |
| Uncertain effect or missing control | Improve the discriminating comparison or precision within budget |
| Positive development result | Complete required controls and fresh confirmation before broadening claims |
| Confirmation contradicts development | Preserve both; examine selection, variability, scope and mechanism |
| Resource or access block | Retain the required row and resume condition; execute independent useful work |

Record a research cycle only after connecting hypothesis, prediction, actual test, result, interpretation and
next decision. Rows, tasks and seeds are not cycle counts. Update the matrix and perform the next useful
action while scope/resources permit. For whole-goal closure, assess each declared criterion against its actual
evidence and remaining obligations; completing a pilot or one hypothesis is not enough.

## Official reporting and review references

Checked 2026-10-10: [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) and [NeurIPS
2026 Reviewer Guidelines](https://neurips.cc/Conferences/2026/ReviewerGuidelines). Use them to compare claim
scope, reproducibility, uncertainty, compute reporting and contribution-appropriate evidence. Review
expectations differ for theory, applications, feasibility and negative results. These references support
design and reporting judgment; completing this workflow is not a guarantee of acceptance.
