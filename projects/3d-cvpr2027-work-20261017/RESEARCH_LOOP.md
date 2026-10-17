# Scientific loop and separate execution acceptance

The research loop for this project is ordered by scientific dependency; execution acceptance A/B/C is a **cross-cutting evidence layer**, not a sequence that substitutes for scientific work.

| Scientific phase | Concrete record this cycle | Status |
| --- | --- | --- |
| Problem and evaluation objective | `PROBLEM.md`: real-IMU unknown-focal localization; pose/focal/failure/time criteria | Provisional; no accepted new method |
| Existing methods | UP2PfORI 2026 source/paper, PoseLib P4Pf, Pautrat 2023, gDLS* 2020, older gravity geometry | Collision risk recorded |
| Mathematics and falsifiable prediction | R004 `Rxz` information counterexample; R006 sample-size derivation and oracle-headroom falsifier | Tested as interface and upper-bound diagnostics |
| Frozen experiment and strong comparator | R006 1440 prospective pairs and R007 pilot then full protocol; unknown-focal P4Pf, all failures retained | In-house local refinement checked; full external localization/LO still pending |
| Resource calibration | R006 and R007 pilots, measured CPU and peak RSS, 4-GB/one-thread process limits | Feasible; hour-long same-sequence queue rejected as redundant |
| Native execution and verification | R001–R007 raw/model equivalence, official data hashes, independent outcome and GT strata recount | Development evidence only; no independent confirmation |
| Interpretation and next round | `runs/R007/REPORT.md`, `REPORT.md`, `CURRENT.json` | Oracle rotation advantage with worse center/focal; choose sensor-valid interface, stronger baseline, independent data or pivot |

Across **each** phase, require provenance/readback, actual native execution receipt and resource accounting, and a separate cross-call continuity check where a host supports it. Publishing source does not prove execution; native execution does not prove a scientific claim; this foreground session and a GitHub checkpoint do not prove unattended Work continuation. The ≈60-minute meaningful-CPU target remains unmet after an observed early scientific gate; it cannot be satisfied by repeating near-identical pairs.
