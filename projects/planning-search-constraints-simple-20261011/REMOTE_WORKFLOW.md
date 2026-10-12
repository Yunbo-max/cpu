# Download, run, publish, verify, evict

User authority: 2026-10-12. Keep historical research in `Yunbo-max/cpu`; use
local storage for the files needed for the current bounded experiment. Do not
delete chat history, other projects' files, active files, unknown attempts, or
the only copy of unpublished results. This changes storage, not the scientific
policy, runtime digest, resource limit, stopping semantics, or cumulative ledger.

## Restore

Use an immutable published commit and configure sparse checkout before
checkout. This avoids downloading every project's historical blobs:

```sh
git clone --filter=blob:none --no-checkout https://github.com/Yunbo-max/cpu.git cpu-restore
git -C cpu-restore sparse-checkout init --no-cone
git -C cpu-restore sparse-checkout set '/projects/planning-search-constraints-simple-20261011/*.py' '/projects/planning-search-constraints-simple-20261011/*.md' '/projects/planning-search-constraints-simple-20261011/LATEST.json' '/projects/planning-search-constraints-simple-20261011/snapshots/'
git -C cpu-restore checkout --detach <verified-commit>
python3 cpu-restore/projects/planning-search-constraints-simple-20261011/archive_store.py restore --repo cpu-restore --project planning-search-constraints-simple-20261011 --dest planning-recovered --prefix CHECKPOINT.json
```

Restore `CURRENT_WINDOW.json`, `RESUME.md`, and the relevant window controls
the same way, then select the source, data, and results required for the next
step. Omit `--prefix` only for a full recovery. Missing pack parts are fetched
with `git show` and checked before use. Never overwrite a newer active project
with an older snapshot. Online SQLite backups are individually consistent;
cross-database/runtime consistency requires receipt reconciliation.

## Publish

After a bounded command finishes, retain all raw results, failures, source/data
identities, design records, and cumulative consumption. Use a fresh tag:

```sh
python3 cpu-restore/projects/planning-search-constraints-simple-20261011/archive_store.py snapshot --repo cpu-restore --root planning-recovered --project planning-search-constraints-simple-20261011 --tag <unique-tag> --overlay
python3 cpu-restore/projects/planning-search-constraints-simple-20261011/archive_store.py verify --repo cpu-restore --project planning-search-constraints-simple-20261011
```

For a selectively restored workspace, `--overlay` retains prior manifest
entries for files absent locally. Updated and new files receive new entries;
absence never implies deletion. Omit `--overlay` only when intentionally
snapshotting the complete project inventory.

Use the authenticated GitHub connector if native Git has no write credential.
Create blobs in pieces no larger than 8 MiB (base64 fits the connector's 16 MiB
request limit). Check Git blob SHA1 and SHA256 manifests. Build a tree on the
latest `main`, changing only this project's paths. Create a commit with that
parent and update `main` using `expected_sha`; on a conflict, refresh and retry
without force. Preserve other projects' concurrent commits. Blob upload alone
does not publish a recoverable archive.

## Verify and evict

Fetch the published immutable commit into a separate verification checkout.
Compare expected paths and blob IDs, then run the verifier against downloaded
parts and restore the essential control files and SQLite databases. Record
the verified commit, member counts, and checksums in a receipt. Keep a copy of
that receipt remotely.

Delete only byte-matching idle originals with verified remote copies. Recheck
local size, hash, open descriptors, mapped files, and known job identity just
before deletion. Keep active runner controls, databases/sidecars, unuploaded
changes, and unknown in-flight attempts. Do not stop another project. A live
supervisor whose PID cannot be addressed from the current namespace remains
live/unknown; a failed signal is not a stop receipt.

Once verified, evict downloaded archives, restored idle payloads, temporary
status exports, and local archive pack copies. Git object caches also occupy
local space: a fresh partial clone may replace an idle full clone once no
unpublished objects remain. Retain only small recovery pointers and the
current working set. Report disk bytes removed separately from measured RAM;
filesystem cache, anonymous memory, and /dev/shm are different quantities.

Existing durable checkpoint files remain a fallback during this migration;
this policy does not authorize deleting those remote originals.

## Memory waiting policy

User clarification on 2026-10-12: if insufficient memory prevents an experiment,
wait for headroom and then run. Keep each wait bounded and observable; avoid
repeatedly submitting the same unchanged command only to collect prelaunch
refusals. Continue independent low-memory analysis and archiving where feasible.
If pressure persists, leave a recoverable waiting state for the existing next
wake; do not create another schedule or declare the continuous goal finished.
Report the actual blocker if repeated observations show no usable headroom, or
the minimum feasible job exceeds the authorized 8 GB. Preserve all previous
failures, resource readings, and pending work. Never stop another project or
raise the memory limit to make a command pass.
