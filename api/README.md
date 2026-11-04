# Commonstar local API contract

**This is a self-contained OpenAPI 3.1 specification, not an implemented HTTP service.** Native Tauri/Rust IPC implements the same operations. The reference HTTP origin is loopback port 17831; it is distinct from the protected local model worker on 17832 and the workstation tunnel on 18082.

## Trust boundary

Ordinary operations require a short-lived LocalSession established through trusted native unlock. The service binds it to its OS user, active profile, permissions and device epoch. Clean-device recovery has a separate RecoverySession that requires no existing or unlocked profile; its narrow rights are defined below. Minimal liveness is public on the loopback listener. Requests cannot provide a profile ID, raw database instruction, arbitrary filesystem path, teacher approval or provider secret. Record IDs refer only to objects the authenticated session may access; objects belonging to another profile yield the same 404 as nonexistent objects.

The UI's local session credential is different from a provider API key or vault key. Those secrets remain backend-only. Lock, profile switch and device-epoch revocation invalidate ordinary sessions. Recovery tokens expire or revoke on cancellation or activation. Loopback binding must be combined with strict Host/Origin checks, denied permissive CORS, authorization and request limits. No token belongs in a URL or SSE query string.

File selection, key entry, backup destination configuration and pairing identity verification use trusted native dialogs. They issue short-lived opaque grant references. The API verifies each grant's issuer, session, purpose, permitted object, expiration and any required confirmation. Supplying a grant-shaped string does not grant authority. This keeps raw keys and arbitrary file paths out of JSON requests.

## Operations

| Area | Local operations |
|---|---|
| Liveness | GET /health, exposing only service/protocol version |
| Learning materials | POST /imports and read-only POST /search |
| Tutoring | POST /turns; GET /jobs/{job_id}; POST /jobs/{job_id}/cancel |
| Streaming | GET /jobs/{job_id}/events with authenticated SSE |
| Proposals | GET /proposals/{proposal_id}; POST /proposals/{proposal_id}/accept |
| Direct user work | POST /notes; POST /tasks/{task_id}/edits, both usable without a model |
| Memory | GET /records/{record_id}; POST correction and deletion requests |
| Plans | GET /plans/{plan_id}/preview; POST /plans/{plan_id}/activate |
| Privacy | GET /receipts |
| Recovery | POST /backups and /restores |
| Portability | POST /exports |
| Providers | POST /providers/pair with verified local setup references |

Paths are relative to /v1. The generated document carries complete request/response/error shapes. Root request objects are closed. Request-scoped model proposals and tutor responses embed the existing frozen contracts; the HTTP API does not accept a complete authoritative memory-record write.

## Mutations, jobs and concurrency

Every mutating operation requires Idempotency-Key. Ordinary requests scope it to the service-derived active profile, authenticated principal and operation. Recovery requests instead scope it to the authenticated OS user, verified recovery attempt and operation, with no circular requirement for an active profile. Preserve the binding across session renewal and restart. The same key with the same body replays the original result; the same key with different input returns 409. Retain the binding through an asynchronous job and for at least 24 hours after completion.

Existing-record/proposal/plan/job mutations carry an expected revision. Validate ownership, authorization, revision, evidence and retention in the same transaction. An accepted model proposal is not permission to create an official grade, custody change or teacher approval. Return denied scope when the authenticated principal lacks the required authority.

An accepted proposal resolves its request-scoped sources and literal current goal through the original turn's retained binding, never through whichever goal happens to be active later. Expired or missing bindings require a fresh proposal; they cannot be reconstructed by trusting the model.

Long operations return 202 with a Job and same-origin Location. The durable states are queued, loading, running, awaiting_input, completed, cancelled and failed. Progress is null when a percentage is not measurable. Completed jobs require a validated result; failed jobs require an error; incomplete or cancelled jobs cannot expose a committed result. Turn results require a tutor-response object, while other result types cannot contain one. A failed or cancelled generation does not commit its partial text. Cancellation cannot undo a result that already committed; return the actual race outcome. Runtime response validation additionally checks that job/result kinds, returned object identities and embedded proposal IDs match their request and stored job.

Restore first validates in isolated storage. Replacement of the active profile requires a normal LocalSession, matching native confirmation grant and current device epoch; new-profile restore cannot quietly open another local profile. Selected-record export requires a nonempty authorized selection; whole-profile export requires a disclosure grant scoped to the active profile. Both produce encrypted exports under the declared contract.

## Clean-device recovery session

The trusted native recovery flow verifies the OS user and a recovery grant bound to the selected encrypted snapshot and unlock method. It can then issue a RecoverySession without creating or unlocking a learner profile. It has exactly four protected API permissions: create a new_profile restore, read that attempt's restore job, stream/replay its events, and cancel it. It cannot invoke ordinary records, search, notes, task edits, receipts, inference, backup, export, provider pairing or existing-profile replacement.

The service binds the token to one verified grant, snapshot, recovery attempt and expiration. An arbitrary job ID, a different attempt, an inference job or another grant does not become accessible because its format is valid; job mismatches return 404. Recovery job responses and event streams expose only recovery status/progress and exclude ordinary record contents or inference deltas. The OpenAPI document supplies RecoveryJob and RecoveryJobEvent schemas for these context-specific views.

After isolated validation and explicit native activation, revoke the recovery token. Access to the restored records requires a freshly authenticated ordinary profile session. A recovery token never silently acquires normal profile privileges.

## Plan identity and direct user editing

For POST /plans/{plan_id}/activate, plan_id is the existing goal.record_id. No separate plan record type is invented. First call GET /plans/{plan_id}/preview, or its native IPC equivalent previewPlan, to read the authorized task/dependency graph and obtain a short-lived snapshot_ref. This read-only preview changes no task, schedule or permission and grants no additional privilege. The service binds the snapshot to the principal/profile, goal and graph; it retains or authenticates that immutable state rather than trusting a client-resubmitted graph.

The activation's expected_revision validates that goal; plan_snapshot_ref is the returned snapshot_ref. It covers the exact included task IDs, their revisions, dependency revisions and edges. Recompute membership and the graph inside the commit transaction. Adding or removing a task, changing a revision or changing an edge after preview returns 409 and requires a fresh preview, even when the goal's own revision is unchanged.

POST /notes takes the existing closed note payload: title, body and artifact_refs. The service verifies references and creates the authoritative record envelope, authenticated user provenance, timestamps, retention and revision. It never calls a model to interpret a straightforward save.

POST /tasks/{task_id}/edits permits only title, due_at, time_zone, status and estimated_minutes. Edits require a task revision and a nonempty changes object. Deadline and timezone are edited together; due_at=null clears the deadline. Validate timezone/date semantics and commit reminders with the task update. Task completion is learner-reported task status, not proof of mastery or an official grade. Neither endpoint accepts envelope fields, teacher authority, permissions or a generic record patch.

## SSE contract

Use authenticated fetch streaming, since putting a bearer token into an EventSource URL leaks credentials. Each SSE event has:

- id: monotonically increasing sequence local to the job.
- event: state, delta, progress, error or complete.
- data: one JSON object conforming to the JobEvent union.

Heartbeat frames are comments. The Last-Event-ID header resumes after an acknowledged sequence. Replay is bounded; a stale cursor returns 410, after which the client reads the current job and explicitly resynchronizes. Closing an SSE connection does not itself cancel the job. Deltas are display-only until a validated completed result is available.

Keep event replay within the encrypted local lifecycle and retention policy. It must not become an unbounded plaintext transcript cache. Responses and events use no-store cache control and omit secrets.

## Generation and verification

The source of operation definitions is build_openapi.py. It embeds all seven contracts from contracts/ and rewrites both URN references and local fragments into document-local component pointers. The generated file records each source contract's SHA-256. There are no remote schema dependencies.

To regenerate and validate after a deliberate contract change:

~~~sh
python3 api/build_openapi.py
python3 -m pip install -r api/verification-requirements.txt
python3 tests/validate_openapi.py
~~~

The validator checks OpenAPI 3.1 structure, embedded-schema source consistency, local reference resolution, authentication/idempotency coverage and security-sensitive negative request cases. It also runs synthetic trusted-context reference checks for recovery scope and plan-snapshot changes. These fixtures are not production token verification, grant verification or transactional enforcement. It does not run an application, create a session, open a socket, execute a model or prove process isolation.
