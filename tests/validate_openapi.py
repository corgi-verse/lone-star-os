#!/usr/bin/env python3
"""Validate specification structure and boundaries; never starts an API service."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from openapi_spec_validator import validate_spec

ROOT = Path(__file__).resolve().parents[1]


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def pointer(document, value):
    if not value.startswith("#/"):
        raise AssertionError("Non-local reference: " + value)
    node = document
    for part in value[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def recovery_reference_allowed(document, operation_id, request, trusted_session, trusted_job=None):
    """Synthetic policy check, not a token verifier or production authorization implementation."""
    policy = document["x-commonstar-recovery-session-policy"]
    if not trusted_session.get("os_user_verified") or not trusted_session.get("recovery_grant_verified"):
        return False
    if not trusted_session.get("unexpired") or operation_id not in policy["allowed_operation_ids"]:
        return False
    if operation_id == "createRestore":
        return (
            request.get("mode") == policy["restore_mode"]
            and request.get("expected_active_epoch") is None
            and request.get("snapshot_id") == trusted_session["snapshot_id"]
            and request.get("restore_grant_ref") == trusted_session["grant_ref"]
        )
    return (
        trusted_job is not None
        and trusted_job.get("kind") == policy["job_kind"]
        and trusted_job.get("recovery_attempt_id") == trusted_session["attempt_id"]
        and request.get("job_id") == trusted_job.get("job_id")
    )


def plan_reference_matches(request, requested_goal, trusted_preview, current_graph):
    """Check the declared snapshot contract against synthetic trusted local graph state."""
    if not trusted_preview.get("verified") or request.get("plan_snapshot_ref") != trusted_preview["grant_ref"]:
        return False
    if requested_goal != trusted_preview["goal_id"] or requested_goal != current_graph["goal_id"]:
        return False
    if request["expected_revision"] != current_graph["goal_revision"] or trusted_preview["goal_revision"] != current_graph["goal_revision"]:
        return False
    for key in ("included_task_ids", "task_revisions", "dependency_revisions", "dependency_edges"):
        if trusted_preview[key] != current_graph[key]:
            return False
    return True


def main():
    path = ROOT / "api" / "openapi.json"
    document = json.loads(path.read_text())
    validate_spec(document)
    refs = [node["$ref"] for node in walk(document) if "$ref" in node]
    for target in refs:
        pointer(document, target)
    for source, expected in document["x-commonstar-source-contract-sha256"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == expected, "Stale embedded contract: " + source
    spec = importlib.util.spec_from_file_location("commonstar_openapi_builder", ROOT / "api" / "build_openapi.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert document == module.build_document(), "Generated document differs from its source; regenerate deliberately."

    operation_ids = set()
    mutations = 0
    recovery_operations = {"createRestore", "readJob", "streamJobEvents", "cancelJob"}
    assert set(document["x-commonstar-recovery-session-policy"]["allowed_operation_ids"]) == recovery_operations
    assert document["x-commonstar-recovery-session-policy"]["requires_active_profile"] is False
    for route, methods in document["paths"].items():
        for method, operation in methods.items():
            assert operation["operationId"] not in operation_ids
            operation_ids.add(operation["operationId"])
            if route != "/health":
                expected_security = [{"LocalSession": []}]
                if operation["operationId"] in recovery_operations:
                    expected_security.append({"RecoverySession": []})
                assert operation.get("security", document["security"]) == expected_security, route
            else:
                assert operation.get("security") == []
            if operation.get("x-commonstar-mutation"):
                mutations += 1
                assert {"$ref": "#/components/parameters/IdempotencyKey"} in operation["parameters"], route
                assert method == "post"
            if method == "post" and route != "/search":
                assert operation.get("x-commonstar-mutation") is True, route

    schemas = document["components"]["schemas"]
    for name, schema in schemas.items():
        if name.endswith("Request") and "properties" in schema:
            assert schema.get("additionalProperties") is False, name
            assert "profile_id" not in schema["properties"], name

    def validator(name):
        envelope = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                    "components": document["components"], "$ref": "#/components/schemas/" + name}
        return Draft202012Validator(envelope)

    valid_turn = {"message": "Explain this source using local evidence.", "max_output_tokens": 768}
    validator("TurnRequest").validate(valid_turn)
    valid_note = {"title": "My observation", "body": "An original user-authored note.", "artifact_refs": []}
    validator("NoteCreateRequest").validate(valid_note)
    validator("TaskEditRequest").validate({
        "expected_revision": 3, "changes": {
            "due_at": "2026-11-06T17:00:00-06:00", "time_zone": "America/Chicago",
            "status": "accepted"
        }
    })
    negative = [
        ("TurnRequest", {**valid_turn, "profile_id": "urn:uuid:00000000-0000-0000-0000-000000000000"}),
        ("TurnRequest", {**valid_turn, "provider_api_key": "synthetic-forbidden-value"}),
        ("TurnRequest", {**valid_turn, "max_output_tokens": 900000}),
        ("FileImportRequest", {"kind": "files", "file_grants": [], "path": "/private/other-user"}),
        ("CorrectionRequest", {"replacement_statement": "Changed.", "reason": "Correction."}),
        ("AcceptProposalRequest", {"expected_revision": 1, "expected_target_revision": None, "approved_by": "teacher"}),
        ("ProviderPairRequest", {"candidate_ref": "urn:commonstar:grant:candidate", "approved": True}),
        ("RestoreRequest", {"snapshot_id": "urn:commonstar:snapshot:synthetic",
                            "restore_grant_ref": "urn:commonstar:grant:restore",
                            "mode": "replace_active_profile", "expected_active_epoch": None}),
        ("ExportRequest", {"scope": "selected_records", "record_ids": [],
                           "format": "jsonl_bundle",
                           "destination_grant_ref": "urn:commonstar:grant:destination",
                           "encryption_grant_ref": "urn:commonstar:grant:encryption",
                           "disclosure_grant_ref": "urn:commonstar:grant:disclosure"}),
        ("Job", {"job_id": "urn:commonstar:job:synthetic", "revision": 1,
                 "kind": "turn", "state": "completed", "stage": "complete", "progress": 1,
                 "created_at": "2026-11-04T08:00:00Z", "updated_at": "2026-11-04T08:00:01Z",
                 "result": None, "error": None}),
        ("NoteCreateRequest", {**valid_note, "profile_id": "urn:commonstar:profile:other"}),
        ("NoteCreateRequest", {**valid_note, "review": {"approved_by": "teacher"}}),
        ("TaskEditRequest", {"changes": {"status": "completed"}}),
        ("TaskEditRequest", {"expected_revision": 3, "changes": {}}),
        ("TaskEditRequest", {"expected_revision": 3, "changes": {"status": "officially_graded"}}),
        ("TaskEditRequest", {"expected_revision": 3, "changes": {"permissions": ["teacher"]}}),
        ("TaskEditRequest", {"expected_revision": 3, "changes": {"due_at": "2026-11-06T17:00:00Z"}}),
        ("TaskEditRequest", {"expected_revision": 3, "changes": {"time_zone": "America/Chicago"}}),
        ("PlanActivationRequest", {"expected_revision": 1, "time_zone": "America/Chicago",
                                   "reminder_policy": "local_notifications"}),
        ("RecoveryJobEvent", {"type": "delta", "sequence": 1, "job_id": "urn:commonstar:job:restore",
                              "text": "A private inference delta must not be exposed during recovery."}),
    ]
    for name, value in negative:
        assert list(validator(name).iter_errors(value)), "Unsafe request accepted: " + name
    session = {
        "os_user_verified": True, "recovery_grant_verified": True, "unexpired": True,
        "active_profile": None, "attempt_id": "synthetic-attempt-1",
        "snapshot_id": "urn:commonstar:snapshot:one", "grant_ref": "urn:commonstar:grant:recovery-one"
    }
    restore = {"snapshot_id": session["snapshot_id"], "restore_grant_ref": session["grant_ref"],
               "mode": "new_profile", "expected_active_epoch": None}
    validator("RestoreRequest").validate(restore)
    assert recovery_reference_allowed(document, "createRestore", restore, session)
    own_job = {"job_id": "urn:commonstar:job:restore", "kind": "restore",
               "recovery_attempt_id": session["attempt_id"]}
    for operation_id in ("readJob", "streamJobEvents", "cancelJob"):
        assert recovery_reference_allowed(document, operation_id, {"job_id": own_job["job_id"]}, session, own_job)
    recovery_negatives = [
        (operation_id, {}, session, None)
        for operation_id in ("searchActiveProfile", "readRecord", "listReceipts", "pairProvider", "previewPlan",
                             "createTurn", "createNote", "editTask", "createBackup", "createExport")
    ]
    recovery_negatives += [
        ("createRestore", {**restore, "mode": "replace_active_profile", "expected_active_epoch": 1}, session, None),
        ("createRestore", {**restore, "restore_grant_ref": "urn:commonstar:grant:other"}, session, None),
        ("createRestore", {**restore, "snapshot_id": "urn:commonstar:snapshot:other"}, session, None),
        ("createRestore", restore, {**session, "recovery_grant_verified": False}, None),
        ("createRestore", restore, {**session, "unexpired": False}, None),
        ("readJob", {"job_id": own_job["job_id"]}, session, {**own_job, "kind": "turn"}),
        ("streamJobEvents", {"job_id": own_job["job_id"]}, session, {**own_job, "recovery_attempt_id": "other"}),
        ("cancelJob", {"job_id": "urn:commonstar:job:other"}, session, own_job),
    ]
    for args in recovery_negatives:
        assert not recovery_reference_allowed(document, *args), "Recovery scope accepted an unauthorized synthetic case."

    graph = {
        "goal_id": "urn:commonstar:goal:one", "goal_revision": 2,
        "included_task_ids": ["task-a"], "task_revisions": {"task-a": 3},
        "dependency_revisions": {"task-b": 4}, "dependency_edges": [["task-a", "task-b"]]
    }
    preview = {**copy.deepcopy(graph), "verified": True, "grant_ref": "urn:commonstar:grant:plan-preview"}
    activate = {"expected_revision": 2, "plan_snapshot_ref": preview["grant_ref"],
                "time_zone": "America/Chicago", "reminder_policy": "local_notifications"}
    validator("PlanActivationRequest").validate(activate)
    assert plan_reference_matches(activate, graph["goal_id"], preview, graph)
    changed_graphs = [
        {**graph, "included_task_ids": ["task-a", "new-task"]},
        {**graph, "included_task_ids": []},
        {**graph, "task_revisions": {"task-a": 4}},
        {**graph, "dependency_revisions": {"task-b": 5}},
        {**graph, "dependency_edges": []},
        {**graph, "goal_revision": 3},
    ]
    for changed in changed_graphs:
        assert not plan_reference_matches(activate, graph["goal_id"], preview, changed)
    assert not plan_reference_matches(activate, "urn:commonstar:goal:other", preview, graph)
    print(json.dumps({
        "result": "passed", "openapi": document["openapi"],
        "operations": len(operation_ids), "mutations_with_idempotency": mutations,
        "local_references_resolved": len(refs), "embedded_contracts_verified": len(document["x-commonstar-source-contract-sha256"]),
        "negative_request_cases": len(negative),
        "recovery_scope_negative_cases": len(recovery_negatives),
        "plan_snapshot_negative_cases": len(changed_graphs) + 1,
        "evidence_scope": "Contract structure, request validation and synthetic trusted-context policy checks only; not real authentication, grants, transactions, service/model/device execution."
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("OpenAPI validation failed: " + str(exc), file=sys.stderr)
        raise
