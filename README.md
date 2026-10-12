# CPU research archive

User-authorized archive for CPU-only research.

## Statistical learning and trustworthy decision-making

Project ID: `statistical-trust-simple-20261011`.

The complete historical snapshot has been published and freshly downloaded for full verification. An original-path restore drill passed, and the verified local project copy was cleaned up. See [the project archive and recovery guide](projects/statistical-trust-simple-20261011/README.md), [LATEST.json](projects/statistical-trust-simple-20261011/LATEST.json), and [the migration receipt](projects/statistical-trust-simple-20261011/MIGRATION_RECEIPT.json).

This migration only operates on the statistical-trust project. Other projects can maintain their own independent directories under [projects/](projects/); their files and processes are not modified by this migration.

The intended workflow is restore a verified snapshot, run bounded CPU tasks, upload and verify the resulting checkpoint, then remove only verified temporary local copies. Running processes and page cache are distinct from files on disk; file deletion is not a guarantee that all memory is immediately freed.

Third-party code and data retain their original licenses and attribution. No new license is granted over third-party materials.
