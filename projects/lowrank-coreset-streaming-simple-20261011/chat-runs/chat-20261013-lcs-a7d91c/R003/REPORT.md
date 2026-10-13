# R003 — Existing-result decision audit and exact witness verification

Date: 2026-10-13. Participant: chat-20261013-lcs-a7d91c. Parent project remains lowrank-coreset-streaming-simple-20261011. User reiterated latest autonomous-rsi-chat and continuing execution. Source publication inspected: Research_Autopilot/autonomous-rsi-chat@c9b34733854f654e2abd072d299e1c115508b965 (.12 publication; chat-execution.md still labels its text .10). Installed Chat entry was actually read. No claim that plugin installation was updated.

## Executed sequential actions
1. Read-only reanalysis of all 31 existing R001 cases at alpha=1/100, beta in {1/10,1/5,2/5}: 93 settings, not 93 new experiments. Both RCDA and c-factor use the existing full-data midpoint median. Define e0=max(RCDA,alpha*c); the Theorem 3.1 sufficient-condition test admits when e0<1/5 and 4*e0<=beta. Finite data-center checks admit 29 settings; full-space numerical brackets admit 27; no bracket straddles the chosen decision thresholds. Two mismatches.
2. Read-only exact recomputation of those two saved witnesses, without importing either RCDA solver. Reconstruct only the two public feature arrays, verify original data/index hashes, and reuse stored sample indices and witness coordinates. No new random draws or optimizer runs. Encode binary64 inputs and exact midpoint medians as common-power-of-two integers. Use direct absolute sums for the saved witness and a separate integer-prefix implementation for all original data centers.

| Existing case | beta | Finite-center exact maximum | Saved witness exact ratio | beta/4 |
|---|---:|---:|---:|---:|
| Wine, m128, seed2 | 0.1 | 0.024709239234679534 | 0.027176122054313117 | 0.025 |
| Breast Cancer, m64, seed2 | 0.2 | 0.046349237325318635 | 0.05022709210603572 | 0.05 |

Both exact c-factors equal 1. Exact witness ratios are respectively 1890575130801912266197/69567509559439127965984 and 424864971971308538847331/8458880539497787694653552. Strict margins above threshold are respectively 756936959079670335237/347837547797195639829920 and 9604724982095770573267/42294402697488938473267760.

## Actual receipts
Reanalysis OS wall 0.94s, user/system 1.27/0.13s, peak RSS96012KiB, exit0. Exact check OS wall2.43s, user/system2.10/0.32s, peak RSS159840KiB, exit0, finished2026-10-13T09:22:35.061162Z. These include interpreter imports; internal analysis times were0.006074s and0.063288s. Host CPU quota4, RAM max4294967296 bytes; observed OOM/OOM-kill0. Exact check requested BLAS/OMP/MKL1 thread and2GiB address-space cap; the preceding stdlib reanalysis did not explicitly set thread environment. No GPU, paid API or other host.

Original results/diagnostic.json SHA256:596e6bb57219ef21f8f5a6fc94c1928dece31c32d87649bf7fa9c58196b68f1d. Full original code hashes were checked against the saved run manifest. Wine data SHA256:8edcf3903afd97c64d51e0212eb10b213f7943da650574d1c055b836c5c35d37; Breast Cancer:6b202a2072f9a0385f405a8f8605b1b06f6f36ae6d23d9cd6cbbc0974a416bc7.

## Interpretation and next decision
This establishes concrete failures of finite-center RCDA certification on these saved inputs. It does not refute stable coresets, Theorem3.1, or prove either coreset is unstable. The overall27/93 figure remains a numerical full-space classification; only the two displayed witnesses and finite-center maxima received new exact verification. Same actor performed both actions; this is not an independent reviewer acceptance. New benchmark runs=0; no new method or scientific-cycle count claimed.

C001 run_study.py blob f1aa4689406bf1b220ed0238655c63d50a3aeec3 uses rcda and median_ratio from the same exact_extremes State; certificate.py blob ca1107f933f363c37ca2d80135e725dd09e6887a uses the same lower-median index for both. Source review found no mixed-anchor c-factor defect. R002 evidence archive had a reported transfer defect; its full primary bytes are not recovered here and are not prerequisites for these R003 results.

Registry revision11 and all four participant entries were refreshed; no incoming completed review or new shared numeric claim was observed there. R003 is safe read-only analysis of this participant's already executed evidence, not a duplicate sampling campaign or takeover of a peer task. Own namespace only; original files, legacy jobs, pauses, and cumulative history unchanged. No new experiment claim was made.

Next scientific action: require a consequential native constrained-output or nonseparable objective and compare the strongest compatible exact sufficient-statistic baseline and full cost before designing a new candidate. Do not extend unchanged RCDA seed grids or label this verifier a practical speedup. New numerical work must obtain the shared registry's unique conditional claim. Continue source acquisition and evidence review where independent.

## Continuing invocation
The already-existing project automation6acc15a522f08191a1bbf19f58f033a1 was observed enabled/hourly but its prompt still pinned Simple. The user now specifies Chat. Intended change: update that same task's future-decision procedure, not create a duplicate automation or alter any running pinned legacy command. Until an actual automation.update receipt, this remains an intended change. Each active invocation should perform result-dependent successive steps, not just report a status. No persistent between-invocation CPU process is claimed.
