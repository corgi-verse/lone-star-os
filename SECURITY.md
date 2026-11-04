# Security status and reporting

This is a specification release. The Commonstar application, encrypted installation and runtime boundaries have not been implemented or audited by this release. Contract tests cover data shapes and synthetic authorization cases, not operating-system isolation or cryptography.

## Report safely

For a non-sensitive design issue, open an issue describing the requirement and a synthetic reproduction. Do not publish real student data, private learning records, secrets, recovery keys, exploitable credentials or sensitive device details.

When a private GitHub vulnerability-reporting channel is enabled for this repository, use it for sensitive reports. Its availability must be checked on the live repository; this document does not claim it is enabled. If unavailable, make a public request for a private contact without disclosing exploit details or private data. No response-time or incident-response service is promised until maintainers establish one.

## Required release controls

Track dependency/model provenance, vulnerabilities, signatures, key rotation, parser isolation, policy enforcement, backup restoration and incident handling. Publish only the evidence safe to disclose. An absence of findings in a narrow test is not a security audit.

The threat model includes lost devices, malicious imported content, cross-profile access, hostile web pages reaching localhost, untrusted model output, compromised dependencies, improperly configured remote workers and recovery failure. It does not claim to protect plaintext from an administrator who controls an unlocked endpoint.
