# Synthetic contract examples

`manifest.json` registers every positive and negative fixture, its schema URN, expected outcome, and synthetic trusted validation context. All people, IDs, hashes, lesson materials, policy approvals and host fingerprints here are synthetic. No record is a production credential, approved curriculum, measured learner result or real provider approval.

The positive set covers all memory record types, all model proposal types, a context capsule, a tutor response, local/workstation provider configuration, an unconfigured optional OpenAI provider and a draft content pack.

The negative set covers forged model authority, unknown fields, unsupported schema versions, cross-profile writes, known identifier leakage, nonexistent evidence and citations, request mismatch, model claims of authoritative scores, unapproved providers, unverified peers, plaintext remote endpoints, path traversal, broken content references and prerequisite cycles.

Run `python3 tests/validate_contracts.py` from the repository root after installing `requirements.txt`. Results apply to these contracts and fixtures only. Keep private adult and student vaults, exports, logs, recordings and recovery secrets outside the public checkout.
