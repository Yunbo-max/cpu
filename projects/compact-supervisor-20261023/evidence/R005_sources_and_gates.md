# R005 immutable artifact and literature inventory
Research project parent commit: 0404c8e177e9b8c8b406e623862ac717b82caa9d
External frozen EventTune repo: Yunbo-max/EventTune @ 3150cae1eecf2ee82e508d32fe7f2e80913f8149
Pinned Git blobs:
- src/eventttt/kv_ttt.py : 954363cd34e9976194618ff01a403ade5c8c798d
- src/eventttt/task_qwen.py : b67a0377000e0494f3a631529ed26b7786370eef
- reports/iclr2027_evidence_audit.md : f7299093731cf78d89ce6135e7b8b1b99c2f2b3e
- reports/task_subspace_diagnostics.md : d985c5bd800ffe83784a9a38077f037e2282efde

## READ ONLY tracked asset check
Exact recursive Git tree of external pin: 274 total tree entries, 228 tracked blobs, not truncated.
No tracked 'predictions.jsonl', per-example candidate log-scores, activation ZB,
per-example projected controller-margin Jacobians or Hessian bounds. The only
tracked filename mentioning predictions is scripts/compare_predictions.py.
reports/internvl3_corrected_task_metrics.json and task_vlm_formal_metrics.json
have per-fold aggregate metrics, not per-item score vectors.
scripts/evaluate_task.py lines 93-106 does produce 'predictions.jsonl',
but puts it inside the command's output directory; typical formal paths
are under runs/. .gitignore explicitly excludes runs/ and artifacts/.
Those directories may still exist on an authorized local machine or other
archive: absence from Git is NOT proof they no longer exist anywhere.
Hugging Face private adapter and dataset repository metadata were inspected,
but not raw artifact listings or per-item logit files.
The entire external experiment is explicitly frozen. No modification to
EventTune or new GPU inference is justified by these records.

## Checked primary novelty neighbors
- Adila et al., ICML 2026, Weight Updates as Activation Shifts:
  https://proceedings.mlr.press/v306/adila26a.html
  establishes first-order activation-vs-weight equivalence with
  intervention-location expressivity, and recommends post-block steering.
  Very close to generic R004 placement/capacity story.
- Skifstad et al., ICML 2026, Local Linearity of LLMs Enables Activation
  Steering via Model-Based Linear Optimal Control:
  https://proceedings.mlr.press/v306/skifstad26a.html
  linearized Jacobian control and setpoint error bounds; strong collision
  against advertising any generic Jacobian-controlled steering as new.
- Lai et al., ICML 2025, Joint Localization and Activation Editing:
  https://proceedings.mlr.press/v267/lai25a.html
  learns selected heads, operation types and intervention coefficients.
- Huang et al., ICML 2026, Von Mises-Fisher Mixture Model with Dynamic
  Shrinkage for Realistic Test-Time Transduction:
  https://proceedings.mlr.press/v306/huang26ag.html
  directly addresses class imbalance / negative transfer in VLM TTA.
- Yang et al., ICLR 2025, Solving Token Gradient Conflict in Mixture-of-Experts
  for Large Vision-Language Model:
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/532ce4fcf853023c4cf2ac38cbc5d002-Abstract-Conference.html
  another close gradient conflict precedent, albeit distinct setting.

## Decision
Do not claim unoccupied novelty for generic reachability, localized steering,
multi-sample conflicting gradients, or class-prior reweighting.
The restricted actuator code yields an exact missing-excitation operator;
this is a concrete falsifiable *mechanism*, not yet model-scale evidence.
A future immutable diagnostic needs per-item masked projected activations ZB,
correct-label/candidate score margins, projected score-margin gradients dmargin/dA,
and justified controller norm/remainder estimates with sample IDs and proper
query-label-only-for-mechanism boundaries. Existing tracked summary metrics
cannot reconstruct these values.
