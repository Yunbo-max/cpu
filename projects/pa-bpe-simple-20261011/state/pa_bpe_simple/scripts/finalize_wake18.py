#!/usr/bin/env python3
import datetime
import hashlib
import json
from pathlib import Path

state = Path(__file__).resolve().parents[1]
project = state.parents[1]
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

def load(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

budget_path = state / "phase_budget.json"
budget = load(budget_path)
if abs(budget["cumulative_charged_seconds"] - 1577.4370255409858) > 1e-12:
    raise RuntimeError("unexpected parent cumulative wall")
budget["updated_utc"] = now
budget["windows"].append({
    "id": "wake18-20261012",
    "root": str(state / "execution_windows/wake18"),
    "attempts": 5,
    "wall_seconds": 74.56982344499556,
    "reserved_seconds": 0,
    "status": "awaiting_decision_supervisor_health_lost_after_controlled_idle_interrupt",
    "scientific_processes_active": 0,
    "receipt_inventory": "execution_windows/wake18/.research-autopilot/runner/attempts",
    "notes": "Fixed FLORES secondary-arm replay, independent verification, exposed-domain robust-frontier analysis and independent verification. All five scientific attempts exit0. One pre-science unsafe-path contract rejection consumed no attempt. Idle supervisor was deliberately interrupted after settlement."
})
budget["cumulative_charged_seconds"] = 1652.0068489859813
write(budget_path, budget)

checkpoint_path = state / "PA_BPE_Simple_Checkpoint.md"
checkpoint = checkpoint_path.read_text()
heading = """# 最新规范状态：generation 19，2026-10-12

本轮对已经冻结的Classical、PA base/window/hybrid/ratio 1000-merge codes，在FLORES-200 devtest的1012个英法西内容对齐句子上完成固定重放，并以既有GlobalVoices结果计算暴露域稳健前沿。FLORES上base/window Gini最低（0.007425/0.007741），但总token成本均增加约4.0%；hybrid Gini 0.022759、总成本+1.7939%、最差语言成本+0.1674%；ratio Gini 0.048134，较Classical恶化。

冻结三目标反证未成立：没有次级臂同时比hybrid更低Gini且不增加总成本或最差语言成本。跨域最小公平收益/最大成本准则下，Classical与hybrid构成稳健Pareto前沿；hybrid严格支配base/window，跨域最小Gini改善0.0179368、最大总成本增幅1.7939%、最大最差语言成本增幅0.1674%。这只支持固定候选中的稳健折中，不证明hybrid在每域Gini最低或其机制具有因果性。两组独立核验分别通过42和19项检查。

五个科学attempt均exit0，新增计费wall 74.569823445秒，累计1652.006848986秒；峰值RSS 37,355,520字节，无OOM、timeout或内存等待。首次提交因跨窗口证据路径不安全在科学启动前被拒绝，复制并哈希绑定为本窗口输入后修复；未消耗attempt。任务全部终态且reservation0，闲置supervisor受控中断后的health为lost，保留为管理事故而非科学失败。

下一步：只用既有固定codes和开发产物，审计hybrid前500个global merges前后merge ownership与逐语言边际token效果，解释其为何避免signed-gap overshoot；两个已暴露确认域不得用于新调参。

恢复必读：本文件、`resources_initial.json`、`manifest.json`、`phase_budget.json`、`PA_BPE_Wake18_Report.md`、`evidence/wake18_handoff.json`、`evidence/incidents_wake18.json`、`execution_windows/wake18/output/flores_secondary.json`、`flores_secondary_verification.json`、`cross_domain_frontier.json`及`cross_domain_frontier_verification.json`。

# 历史原字节段落保留

"""
checkpoint_path.write_text(heading + checkpoint)

old_manifest = load(state / "manifest.json")
if old_manifest["generation"] != 18:
    raise RuntimeError("expected generation 18")
excluded_exact = {
    "manifest.json",
    "execution_windows/wake18/inputs/flores200_dataset.tar.gz",
}
excluded_parts = {".writer.lock", "__pycache__", ".venv"}
files = dict(old_manifest["files"])
for path in sorted(state.rglob("*")):
    if not path.is_file() or path.is_symlink():
        continue
    rel = path.relative_to(state).as_posix()
    if rel in excluded_exact or any(part in excluded_parts for part in path.relative_to(state).parts):
        continue
    if path.suffix in {".pyc", ".lock"} or path.name.endswith(("-wal", "-shm")):
        continue
    files[rel] = sha(path)
manifest = {
    "generation": 19,
    "created_utc": now,
    "library_file_id": old_manifest.get("library_file_id"),
    "previous_generation": 18,
    "previous_library_version": old_manifest.get("previous_library_version"),
    "previous_archive_sha256": old_manifest.get("previous_archive_sha256"),
    "goal_mode": "continuous_research",
    "science_identity": "one active idea; fixed FLORES secondary arms and exposed-domain robust frontier verified; hybrid is the robust fixed-arm tradeoff, mechanism audit next; no tuning on exposed confirmation domains",
    "files": dict(sorted(files.items())),
}
write(state / "manifest.json", manifest)

current_path = project / "CURRENT.json"
current = load(current_path)
if current["generation"] != 18:
    raise RuntimeError("expected CURRENT generation 18")
current.update({
    "generation": 19,
    "manifest_sha256": sha(state / "manifest.json"),
    "active_science_processes": 0,
    "reserved_seconds": 0,
    "next_action": "Audit merge ownership and per-language marginal token effects before versus after hybrid's fixed 500-global prefix using existing codes and development artifacts; do not tune on exposed confirmation domains.",
    "confirmation_outcome_status": "GlobalVoices512 and FLORES-200 devtest1012 exposed; all fixed arms scored; robust frontier is Classical plus hybrid; mechanism remains descriptive"
})
write(current_path, current)
print(json.dumps({"generation": 19, "manifest_files": len(files), "manifest_sha256": current["manifest_sha256"], "cumulative_wall": budget["cumulative_charged_seconds"]}))
