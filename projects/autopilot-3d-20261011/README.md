# 3D CPU research: archive and on-demand working set

Project identity: `autopilot-3d-20261011`. Adopted procedure: **Research Autopilot Simple 0.3.0-simple.9**, source digest `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`.

The current scientific state is sequence **153**, active idea **gravity-pose-positive-selector-v1**. Read `CHECKPOINT.json` and the restored runner journal before taking scientific action. Historical `config.json` and `RESUME.md` contain startup context and must not reinitialize the project or reset cumulative usage.

## Storage

`archive-manifest.json` is the current pointer. It describes immutable, SHA256-verified ZIPs stored in 4 MiB content-addressed parts under `objects/`.

- `history`: complete R001–R016 checkpoint, 4,203 inventoried files, including original negative results, raw outputs, code, plans, receipts and all saved database failure/recovery evidence. Its exact SHA256 is `8457ed2ad3af98ca98cdc4d36617822a34778a97d9e346d7bfa8fad1050d9ac2`.
- `active`: the working set needed for the next hypothesis. It retains the complete runner database/history, fixed runtime, task receipts, all scripts/plans, small notes, source code, and R015/R016 raw evidence. Older cold files remain in `history`.
- Later `snapshot` entries retain every former active snapshot. Never rewrite an old object or discard a negative outcome.

The environment, bytecode caches and re-downloadable native input data are not historical experimental evidence. They are reconstructed from pinned source/data/dependency records as needed. No native data directory was present at migration. Do not treat the original small author-code smoke test as full-paper reproduction.

## Restore only what is needed

Resolve the current `main` commit using GitHub, then pin that full commit SHA for the entire download. Fetch `tools/restore.py` from the same commit and run:

```bash
python3 restore.py --commit FULL_COMMIT_SHA --kind active --destination EMPTY_PARENT
```

The helper verifies every part, whole archive, ZIP CRC and inventoried member before exposing `EMPTY_PARENT/autopilot_3d/`. It rejects path traversal, symlinks, duplicate entries and existing destinations. It does not execute or initialize research. For missing older evidence use `--kind history` in a separate empty directory. Never overlay historical state onto a newer working set. Restore at the original recorded root when possible; reconcile runner root/process identities before any relocation or restart.

Before execution: read fixed Simple guidance, CHECKPOINT, runner status/inbox/alerts/health, user stop, real process identities and current CPU/memory. Recreate only the needed environment. Research remains CPU-only, at most 8 cores/8 GiB and one experiment at a time. Open-ended authorization remains in force; cumulative use and failures never reset.

## Save, verify, then clean

1. Finish or reconcile all attempts, stop only this project's idle supervisor, and hold its project lock. Never clean active or unknown work.
2. Save all new code, raw results, plans, reviews and the next action. Update CHECKPOINT from the real runner state.
3. Download and retain the previous manifest and its exact commit. Create a fresh staging directory, then run the included `prepare_snapshot.py` with `--previous-manifest`. It retains every new/changed working file and keeps the historical manifests. Initial cold-file exclusion is allowed only for files with an exact archived size/SHA match.
4. Publish only this project namespace with an expected parent/subtree check. Keep unrelated project changes. `publish_snapshot.py` uses the session's authenticated GitHub connector through the current platform HostedAppsClient; obtain its connector identity through legitimate tool discovery. Alternatively use an authenticated git workflow with the same safeguards. No force pushes.
5. From the resulting immutable remote commit, run `restore.py --kind active --verify-only`; record its output, then verify restored SQLite integrity and cumulative identity. New archives are not accepted merely because upload returned success.
6. Confirm every non-reproducible local file is covered unchanged by a remotely verified archive. Recheck the project lock, no live command, no unknown attempt and no changed state. Then delete only this project's worktree, native download caches, temporary archives, staging files and environment. Keep a small local restore pointer and verification receipt. If upload, conflict handling or verification fails, retain the local files and report the actual failure.

Example subsequent snapshot:

```bash
python3 prepare_snapshot.py --root PROJECT_ROOT --previous-manifest previous-manifest.json --output FRESH_STAGING
python3 publish_snapshot.py --staging FRESH_STAGING --helper-dir CURRENT_HOSTED_HELPER_DIR --connector-id OBSERVED_GITHUB_CONNECTOR --expected-project-commit REVIEWED_COMMIT --message 'Archive next 3D evidence checkpoint'
```

The historical Library checkpoint v17 remains a fallback, not the authoritative latest record after new GitHub snapshots. Do not overwrite new GitHub evidence with that older backup.

## Scientific boundary

R016 supports mechanism attribution on one fixed author-generated synthetic stream: UP1/UP2 have 96/9 unassigned zero-slot cases and 12/84 cases where the native selector chooses non-positive focal despite an eligible positive alternative. It does not yet establish improved pose/focal quality. The next comparison must retain all candidate poses and evaluate quality after selection, with zero-root and no-positive-candidate controls.

Third-party source files retain their original notices and authorship. This archive does not apply a new blanket license to upstream code.
