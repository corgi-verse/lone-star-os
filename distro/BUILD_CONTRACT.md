# Commonstar image and package build contract

**Status: complete specification of required build behavior; no image or application package has been built in this repository.** The JSON files describe the selected platform. They are not accepted directly by live-build or Calamares and must not be passed to an installer as if they were generated installer configuration.

## 1. Source layout

The implementation must provide these source boundaries. This table is a contract for the implementation repository, not a claim that all listed source files already exist.

| Source boundary | Responsibility |
|---|---|
| Desktop workspace | Tauri 2 application, React/TypeScript views, typed IPC contracts, accessibility and error states |
| Rust core workspace | Vault, SQLCipher migrations, attachments, retrieval, permissions, provider routing, memory validation and backup orchestration |
| Worker workspace | Sandboxed extraction, OCR and embedding workers with independent capability manifests |
| Runtime packaging | Pinned llama.cpp source, build definitions, CPU/GPU variants, supervisor and authenticated route wrapper |
| Debian packaging | Named packages in package-boundaries.json, dependency constraints, maintainer scripts and upgrade/removal behavior |
| Live-image configuration | auto/config, package lists, file includes, ordered hooks, Calamares modules, bootloader and recovery configuration |
| Release tooling | Input locks, license/SBOM generation, artifact hashes, signing requests, build reports and evidence inventory |

The live-image configuration resides under distro/live/ when implemented. Its auto/config must select Debian mode explicitly, suite trixie, amd64, an ISO-hybrid live image and the tested installer configuration. It must not rely on the builder host's distribution or a moving “stable” suite alias. The default desktop selects KDE Plasma and the maintained Debian browser/accessibility packages. Import installed package dependencies faithfully rather than aggressively removing recommended packages without a demonstrated reason.

The image builder takes the already-built Commonstar .deb artifacts as inputs. It does not download an arbitrary branch during a privileged build hook. Root filesystem includes contain product defaults and policy, never a learner profile, provider key, SSH private key, LUKS recovery secret or real personal document.

## 2. Prerequisites and authority

Use a disposable amd64 Linux build VM with sufficient disk space for source, package caches, unpacked root filesystem and two image builds. Debian live-build, debootstrap, xorriso, squashfs tools, signed boot packages, Calamares, packaging tools and an emulator are builder prerequisites. The exact installed versions belong in the release input lock. Docker alone does not prove that live-build's mount/loop-device privileges are available; use a VM where necessary.

The application build needs the pinned Rust and JavaScript toolchains, locked dependencies and the documented Tauri/WebKitGTK and SQLCipher build dependencies. The model runtime build uses the researched source revision in runtime-lock.json. CPU and GPU variants are built separately with recorded architecture and instruction-set requirements. An accelerated binary compiled for the builder's GPU or CPU must not silently replace the portable learner build.

The builder runs only on disposable build storage. The ISO construction job has no access to a user's physical installation target. Signing authority is separate from ordinary CI: keys are held by the maintainer or an approved signing service, with public verification material committed through a reviewed change. A public GitHub repository does not itself provide a signing key, an update repository, a binary hosting allocation or an operating-system support team.

## 3. Required input lock

Before any artifact is called a release candidate, produce one machine-readable lock with:

- Commonstar source commit and clean-worktree state.
- Debian suite, architecture, snapshot/retrieval date, repository identities, signed metadata fingerprints and all resolved package versions.
- Build environment image digest or VM image checksum; exact live-build, Calamares, bootloader, kernel and compiler versions.
- Rust and JavaScript dependency locks, registry provenance and integrity data.
- llama.cpp commit, patches, build flags, target CPU features and GPU backend dependencies.
- Exact model checkpoint, selected file names, byte counts, SHA-256 values, license text and revision, tokenizer/chat-template version and projector files if used.
- Content pack versions, file hashes, origins, license compatibility and review records.
- Installer settings including encryption and boot layout; firmware/non-free components identified individually.

Missing an input prevents candidate promotion. Do not fill gaps with a guessed checksum, invented package version, example signing fingerprint or a claim that a moving branch is reproducible.

## 4. Ordered build

1. Resolve and verify all inputs in an unprivileged preparation stage. Record upstream signatures and checksums; quarantine any mismatch.
2. Build the desktop, Rust core and workers. Run their contract, persistence, migration, isolation and accessibility checks. A failed test remains a failed gate.
3. Compile the pinned runtime variants. Compare selected flags with the built help output; load the exact local/workstation model files and test generation. A documentation-only pin does not pass this step.
4. Build .deb packages with declared dependencies, notices, removal semantics and no post-install network downloads of unpinned code. Package install must not enable a cloud provider, alter SSH access or format a disk.
5. Create the live-build configuration from the selected distro profile. Review generated Calamares partition, mount, bootloader and encryption modules against the exact packaged Calamares version.
6. Assemble the live filesystem, model pack, starter content, offline documentation and recovery environment. Verify that the image contains no learner state or maintainer secrets.
7. Build an ISO-hybrid artifact and a package artifact set. Extract manifests from the resulting filesystem rather than assuming the requested package list equals installed contents.
8. Boot the artifact in a disposable UEFI VM, install to an expendable virtual disk, reboot into the encrypted installation, perform offline learning and restore tests, then repeat on the target hardware.
9. Rebuild in a clean independent environment using the same input lock. Compare image/package output and explain differences. Claim bit-for-bit reproducibility only for artifacts that actually match.
10. Produce the release evidence report, sign authenticated metadata and checksums, and publish the verified candidate only after the relevant release gates pass.

No destructive installer is generated by this specification. The implementation must require visible confirmation of the actual target disk and affected partitions; a model never approves that step on the learner's behalf.

## 5. Artifact set

Each release must provide the following artifacts, using its actual version and architecture:

| Artifact | Required content |
|---|---|
| Live installer ISO | Tested boot/installer, local runtime, verified model pack, starter content and recovery tools |
| Debian package set | Application/core/workers and relevant runtime/model/content metadata packages |
| Input lock and build report | Exact source and dependencies, build host identity without secrets, command outcome and timestamps |
| Installed-package manifest | Package names, versions, architecture and firmware inventory extracted from the actual image |
| SPDX or CycloneDX SBOM | Application, distro, runtime, model and content components with distinct license treatment |
| Checksums and detached signatures | Real artifact hashes and maintainer-controlled signatures |
| Release verification material | Public key identity/rotation policy and independent verification instructions |
| Test evidence bundle | VM/device identities, model hashes, executed acceptance checks, failures and unresolved limitations |
| Recovery instructions | Known-good image/version, previous-kernel path, package/schema compatibility and vault restore |
| Corresponding source/notices | Source availability and attribution required by redistributed upstream licenses |

Large weight files belong in appropriately licensed release distribution or verified model storage, not routine Git source history. Distribution must not bypass any model-license acceptance or redistribution requirement.

## 6. Package and data invariants

An upgrade, downgrade or removal never silently deletes the learner's vault. Removing a package stops its services and removes its executables; erasing personal data is a distinct explicit action. Old model packs may be removed only after the replacement is verified and the user has sufficient remaining local capability. A failed model download cannot remove the working model.

OS package signing, application release signing and model/content manifest verification are separate controls. A compromised validly signed upstream artifact is still a security event; signatures establish provenance, not correctness. Review the update threat model, key rotation and revocation process.

The school deployment policy can lock down administration while retaining learner access to their records and the authorized correction/export process. Device administration is not delegated to the generative model.

## Sources

- Debian live-build customization: https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html
- Debian live-build includes/hooks: https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-contents.en.html
- Debian live images and Calamares: https://www.debian.org/CD/live/
- Debian image authenticity: https://www.debian.org/CD/verify.html
- Calamares partition module: https://github.com/calamares/calamares/blob/calamares/src/modules/partition/partition.conf
- Pinned llama.cpp server documentation: https://github.com/ggml-org/llama.cpp/blob/bee23322f1baa3d2dd16b8339bed6aff4a8eb663/tools/server/README.md
