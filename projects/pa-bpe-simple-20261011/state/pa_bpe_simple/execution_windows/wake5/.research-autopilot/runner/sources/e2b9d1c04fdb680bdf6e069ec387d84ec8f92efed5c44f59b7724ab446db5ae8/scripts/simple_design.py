#!/usr/bin/env python3
"""Read-only, claim-scoped experiment design and artifact coverage checks.

This is neither a statistical engine nor an admission gate. Declared predictions,
timestamps, hashes and complete fields do not establish scientific validity or
prospective independence. Missing work is reported for the claims that need it.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _oneof(value, choices):
    return isinstance(value, str) and value in choices


def _note(value):
    return _text(value) or (isinstance(value, dict) and set(value) == {"not_applicable_reason"}
                            and _text(value["not_applicable_reason"]))


def _relative(value):
    if (not _text(value) or PurePosixPath(value).is_absolute() or "\\" in value or "\x00" in value
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError("Expected a safe project-relative path")
    return value


def _read(root, relative, document=False):
    """Read and hash the same regular bytes through no-follow descriptors."""
    _relative(relative)
    descriptors = []
    try:
        current = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(current)
        parts = relative.split("/")
        for part in parts[:-1]:
            current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            descriptors.append(current)
        handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current)
        descriptors.append(handle)
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("Evidence must be a regular file")
        limit = 8 * 1024 * 1024
        if document and before.st_size > limit:
            raise ValueError("Design/results metadata JSON exceeds 8 MiB; reference large artifacts instead of embedding them")
        chunks, digest, total = [], hashlib.sha256(), 0
        while block := os.read(handle, 1024 * 1024):
            digest.update(block)
            if document:
                total += len(block)
                if total > limit:
                    raise ValueError("Design/results metadata JSON grew beyond 8 MiB")
                chunks.append(block)
        after = os.fstat(handle)
        signature = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if signature(before) != signature(after):
            raise ValueError("File changed while being read")
        return b"".join(chunks) if document else None, {"path": relative, "sha256": digest.hexdigest()}
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


class _Check:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve(strict=True)
        self.gaps, self.claims, self.comparisons = [], {}, {}

    def gap(self, code, path, message, action, claims=None, comparisons=None):
        self.gaps.append({"code": code, "path": path, "message": message, "next_action": action,
                          "claim_ids": sorted(set(self.claims if claims is None else claims)),
                          "comparison_ids": sorted(set(comparisons or []))})

    def load(self, path):
        supplied = Path(path)
        relative = supplied.relative_to(self.root).as_posix() if supplied.is_absolute() else str(supplied)
        raw, ref = _read(self.root, relative, document=True)
        document = json.loads(raw)
        if not isinstance(document, dict):
            raise ValueError("Document must be a JSON object")
        return document, ref

    def entries(self, value, path, key="id", claims=None, comparisons=None):
        result = {}
        if not isinstance(value, list):
            self.gap("invalid_structure", path, "Expected an array", "Supply an explicit array for this field", claims, comparisons)
            return result
        for index, item in enumerate(value):
            name = item.get(key) if isinstance(item, dict) else None
            if not _text(name) or name in result:
                self.gap("invalid_identifier", f"{path}[{index}]", "Missing or duplicate identifier",
                         "Give each entry a distinct stable identifier", claims, comparisons)
            else:
                result[name] = item
        return result

    def ids(self, value, path, claims=None, comparisons=None):
        if not isinstance(value, list) or any(not _text(item) for item in value) or len(set(value)) != len(value):
            self.gap("invalid_structure", path, "Expected unique string identifiers",
                     "List each required identifier once", claims, comparisons)
            return []
        return value

    def fields(self, value, names, path, claims=None, comparisons=None):
        value = value if isinstance(value, dict) else {}
        for name in names:
            if not _note(value.get(name)):
                self.gap("missing_design_field", f"{path}.{name}", f"Missing {name} or a specific applicability reason",
                         f"Specify {name} for this comparison, or explain why it does not apply", claims, comparisons)

    def identifiers(self, value, names, path, claims=None, comparisons=None):
        for name in names:
            if not _text(value.get(name)):
                self.gap("invalid_identifier", f"{path}.{name}", "An actual nonempty identity string is required",
                         f"Record the actual {name}; an applicability note cannot substitute for an identity", claims, comparisons)

    def refs(self, refs, path, claims=None, comparisons=None, required=False):
        if not isinstance(refs, list) or (required and not refs):
            self.gap("missing_evidence", path, "Actual artifact references are required here",
                     "Produce or locate the real artifacts and record their current hashes", claims, comparisons)
            return False
        valid, seen = True, set()
        for index, ref in enumerate(refs):
            try:
                if (not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
                        or not isinstance(ref["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"])):
                    raise ValueError("Reference requires path and a lowercase SHA256")
                _, observed = _read(self.root, ref["path"])
                if observed != ref or ref["path"] in seen:
                    raise ValueError("Artifact hash changed or reference is duplicated")
                seen.add(ref["path"])
            except (OSError, ValueError, TypeError) as exc:
                valid = False
                self.gap("invalid_evidence", f"{path}[{index}]", str(exc),
                         "Recover the correct versioned artifact; do not invent a future receipt", claims, comparisons)
        return valid

    def affected(self, comparison_id, comparison):
        declared = comparison.get("claim_ids", [])
        declared = declared if isinstance(declared, list) else []
        return sorted({name for name in declared if isinstance(name, str) and name in self.claims}
                      | {name for name, claim in self.claims.items()
                         if isinstance(claim.get("required_comparison_ids"), list) and comparison_id in claim["required_comparison_ids"]})

    def resources(self, value, path, claims, comparisons):
        resource = value if isinstance(value, dict) else {}
        authorization = resource.get("authorization") if isinstance(resource.get("authorization"), dict) else {}
        missing = [name for name in ("basis", "allocation", "duration") if not _text(authorization.get(name))]
        if authorization.get("status") != "recorded":
            missing.insert(0, "status")
        if missing:
            self.gap("authorization_documentation_missing", path + ".authorization",
                     "Resource authorization/allocation documentation is incomplete: " + ", ".join(missing),
                     "Record the existing user/session authorization, exact allocation and time window; reuse known permission and continue resource/source work while resolving this prerequisite",
                     claims, comparisons)
        self.refs(authorization.get("evidence", []), path + ".authorization.evidence", claims, comparisons)
        if not _oneof(resource.get("hardware_kind"), {"cpu", "gpu"}) or not _oneof(resource.get("hardware_status"), {"declared", "observed"}) or not _text(resource.get("hardware")):
            self.gap("hardware_unknown", path, "The actual execution hardware is not established",
                     "Inspect the authorized host, record CPU/GPU and memory constraints, then adapt the matrix", claims, comparisons)
        self.refs(resource.get("inventory_refs", []), path + ".inventory_refs", claims, comparisons,
                  required=resource.get("hardware_status") == "observed")
        estimates = resource.get("estimates") if isinstance(resource.get("estimates"), dict) else {}
        for name in ("wall_seconds", "peak_memory_gib"):
            value = estimates.get(name)
            if type(value) not in {int, float} or not math.isfinite(value) or value <= 0:
                self.gap("resource_estimate_missing", path + ".estimates." + name, "No positive finite resource estimate",
                         f"Calibrate {name} on the available hardware and record a feasible estimate", claims, comparisons)
        calibration = resource.get("calibration") if isinstance(resource.get("calibration"), dict) else {}
        if calibration.get("status") != "observed":
            self.gap("calibration_missing", path + ".calibration", "Execution estimates have no recorded calibration",
                     "Run a bounded resource calibration, or record the unavailable condition and narrow the planned scope", claims, comparisons)
        self.refs(calibration.get("evidence", []), path + ".calibration.evidence", claims, comparisons,
                  required=calibration.get("status") == "observed")
        self.fields(calibration, ["reason"], path + ".calibration", claims, comparisons)
        self.fields(resource, ["scope_adjustment"], path, claims, comparisons)

    def plan(self, plan, goal_version):
        self.claims = self.entries(plan.get("claims"), "claims")
        if not self.claims:
            self.gap("missing_claims", "claims", "No scoped research claim is declared", "State the claims this design can investigate")
        self.comparisons = self.entries(plan.get("comparisons"), "comparisons")
        if type(plan.get("schema_version")) is not int or plan["schema_version"] != 1:
            self.gap("schema_version", "schema_version", "Unsupported design schema", "Use schema_version 1")
        self.identifiers(plan, ["design_id", "idea"], "plan")
        for key in ("goal_contract_version", "revision"):
            if type(plan.get(key)) is not int or plan[key] < 1:
                self.gap("invalid_version", key, "A positive declared version is required", "Bind the plan to its actual goal contract and idea revision")
        if goal_version is not None and plan.get("goal_contract_version") != goal_version:
            self.gap("goal_contract_mismatch", "goal_contract_version", "Plan belongs to a different supplied goal contract version",
                     "Review affected claims and create a versioned plan for the current goal; preserve the old plan")
        self.fields(plan.get("scope"), ["claim_scope"], "scope")
        scope = plan.get("scope") if isinstance(plan.get("scope"), dict) else {}
        if not _oneof(scope.get("level"), {"diagnostic", "development", "confirmation", "formal"}):
            self.gap("scope_missing", "scope.level", "Design scope is not declared", "Declare diagnostic, development, confirmation or formal scope")
        exposure = plan.get("exposure") if isinstance(plan.get("exposure"), dict) else {}
        if not _oneof(exposure.get("mode"), {"prospective", "retrospective", "confirmation"}):
            self.gap("exposure_missing", "exposure.mode", "Prior result exposure is not declared",
                     "Declare whether the design precedes results, follows inspected results, or uses separate confirmation")
        self.fields(exposure, ["prior_observations", "heldout_policy"], "exposure")
        papers = self.entries(plan.get("paper_designs"), "paper_designs")
        for name, paper in papers.items():
            claims = sorted({claim for cid, comparison in self.comparisons.items()
                             if isinstance(comparison.get("paper_design_ids"), list) and name in comparison["paper_design_ids"]
                             for claim in self.affected(cid, comparison)})
            self.fields(paper, ["url", "locator", "borrowed_design", "adaptation_reason"], f"paper_designs.{name}", claims)
            if not isinstance(paper.get("url"), str) or not re.match(r"^https?://[^/\s]+", paper["url"]):
                self.gap("paper_source_missing", f"paper_designs.{name}.url", "A primary-paper URL is required",
                         "Record the paper URL and exact section/table whose design was examined", claims)
        for name, claim in self.claims.items():
            self.fields(claim, ["statement"], f"claims.{name}", [name])
            required = self.ids(claim.get("required_comparison_ids"), f"claims.{name}.required_comparison_ids", [name])
            if not _oneof(claim.get("kind"), {"empirical", "formal"}):
                self.gap("claim_kind", f"claims.{name}.kind", "Claim kind is unspecified", "Declare empirical or formal scope", [name])
            if not required and not (claim.get("kind") == "formal" and _text(claim.get("not_applicable_reason"))):
                self.gap("missing_comparison", f"claims.{name}", "Claim has no required comparison or formal applicability rationale",
                         "Map the empirical claim to comparisons, or explain why a formal result needs no experiment", [name])
            for cid in required:
                comparison = self.comparisons.get(cid)
                if comparison is None or not isinstance(comparison.get("claim_ids"), list) or name not in comparison["claim_ids"]:
                    self.gap("comparison_mapping", f"claims.{name}.required_comparison_ids", f"Comparison {cid} is absent or does not link back to this claim",
                             "Add the required comparison and its claim link", [name], [cid])
        for cid, comparison in self.comparisons.items():
            claims, ids, path = self.affected(cid, comparison), [cid], f"comparisons.{cid}"
            mapped = self.ids(comparison.get("claim_ids"), path + ".claim_ids", claims, ids)
            if not mapped or any(name not in self.claims for name in mapped):
                self.gap("comparison_mapping", path + ".claim_ids", "Comparison needs known affected claims", "Map this comparison to declared claims", claims, ids)
            borrowed = self.ids(comparison.get("paper_design_ids"), path + ".paper_design_ids", claims, ids)
            if not borrowed or any(name not in papers for name in borrowed):
                self.gap("missing_paper_design", path + ".paper_design_ids", "No complete published design mapping",
                         "Read the relevant published comparison and record what was borrowed and adapted", claims, ids)
            self.fields(comparison, ["purpose", "prediction"], path, claims, ids)
            for section, fields in {"outcome_rules": ["supports", "weakens", "inconclusive"],
                                    "data": ["source", "version", "split", "leakage_control"],
                                    "metric": ["definition", "aggregation", "direction"],
                                    "statistics": ["unit", "pairing", "precision", "randomness", "multiplicity", "stopping"]}.items():
                self.fields(comparison.get(section), fields, path + "." + section, claims, ids)
            arms = self.entries(comparison.get("arms"), path + ".arms", claims=claims, comparisons=ids)
            roles = {arm.get("role") for arm in arms.values() if isinstance(arm.get("role"), str)}
            if "method" not in roles or not roles.intersection({"baseline", "control"}):
                self.gap("missing_control_arm", path + ".arms", "Comparison needs method and baseline/control arms",
                         "Add the consequential baseline or simple control and specify matched resources/protocol", claims, ids)
            for aid, arm in arms.items():
                self.fields(arm, ["implementation", "fairness"], path + ".arms." + aid, claims, ids)
                if not _oneof(arm.get("role"), {"method", "baseline", "control"}):
                    self.gap("arm_role", path + ".arms." + aid, "Unknown arm role", "Declare method, baseline or control", claims, ids)
            execution = comparison.get("execution") if isinstance(comparison.get("execution"), dict) else {}
            self.fields(execution, ["analysis"], path + ".execution", claims, ids)
            for key in ("task_ids", "outputs"):
                values = self.ids(execution.get(key), path + ".execution." + key, claims, ids)
                if not values:
                    self.gap("execution_mapping", path + ".execution." + key, "Execution/analysis handoff is missing",
                             "Name planned task IDs and versioned output paths; future files need no fabricated hashes", claims, ids)
                if key == "outputs":
                    for value in values:
                        try:
                            _relative(value)
                        except ValueError as exc:
                            self.gap("unsafe_output", path + ".execution.outputs", str(exc), "Use project-relative versioned output paths", claims, ids)
            self.resources(comparison.get("resources"), path + ".resources", claims, ids)

    def results(self, plan, plan_ref, results):
        start = len(self.gaps)
        for key in ("schema_version", "design_id", "goal_contract_version", "idea", "revision"):
            if results.get(key) != plan.get(key):
                self.gap("plan_mismatch", "results." + key, "Results refer to a different design identity/version",
                         "Use the actual frozen plan for these results and keep later designs separate")
        if results.get("plan_ref") != plan_ref or not self.refs([results.get("plan_ref")], "results.plan_ref", required=True):
            self.gap("plan_mismatch", "results.plan_ref", "Results do not pin the exact supplied plan bytes",
                     "Preserve the original plan and link these results to its real path and SHA256")
        binding_valid = len(self.gaps) == start and not any(g["code"] == "goal_contract_mismatch" for g in self.gaps)
        records = self.entries(results.get("comparisons"), "results.comparisons", key="comparison_id")
        documented = set()
        for cid, record in records.items():
            comparison = self.comparisons.get(cid)
            if comparison is None:
                self.gap("unknown_comparison", "results.comparisons." + cid, "Result has no declared comparison",
                         "Record the actual plan for this result before using it for a claim", comparisons=[cid])
                continue
            claims, ids, path, before = self.affected(cid, comparison), [cid], "results.comparisons." + cid, len(self.gaps)
            if not _oneof(record.get("status"), {"complete", "partial", "invalid", "not_run"}):
                self.gap("result_status", path + ".status", "Result execution status is not declared", "Declare complete, partial, invalid or not_run", claims, ids)
            self.fields(record, ["limitations", "next_action"], path, claims, ids)
            if not _oneof(record.get("conclusion"), {"supported", "not_supported", "inconclusive"}):
                self.gap("result_conclusion", path + ".conclusion", "No scoped reported conclusion", "Report supported, not_supported or inconclusive with limitations", claims, ids)
            planned_arms = comparison.get("arms") if isinstance(comparison.get("arms"), list) else []
            expected = {arm["id"] for arm in planned_arms if isinstance(arm, dict) and _text(arm.get("id"))}
            arms = self.entries(record.get("arms"), path + ".arms", key="arm_id", claims=claims, comparisons=ids)
            for aid in sorted(expected - set(arms)):
                self.gap("missing_result_arm", path + ".arms", f"No observed artifacts for arm {aid}",
                         f"Run or recover arm {aid}; limit this claim until its comparison is available", claims, ids)
            for aid, arm in arms.items():
                if aid not in expected:
                    self.gap("unknown_result_arm", path + ".arms." + aid, "Arm was not declared in this plan", "Link the result to its actual design revision", claims, ids)
                self.identifiers(arm, ["task_id", "run_id"], path + ".arms." + aid, claims, ids)
                execution = comparison.get("execution") if isinstance(comparison.get("execution"), dict) else {}
                task_ids = execution.get("task_ids") if isinstance(execution.get("task_ids"), list) else []
                if arm.get("task_id") not in task_ids:
                    self.gap("execution_mapping", path + ".arms." + aid, "Observed task is absent from the declared execution mapping",
                             "Link the real run to the planned task or document a new plan revision", claims, ids)
                self.refs(arm.get("artifact_refs"), path + ".arms." + aid + ".artifact_refs", claims, ids, required=True)
            self.refs(record.get("analysis_refs"), path + ".analysis_refs", claims, ids, required=True)
            if record.get("status") != "complete":
                self.gap("comparison_incomplete", path, "Comparison is partial, invalid or unrun",
                         "Repair or finish the affected comparison and preserve the present evidence", claims, ids)
            if len(self.gaps) == before and binding_valid:
                documented.add(cid)
        for cid, comparison in self.comparisons.items():
            if cid not in records:
                self.gap("missing_result_comparison", "results.comparisons", f"No results supplied for {cid}",
                         "Execute or recover this comparison before using it to support the linked claims", self.affected(cid, comparison), [cid])
        return documented


class _DecisionReview(_Check):
    """Optional declarations produce advisories, never change legacy coverage."""

    def object(self, value, path, claims=None, comparisons=None):
        if not isinstance(value, dict):
            self.gap("invalid_review_structure", path, "Expected a review object",
                     "Repair this declared review field; continue unrelated work", claims, comparisons)
            return {}
        return value

    def block(self, value, path, fields, claims, comparisons):
        if value is None:
            self.gap("review_unreviewed", path, "No review is recorded for this question",
                     "Decide whether this review can change the next action; perform it or record why it does not apply",
                     claims, comparisons)
            return
        block = self.object(value, path, claims, comparisons)
        status = block.get("status")
        if not _oneof(status, {"unreviewed", "planned", "executed", "not_applicable"}):
            self.gap("review_status", path + ".status", "Unknown declared review status",
                     "Use unreviewed, planned, executed or not_applicable", claims, comparisons)
        elif status == "unreviewed":
            self.gap("review_unreviewed", path, "This question is explicitly unreviewed",
                     "Prioritize the consequential unanswered question; do not treat the blank as a completed check",
                     claims, comparisons)
        elif status == "not_applicable":
            self.fields(block, ["rationale"], path, claims, comparisons)
        else:
            self.fields(block, ["rationale", *fields], path, claims, comparisons)
            if status == "planned":
                self.gap("review_not_executed", path, "Review is planned, not observed",
                         "Perform the declared check before relying on its outcome; retain planning as planning",
                         claims, comparisons)
        self.refs(block.get("evidence_refs", []), path + ".evidence_refs", claims, comparisons,
                  required=status == "executed")

    def inspect(self, plan, results, claim_id):
        binding = plan.get("workflow_binding")
        if binding is None:
            self.gap("workflow_binding_unreviewed", "workflow_binding",
                     "Scientific policy and executor editions are not separately declared",
                     "Recover the active scientific edition and executor from project records; do not infer a policy migration from an executor upgrade")
        else:
            binding = self.object(binding, "workflow_binding")
            self.identifiers(binding, ["scientific_edition", "executor_edition"], "workflow_binding")
            self.refs(binding.get("evidence_refs", []), "workflow_binding.evidence_refs")
        declared = set()
        for cid, comparison in self.comparisons.items():
            claims, ids = self.affected(cid, comparison), [cid]
            path = "comparisons." + cid
            review = comparison.get("decision_review")
            if review is None:
                self.gap("decision_review_unreviewed", path + ".decision_review",
                         "No structured decision review is recorded; existing design coverage is unchanged",
                         "Identify the decision this comparison changes and the cheapest discriminating check when useful",
                         claims, ids)
            else:
                declared.add(cid)
                review = self.object(review, path + ".decision_review", claims, ids)
                for section, names in {
                    "next_decision": ["question", "cheaper_check", "why_next"],
                    "objectives": ["primary"],
                    "comparison_basis": ["tolerances", "justification"],
                }.items():
                    item = self.object(review.get(section), path + ".decision_review." + section, claims, ids)
                    self.fields(item, names, path + ".decision_review." + section, claims, ids)
                    if section == "objectives":
                        for name in ("protected_constraints", "secondary"):
                            self.ids(item.get(name), path + ".decision_review.objectives." + name, claims, ids)
                    elif section == "comparison_basis" and not _oneof(item.get("mode"), {"implementation_equivalence", "task_quality"}):
                        self.gap("comparison_basis_unspecified", path + ".decision_review.comparison_basis.mode",
                                 "Implementation equivalence and task-quality comparison are not distinguished",
                                 "Declare the intended comparison and justify its tolerances without requiring identical trajectories for a new algorithm",
                                 claims, ids)
                for name, fields in {
                    "baseline": ["strongest_relevant_comparator"],
                    "metric": ["independent_method"],
                    "efficiency": ["profile", "opportunity_bound", "full_cost_accounting", "timing_isolation"],
                    "novelty": ["mechanism_delta", "closest_collision"],
                    "proxy": ["decision_target", "availability_cost"],
                }.items():
                    self.block(review.get(name), path + ".decision_review." + name, fields, claims, ids)
            rules = comparison.get("outcome_rules")
            policy = rules.get("performance_policy") if isinstance(rules, dict) else None
            if isinstance(rules, dict) and "performance_policy" in rules:
                policy = self.object(policy, path + ".outcome_rules.performance_policy", claims, ids)
                for flag, reason, code, message in (
                    ("require_every_repeat_win", "every_repeat_requirement_reason", "all_repeats_win_policy",
                     "Every-repeat superiority is stricter than an aggregate performance claim"),
                    ("reject_any_fallback", "no_fallback_requirement_reason", "automatic_fallback_rejection",
                     "Fallback is automatically rejected instead of being accounted for in the declared quality/cost comparison"),
                ):
                    if flag not in policy:
                        continue
                    if type(policy[flag]) is not bool:
                        self.gap("invalid_performance_policy", path + ".outcome_rules.performance_policy." + flag,
                                 "Expected a boolean flag", "State the policy explicitly as true or false", claims, ids)
                    elif policy[flag] and not _text(policy.get(reason)):
                        self.gap(code, path + ".outcome_rules.performance_policy." + flag, message,
                                 "Review this rule against the real task requirement; justify it explicitly or revise a future plan, preserving historical decisions",
                                 claims, ids)
        if isinstance(results, dict):
            records = results.get("comparisons")
            for index, record in enumerate(records if isinstance(records, list) else []):
                if not isinstance(record, dict):
                    continue
                cid = record.get("comparison_id")
                if not isinstance(cid, str) or cid not in self.comparisons:
                    continue  # Original results checks already diagnose the identity.
                claims, ids = self.affected(cid, self.comparisons[cid]), [cid]
                self.block(record.get("decision_feedback"), f"results.comparisons[{index}].decision_feedback",
                           ["decision", "correctness", "performance", "remaining_work"], claims, ids)
        advisories = [g for g in self.gaps if claim_id is None or not g["claim_ids"] or claim_id in g["claim_ids"]]
        summaries = []
        for name, claim in self.claims.items():
            if claim_id is not None and name != claim_id:
                continue
            linked = [g for g in advisories if not g["claim_ids"] or name in g["claim_ids"]]
            compared = {cid for cid, comparison in self.comparisons.items() if name in self.affected(cid, comparison)}
            state = ("unreviewed" if compared - declared else "advisories" if linked else
                     "declarations_checked" if compared else "not_applicable_declared")
            summaries.append({"id": name, "status": state, "advisory_codes": sorted({g["code"] for g in linked})})
        return {"status": "advisories" if advisories else "declarations_checked", "claims": summaries,
                "advisories": advisories,
                "next_actions": [{"claim_ids": g["claim_ids"], "comparison_ids": g["comparison_ids"],
                                  "action": g["next_action"]} for g in advisories],
                "limitations": "Optional structured declarations and local artifact bytes only. No natural-language policy inference, semantic baseline/metric verification, statistical acceptance, historical decision rewrite, dispatch or admission gate. A matching hash does not establish who ran a check, its correctness, or prospective independence."}


def check(root, plan_path, results_path=None, *, claim_id=None, goal_contract_version=None):
    """Return structural gaps and observed coverage; never mutate or dispatch."""
    checker = _Check(root)
    report = {"schema_version": 1, "scientific_certification": False, "execution_authorization": False,
              "dispatch_performed": False, "prospective_independence_verified": False,
              "resource_snapshot_is_a_lease": False, "run_identity_authenticated": False,
              "resource_authorization_verified": False,
              "supplied_goal_contract_version": goal_contract_version}
    documented, plan, plan_ref, results = set(), {}, None, None
    try:
        plan, plan_ref = checker.load(plan_path)
        checker.plan(plan, goal_contract_version)
        if results_path is not None:
            results, report["results_ref"] = checker.load(results_path)
            documented = checker.results(plan, plan_ref, results)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        checker.gap("unreadable_document", "documents", str(exc), "Recover valid project-local JSON documents and rerun this read-only check")
    if claim_id is not None and claim_id not in checker.claims:
        checker.gap("unknown_claim", "claim_id", "Requested claim is not declared", "Select a declared claim ID", [claim_id])
    claims = []
    for name, claim in checker.claims.items():
        if claim_id is not None and name != claim_id:
            continue
        raw = claim.get("required_comparison_ids", [])
        required = [value for value in raw if isinstance(value, str)] if isinstance(raw, list) else []
        linked = [g for g in checker.gaps if name in g["claim_ids"] or not g["claim_ids"]]
        formal = claim.get("kind") == "formal" and not required and _text(claim.get("not_applicable_reason"))
        coverage = "gaps" if linked else "not_applicable_declared" if formal else "not_checked" if results_path is None else "documented" if set(required) <= documented else "gaps"
        claims.append({"id": name, "coverage": coverage, "required_comparison_ids": required,
                       "documented_comparison_ids": sorted(set(required) & documented),
                       "missing_comparison_ids": sorted(set(required) - documented), "gap_codes": sorted({g["code"] for g in linked})})
    gaps = [g for g in checker.gaps if claim_id is None or not g["claim_ids"] or claim_id in g["claim_ids"]]
    report.update(design_id=plan.get("design_id"), goal_contract_version=plan.get("goal_contract_version"),
                  plan_ref=plan_ref, status="gaps" if gaps else "documented" if results_path else "plan_documented",
                  claims=claims, gaps=gaps,
                  next_actions=[{"claim_ids": g["claim_ids"], "comparison_ids": g["comparison_ids"], "action": g["next_action"]} for g in gaps])
    review = _DecisionReview(root)
    review.claims, review.comparisons = checker.claims, checker.comparisons
    report["decision_review"] = review.inspect(plan, results, claim_id)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("check", help="Report affected-claim gaps without launching work")
    command.add_argument("--root", required=True)
    command.add_argument("--plan", required=True)
    command.add_argument("--results")
    command.add_argument("--claim-id")
    command.add_argument("--goal-contract-version", type=int)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check(args.root, args.plan, args.results, claim_id=args.claim_id,
                               goal_contract_version=args.goal_contract_version), indent=2, sort_keys=True, allow_nan=False))
        return 0  # Gaps are diagnostic feedback, never an execution admission code.
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "scientific_certification": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
