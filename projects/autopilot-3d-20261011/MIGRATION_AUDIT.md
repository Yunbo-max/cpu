# GitHub storage migration audit

Project: autopilot-3d-20261011. User requested GitHub as the durable project store on 2026-10-12. Scope is this 3D project only.

The immutable scientific archive commit is `c6f7b0a1253f30319bc3524d14396f87a1969d97`. Historical checkpoint v17 is preserved exactly as 4 MiB content-addressed parts. The complete history contains 4,203 files in a 232,473,397-byte ZIP. A separate active workset contains 1,642 files in a 26,462,324-byte ZIP. Files omitted from the working set remain in history. Author source identities, negative results, failed attempts, repairs, authorization, raw outputs and historical runtime records are preserved. Reproducible dependencies and original input downloads remain recoverable by their existing source pins/manifests.

The active archive was independently downloaded from the immutable GitHub commit, verified by every part SHA256, whole ZIP SHA256, inventory and ZIP CRC, and extracted into a clean directory. Its database passes integrity_check at sequence 153, with 113 terminal journal attempts and 13,137.27925871903 command-seconds. No nonterminal attempt exists. Three separately preserved recovery receipts retain the full observed total of 116 attempts and 13,139.140214 command-seconds. The current idea is gravity-pose-positive-selector-v1. No scientific experiment was executed during this migration.

The complete history remote readback result and the local coverage audit are recorded in the accompanying verification JSON files. Local cleanup is a later separate action and is permitted only after those checks pass, no project process or unknown attempt remains, and the project lock is held. This document does not by itself assert that cleanup occurred.

The recurring project task is configured for restore-active → resume the pinned Simple runner → publish all new evidence with optimistic concurrency → immutable remote verification → local project cleanup. Failure or conflict retains local files. The publisher preserves unrelated repository updates and blocks same-project changes. The latest helper additionally requires a full hexadecimal commit and limits writes to this project's namespace. The user's open-ended CPU authorization remains unchanged.

The reported host memory before migration was shared across work: 7,968,645,120 bytes charged, comprising approximately 1.45 GB anonymous memory, 6.04 GB file cache, and 135 MB shmem. There was no OOM or OOM-kill evidence. Removing local files can reclaim storage and associated cache; it is not a guarantee to release unrelated process memory.
