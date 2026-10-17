# R006 outcome: real-feature oracle headroom is metric-dependent

This is a development **upper-bound/source qualification**, not a measured-IMU result. The oracle UP2PfORI receives `Rxz` derived from each evaluated pair's ground-truth pose. The focal-unknown visual competitor is the source-native PoseLib P4Pf; both draw 512 hypotheses from the identical frozen R001 feature/match input and use a 3-pixel score. Neither arm has a full localization pipeline or local optimization. Fr2/xyz is already exposed; adjacent reference times and six offsets are correlated.

The prospective 240 reference times × 6 offsets produced 1440 pairs, of which 1438 met timestamps and 1418 had ≥24 depth/normal correspondences. Both arms returned valid output on all 1418 qualifying pairs. The independent raw-row and true-reprojection recount matched the original summary, and `artifacts.json` reconstructs the exact 17.7-MB correspondence CSV from six compressed parts. The official dataset archive and native dependencies retain their recorded source hashes.

| Offset (s) | Qualified / 240 | Median GT match-inlier fraction | Oracle rotation (°) | P4Pf rotation (°) | Oracle paired rotation wins |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.15 | 238 | 0.892 | 0.120 | 0.231 | 192/238 |
| 0.30 | 240 | 0.871 | 0.144 | 0.258 | 186/240 |
| 0.60 | 240 | 0.831 | 0.162 | 0.284 | 180/240 |
| 1.20 | 240 | 0.765 | 0.194 | 0.300 | 167/240 |
| 2.40 | 240 | 0.511 | 0.314 | 0.359 | 134/240 |
| 4.80 | 220 | 0.344 | 0.507 | 0.491 | 104/220 |

Overall median rotation error is **0.1864° oracle versus 0.3020° P4Pf**, with 963/1418 strict oracle wins. The effect does **not** strengthen monotonically at lower overlap: at 4.8 seconds the oracle loses its median rotation advantage. P4Pf has better overall camera-center error (**0.01027 versus 0.01626 m**), focal relative error (**0.00559 versus 0.00975**) and median inliers (**77 versus 74**). In the `<0.5` GT-inlier-fraction stratum (457 qualifying pairs), oracle rotation is 0.328° versus P4Pf 0.460°, but center is 0.0293 versus 0.0138 m and focal relative error 0.0189 versus 0.0069. These are descriptive, dependent observations; use no pairwise independent standard error or paper-level significance claim.

For 512 hypotheses per pair, summed native solver/scoring CPU is 2.731 seconds oracle versus 3.592 seconds P4Pf. The full process took **169.199395 measured CPU seconds**, peak recorded compile-child RSS ≈572 MiB; the 12-pair source/resource pilot took **34.229718 CPU seconds**. The cycle's explicitly metered R001–R006 process total is **255.605581 CPU seconds**, plus small unmetered postanalysis/compression. It is far short of the user's ≈3600-second meaningful target. A pilot indicated native pose estimation is only milliseconds per pair; prolonging the same 122-second fr2 sequence to an hour would require many near-duplicate correlated cases. That is a scientific stopping decision, not completion of the hour target.

Interpretation: the ideal oracle gives some rotation headroom at short/medium offsets, but sacrifices center/focal and stops winning rotation at the largest offset. This does not justify a real measured-gravity method yet: R004 invalidated the old `Rxz` sensor interface, R005 found weak query-observable reliability predictors, and the closest papers already cover unknown-focal gravity and weighted/rough priors. A next genuine research task must qualify a correct sensor-derived map interface and a strong focal-unknown visual pipeline with local optimization on independent sequences; or choose a sharper 3D pose question if the distinction disappears. Do not spend further CPU on duplicated fr2 sweeps to meet a clock target.
