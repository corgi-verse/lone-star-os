# Commonstar distribution specification assets

These files are **declarative specifications and uninstalled reference templates**. They do not constitute a built operating-system image, application package, functioning inference service or tested installer.

| File | Purpose |
|---|---|
| profiles/commonstar-amd64.json | Selected learner OS, installation, update and recovery contract |
| runtime-lock.json | Researched llama.cpp source revision, explicit runtime profiles and validation gates |
| package-boundaries.json | Package ownership, privileges and persistence boundaries |
| schemas/distro-profile.schema.json | Machine-checkable structural constraints for the selected distro profile |
| workstation/sshd-commonstar.conf.example | Restricted, tunnel-only SSH account policy; not installed |
| workstation/ssh-client.conf.example | Pinned-host-key client tunnel template; intentionally nonresolving host |
| BUILD_CONTRACT.md | Source layout, build inputs, outputs and provenance contract |
| verification-report.json | Actual schema/JSON and SSH-client parsing evidence, file hashes and explicit unexecuted checks |

The complete installation and release procedure is in [INSTALLATION_AND_RELEASE.md](../docs/INSTALLATION_AND_RELEASE.md). A field marked “required at release” is a release input, not evidence that the input already exists. No image, model file, signature, installation result or benchmark is fabricated.

The model and memory contracts belong to the main product specification. Runtime profile identifiers here are learner-flagship, learner-compact and workstation-reference. A runtime profile selects an existing, verified model manifest; it never substitutes a moving “latest” download for that manifest.
