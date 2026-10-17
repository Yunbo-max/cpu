# R007: nonminimal refinement diagnostic on exposed fr2/xyz

**Scientific decision:** ideal GT-derived orientation information retains a
rotation advantage after both arms receive the same class of robust local
reprojection refinement. It still does not yield better camera-center or
focal accuracy, and it is unavailable from the current measured-IMU interface.
No measured-gravity algorithm, new solver, independent test, or CVPR-level
claim has been established.

The question and falsifiers were frozen in `PLAN.md`. A 48-pair pilot verified
that the child native wrapper reproduced all first ten scientific fields of
the 2836 R006 source rows; 46 pilot pairs qualified, all 92 refinements
converged. `FULL_PLAN.md` then froze all 1440 original R006 pair IDs, the
same model rows and correspondences, the 3-pixel initial consensus, robust
soft-L1 scale 3 px, max 100 evaluations, and unknown focal in both arms.
The oracle rotates only about gravity while preserving the **query-GT-derived**
tilt; P4Pf's rotation is unconstrained. The process uses one CPU thread and a
4-GB address-space cap. This is an in-house fixed-consensus local optimizer,
**not** PoseLib's full LO-RANSAC localization pipeline.

The first full attempt stopped before any outcomes: two source-valid oracle
models (pairs 83, 101) have four initial inliers and cannot meet the script's
six-inlier nonminimal optimization precondition. `AMENDMENT.md` and
`full/first_attempt.log` disclose the after-failure correction: retain those
initial models as the refined output and record explicit unsuccessful skips.
No pair was replaced or removed; both stay in the paired denominator.

| Metric, median on 1418 qualified pairs | Oracle before | P4Pf before | Oracle after | P4Pf after |
| --- | ---: | ---: | ---: | ---: |
| Rotation error (°) | 0.1864 | 0.3020 | **0.1048** | 0.2406 |
| Camera-center error (m) | 0.01626 | 0.01027 | 0.00790 | **0.00498** |
| Focal relative error | 0.00975 | 0.00559 | 0.00418 | **0.00264** |
| Inlier count | 74 | 77 | 76 | 76 |

After optimization the oracle wins paired rotation on 1206/1418 pairs,
P4Pf wins center on 1033/1418 and focal on 960/1418. These outcomes
include the two unchanged oracle models. The six frozen offsets each retain
an oracle rotation median advantage after refinement (at 4.8 s: 0.226°
versus 0.377°, 154/220 paired rotation wins), even though the unrefined
4.8-s R006 comparison slightly favored P4Pf. The fixed true-pose
reprojection overlap strata also retain the rotation/center/focal tradeoff:
at GT match-inlier fraction <0.5 (457 pairs), rotation 0.190° versus 0.412°,
center 0.0168 versus 0.0080 m, and focal relative 0.00917 versus 0.00406.
The complete per-offset, overlap-stratum, and 10-second reference-block
recounts are in `full/analysis.json`; the 1418 pairs are correlated within
one exposed 122-second sequence, not independent confirmation.

The R007 pilot consumed **37.739259 measured CPU seconds** including
compilation; the full reusable-model run consumed **10.070783 measured CPU
seconds**, peak self RSS 124,604 KiB. The first failed attempt and small
postanalysis are not included in that full-run meter. Explicitly metered
R001–R007 completed processes sum to **303.415623 CPU seconds**, versus
the requested ≈3600 seconds of *meaningful* compute. R006 calibration showed
native solving takes milliseconds per pair; a longer sweep on these already
exposed, correlated frames would not settle the sensor information interface
or distinguish the method from closest work. We stop this scientific branch
at the prerequisite gate rather than misstate the hour target.

Next research decision: define an independently gravity-aligned 3D map and
calibrated accelerometer-to-camera interface, with query GT excluded from all
inputs; identify a genuinely different uncertainty treatment after a
closest-work audit. Freeze failure/rotation/center/focal and time targets,
run a full focal-unknown visual localization/LO comparator, then test on
independent, more dynamic inertial data. If no distinct method and
sensor-valid gain survive those gates, redefine the 3D pose paper problem.
The A/B/C provenance, execution, and continuity checks are separate across
every scientific stage. No unattended Work continuation has been verified.
