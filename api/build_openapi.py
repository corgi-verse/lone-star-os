#!/usr/bin/env python3
"""Build the local API contract; this does not implement or start a service."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ref(name):
    return {"$ref": "#/components/schemas/" + name}


def obj(properties, required=None, **extra):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False, **extra}


def string(limit=1000, **extra):
    return {"type": "string", "minLength": 1, "maxLength": limit, **extra}


def array(items, maximum=100, minimum=0):
    return {"type": "array", "items": items, "maxItems": maximum, "minItems": minimum}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def build_document():
    names = ["common", "memory-record", "model-proposal", "context-capsule",
             "provider-profile", "tutor-response", "content-pack"]
    source = {}
    source_evidence = {}
    uris = {}
    for name in names:
        path = ROOT / "contracts" / (name + ".schema.json")
        data = json.loads(path.read_text())
        component = "Commonstar" + "".join(p.title() for p in name.split("-"))
        source[component] = data
        uris[data["$id"]] = component
        source_evidence[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

    def embed(value, own_component):
        if isinstance(value, list):
            return [embed(v, own_component) for v in value]
        if not isinstance(value, dict):
            return value
        out = {}
        for key, item in value.items():
            if key in {"$id", "$schema"}:
                continue
            if key == "$ref":
                if item.startswith("#"):
                    out[key] = "#/components/schemas/" + own_component + item[1:]
                else:
                    base, _, fragment = item.partition("#")
                    if base not in uris:
                        raise ValueError("Unknown contract reference: " + item)
                    out[key] = "#/components/schemas/" + uris[base] + fragment
            else:
                out[key] = embed(item, own_component)
        return out

    schemas = {name: embed(data, name) for name, data in source.items()}
    schemas.update({
        "OpaqueId": string(200, pattern=r"^urn:(uuid:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|commonstar:[A-Za-z0-9:._-]+)$"),
        "GrantRef": string(200, pattern=r"^urn:commonstar:grant:[A-Za-z0-9:._-]+$",
                           description="Opaque grant issued by trusted native setup; the service verifies purpose, session, expiry and scope. It is not a caller assertion of authority."),
        "Revision": {"type": "integer", "minimum": 1},
        "Timestamp": {"type": "string", "format": "date-time"},
        "ErrorCode": {"type": "string", "enum": [
            "invalid_input", "unauthenticated", "denied_scope", "not_found", "stale_revision",
            "idempotency_conflict", "missing_evidence", "unsupported_capability", "locked_vault",
            "unavailable_model", "invalid_provider_output", "budget_exhausted",
            "insufficient_storage", "integrity_failure", "event_cursor_expired",
            "rate_limited", "unavailable_service", "cancelled"]},
        "Error": obj({"code": ref("ErrorCode"), "message": string(1000),
                      "request_id": ref("OpaqueId"), "retryable": {"type": "boolean"}}),
        "Health": obj({"status": {"const": "ok"}, "protocol_version": {"const": "1.0"},
                       "application_version": string(100)}),
        "FileImportRequest": obj({
            "kind": {"const": "files"}, "file_grants": array(ref("GrantRef"), 100, 1),
            "collection_id": nullable(ref("OpaqueId"))}, ["kind", "file_grants"]),
        "PackImportRequest": obj({
            "kind": {"const": "content_pack"}, "pack_grant": ref("GrantRef"),
            "expected_manifest_sha256": string(64, pattern="^[a-f0-9]{64}$")}),
        "UrlImportRequest": obj({
            "kind": {"const": "url"}, "url": string(4000, format="uri", pattern="^https://"),
            "fetch_permission_ref": ref("GrantRef")},
            description="Deliberate fetch only. Resolve/validate hosts and redirects against SSRF, private-address and policy restrictions before any connection."),
        "ImportRequest": {"oneOf": [ref("FileImportRequest"), ref("PackImportRequest"), ref("UrlImportRequest")]},
        "SearchFilters": obj({
            "record_types": array({"type": "string", "enum": ["artifact", "note", "fact", "preference", "goal", "task", "learning_event", "learning_state", "session_summary"]}, 10),
            "source_ids": array(ref("OpaqueId"), 100),
            "goal_id": ref("OpaqueId")}, []),
        "SearchRequest": obj({
            "query": string(8000), "purpose": {"type": "string", "enum": ["study", "organize", "review"]},
            "filters": ref("SearchFilters"), "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}},
            ["query", "purpose"]),
        "SearchHit": obj({
            "record_id": ref("OpaqueId"), "revision": ref("Revision"),
            "title": string(500), "excerpt": string(6000), "locator": string(1000),
            "retrieval_method": {"type": "string", "enum": ["structured", "lexical", "semantic", "hybrid"]},
            "score": {"type": "number", "description": "Ranking score; not calibrated truth or learning probability."}}),
        "SearchResponse": obj({"hits": array(ref("SearchHit"), 100),
                                "incomplete_index": {"type": "boolean"},
                                "limitations": array(string(1000), 20)}),
        "TurnRequest": obj({
            "message": string(32000), "goal_id": nullable(ref("OpaqueId")),
            "source_ids": array(ref("OpaqueId"), 100),
            "provider_id": ref("OpaqueId"),
            "max_output_tokens": {"type": "integer", "minimum": 16, "maximum": 8192, "default": 768},
            "thinking": {"type": "string", "enum": ["bounded", "extended"], "default": "bounded"}},
            ["message"],
            description="Absent provider_id means the currently explicitly selected route, initially local. The service enforces permission, context and token budgets; no automatic remote fallback."),
        "JobResult": obj({
            "kind": {"type": "string", "enum": ["turn", "import", "deletion", "backup", "restore", "export"]},
            "record_ids": array(ref("OpaqueId"), 1000),
            "tutor_response": nullable(ref("CommonstarTutorResponse")),
            "artifact_grant": nullable(ref("GrantRef")),
            "snapshot_id": nullable(ref("OpaqueId")),
            "receipt_id": ref("OpaqueId")}),
        "Job": obj({
            "job_id": ref("OpaqueId"), "revision": ref("Revision"),
            "kind": {"type": "string", "enum": ["turn", "import", "deletion", "backup", "restore", "export"]},
            "state": {"type": "string", "enum": ["queued", "loading", "running", "awaiting_input", "completed", "cancelled", "failed"]},
            "stage": string(200), "progress": nullable({"type": "number", "minimum": 0, "maximum": 1}),
            "created_at": ref("Timestamp"), "updated_at": ref("Timestamp"),
            "result": nullable(ref("JobResult")), "error": nullable(ref("Error"))},
            description="Progress is null when completion cannot be measured. Result exists only after validated completion. A partial model answer is never a committed memory record."),
        "CancelJobRequest": obj({"expected_revision": ref("Revision"), "reason": string(500)}, ["expected_revision"]),
        "PendingProposal": obj({
            "proposal_id": ref("OpaqueId"), "revision": ref("Revision"), "job_id": ref("OpaqueId"),
            "state": {"type": "string", "enum": ["pending", "accepted", "rejected", "expired"]},
            "proposal": ref("CommonstarModelProposal"), "created_at": ref("Timestamp"),
            "expected_target_revision": nullable(ref("Revision"))}),
        "AcceptProposalRequest": obj({
            "expected_revision": ref("Revision"),
            "expected_target_revision": nullable(ref("Revision")),
            "review_grant_ref": ref("GrantRef")},
            ["expected_revision", "expected_target_revision"],
            description="The local service resolves request-scoped proposal references and verifies current target revisions and authority. A grant reference cannot forge teacher or custody authority."),
        "MutationReceipt": obj({
            "receipt_id": ref("OpaqueId"),
            "affected_records": array(obj({"record_id": ref("OpaqueId"), "revision": ref("Revision")}), 1000),
            "committed_at": ref("Timestamp")}),
        "NoteCreateRequest": {
            "allOf": [{"$ref": "#/components/schemas/CommonstarMemoryRecord/$defs/note"}],
            "description": "User-authored title/body/artifact references only. Verify referenced artifacts within the active profile. The service creates record identity, profile, timestamps, revision, user provenance, review and retention; a model is not involved."
        },
        "TaskChanges": obj({
            "title": string(300),
            "due_at": nullable(ref("Timestamp")),
            "time_zone": string(100),
            "status": {"type": "string", "enum": ["proposed", "accepted", "completed", "cancelled"]},
            "estimated_minutes": nullable({"type": "integer", "minimum": 1})},
            [], minProperties=1,
            dependentRequired={"due_at": ["time_zone"], "time_zone": ["due_at"]},
            description="Whitelisted user edits only. due_at and time_zone change together; null due_at removes the deadline. Goal identity, dependencies, provenance, grades and permissions are not editable here."),
        "TaskEditRequest": obj({
            "expected_revision": ref("Revision"), "changes": ref("TaskChanges")},
            description="The target must be an authorized task. Validate IANA timezone, date semantics, state transition and expected revision, then commit user provenance and reminder changes atomically. Completed means learner-reported task completion, not independently verified mastery."),
        "CorrectionRequest": obj({
            "expected_revision": ref("Revision"), "replacement_statement": string(16000),
            "reason": string(4000), "supporting_record_ids": array(ref("OpaqueId"), 100)},
            ["expected_revision", "replacement_statement", "reason"],
            description="Corrects an authorized factual/text statement with provenance. Does not expose a generic JSON Patch, grade edit, permission edit or raw database write."),
        "DeletionRequest": obj({
            "expected_revision": ref("Revision"), "reason": string(4000),
            "backup_handling": {"type": "string", "enum": ["apply_retention_policy", "request_authorized_purge"]}},
            description="Records and dependent representations are handled under current authority and retention policy. A purge request is not a client override of legal retention."),
        "PlanActivationRequest": obj({
            "expected_revision": ref("Revision"), "plan_snapshot_ref": ref("GrantRef"),
            "time_zone": string(100),
            "reminder_policy": {"type": "string", "enum": ["local_notifications", "off"]},
            "automation_grant_ref": ref("GrantRef")},
            ["expected_revision", "plan_snapshot_ref", "time_zone", "reminder_policy"],
            description="plan_id is the goal record_id; expected_revision is that goal revision. The service-issued immutable preview snapshot binds the exact included task set, task/dependency revisions and dependency edges. Recompute membership and graph in the commit transaction; any addition, removal or revision/edge change yields 409 and requires fresh preview. Validate an IANA time zone and commit acceptance/reminders atomically."),
        "PlanPreview": obj({
            "plan_id": ref("OpaqueId"), "goal_revision": ref("Revision"),
            "snapshot_ref": ref("GrantRef"), "expires_at": ref("Timestamp"),
            "included_tasks": array(obj({"task_id": ref("OpaqueId"), "revision": ref("Revision")}), 1000),
            "dependency_versions": array(obj({"task_id": ref("OpaqueId"), "revision": ref("Revision")}), 1000),
            "dependency_edges": array(obj({"task_id": ref("OpaqueId"), "depends_on": ref("OpaqueId")}), 10000)},
            description="Authorized read-only preview of a goal and exact current task graph. The short-lived snapshot grant adds no privilege and is bound to the active principal/profile, goal, graph and expiry. The service retains or authenticates the full immutable snapshot; the client cannot substitute returned JSON as trusted proof."),
        "ReceiptList": obj({"items": array(ref("CommonstarMemoryRecord"), 100),
                            "next_cursor": nullable(string(500))},
                           description="Every item has record_type receipt. Only the authenticated session's permitted receipts are returned."),
        "BackupRequest": obj({"expected_policy_revision": ref("Revision"), "label": string(100)},
                             ["expected_policy_revision"],
                             description="Uses the one already configured approved backup destination. No arbitrary destination URL or raw key is accepted."),
        "RestoreRequest": obj({
            "snapshot_id": ref("OpaqueId"), "restore_grant_ref": ref("GrantRef"),
            "mode": {"type": "string", "enum": ["new_profile", "replace_active_profile"]},
            "expected_active_epoch": nullable(ref("Revision"))},
            description="A trusted native grant binds selected snapshot, unlock method and any overwrite confirmation. A recovery-scoped session needs no active profile, but may use only mode=new_profile with its bound grant/snapshot and expected_active_epoch=null. Replacement requires a normal active-profile session. Validate in isolated storage; profile identity comes from verified recovery metadata. Activation revokes recovery access and requires fresh normal authentication."),
        "ExportRequest": obj({
            "scope": {"type": "string", "enum": ["selected_records", "whole_active_profile"]},
            "record_ids": array(ref("OpaqueId"), 10000),
            "format": {"type": "string", "enum": ["jsonl_bundle", "human_readable_bundle"]},
            "destination_grant_ref": ref("GrantRef"), "encryption_grant_ref": ref("GrantRef"),
            "disclosure_grant_ref": ref("GrantRef")},
            ["scope", "format", "destination_grant_ref", "encryption_grant_ref", "disclosure_grant_ref"],
            description="Selected-record exports require a nonempty authorized record_ids list. Whole-profile scope is restricted to the active session and a matching disclosure grant. This operation creates a disclosed additional encrypted copy."),
        "ProviderPairRequest": obj({
            "candidate_ref": ref("GrantRef"), "verified_identity_ref": ref("GrantRef"),
            "credential_binding_ref": ref("GrantRef"), "policy_approval_ref": ref("GrantRef"),
            "make_preferred": {"type": "boolean", "default": False}},
            ["candidate_ref", "verified_identity_ref", "credential_binding_ref", "policy_approval_ref"],
            description="References locally established pairing evidence. The service revalidates peer identity, transport/app credentials, policy, age conditions and capability checks. The request cannot assert approval with a Boolean or submit a trusted provider-profile object."),
        "StateEvent": obj({"type": {"const": "state"}, "sequence": {"type": "integer", "minimum": 1},
                           "job_id": ref("OpaqueId"), "job": ref("Job")}),
        "DeltaEvent": obj({"type": {"const": "delta"}, "sequence": {"type": "integer", "minimum": 1},
                           "job_id": ref("OpaqueId"), "text": string(16000)},
                          description="Untrusted display-only partial text; never an accepted memory write."),
        "ProgressEvent": obj({"type": {"const": "progress"}, "sequence": {"type": "integer", "minimum": 1},
                              "job_id": ref("OpaqueId"), "stage": string(200),
                              "progress": nullable({"type": "number", "minimum": 0, "maximum": 1})}),
        "ErrorEvent": obj({"type": {"const": "error"}, "sequence": {"type": "integer", "minimum": 1},
                           "job_id": ref("OpaqueId"), "error": ref("Error")}),
        "CompleteEvent": obj({"type": {"const": "complete"}, "sequence": {"type": "integer", "minimum": 1},
                              "job_id": ref("OpaqueId"), "job": ref("Job")}),
        "JobEvent": {"oneOf": [ref(name) for name in ["StateEvent", "DeltaEvent", "ProgressEvent", "ErrorEvent", "CompleteEvent"]]}
    })
    schemas["JobResult"]["allOf"] = [{
        "if": {"properties": {"kind": {"const": "turn"}}},
        "then": {"properties": {"tutor_response": ref("CommonstarTutorResponse")}},
        "else": {"properties": {"tutor_response": {"type": "null"}}}
    }]
    schemas["Job"]["allOf"] = [
        {"if": {"properties": {"state": {"const": "completed"}}},
         "then": {"properties": {"result": ref("JobResult"), "error": {"type": "null"}}},
         "else": {"properties": {"result": {"type": "null"}}}},
        {"if": {"properties": {"state": {"const": "failed"}}},
         "then": {"properties": {"error": ref("Error")}},
         "else": {"properties": {"error": {"type": "null"}}}}
    ]
    schemas["CompleteEvent"]["properties"]["job"] = {
        "allOf": [ref("Job"), {"properties": {"state": {"enum": ["completed", "cancelled", "failed"]}}}]
    }
    schemas["RestoreRequest"]["allOf"] = [{
        "if": {"properties": {"mode": {"const": "replace_active_profile"}}},
        "then": {"properties": {"expected_active_epoch": ref("Revision")}},
        "else": {"properties": {"expected_active_epoch": {"type": "null"}}}
    }]
    schemas["ExportRequest"]["allOf"] = [{
        "if": {"properties": {"scope": {"const": "selected_records"}}},
        "then": {"required": ["record_ids"], "properties": {"record_ids": {"minItems": 1}}},
        "else": {"properties": {"record_ids": {"maxItems": 0}}}
    }]
    schemas["RecoveryJobResult"] = {"allOf": [
        ref("JobResult"), {"properties": {
            "kind": {"const": "restore"}, "record_ids": {"maxItems": 0},
            "tutor_response": {"type": "null"}, "artifact_grant": {"type": "null"}
        }}
    ]}
    schemas["RecoveryJob"] = {"allOf": [
        ref("Job"), {"properties": {
            "kind": {"const": "restore"}, "result": nullable(ref("RecoveryJobResult"))
        }}
    ]}
    schemas["RecoveryStateEvent"] = {"allOf": [
        ref("StateEvent"), {"properties": {"job": ref("RecoveryJob")}}
    ]}
    schemas["RecoveryCompleteEvent"] = {"allOf": [
        ref("CompleteEvent"), {"properties": {"job": ref("RecoveryJob")}}
    ]}
    schemas["RecoveryJobEvent"] = {"oneOf": [
        ref(name) for name in ["RecoveryStateEvent", "ProgressEvent", "ErrorEvent", "RecoveryCompleteEvent"]
    ]}
    parameters = {
        "IdempotencyKey": {"name": "Idempotency-Key", "in": "header", "required": True,
            "schema": string(128, pattern="^[A-Za-z0-9._:-]{16,128}$"),
            "description": "Normal sessions: scope to service-derived active profile, principal and operation. Recovery sessions: scope to authenticated OS user, verified recovery attempt and operation, without requiring a profile. Preserve across renewal/restart. Same key/body replays the prior result; different input yields 409. Retain through job completion and at least 24 hours afterward."},
        "Cursor": {"name": "cursor", "in": "query", "required": False, "schema": string(500)},
        "Limit": {"name": "limit", "in": "query", "required": False,
                  "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}},
        "LastEventId": {"name": "Last-Event-ID", "in": "header", "required": False,
                       "schema": string(32, pattern="^[0-9]+$"),
                       "description": "Resume after this job-local durable sequence. An expired cursor yields 410; fetch the current job and reconnect without silently inventing missed deltas."}
    }
    errors = {str(code): {"description": description, "content": {"application/json": {"schema": ref("Error")}}}
              for code, description in {
                  400: "Closed-schema input validation failed.", 401: "Missing, expired or locked-profile session.",
                  403: "Authenticated session lacks the required scope or verified grant.",
                  404: "Object absent or outside this session; do not reveal another profile's object.",
                  409: "Revision, state or idempotency conflict.", 410: "Event cursor or capability expired.",
                  413: "Configured request size limit exceeded.", 422: "Semantic validation or evidence check failed.",
                  429: "Rate or execution budget limit reached.", 503: "Required local/selected service unavailable.",
                  507: "Insufficient storage; preserve committed data."}.items()}
    paths = {}

    def operation(path, method, operation_id, summary, response_schema, request_schema=None,
                  status="200", mutation=False, description="", extra_parameters=None, public=False,
                  recovery_allowed=False):
        params = []
        for segment in path.split("/"):
            if segment.startswith("{"):
                params.append({"name": segment[1:-1], "in": "path", "required": True, "schema": ref("OpaqueId")})
        if mutation:
            params.append({"$ref": "#/components/parameters/IdempotencyKey"})
        params += extra_parameters or []
        value = {"operationId": operation_id, "summary": summary, "description": description,
                 "responses": {status: {"description": "Accepted as a durable job." if status == "202" else "Successful scoped result.",
                                        "content": {"application/json": {"schema": ref(response_schema)}}}, **errors}}
        if params:
            value["parameters"] = params
        if request_schema:
            value["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref(request_schema)}}}
        if public:
            value["security"] = []
        elif recovery_allowed:
            value["security"] = [{"LocalSession": []}, {"RecoverySession": []}]
            value["x-commonstar-recovery-access"] = (
                "Bound snapshot/grant; new_profile restore only; no active profile required"
                if operation_id == "createRestore"
                else "Only restore jobs owned by this verified recovery attempt; other jobs return 404"
            )
            value["responses"][status]["content"]["application/json"]["x-recovery-session-schema"] = ref("RecoveryJob")
        if mutation:
            value["x-commonstar-mutation"] = True
        if status == "202":
            value["responses"][status]["headers"] = {
                "Location": {"description": "Relative same-origin URL for this job, such as /v1/jobs/{job_id}.", "schema": {"type": "string"}}}
        paths.setdefault(path, {})[method] = value

    operation("/health", "get", "readHealth", "Read minimal service liveness", "Health", public=True,
              description="No vault status, user identity, model details, paths or secrets. Loopback-only even without authentication.")
    operation("/imports", "post", "createImport", "Import selected materials", "Job", "ImportRequest", "202", True)
    operation("/search", "post", "searchActiveProfile", "Search permitted active-profile evidence", "SearchResponse", "SearchRequest",
              description="Read-only POST: no idempotency key required. No raw SQL, caller profile ID or cross-profile filter.")
    operation("/turns", "post", "createTurn", "Start an explicitly routed learning turn", "Job", "TurnRequest", "202", True)
    operation("/jobs/{job_id}", "get", "readJob", "Read one authorized job", "Job", recovery_allowed=True)
    operation("/jobs/{job_id}/cancel", "post", "cancelJob", "Request cancellation", "Job", "CancelJobRequest", mutation=True,
              description="Cancellation is idempotent and cannot undo an already committed result. Report a completed/cancelled race accurately. Recovery sessions may cancel only their bound restore-attempt job.", recovery_allowed=True)
    operation("/jobs/{job_id}/events", "get", "streamJobEvents", "Resume an authenticated SSE job stream", "Job",
              extra_parameters=[{"$ref": "#/components/parameters/LastEventId"}],
              description="Use authenticated fetch streaming, not credentials in a query string. SSE id equals sequence; event equals type; data is one JobEvent JSON object. Heartbeats are SSE comments. Replay is bounded; an expired cursor yields 410. Cancel through the explicit endpoint; closing the stream alone does not cancel the job. Recovery sessions see only their restore job's progress/state, with no record content or inference deltas.", recovery_allowed=True)
    stream = paths["/jobs/{job_id}/events"]["get"]["responses"]["200"]
    stream["content"] = {"text/event-stream": {
        "schema": {"type": "string"}, "x-event-schema": ref("JobEvent"),
        "x-recovery-event-schema": ref("RecoveryJobEvent")
    }}
    stream["headers"] = {"Cache-Control": {"schema": {"const": "no-store"}},
                         "X-Accel-Buffering": {"schema": {"const": "no"}}}
    operation("/proposals/{proposal_id}", "get", "readProposal", "Read a pending proposal and its revision", "PendingProposal")
    operation("/proposals/{proposal_id}/accept", "post", "acceptProposal", "Accept an authorized validated proposal", "MutationReceipt", "AcceptProposalRequest", mutation=True)
    operation("/notes", "post", "createNote", "Create an authenticated user-authored note without a model", "MutationReceipt", "NoteCreateRequest", "201", True,
              description="The service supplies the authoritative envelope and user provenance. Referenced artifacts must be authorized; no profile, actor, review or permission field is accepted.")
    operation("/tasks/{task_id}/edits", "post", "editTask", "Edit whitelisted task fields without a model", "MutationReceipt", "TaskEditRequest", mutation=True)
    operation("/records/{record_id}", "get", "readRecord", "Read a permitted record", "CommonstarMemoryRecord")
    operation("/records/{record_id}/corrections", "post", "correctRecord", "Correct an authorized statement", "MutationReceipt", "CorrectionRequest", mutation=True)
    operation("/records/{record_id}/deletions", "post", "requestDeletion", "Request scoped deletion and derivative handling", "Job", "DeletionRequest", "202", True)
    operation("/plans/{plan_id}/preview", "get", "previewPlan", "Preview a goal's exact task graph and obtain its scoped snapshot", "PlanPreview",
              description="Read-only; no task, deadline or permission is changed. plan_id is goal.record_id. Resolve authorized membership/dependency state in one consistent read and issue a short-lived no-additional-privilege snapshot grant for activation. Native IPC uses the same previewPlan operation.")
    operation("/plans/{plan_id}/activate", "post", "activatePlan", "Activate a goal and its verified task graph", "MutationReceipt", "PlanActivationRequest", mutation=True,
              description="plan_id is the existing goal.record_id, not a new plan-record type. A matching goal revision and service-issued exact task/dependency snapshot are required; any graph or membership change yields 409.")
    operation("/receipts", "get", "listReceipts", "Inspect minimized operation receipts", "ReceiptList",
              extra_parameters=[{"$ref": "#/components/parameters/Cursor"}, {"$ref": "#/components/parameters/Limit"}])
    operation("/backups", "post", "createBackup", "Create a consistent encrypted snapshot", "Job", "BackupRequest", "202", True)
    operation("/restores", "post", "createRestore", "Validate and restore a selected encrypted snapshot", "Job", "RestoreRequest", "202", True,
              description="A native-issued RecoverySession permits a clean-device new-profile restore without an unlocked profile. It is bound to verified recovery grant/snapshot and cannot replace an existing profile. A normal LocalSession is required for replace_active_profile.", recovery_allowed=True)
    operation("/exports", "post", "createExport", "Create an approved encrypted export", "Job", "ExportRequest", "202", True)
    operation("/providers/pair", "post", "pairProvider", "Bind an explicitly approved inference provider", "CommonstarProviderProfile", "ProviderPairRequest", mutation=True)
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "info": {"title": "Commonstar Local Learning API", "version": "1.0.0",
                 "description": "Specification only; no running service. Authenticated, session-bound local interface. Native IPC implements the same operations. Provider-facing capsules remain a separate minimized boundary."},
        "servers": [{"url": "http://127.0.0.1:17831/v1", "description": "Reference loopback development API; unimplemented. Native production IPC remains private."}],
        "security": [{"LocalSession": []}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "LocalSession": {"type": "http", "scheme": "bearer",
                    "description": "Short-lived unpredictable normal session established through trusted native unlock; bound to the active OS user/profile, scopes and device epoch. Never a model/provider API key."},
                "RecoverySession": {"type": "http", "scheme": "bearer",
                    "description": "Distinct native-issued recovery token bound to authenticated OS user, verified recovery grant/snapshot, recovery attempt and expiry. Requires no active profile. Accepted only for new_profile restore and that attempt's restore-job read/events/cancel; cannot read ordinary records or infer. Revoked at activation, cancellation or expiry; never upgrades automatically into a normal session."}},
            "parameters": parameters, "schemas": schemas},
        "x-commonstar-status": "contract-only-not-an-implemented-service",
        "x-commonstar-source-contract-sha256": source_evidence,
        "x-commonstar-recovery-session-policy": {
            "issued_by": "Trusted native recovery flow after OS-user and recovery-grant verification",
            "requires_active_profile": False,
            "allowed_operation_ids": ["createRestore", "readJob", "streamJobEvents", "cancelJob"],
            "restore_mode": "new_profile",
            "must_match_bound_snapshot_and_grant": True,
            "job_kind": "restore",
            "job_scope": "same_recovery_attempt",
            "activation": "Revoke recovery token and require fresh ordinary profile authentication",
            "response_scope": "Restore progress/state only; no record contents, inference deltas, raw keys or cross-profile metadata"
        },
        "x-commonstar-security-invariants": [
            "No caller-selected profile_id field or cross-profile request routing.",
            "Resolve normal objects/grants against the active-profile session; recovery access is limited to its verified attempt and never selects an arbitrary profile.",
            "All mutations require Idempotency-Key and current revision where applicable.",
            "Revalidate grants, peer identity, age/policy and retention at use; schemas cannot establish authorization.",
            "Strict Host/Origin checks, no permissive CORS, no query-string credentials, no remote listener.",
            "No raw encryption keys, raw provider secrets, arbitrary filesystem paths, shell or SQL in the API.",
            "Response and SSE payloads use Cache-Control no-store; log only minimized operational metadata.",
            "Normal tokens are invalidated on vault lock, session switch and device-epoch revocation; recovery tokens expire or revoke on activation/cancellation.",
            "A recovery token cannot invoke search, records, notes, tasks, receipts, inference, export or provider pairing.",
            "plan_id equals goal.record_id; activation atomically validates goal revision and exact included task/dependency snapshot."
        ]}


if __name__ == "__main__":
    destination = ROOT / "api" / "openapi.json"
    destination.write_text(json.dumps(build_document(), indent=2, ensure_ascii=False) + "\n")
    print("Wrote api/openapi.json (contract only)")
