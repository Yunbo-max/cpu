# CVPR 2027 camera-pose research: gravity reliability

Goal: test whether an independently observed, uncertain gravity direction can improve sparse 2D–3D pose recovery with imperfect focal calibration, and develop a genuinely distinct method only if a strong comparison supports the opportunity. A positive diagnostic is not a paper claim.

This is an Auto Work research project begun on 2026-10-17 after the user chose 3D camera pose estimation and requested execution. It links to `projects/3d-autopilot-simple` for source and historical fr1/xyz development evidence. It does not resume `projects/autopilot-3d-20261011` (explicitly stopped) or overwrite the older Auto Chat coordinator, whose project authority did not include Work.

## Question and falsifier

Given RGB-D reference 3D points, query RGB feature correspondences, unknown/perturbed focal length, and a measured accelerometer gravity direction, can a calibrated confidence-aware gravity-assisted pose estimator lower rotation error or failure probability at equal time/feature budget relative to well-qualified focal-aware/general pose estimators? If measured gravity is uninformative under dynamics, or a general pose estimator matches it after fair tuning, discard the proposed route or narrow the conditions; do not rename a prior-noise sweep as novelty.

The 2026 UP2PfORI implementation and PoseLib P3P are inherited components. The historical fr1/xyz result was mixed (8 exposed development pairs: rotation median 0.378074° versus 0.579298°, center median 0.025534 m versus 0.007348 m; fixed focal P3P is not focal-fair). Historical `Rxz` comes from ground truth and is not a measured inertial prior. The current project must retain this distinction.

First scope: a bounded frozen-source transfer diagnostic on previously unused TUM fr2/xyz pairs, then measured accelerometer alignment/reliability analysis. Fr2 has `accelerometer.txt` in the official TGZ. Use ground truth only to score pose in a future valid evaluation; the first inherited solver comparison uses a GT-derived `Rxz` solely to qualify the code path. An IMU-to-camera frame mapping must be calibrated on separate data before a measured-prior claim. Independent held-out sequences, focal-aware competitors (including P4Pf/P3.5Pf where compatible), uncertainty, runtime and an external review remain required.

Resources: this host has 8 CPU quota cores and 8 GiB cgroup RAM. Respect the earlier conservative 4 GiB process address-space ceiling, one numerical thread/process, finite individual commands and the already requested target of about one hour of meaningful CPU per cycle where feasible. Count actual CPU from receipts; never pad workload to hit the target. No GPU, paid service or GitHub Actions. Source/evidence is saved through ordinary GitHub commits; scheduling requires a verified Work-capable host task.
