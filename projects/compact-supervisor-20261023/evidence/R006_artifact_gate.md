# R006 cross-surface availability and negative evidence
Exact EventTune source pin: 3150cae1eecf2ee82e508d32fe7f2e80913f8149.
Git tracked tree checked previously: 228 blobs with no predictions.jsonl,
margin Jacobians, masked ZB or Hessian bounds. No GitHub Releases detected.
Code sources: src/eventttt/task_qwen.py gives sequence candidate scores
(sum of target-token log probabilities); scripts/evaluate_task.py and
scripts/run_task_vlm_suite.py write predictions.jsonl under run output root.
.gitignore excludes runs/, artifacts/.
Checked report JSONs: reports/multiseed_significance.json,
reports/balanced_inference_results.json, reports/failure_efficiency.json,
reports/bright_uniform_two_model_metrics.json, reports/task_run_audit.json,
reports/internvl3_corrected_task_metrics.json,
reports/task_vlm_formal_metrics.json. None provides matched per-sample
masked projected activations or effective-controller margin gradients.
Google Drive filename search 'predictions.jsonl' yielded no result;
'EventTune' returned one untitled document, not an identified run artifact.
Files Library semantic query returned a figure note and a VIGOR patch,
not per-example predictions or controller-gradient arrays.
Hugging Face read-only jobs ps and ps(all=true): zero jobs currently
or historically returned through this connector, not proof other hosts
lack work. Private HF adapter and dataset exist in metadata but no
per-example control tensors were surfaced by the available action.
No local shell, mounted GPU host storage, or private run archive
was made available here. ABSENCE IS LIMITED TO THESE CHECKED SOURCES.

Required for first real diagnosis: immutable manifest/sample ID,
model and split hashes, support-fitted B and effective A, mask, each
candidate's sequence score before and after adaptation, per-sample
H=M*(ZB), margin d(score_correct-score_competitor)/dA,
and a validated remainder bound if claiming nonlinear certificates.
Query ground-truth labels may be inspected ONLY as labeled oracle
mechanism evidence; no label-dependent model selection.
