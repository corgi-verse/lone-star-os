# Commonstar v1 contracts

These are JSON Schema Draft 2020-12 specifications for the proposed application. They are not an application implementation or evidence that a vault, model adapter, distro image or security boundary exists.

All schema identities use `urn:commonstar:schema:<name>:1`. They resolve through the local registry in the verifier; validation requires no network access. Internal record identifiers use `urn:uuid:`. Product-owned conceptual identifiers use `urn:commonstar:`. Example identifiers, hashes, peer fingerprints and approvals are synthetic and must never be used as production configuration.

| Schema | Authority and purpose |
| --- | --- |
| `common.schema.json` | Shared closed field types |
| `memory-record.schema.json` | Authoritative service-owned envelope plus 13 typed payloads |
| `model-proposal.schema.json` | Eight untrusted proposal types; no profile, permission, actor, retention or approval fields |
| `context-capsule.schema.json` | Bounded inference request with request-scoped source labels |
| `provider-profile.schema.json` | Locally approved endpoint/model/privacy configuration; secrets are references only |
| `tutor-response.schema.json` | Tutor output, citation labels and proposed memory changes |
| `content-pack.schema.json` | Versioned content rights, assets, standards, objectives, lessons, review and optional signature |

## Authority rules

The future `/v1` API is local and bound to an authenticated session. The caller cannot select a profile by putting an ID in a request. The complete memory-record object is an internal storage/read contract; models submit only model-proposal objects. Model proposals cannot create permissions, approve themselves, turn suggested practice answers into validated answer keys, or claim an official grade.

Unknown fields are rejected at both envelope and typed-payload levels. Schema version `1.0` is exact. The local service is responsible for record ownership, actor authentication, revisions, atomic transactions, consent, permissions and retention. Passing a JSON Schema is insufficient to establish any of those facts.

Context capsules contain no stable profile, school or internal record ID fields. Their free text can still contain personal information. The fixture validator checks known forbidden identifiers only; it is not a general redactor or anonymity proof. The capsule's requested retention policy is an input to provider negotiation, not proof that a provider honors it.

Model proposals use request-scoped `S1` source labels, `E1` evidence labels, `T1` existing-task labels and the literal `current` for the current goal. Plan-local `step_1` labels identify steps within one proposal. The service resolves these through its private request-to-record mapping before creating authoritative records. Stable record IDs are never needed in a remote model's proposal. Proposal identities and request identities are newly generated correlation IDs, not learner identities.

An accepted plan is a goal plus a set of committed task records, not an additional record type. Acceptance allocates record IDs, translates proposed step dependencies into `depends_on_task_ids`, checks dependencies against the authorized task catalog and graph, and commits the whole plan atomically. Unknown dependencies and cycles are rejected. Existing task mutations still require the service's revision/idempotency checks; these payload schemas do not implement a transaction manager.

Provider authentication is bound to transport. Unix IPC requires peer credentials and `local_socket`; local loopback HTTP requires an API-key secret reference. Workstation SSH and mTLS profiles carry a transport credential reference and a distinct application inference credential reference. The examples contain references only, never real secrets. Static validation does not prove that a running server enforces authentication.

Tutor citations must name labels and locators supplied in the corresponding request. The semantic verifier checks that relationship. It does not establish that a source supports the answer, that the answer is mathematically correct, or that learning has improved.

Content-pack assets and prerequisite references must resolve, and prerequisite cycles are rejected. Draft synthetic content is valid for adult engineering tests. School mode additionally requires educator review and separately verified signature evidence. The verifier does not implement cryptographic verification or read the claimed asset bytes; synthetic fixture hashes are deliberately not release hashes.

Content packs declare authors, exercises, answer specifications, checkers and accessibility assets. Every lesson/exercise/accessibility reference must resolve. A checker implementation reference must identify an already installed, approved checker; content cannot install arbitrary executable graders. Numeric, choice and expression checker contracts represent deterministic checking; rubric contracts require educator review. These tests validate the contracts and cross-references, not the correctness of the actual educational material or checker implementation.

## Run contract verification

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 tests/validate_contracts.py
python3 tests/validate_contracts.py --verbose
```

The verifier checks every schema against its meta-schema, every fixture against the correct schema, and reference/authority/privacy invariants against explicit synthetic trusted context. Negative fixtures distinguish schema failures from semantic failures. The trusted context is test input standing in for authenticated service state; a runtime must never accept that context from a model or request body.

Adult self-testing with real learning material must use a vault outside this repository. The fixtures contain no real student records. No test here runs a model, contacts a provider, builds an ISO, encrypts data, proves process isolation or evaluates learning outcomes.
