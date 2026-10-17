# PRAXIS → CREDO CPU research loop (checkpoint 2026-10-17)

This is a separate continuing project archive for the ordered CPU-only research requested in this conversation. PRAXIS's initial diagnostics and provisional reroute precede CREDO, the current line. No visual experiment, Gate A, novelty claim, or CVPR claim has been established.

Cycle 11 compares the pinned CREDO implementation with PTO, RO, and SPO+ over the same three chronological 24-month test blocks. Ranks (lower is better): CREDO 1/5/1, PTO 1/5/1, RO 1/4/5, SPO+ 1/6/1. The single dependent time series and three test blocks support descriptive observations only. DFL was not executable because the pinned Mac environment lacks cvxpy and cvxpylayers.

## Files

- `continuation-checkpoint.md`: current state, ordering, limits, and next action.
- `autoresearch/cycles.md`: cycle history through Cycle 11.
- `credo_temporal_baseline_audit.py`: reproducible one-worker CPU comparison using pinned source implementations.
- `credo_temporal_baseline_results.json`: per-block decisions, ranks, provenance, and limitations.
- `autoresearch/research-state.json`, `research-intake.yaml`, `event-ledger.jsonl`, `ledger-anchor.json`: preserved local procedure records (the state ledger is still at its initialization transition; do not infer a formal gate or state advancement from the narrative cycle log).
- `literature_notes.md`: current targeted sources/collision notes.

The source CREDO commit is `19e884718599cd390564ddf93aff943a720f3e22`. The locally inspected source CSV SHA-256 is `d31a480ce63621155d399f3e1740bff0950bc982b2ba41991f58d9afe6322b67`; source data are not copied into this archive. The older statistical-trust project's explicit stop receipt is unchanged. This project has no verified unattended runner; work proceeds in active sessions and resumes from the checkpoint.
