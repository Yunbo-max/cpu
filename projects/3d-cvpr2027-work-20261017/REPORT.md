# Work cycle 2026-10-17: source-transfer and measured-IMU diagnostics

Status: active research, development evidence only. No new method has been accepted, no CVPR-level claim or independent evaluator review exists, and unattended Work continuation has not been verified.

## R001: independent TUM fr2/xyz source transfer

The official `rgbd_dataset_freiburg2_xyz.tgz` was downloaded (2,201,854,648 bytes; exact SHA-256 `a4903027a7fe6bc6573a1ce96a8afa5689f15d74f4a3f0627e91b5799f62e40b`). The preregistered timestamp selection yielded 24/24 accepted and qualifying RGB-D pairs, each with 72–122 valid depth/normal correspondences. Original UP2PfORI and PoseLib P3P were compiled without solver changes. Two full attempts and a stand-alone compile failed because archive restoration omitted transitive PoseLib headers; after complete PoseLib source restoration, the same C++ built successfully. The full-run failure logs and results remain in `runs/R001`; the third stand-alone compile's missing-`types.h` error was observed in tool output but was not saved to a file.

| Metric on 24 valid pairs | UP2PfORI + RANSAC | fixed-focal P3P + RANSAC |
| --- | ---: | ---: |
| Median rotation error | 0.153325° | 0.304248° |
| Median camera-center error | 0.010708 m | 0.006035 m |
| Median inliers | 88.5 | 91.0 |
| Strict paired wins for UP2PfORI | 19/24 rotation | 5/24 center; 0/24 inliers |

An independent standard-library CSV recount reproduced these values. Crucial limitation: `Rxz` is derived from the evaluated pair's ground-truth rotation, while P3P is handed the true 525-px focal length and UP2PfORI estimates it. The test establishes source transfer and a mixed development signal, **not** measured gravity, information-fair performance, novelty, or a publication result. These fr2 images are now exposed development data. The previously exposed fr1/xyz experiment had the same directional tradeoff, so no cherry-picking or repetition as new confirmation.

## R002–R003: measured accelerometer prerequisite

The official archive contains `accelerometer.txt` with 61,162 non-comment samples; R002 uses ±50-ms windows at the 24 pairs. Median observed pair direction change is 1.0205°, maximum 2.3998°, median within-window 95th-percentile direction dispersion 1.5397°, and median mean acceleration magnitude 9.6065 m/s². Direction change includes both rotation and dynamic acceleration, and cannot yet be interpreted as a camera tilt error.

R003 fits a fixed sensor-to-camera rotation and a world gravity vector using the **first 30 seconds only** (299 10-Hz observations), then scores predicted versus measured acceleration direction on the later ≈92 seconds (920 observations). Training median angular discrepancy is 0.8095°, later median 0.7698°, and later 90th percentile 1.4306°. Ground-truth orientation enters calibration and diagnostic scoring, not a query pose solver. The model has a vector-norm gauge singularity; other Jacobian singular values span 0.356–32.32, so rotational excitation/identifiability require more scrutiny. The later interval is held out from calibration, not untouched confirmation of a pose method.

## Interpretation and next decision

The closest 2026 UP2PfORI paper already includes simulated IMU perturbations and P4Pf/P3.5Pf/UP2.5Pf comparisons; adding a noise sweep alone is not original. Its real-data evaluation uses stronger localization pipelines than this 512-sample minimal-solver pilot. The next decisive question is whether measured accelerometer gravity can be converted into the author's exact `Rxz` information condition without ground-truth query pose, given that the present RGB-D 3D points live in the arbitrary reference camera frame. Prove or disprove the information mapping before another effectiveness run. If necessary move to a gravity-aligned, independently mapped world coordinate and use real sensor-to-camera extrinsics; retain a focal-aware general estimator and adaptive uncertainty control as rivals. Keep original solver interfaces and the mixed 24-pair result intact.

R004 resolved that information check for the current wrapper. On fixed pair 0, applying yaw rotations of −20° and +20° about the ideal query gravity direction preserves the identical reference-to-query gravity relation with residual <3×10⁻¹⁶, yet changes the inherited `Rxz` by 9.61429° and 9.61424°. The old GT-derived `Rxz` is not identifiable from the two measured directions in this coordinate frame. `PROBLEM.md` records the revised, falsifiable information condition; this counterexample is not novel by itself.

Measured CPU for the two R001 feature/failed-compile invocations, R002, R003, R004, initial native solve and two identical accounting replays sums to **44.769042 seconds** (user+sys). The replays correct failure-history metadata without changing the scientific denominator or result. The stand-alone C++ compile attempts and dataset transfer/extraction were not CPU-metered, so total CPU is higher but unknown; do not count them toward the requested ~3600-second meaningful-CPU target. Final native solve alone used 0.116753 CPU seconds; peak recorded child RSS in the failed compilation attempts was about 463 MiB. Results are fast because the qualification and identifiability prerequisites, rather than a large campaign, are the current decision bottleneck. The target remains unfinished.

Sources: official TUM file formats https://cvg.cit.tum.de/data/datasets/rgbd-dataset/file_formats; original paper https://arxiv.org/pdf/2608.20056; archived native code and historical Chat audit at main `18c1259ce6f22cc83f594308bc8c3012919e72d9`. Individual raw inputs, output, hashes, failure stderr and commands are in `runs/R001`–`R003`. The 2.1-GiB official archive is referenced by SHA and URL, not committed.

The exact native correspondence input is stored as `runs/R001/matches.csv.gz` (deterministic gzip, SHA-256 `f6373cd2277cd91275d4a70db214f4c432b403f9de12832a8e373335737f58a7`); decompressing yields `matches.csv` SHA-256 `2959f8cb90ff245de6b22f0b7b4daaa90fc71b51d45e3965d4affd8a22fbe48c`. The original archive and compiled host binary stay local; their hashes are recorded in the receipts.

## R005: does observable IMU quality predict direction error?

The preregistered R005 used the fixed R003 calibration from seconds 0–30 and its 10-Hz eligibility grid for seconds 30–122: 299 calibration and 920 temporal-test windows. Ground-truth orientation was used only to *score* the static-gravity direction discrepancy. The test median remained 0.769845°, p90 1.430588°; 75/920 errors exceeded 1.5° and 19/920 exceeded 2°.

| Query-observable predictor | Spearman with error (10-s block-bootstrap 95% interval) | Top vs bottom quartile median error | AUROC, error >1.5° |
| --- | ---: | ---: | ---: |
| Within-window direction p95 dispersion | 0.130 (0.065, 0.196) | 0.897° vs 0.692° | 0.620 |
| Mean acceleration-norm deviation from early median | 0.115 (0.030, 0.197) | 0.874° vs 0.733° | 0.594 |
| Sample-norm standard deviation | 0.045 (0.004, 0.098) | 0.781° vs 0.673° | 0.528 |

This is weak discrimination on one exposed, mostly mild-motion sequence; the >2° AUROC is based on only 19 positives. A 10-s block bootstrap reflects this sequence's temporal dependence but cannot provide independent-sequence generalization. R005 consumed 7.407426 measured CPU seconds, ≈115 MiB peak RSS, total current measured CPU now **52.176468 seconds** versus the 3600-s meaningful target. More compute on the same weakly predictive signal would not resolve the decisive research risk. ICCV 2023 Pautrat et al. already use a hybrid estimator under rough gravity for vanishing points; CVPR 2020 gDLS* already weights noisy gravity priors; and Pruss 2026 explicitly connects accelerometer-equipped reference coordinates to gravity-aligned maps. See `PROBLEM.md` for the narrowed question and primary sources. No pose improvement, new solver, or CVPR-ready novelty has been established.

## R006: complete frozen oracle-headroom cohort after user's loop correction

We revisited the scientific dependency rather than setting a timer. R006 asks whether **ideal** GT-derived tilt lets the archived oriented two-feature solver beat source-native PoseLib P4Pf, which also estimates focal. A 12-pair pilot verified both native sources and resources, then froze 240 reference times × six offsets before the full run. Of 1440 prospective pairs, 1438 passed timestamps and 1418 had ≥24 matches; 2836 arm rows were valid. Independent recount confirmed all rows and true-reprojection inlier strata. Overall oracle rotation median 0.1864° vs P4Pf 0.3020°, but P4Pf center median 0.01027 vs 0.01626 m, focal relative median 0.00559 vs 0.00975, and median inliers 77 vs 74. At 4.8 seconds, even oracle rotation is slightly worse (0.507° vs 0.491°). The complete offset table, exact input-part manifest, caveats and decision are in `runs/R006/REPORT.md`.

The pilot and full process add 203.429113 measured CPU seconds, bringing explicitly metered R001–R006 to **255.605581 seconds**. Calibration showed native solving takes only 0.002–0.003 seconds per pair; a full hour on the same 122-second sequence would be largely correlated repetition. We therefore did not claim the user's 3600-second target or continue padding the weak hypothesis. `RESEARCH_LOOP.md` records the scientific order and separate A/B/C execution evidence. No measured-gravity pose method or independent CVPR-level confirmation exists.
