# Latest continuation — B048 pre-execution repair

Read notes/B048_findings.md first. Original B047 remains unrun and immutable;
use the qualified B047v2 plan/script when the retained memory gate clears.
Only the rerun signal threshold now uses the candidate minimum; reference data
is reserved for post-decision scoring. All 22 historical feature values match.
No native fit this wake. 45 terminal attempts, 642.4580039849707 command seconds,
24 recorded cycles (previous 23 was a summary error; this repair adds no cycle).
Last formal memory 7.890 GB, interim shared usage 8.229 GB, OOM counters zero.
Do not clear b047-memory-gate or launch native fits above the 7.5 GB gate.

---
# Previous continuation — 2026-10-12 PRAXIS Bike-43 lookahead transport

The active idea remains `praxis-near-optimal-tree-sets-v1`. Read
notes/B045_B047_findings.md first. The project was restored from exact Library
checkpoint version 10 after host replacement, all 899 manifest hashes passed,
the original absolute root was preserved, and every retained attempt was
already terminal. The isolated PRAXIS environment was rebuilt from pinned local
source; no model fit occurred during environment restoration.

B045 completed the frozen Bike-43 hash/lookahead-1 comparison. It returned the
same minimum objective 4,138 and the same 88 eligible canonical tree identities
as retained exact/lookahead-4 at threshold 4,262: identity recall 1.0, no missing
or extra trees. Fit time was 0.688 s, 0.113x retained hash/lookahead-4; peak RSS
was 191,076 KiB. Thus the Compas upper-tail deficit is not universal across the
two tested datasets.

B046 applied the unchanged Compas-derived tail rule. Bike's top-two fraction
was zero, so the rule correctly skipped and the one-unit cost inequality passed
(2.253 s adaptive versus 8.545 s direct lookahead 4). This single case does not
identify sensitivity and does not reverse B043's aggregate cost-futility result.

B047 is frozen as ten fresh Bike bootstrap pairs under hash/lookahead 1/4, but
has not run. Formal preflight readings of 7.541 and 7.589 GB exceeded the 7.5 GB
launch gate; OOM counters remained zero. The runner is waiting on
`resources/B047_resource_gate_cleared.json`. Only create that event after a
fresh formal reading <=7.5 GB with zero OOM counters, then submit the unchanged
B047 plan/script. All 44 attempts are terminal; cumulative command time is
642.34168149997 s and 23 research cycles are recorded. No validated new method
exists.

---

# Previous continuation — 2026-10-12 PRAXIS Bike-43 exact-depth audit

The active idea remains `praxis-near-optimal-tree-sets-v1`. Read
notes/B044_B045_findings.md first. Heart-42 is not present in the pinned author
release, so no unverified reconstruction was used. B044 instead used the
byte-verified author-tracked Bike-43 data with the paper's lambda=0.02, depth=5
and epsilon multiplier=0.03.

At lookahead 4, hash and exact cache keys both returned minimum objective 4,138,
threshold 4,262 and exactly 88 eligible trees. Their full objective histograms
and canonical tree-identity multisets matched, with zero missing or extra
identities. Hash fit time was 6.110 s versus 10.500 s for exact, and peak child
RSS was 195,696 KiB versus 1,451,336 KiB. This supports hash/lookahead-4 as an
empirical exact-depth control on two tested native datasets; it is not a
universal proof or a validated new method.

B045 is frozen to compare one Bike-43 hash/lookahead-1 arm against B044's
retained exact/lookahead-4 identities. It did not run because shared memory
failed the prelaunch gate: the formal probe read 7.606 GB and later observations
reached 8.246 GB with no scientific child. OOM counters remained zero. The idle
runner was stopped at a quiet boundary with all 42 attempts terminal; cumulative
command time is 639.642 s and 21 fully recorded research cycles remain. Resume
only after a fresh formal memory.current <=7.5 GB, then submit
plans/response_B044_cycle_and_B045.json after refreshing its request id. Do not
replan B045 from outcomes or rerun B044.

---

# Previous continuation — 2026-10-12 PRAXIS identity mechanism and cost result

The active idea remains `praxis-near-optimal-tree-sets-v1`. Read
notes/B040_B043_findings.md before older notes. The earlier shared-memory hold
cleared at a measured 3,121,516,544 bytes with unchanged zero OOM counters.
B040 then compared hash/exact keys crossed with lookahead 1/4 on the full
Compas-44 lambda=0.01 setting and validated canonical per-tree identities.
Hash and exact keys were identical at each fixed lookahead. Both lookahead-1
arms omitted the same four objective-1900 identities from the 7,074-tree
lookahead-4 reference while preserving the minimum objective 1845. This
attributes the observed upper-tail deficit to lookahead depth, not hash keys,
for this setting.

B041 prospectively repeated the four-arm comparison on ten new fixed project
bootstrap samples (40 native fits). All minimum objectives agreed; hash and
exact identities agreed at both lookaheads in 10/10 samples. Three samples had
lookahead-1 deficits of 12, 7 and 4 identities, confirming the mechanism on
fresh samples. Peak child RSS was 254,568 KiB and no OOM occurred.

B042 found a retrospective candidate-only signal that caught all six exposed
deficit cases but selected 15/21 cases for rerun. B043 rejected the resulting
run-from-scratch adaptive policy on measured end-to-end cost: 9.964 seconds
versus 6.994 seconds for direct hash/lookahead-4 (1.425x slower). Do not launch a
fresh confirmation of that rejected policy. Use hash/lookahead-4 as the current
exact-depth empirical control, then inspect and predeclare the analogous native
Heart-42 comparison before considering cache sharing. This is not a universal
exactness theorem or a validated new method.

All 41 attempts are terminal; cumulative runner command time is 616.230 seconds
and 21 research cycles are recorded. Window-0008 increased only finite safety
ceilings. The runner was intentionally stopped at a quiet boundary; its stale
health record must not be interpreted as an unknown scientific process.

---

# Latest continuation — 2026-10-12 PRAXIS boundary audit and resource hold

B039 used preserved B037/B038 JSON to localize every lambda=0.01 deficit. The
full-data four-count deficit is exactly at objective threshold 1900. Bootstrap
seed 2026101203 misses 5/5/2 counts at objectives 1903/1908/1909 with threshold
1909; seed 2026101206 misses four at objective 1931 with threshold 1932. Thus
all observed misses are in the eligible upper tail, zero to six integer objective
units below the cutoff, while every minimum objective remains unchanged. See
results/B039_histogram_difference_audit.json.

Static source audit found that the pinned public API exposes per-tree signed
paths, leaf predictions and objectives. B040 therefore freezes a four-arm
`key_mode` (hash/exact) by `lookahead_k` (1/4) comparison and canonical tree
identity extraction, rather than proceeding directly to lambda=0.005. This can
separate hash, lookahead and interaction effects and replace histogram overlap
with actual full-data tree-set recall if its internal count checks pass.

No new scientific attempt was launched. Shared memory with no scientific child
ranged near 7.86--7.91 GB and later peaked at 8,579,702,784 bytes, above the
project's stricter 8,000,000,000-byte ceiling; OOM and OOM-kill counters stayed
zero. A trial idle runner was stopped before task submission. Resume only when
pre-run memory.current is at most 7,500,000,000 bytes. Window-0007 extended only
finite safety ceilings; cumulative usage remains 37 attempts and 553.557 command
seconds, with 18 research cycles.

---

# Previous continuation — 2026-10-12 PRAXIS Compas-44 confirmation

The active idea remains `praxis-near-optimal-tree-sets-v1`. Read
notes/PRAXIS_B033_B038_findings.md first. B033 recovered the exact bundled
Compas-44 mapping and documented that the author bootstrap seeds/scripts are
not available. B034 retained a missing-`/usr/bin/time` harness failure; B035
repaired only measurement and found full-data lambda=0.02 parity (minimum 1992,
28 trees, histogram-count recall 1.0). B036 then confirmed 1.0 recall and equal
minimum objectives on all ten fixed project-seeded bootstraps.

The harder paper-listed lambda=0.01 setting is more discriminating. B037 found
equal full-data minima (1845) but 7,070 candidate versus 7,074 exact trees,
recall 0.9994345. B038 reused B036's exact row-index arrays: all ten minimum
objectives agreed; mean recall was 0.9996247, sample SD 0.0011252, minimum
0.9964264; eight seeds were perfect and two missed 16 counts total. This
supports the paper's high-recall trend but falsifies universal exact parity.
The metric is objective-histogram count overlap, not individual tree identity.

All 37 attempts are terminal; cumulative command time is 553.557 seconds and
18 research cycles are recorded. The B038 reference peak RSS was 243,316 KiB;
no OOM event was observed. Window-0006 extended only the finite safety window
without resetting cumulative usage.

Next: audit the exact objective bins behind B038's 16 misses. Then predeclare
either a bounded lambda=0.005 resource probe or a tree-identity instrumentation
step. Do not claim exact author-bootstrap or tree-set recall reproduction.

---

# Previous continuation — 2026-10-12 PRAXIS handoff

CREDO `credo-risk-calibration-v1` is closed with an inconclusive, sharply scoped
conclusion. B025 found the n=100 gate was not locally threshold-brittle. B026
then failed transport of the co-primary DET comparison at n=50 and n=200.
B027 selected n=200 for higher precision, but B028 still failed: DET-minus-GATE
was +0.000217 with retained 98.75% interval [-0.000817, 0.001257]. The original
n=100 support remains; sample-size transport is unsupported. See
notes/CREDO_B001_B028_conclusion.md.

The active idea is now `praxis-near-optimal-tree-sets-v1`. Source is pinned to
zakk-h/PRAXIS commit ef6ce624cc40bcb00fcd39f4520364a3a05c8c80. The full
paper and source archive are preserved. B029 failed because the host Python
selected absent clang++; B030 compiled with GCC but exposed missing declared
import dependencies; B031 reached a zero-exit native run but its wrapper could
not parse buffered C++ output. All failures are retained. B032 succeeded after
repairing only infrastructure/wrapper issues: on the full author 32x5 parity
CSV, lookahead 1 and exact lookahead 4 both returned objective 0 and 1,658,880
trees, with native child peak RSS 172,036 KiB. This is an integration smoke,
not a paper-table reproduction or recall validation.

All 32 attempts are terminal; cumulative command time is 493.371 s and 14
research cycles are recorded. Window-0005 extended only the finite safety
window and retained cumulative usage. No OOM event was observed.

Next: extract one exact small paper-table protocol (prefer Compas-44 or
Heart-42), map its data/bootstrap/parameters to the pinned repository, and
predeclare an exact-key reference versus reported approximate 64-bit-hash
comparison. Measure runtime, peak RSS, minimum objective recovery, tree count
and Rashomon recall before any paper reproduction claim.

---

# Previous continuation — 2026-10-12 run5

Read CHECKPOINT.json and notes/B016_B024_findings.md before older notes. B023
used retained B022 development rows to compare four training-only scalar gates
between deterministic fitted-model selection (DET) and simultaneous
calibration-mode selection (CAL). Only the top-two fitted-probability margin
passed all leave-one-condition-out eligibility rules. Its frozen rule is DET if
the margin exceeds 0.03777072711166893, otherwise CAL.

B024 confirmed that unchanged rule on 600 disjoint native-setting trials. The
equal-condition paired regret improvements were +0.003092 versus DET,
bootstrap 95% [0.001246,0.004978], and +0.004898 versus CAL,
[0.002779,0.007151]. Certificate validity was 574/600 with exact 95%
[0.9371,0.9715]. The rule still lost to DET at triangle x0.1, so report an
average synthetic confirmation only: no uniform dominance, real-data result,
or novelty claim.

All 24 scientific attempts are terminal; cumulative command time is 292.068 s
and nine research cycles are recorded. The finite safety window was renewed as
window-0004 without resetting cumulative usage. The old supervisor expired;
the current execution-only supervisor has a newly verified process identity.
Shared cgroup memory briefly exceeded 8.0 GB during the otherwise small B023
analysis, without an OOM event, then fell below 7.5 GB. Require a larger
pre-launch headroom for subsequent native work.

Next useful action: audit retained B024 rows for sensitivity around the frozen
threshold and for the mechanism of branch benefit, without retuning. Then
predeclare robustness across altered sample sizes or a source-native
non-synthetic decision task if available. Do not rerun B024 unchanged or treat
the independent synthetic confirmation as a completed research program.

---

# Previous continuation — 2026-10-12 run4

Read CHECKPOINT.json and notes/B011_B015_findings.md before older notes. B020
falsified the post-hoc octagon ×10 undercoverage concern in 2,000 fresh trials:
MODEL_SELECT_CP validity was 1,928/2,000 and the 99% upper bound on failure was
0.04690. B021 then qualified a deterministic bivariate-Gaussian normal-cone
evaluator: six-setting truth error at most 8.16e-13, zero violations of a global
99% Monte Carlo envelope over 660 fitted-model probabilities, and bitwise repeatability.

B022 used the deterministic evaluator in 600 new native-setting trials. The
stratified paired regret `CREDO - DET_MODEL_SELECT_CP` was +0.009882, bootstrap
95% [0.007540, 0.012165], and certificate validity was 569/600. This confirms a
second aggregate synthetic advantage after removing MC selection noise, but the
result remains heterogeneous: deterministic selection loses at octagon ×0.1
and leans worse at octagon ×1. There are still zero validated novel methods and
no real-data claim. Do not report uniform dominance.

The finite safety window was renewed as window-0003 without resetting usage.
All 22 scientific attempts are terminal; cumulative command time is 270.113 s.
The current supervisor has no agent command and supplies execution only. Check
actual status/inbox/health and shared memory headroom before resuming; do not
infer liveness from this archive. Native venv remains outside the archive at
`/workspace/scratch/a5c97e2248bf/sts_native_env`.

Next useful action: use retained B022 rows for a disagreement/margin and model-
fit decomposition that explains the concentrated-octagon losses. Any candidate
gate must use training information only if it is to preserve the existing
independent calibration certificate. Predeclare a new fresh-seed comparison
after development; do not tune and confirm on B022, do not choose between methods
using calibration outcomes without a new validity correction, and do not rerun
B019/B020/B021/B022 unchanged.

---

# 统计学习与可信决策：持续 CPU 研究

Project: statistical-trust-simple-20261011. Policy: rsi-simple 0.3.0-simple.9 only, exported unchanged from cloud package c23/research-autopilot. This is an ongoing scientific goal, not a request merely to reproduce a runnable example. No other research edition, 20-to-15 quota, Gate 0 or mandatory GitHub/HF intake applies.

## Authority and resources

The user authorized on 2026-10-11 Europe/London: “对于这个统计学习与可信决策，请你只用rsi-simple来后台跑无限长任务吧，然后就是cpu的8GB以内能做的”. Mode is continuous_research, no project completion date or cumulative attempt/time/cycle cap. User stop takes precedence. This does not authorize GPUs, paid services, external messaging or unrelated projects.

Use only the actual available CPU host, one scientific command at a time, initially one BLAS/OpenMP thread. The project aggregate RAM ceiling is 8,000,000,000 bytes, also obeying lower actual shared headroom; initial diagnostics use a 2 GiB address-space limit and <1 GiB anticipated resident memory. Observe resources at every wake. Source reads and scientific CPU time are separate. Never infer sustained availability between scheduled wakes.

Finite command timeouts and execution windows protect recovery, not an overall research allowance. The first runner window uses at most 12 attempts, 600 command-seconds, 1800 elapsed seconds. Future finite windows are already authorized. Use scripts/renew_authorized_window.py --apply only at a reconciled, unlocked boundary; it records before/after windows in the existing state and increases finite ceilings while retaining all usage, original configuration, failures, tasks, source pins and user stops. Never reinitialize or reset a project. If an idle supervisor still holds its lock and cannot safely be interrupted, reuse it for useful work while its window permits; after its normal deadline exit renew at the quiet boundary. An unknown running attempt blocks renewal until reconciled. No recursive automations/run_now. The adapter was observed to reject renewal while the supervisor holds the lock; its renewal write branch has not yet been executed.

## Initial active question

One active idea: credo-risk-calibration-v1, revision 1. Determine whether the native CREDO risk evaluation is both reliable and informative, including the distinction between per-trial conservativeness, marginal expectations, Monte Carlo reference error, and selection of decisions. First qualify source semantics and the evaluator before testing a proposed change.

Other in-scope serial successors: PRAXIS near-optimal decision-tree sets and IHM private regression. Retire the current hypothesis with evidence before replacing it. Choose a successor for scientific reasons rather than sweeping all three concurrently. LLM/agent transfer is not the present experimental target.

## Source and evidence

The user attachment is preserved at sources/CPU_8GiB_2026_Passed_Only_9.md. It records earlier limited successful native runs, not new runs in this project and not full paper replications. CREDO: 99 Gaussian trials, ntr=ncal=100, K=100, reference MC K=10000, conservative rate CREDO=1, Point=1, NS=0.515152. No corresponding raw receipts were supplied here.

CREDO author source is pinned to 19e884718599cd390564ddf93aff943a720f3e22 in wbzhou2001/CREDO; source tree is retained and downloaded text files verified against Git blob hashes. Source includes a full original notebook with stored author outputs: treat those outputs as previously published, not newly computed. Never use the tracked __pycache__ from upstream.

Paper: https://proceedings.iclr.cc/paper_files/paper/2026/file/11e0fdc1f9ec9303e5de60670e884e53-Paper-Conference.pdf
PRAXIS: https://proceedings.mlr.press/v306/heile26a.html ; zakk-h/PRAXIS @ ef6ce624cc40bcb00fcd39f4520364a3a05c8c80.
IHM: https://proceedings.mlr.press/v306/lev26a.html ; omrilev1/HessianMix @ 37651364bdfa9814fa3220dd2512cdb94f6c213a.

Source inspection found that NaiveDecisionRiskAssessment.get_prob uses >=0 and hence maximization, while the paper presents minimization. Resolve the mapping consistently before comparing values; a sign convention alone is not proof of a bug. GaussianMixtureSampler interprets scale as covariance scale, and fit(return_kwds=True) reduces full fitted covariance to a scalar diagonal mean. The notebook TPR implementation returns a joint proportion rather than explicitly dividing by the fraction of truly positive decisions; assess when these differ. Do not call any finding a new method or a proven paper error without verification.

The initial diagnostic checks these exact native Gaussian/triangle semantics with independent analytic integration and Monte Carlo. It is a mathematical/evaluator diagnostic using the author's setting, not an end-to-end CREDO run or a replacement benchmark. Native pipeline currently lacks torch, shapely and pypoman in this host; use an isolated dependency environment if needed, preserving failures and resource measurements. Repair the blocked path while advancing independent valid work.

## Resume and report

Read CHECKPOINT.json and the latest immutable notes/results. Check the actual runner status/inbox/health/alerts and owned process identities before resuming. The policy, command executor and cloud wake mechanism are separate. Use runtime/scripts/simple_runner.py for scientific commands, with pinned plan/code/source inputs and real stdout/stderr/receipts. One coordinator writes shared state. Read the included Simple references for design, next-action and collaboration rules.

Background wakes should perform necessary reading, mathematical analysis, implementation, native comparison and interpretation within the available session, then save concrete next work. Do not stop after a feasibility milestone or merely send a reminder. Full comparisons need strong/simple baselines, calibrated metrics, appropriate uncertainty, fair data/compute and separate confirmation; keep remaining coverage visible. Only published native datasets/protocols support benchmark claims; constructed checks remain diagnostics.

On actual exceptions, report observation time, task/attempt, evidence, affected work, repair and next action in the current conversation. If host/CPU/network/execution is unavailable, explicitly report it; missing heartbeat is not proof of OOM or a stopped job. Deduplicate unchanged incidents. Save failures, observed CPU/wall/RSS and unknown model usage honestly. No email/Slack notifications.

Persist the whole project as the same Statistics_Trustworthy_Decision_RSI_Simple_Checkpoint.zip Library item, replacing with a concrete expected version. On host loss materialize the latest exact item, safe-extract, verify hashes and reconcile old identities before launching replacements. A stale archive must never overwrite a newer live project. New source adoption requires a versioned, reconciled handoff; never silently switch editions.
