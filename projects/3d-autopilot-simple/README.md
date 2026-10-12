# 3D Autopilot Simple research archive

Read `latest.json` on current main first. It identifies the immutable base and additive overlays; older base history is retained. Only this directory belongs to this research project.

Restore `restore_checkpoint.py` from the same current commit; verify its blob SHA and SHA256 from latest. Run `python3 restore_checkpoint.py --commit CURRENT_MAIN_COMMIT --destination NEW_EMPTY_DIRECTORY --include START_HERE.md --include runtime --include notes --include plans --include scripts` and add required data/results/state paths. The helper resolves the latest file versions across base and overlays before extraction, verifies part/file hashes, and refuses differing existing files. Do not restore the base alone over a newer run. Use the current-main commit here, not merely archive_commit.

Local state may be partial because host file deletion has reappeared in later calls. Restore to a fresh staging directory, compare actual state, copy only missing files. SQLite reconciliation uses logical contents, receipts and timestamps, not file-layout hash alone. Preserve cumulative attempts. Never clean another project or global /dev/shm/page cache.

See `LATEST_REPORT.md`, `verification-wake17.json` when available, and the latest cleanup receipt. Archive upload is not scientific progress and a supervisor waiting for decisions is not an experiment. No user-imposed lifetime research budget; each command remains finite, CPU-only,4core/6GiBAS,1concurrent.
