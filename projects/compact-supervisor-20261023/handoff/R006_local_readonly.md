# R006 Local actor handoff - read only, not executed
Parent project commit: 0bf88a5828567bb75bd3f50552da7bc8d668a06e
Source EventTune: 3150cae1eecf2ee82e508d32fe7f2e80913f8149.
Do not start inference, training, HF Jobs, GitHub Actions, SSH or
rerun anything. Only search authorized existing local/archived paths:
  runs/task_vlm_formal_v2/internvl3/**/predictions.jsonl
  runs/task_vlm_formal/**/predictions.jsonl
  runs/diagnostics/**/ 
  artifacts/**
These paths are suggestions from source code, not verified existing files.
For found files, report path, byte size, SHA256, model revision,
split and support seeds, presence of candidate sequence scores,
masked ZB, score-margin Jacobian wrt effective A and Taylor remainder
estimates. Preserve fingerprints, negative/missing rows, privacy controls.
If only predictions exist, declare partial, no nonlinear
reachability certificate. Report to a genuinely separate Work reviewer
for decision/design gate, exact commit and evidence manifests.
