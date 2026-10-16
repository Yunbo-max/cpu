# Handoff wake24

- Last verified: 2026-10-13T09:31:16Z.
- Fixed runtime remains Research Autopilot Simple 0.3.0-simple.9, digest `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`.
- Unique active idea remains `gravity-pose-public-rgbd-validation`, revision 1, goal contract 1.
- Completed a real public RGB-D source-model experiment on TUM fr1/xyz and an independent raw-row verifier. See `notes/gravity-pose-tum-fr1xyz-analysis-v1.md`.
- Frozen v3 result: UP2 vs P3P median rotation 0.378074 vs 0.579298 deg; centre error 0.025534 vs 0.007348 m; inliers 46.5 vs 63.0. UP2 paired wins: rotation 5/8, centre 1/8, inliers 0/8.
- v2 failed due a missing centre-depth guard and is retained as engineering failure; v3 repaired only that guard.
- Cumulative runner ledger after independent verification: 95 attempts, 3759.1021510600285 command seconds. Empirical-cycle count becomes 33 after recording the event.
- Primary v3 peak RSS 494200 KiB. At 09:31:16Z cgroup memory current/max was 7,835,824,128 / 8,589,934,592 bytes, but anon was only 658,436,096 bytes and file cache 6,719,131,648 bytes; OOM and OOM-kill remained zero.
- Next scientific action: acquire/hash-pin one independent TUM RGB-D sequence (prefer fr2/xyz), then run the complete v3 protocol unchanged. Do not tune the exposed fr1/xyz data. Retire on non-transfer.
- GitHub is authoritative; update the base+overlay latest pointer only after consistent checkpoint and sparse-restore verification. Do not overwrite it from the old Library archive.
