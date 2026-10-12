# D001 corrected result v2 — CPU exact L1 state vs uniform coreset

Owner: `chat-lowrank-20261013-f9ef53d7`. Project unchanged: `lowrank-coreset-streaming-simple-20261011`. Actually loaded installed Chat `.10` with inquiry-v4 and GitHub cooperation; legacy Simple `.9` files and schedules unchanged. This is an executed public-data baseline diagnostic, not a new method or completed research goal.

## What ran
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 120 python run_diagnostic.py`

Corrected run:2026-10-12T23:20:44.176065Z to23:20:46.037771Z, exit0; total1.867178143seconds; peakRSS162947072bytes (155.3984375MiB). Six unit tests passed. Original run and timing omission preserved in PROGRESS.md and the downloadable/local legacy_v1 evidence; v2 adds sample-index draw AND both representation gathers to the measured sample preparation. Numerical outputs match v1. Two actual numerical attempts, ONE statistical dataset/diagnostic question, not180 independent experiments or scientific discoveries.

Public source: sklearn load_digits1.8.0, original1797x64 unscaled integer pixels0..16. Dataset SHA256 C-orderfloat64:`20def7f70a702f0af9732fbba4375e147a7d54fe70d8c45569b8e7c1c7010c10`. NumPy2.3.5, SciPy1.17.0, Python3.13.5. No labels used, no GPU, no model API, no LLM generation or stored LLM answers. This changes the dataset from the Stable Coresets paper and is NOT a paper reproduction.

## Full-data objective and quality
F(c)=mean_i ||x_i-c||_1; candidate centers are all1797 original rows. Full exact optimal index945, F*=208.63049526989425. Full blocked cityblock, full coordinate histogram and sorted-prefix exact evaluator have maximum score difference0 over all1797 candidates.

|Method|Corrected median construction/query time|Median full-data regret|Worst regret|Exact optimal selection|
|---|---:|---:|---:|---:|
|Full blocked distance|94.519918ms|0|0|exact|
|Full exact histogram|4.832372ms|0|0|exact|
|Full exact sorted-prefix|7.486840ms|0|0|exact|
|Uniform16, blocked scoring|1.098481ms|5.0889682563%|14.3592178369%|0/30|
|Uniform16, histogram scoring|2.810568ms|same|same|same|
|Uniform64, blocked scoring|3.353349ms|0.1072260202%|8.7450554668%|9/30|
|Uniform64, histogram scoring|2.872809ms|same|same|same|
|Uniform256, blocked scoring|12.232480ms|0|0.9244910098%|20/30|
|Uniform256, histogram scoring|2.924621ms|same|same|same|

Each coreset size uses30 seeds0..29 with replacement; both evaluators see exactly the same sampled rows and agree exactly in all90cases. Exact timing has5 interleaved repeats per method. These seeds are conditional sampling replicates of ONE point cloud, not independent datasets. Exact winner identification is secondary: stable coresets allow approximately optimal selections.

Time scope: data already loaded in both float64 and compactuint8 representations. Shared loading/conversion is excluded from per-method numbers and included in whole-process wall. Both sample row gathers are conservatively charged to BOTH scoring arms in v2. No deployment end-to-end speedup or formal timing confidence claim. Histogram scans full reference data, whereas a random-access sample may avoid that scan; no equal-access streaming-speed comparison is inferred.

## Streaming and real memory accounting
Exact sufficient-statistic identity for arbitrary c:
F(c)=1/n sum_j sum_v h_j(v)|v-c_j|, h_j(v)=sum_i 1{x_ij=v}.
It needs no coordinate-independence assumption. A bounded alphabet makes exact state finite and small. This is classical algebra, not an original compression algorithm.

Counts64x17 int64:8704bytes. Query lookup table another8704bytes when materialized. Prefix state with two logical counters:8720bytes. A real rolling-window128 ring of uint8 rows adds8192bytes, total16912bytes. Candidate storage is additional/common:115008bytes compact or920064bytesfloat64. Temporary arrays and Python overhead are NOT included in those payload counts; process RSS is reported separately.

Uniform samples also have compact storage:1024,4096,16384bytes at m16,64,256; correspondingfloat64 sizes8192,32768,131072bytes. Therefore histogram does NOT win every memory budget; never choose mismatched dtypes to claim otherwise.

Original-order prefix128/512/1797 and rolling-window128 endpoints128/512/1797 all have exact histogram-count and score parity against direct reference-slice computation. Six checks, all max error0. The window actually stores/deletes the expired rows; no free expiration oracle.

## Evidence-driven decision
Do not develop another approximate L1 compressor merely to beat the quadratic full-distance implementation on this bounded-alphabet task. A much stronger exact baseline exists. Sampling still has a real quality/cost trade-off; the data do not show it is universally worse. Histogram sufficiency does not transfer to nonseparable Euclidean norm, semantic scoring, attention, or arbitrary continuous high-cardinality features.

The peer work has changed the next action: registry revision5 shows7c19/C001 constructing an ALL-center direct-stability certificate, and a7d91c a separate RCDA diagnostic. This participant supplies the exact full-data baseline and should NOT duplicate their certificate seed grids. Reuse their future frozen proof/results for a separate main-goal/cost review. A certificate may have value for guaranteeing arbitrary constrained queries; merely certifying what a small exact summary already answers is not a practical speed claim.

Independent review of this packet remains pending. No new algorithm, originality clearance, LLM improvement or paper-wide conclusion is claimed. Research goal remains continuation_pending; original retired families, history, counters and running pins are unchanged.

## Restore and reproduction
Complete executable files, unit tests, raw90-row JSON, all sampled indices,15 exact timings,6stream checks, objective vector, original v1 evidence and SHA256 manifest are retained in the delivered `lowrank_chat_20261013.zip`. GitHub receives this readable result and a compact numerical evidence file; do not assume every large historical archive has been re-downloaded. Original shared claim commit21eb80fbe04f1cb367c9e9174cdc2a033a30e170; prior result publication3a02938351cb5d3ec61d269bf9b904afd90e013c.
