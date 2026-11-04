#!/usr/bin/env python3
"""Validate Commonstar v1 contracts and synthetic semantic fixtures offline.

This is a specification verifier, not a running vault, security boundary, model
adapter, signature verifier, learning assessment, or application implementation.
Fixture context stands for trusted service state; it must never be accepted from
an untrusted model or HTTP request body in a future implementation.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as exc:
    raise SystemExit(
        "Missing contract-verification dependency. Run: "
        "python3 -m pip install -r requirements.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "urn:commonstar:schema:"


class SemanticViolation(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise SemanticViolation(code, detail)


def timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def verify_acyclic(graph: dict, code: str) -> None:
    active, visited = set(), set()

    def visit(identifier: str) -> None:
        require(identifier not in active, code, "Dependency graph contains a cycle.")
        if identifier in visited:
            return
        active.add(identifier)
        for dependency in graph.get(identifier, []):
            visit(dependency)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in graph:
        visit(identifier)


def verify_references(data: dict, context: dict) -> None:
    """Check only references against the already scoped trusted record catalog."""
    reference_lists = {
        "source_refs", "artifact_refs", "resource_refs", "evidence_refs",
        "statement_refs", "scope_refs", "invalidated_refs",
    }
    known = context.get("known_records", {})

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in reference_lists and isinstance(item, list):
                    for reference in item:
                        record_id = reference.get("record_id", reference.get("artifact_id"))
                        require(
                            reference.get("revision") in known.get(record_id, []),
                            "unknown_evidence",
                            "Reference is absent from the current authorized catalog/revision.",
                        )
                if key == "goal_ref" and item is not None:
                    require(item in known, "unknown_goal", "Goal is unavailable to this session.")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)


def verify_memory(data: dict, context: dict) -> None:
    require(
        data["profile_id"] == context.get("authenticated_profile_id"),
        "profile_mismatch", "The authenticated session owns profile selection.",
    )
    require(context.get("actor_kind") != "model", "model_direct_write", "Models submit proposals only.")
    require(
        "commit_record" in context.get("authorized_actions", []),
        "unauthorized_write", "The trusted caller has no record-commit capability.",
    )
    review = data["review"]
    if review["status"] in {"teacher_reviewed", "approved"}:
        require(
            review["reviewer_id"] in context.get("approved_reviewers", []),
            "unauthorized_review", "A review label does not authenticate a reviewer.",
        )
    if data["valid_until"]:
        require(
            timestamp(data["valid_until"]) >= timestamp(data["valid_from"]),
            "invalid_time_range", "Validity cannot end before it starts.",
        )
    payload = data["payload"]
    if data["record_type"] == "permission":
        require(
            "manage_permissions" in context.get("authorized_actions", [])
            and payload["granted_by"] == context.get("authenticated_actor_id"),
            "unauthorized_permission_change", "Record commit alone cannot grant permissions.",
        )
        require(
            timestamp(payload["expires_at"]) > timestamp(payload["valid_from"]),
            "invalid_time_range", "A permission must expire after it becomes valid.",
        )
    if data["record_type"] == "learning_event":
        scoring = payload["scoring"]
        if scoring["method"] == "model_feedback":
            require(
                scoring["status"] in {"unscored", "review_required"} and scoring["score"] is None,
                "unverified_model_score", "Model feedback is not an authoritative checked score.",
            )
    if data["record_type"] == "task":
        verify_time_zone(payload["time_zone"])
        require(set(payload["depends_on_task_ids"]) <= set(context.get("known_records", {})),
                "unknown_task_dependency", "A task dependency must resolve within the authorized profile.")
        require(set(payload["depends_on_task_ids"]) <= set(context.get("task_dependencies", {})),
                "unknown_task_dependency", "A dependency must be an authorized task, not another record type.")
        graph = dict(context.get("task_dependencies", {}))
        graph[data["record_id"]] = payload["depends_on_task_ids"]
        verify_acyclic(graph, "task_dependency_cycle")
    verify_references(data, context)


def verify_time_zone(value: str) -> None:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise SemanticViolation("invalid_time_zone", "Expected an installed IANA time zone.") from exc


def verify_proposal(data: dict, context: dict) -> None:
    # The model sees request-local labels, never stable internal record IDs.
    sources = context.get("sources", {})
    evidence = context.get("evidence", {})

    def walk(value: object) -> None:
        if isinstance(value, dict):
            if "ref" in value:
                require(value["ref"] in sources or value["ref"] in evidence,
                        "unknown_evidence", "Proposal refers to evidence absent from its request.")
            if "source_ref" in value:
                label = value["source_ref"]
                require(label in sources, "unknown_evidence", "Proposal source is absent from its request.")
                require(value["locator"] == sources[label]["locator"],
                        "invalid_citation_locator", "Proposal locator was not supplied for this source.")
            if value.get("goal_ref") == "current":
                require(context.get("current_goal_available") is True,
                        "unknown_goal", "There is no current goal in the trusted session.")
            if "depends_on_task_refs" in value:
                require(set(value["depends_on_task_refs"]) <= set(context.get("tasks", {})),
                        "unknown_task_reference", "A model may reference only supplied task labels.")
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    if data["kind"] == "task.propose":
        verify_time_zone(data["payload"]["time_zone"])
    if data["kind"] == "plan.propose":
        verify_time_zone(data["payload"]["time_zone"])
        steps = data["payload"]["steps"]
        labels = [step["step_ref"] for step in steps]
        require(len(labels) == len(set(labels)), "duplicate_step_label", "Plan step labels must be unique.")
        for step in steps:
            require(set(step["depends_on_steps"]) <= set(labels),
                    "unknown_step_dependency", "A dependency must refer to a step in this proposal.")
        verify_acyclic({step["step_ref"]: step["depends_on_steps"] for step in steps}, "step_dependency_cycle")


def verify_capsule(data: dict, context: dict) -> None:
    labels = [source["ref"] for source in data["sources"]]
    labels.extend(item["ref"] for item in data["learning_context"]["recent_evidence"])
    labels.extend(item["ref"] for item in data["learning_context"]["current_tasks"])
    require(len(labels) == len(set(labels)), "duplicate_source", "Source labels must be unique within a request.")
    # This verifies known canaries, not universal de-identification or anonymity.
    serialized = json.dumps(data, ensure_ascii=False)
    for identifier in context.get("forbidden_identifiers", []):
        require(identifier not in serialized, "forbidden_identifier", "A known private identifier reached context.")
    mode_policy = {"local": "on_device", "workstation": "workstation_ephemeral", "cloud": "provider_approved"}
    require(
        data["requested_data_policy"]["retention_profile"] == mode_policy[data["mode"]],
        "mode_policy_mismatch", "Inference mode and requested retention policy disagree.",
    )


def verify_response(data: dict, context: dict) -> None:
    require(data["request_id"] == context.get("request_id"), "request_mismatch", "Response is for a different request.")
    sources = context.get("sources", {})
    for citation in data["message"]["citations"]:
        label = citation["source_ref"]
        require(label in sources, "unknown_citation", "The model cited a source absent from its request.")
        require(
            citation["locator"] == sources[label]["locator"],
            "invalid_citation_locator", "The citation locator was not supplied for this source.",
        )
    proposal_ids = [proposal["proposal_id"] for proposal in data["memory_proposals"]]
    require(len(proposal_ids) == len(set(proposal_ids)), "duplicate_proposal", "Proposal IDs repeat in a response.")
    for proposal in data["memory_proposals"]:
        verify_proposal(proposal, context)


def verify_provider(data: dict, context: dict) -> None:
    require(not data["preferred"] or data["enabled"], "disabled_preferred_provider", "A disabled provider cannot be preferred.")
    endpoint = data["endpoint"]
    address = endpoint["address"]
    transport = endpoint["transport"]
    if transport in {"http-loopback", "ssh-forward"}:
        parsed = urlparse(address)
        require(
            parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "::1"}
            and parsed.username is None and parsed.password is None,
            "unsafe_endpoint", "Plain HTTP is permitted only for a numeric loopback endpoint.",
        )
    elif transport in {"https", "https-mtls"}:
        parsed = urlparse(address)
        require(
            parsed.scheme == "https" and bool(parsed.hostname)
            and parsed.username is None and parsed.password is None,
            "unsafe_endpoint", "Remote endpoints require HTTPS without URL credentials.",
        )
    elif transport == "unix":
        require(address.startswith("/"), "unsafe_endpoint", "Unix socket paths must be absolute.")
    if data["kind"] == "workstation":
        authentication = endpoint["authentication"]
        require(
            authentication["credential_ref"] != authentication["application_credential_ref"],
            "credential_role_reuse", "Transport identity and inference API credential are separate bindings.",
        )
    if not data["enabled"]:
        return
    policy = data["data_policy"]
    require(policy["approval_status"] == "approved", "provider_not_approved", "Enabled provider needs local approval.")
    require(
        timestamp(policy["policy_valid_until"]) > timestamp(context["now"]),
        "provider_policy_expired", "Provider policy approval has expired.",
    )
    if data["kind"] == "workstation":
        require(context.get("identity_verified") is True, "unverified_peer", "Workstation identity has not been verified.")
    if data["kind"] == "openai":
        require(endpoint["authentication"]["credential_ref"] is not None, "missing_credential", "No approved credential binding.")
        if policy["age_policy"] == "under13_school_reviewed":
            require(
                policy["retention_control"] == "approved_zdr" and context.get("provider_zdr_verified") is True,
                "unverified_minor_retention", "Under-13 provider prerequisites have not been verified.",
            )


def verify_pack(data: dict, context: dict) -> None:
    asset_ids = [asset["asset_id"] for asset in data["assets"]]
    paths = [asset["path"] for asset in data["assets"]]
    objective_ids = [objective["objective_id"] for objective in data["objectives"]]
    require(len(asset_ids) == len(set(asset_ids)), "duplicate_asset", "Asset identifiers must be unique.")
    require(len(paths) == len(set(paths)), "duplicate_asset_path", "Asset paths must be unique.")
    require(len(objective_ids) == len(set(objective_ids)), "duplicate_objective", "Objective identifiers must be unique.")
    objectives = {item["objective_id"]: item for item in data["objectives"]}
    for lesson in data["lessons"]:
        require(set(lesson["asset_ids"]) <= set(asset_ids), "unknown_asset", "Lesson refers to an absent asset.")
        require(set(lesson["objective_ids"]) <= set(objective_ids), "unknown_objective", "Lesson refers to an absent objective.")
    for objective in data["objectives"]:
        require(
            set(objective["prerequisite_ids"]) <= set(objective_ids),
            "unknown_prerequisite", "Prerequisites must resolve in this declared pack graph.",
        )
    active, visited = set(), set()

    def visit(identifier: str) -> None:
        require(identifier not in active, "prerequisite_cycle", "Prerequisite relationships cannot contain a cycle.")
        if identifier in visited:
            return
        active.add(identifier)
        for predecessor in objectives[identifier]["prerequisite_ids"]:
            visit(predecessor)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in objectives:
        visit(identifier)
    checker_ids = [item["checker_id"] for item in data["checkers"]]
    exercise_ids = [item["exercise_id"] for item in data["exercises"]]
    accessibility_ids = [item["accessibility_id"] for item in data["accessibility_assets"]]
    require(len(checker_ids) == len(set(checker_ids)), "duplicate_checker", "Checker identifiers must be unique.")
    require(len(exercise_ids) == len(set(exercise_ids)), "duplicate_exercise", "Exercise identifiers must be unique.")
    require(len(accessibility_ids) == len(set(accessibility_ids)), "duplicate_accessibility", "Accessibility identifiers must be unique.")
    checkers = {item["checker_id"]: item for item in data["checkers"]}
    for checker in data["checkers"]:
        if checker["kind"] == "educator_rubric":
            require(checker["authority"] == "educator_review_required" and checker["implementation_ref"] is None,
                    "checker_authority_mismatch", "Educator rubric requires human review, not an executable grading authority.")
        else:
            require(checker["authority"] == "deterministic" and checker["implementation_ref"] is not None,
                    "checker_authority_mismatch", "A deterministic checker needs an identified implementation.")
            require(checker["implementation_ref"] in context.get("allowed_checker_implementations", []),
                    "unapproved_checker_implementation", "Content cannot install or select arbitrary executable checkers.")
    expected_types = {"numeric": ("number", "numeric"), "choice": ("choice", "choice"),
                      "expression": ("expression", "expression"), "educator_rubric": ("short_text", "rubric")}
    for exercise in data["exercises"]:
        require(exercise["checker_ref"] in checkers, "unknown_checker", "Exercise checker is absent from the pack.")
        require(exercise["prompt_asset_id"] in asset_ids, "unknown_prompt_asset", "Exercise prompt asset is absent.")
        require(set(exercise["objective_ids"]) <= set(objective_ids), "unknown_objective", "Exercise objective is absent.")
        require(set(exercise["feedback_asset_ids"]) <= set(asset_ids), "unknown_feedback_asset", "Feedback asset is absent.")
        require(set(exercise["accessibility_refs"]) <= set(accessibility_ids), "unknown_accessibility", "Exercise accessibility reference is absent.")
        checker = checkers[exercise["checker_ref"]]
        require((exercise["response_type"], exercise["answer_spec"]["type"]) == expected_types[checker["kind"]],
                "checker_response_mismatch", "Response format, answer specification and checker disagree.")
        option_ids = [item["option_id"] for item in exercise["choices"]]
        require(len(option_ids) == len(set(option_ids)), "duplicate_option", "Choice identifiers must be unique.")
        if checker["kind"] == "choice":
            require(set(exercise["answer_spec"]["correct_option_ids"]) <= set(option_ids),
                    "unknown_correct_option", "A choice answer must identify an offered option.")
        else:
            require(not option_ids, "unexpected_choices", "Only choice responses may declare options.")
    for item in data["accessibility_assets"]:
        require(item["asset_id"] in asset_ids and item["for_asset_id"] in asset_ids,
                "unknown_accessibility_asset", "Accessibility assets and their targets must resolve.")
        require(item["language"] in data["languages"], "unsupported_accessibility_language", "Accessibility language is not declared by the pack.")
    for lesson in data["lessons"]:
        require(set(lesson["exercise_ids"]) <= set(exercise_ids), "unknown_exercise", "Lesson exercise is absent.")
        require(set(lesson["accessibility_refs"]) <= set(accessibility_ids), "unknown_accessibility", "Lesson accessibility reference is absent.")
    if context.get("school_mode"):
        require(data["review"]["status"] == "educator_reviewed", "school_pack_not_reviewed", "School mode needs reviewed content.")
        require(
            data["signature"] is not None and context.get("signature_verified") is True,
            "school_pack_signature_unverified", "School mode requires independently verified signature evidence.",
        )


SEMANTIC_CHECKS = {
    "memory-record": verify_memory,
    "model-proposal": verify_proposal,
    "context-capsule": verify_capsule,
    "provider-profile": verify_provider,
    "tutor-response": verify_response,
    "content-pack": verify_pack,
}


def load_validators() -> tuple[dict, int]:
    schemas = {}
    for path in sorted((ROOT / "contracts").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        if schema["$id"] in schemas:
            raise ValueError(f"Duplicate schema identifier: {schema['$id']}")
        if not schema["$id"].startswith(PREFIX):
            raise ValueError(f"Unexpected schema namespace in {path.name}")
        schemas[schema["$id"]] = schema
    registry = Registry().with_resources(
        (identifier, Resource.from_contents(schema)) for identifier, schema in schemas.items()
    )
    validators = {
        identifier: Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
        for identifier, schema in schemas.items()
    }
    return validators, len(schemas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="Print each fixture outcome.")
    args = parser.parse_args()
    validators, schema_count = load_validators()
    manifest = json.loads((ROOT / "examples" / "manifest.json").read_text(encoding="utf-8"))
    counts, failures, seen_paths = Counter(), [], set()
    for case in manifest["cases"]:
        path = (ROOT / case["path"]).resolve()
        if not path.is_relative_to((ROOT / "examples").resolve()) or path in seen_paths:
            failures.append(f"{case['name']}: duplicate or escaping fixture path")
            continue
        seen_paths.add(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validators[case["schema"]].iter_errors(data), key=lambda item: str(list(item.path)))
        actual, code, detail = "valid", None, ""
        if errors:
            actual, detail = "invalid_schema", errors[0].message
        else:
            kind = case["schema"][len(PREFIX):].rsplit(":", 1)[0]
            try:
                SEMANTIC_CHECKS[kind](data, case.get("context", {}))
            except SemanticViolation as exc:
                actual, code, detail = "invalid_semantic", exc.code, str(exc)
        matched = actual == case["expect"] and ("error_code" not in case or case["error_code"] == code)
        if not matched:
            failures.append(f"{case['name']}: expected {case['expect']} {case.get('error_code', '')}; got {actual} {detail}")
        else:
            counts[actual] += 1
        if args.verbose:
            print(f"{'PASS' if matched else 'FAIL'} {case['name']}: {actual}" + (f" ({code})" if code else ""))
    discovered = set((ROOT / "examples" / "valid").glob("*.json")) | set((ROOT / "examples" / "invalid").glob("*.json"))
    if discovered != seen_paths:
        failures.append("Unregistered or missing example files in manifest.")
    if failures:
        print("CONTRACT VERIFICATION FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"PASS: {schema_count} Draft 2020-12 schemas; {sum(counts.values())} synthetic fixtures "
          f"({counts['valid']} valid, {counts['invalid_schema']} schema rejections, "
          f"{counts['invalid_semantic']} semantic rejections).")
    print("Scope: contracts only. No runtime, inference, encryption, network isolation, signature, device or learning-outcome claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
