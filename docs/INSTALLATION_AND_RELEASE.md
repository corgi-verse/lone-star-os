# Commonstar installation, workstation connection and release specification

Date: 4 November 2026, America/Chicago.

**This is an implementation and acceptance specification. There is currently no built Commonstar ISO, executable application release, verified installer, measured model performance or certified device.** The concrete platform and runtime choices are recorded in the distro profiles. A source-read runtime revision is not an inference test.

## 1. Selected delivery

The learner distribution uses Debian 13.7 Trixie as the researched point release, the maintained Debian 13 security/update channels, KDE Plasma 6.3 on Wayland and Debian's supported signed stock kernel. The initial bootable image targets amd64 UEFI laptops. Native arm64 application packages are required; an arm64 device image is certified by hardware model and firmware.

The same Tauri 2/React/TypeScript application and Rust/SQLCipher core must install as Debian packages on supported existing Linux systems. The initial Ubuntu target is 26.04 LTS, with actual ABI, library, GPU and desktop integration tests before it is advertised as supported. Installing the application on Ubuntu does not replace Ubuntu.

Three distinct acceptance claims must remain separate:

- **Application package:** real local learning and memory on an already installed Linux laptop.
- **Distribution image:** live boot, encrypted installation, restart, updates and recovery from the generated ISO.
- **Chromebook deployment:** the application inside the approved ChromeOS Linux environment on a specific device/policy combination.

Google's managed-device policy currently blocks Linux virtual machines by default. A school administrator can enable the appropriate policy. A Chromebook's architecture alone does not prove its native Linux boot, audio, graphics, touchpad or suspend compatibility. The initial user test can use a normal laptop as the learner device; that is useful evidence for the architecture, while actual Chromebook certification remains a distinct test. [S1–S4]

## 2. What each machine owns

The learner laptop owns the authoritative encrypted vault, documents, learning evidence, retrieval indexes, preferences, permissions and local model. It performs local inference without a network. The Rust orchestrator is the only component allowed to turn validated model proposals into durable memory.

The Ubuntu workstation supplies a more capable, request-scoped inference service. It receives only context approved by the learner's local policy for that request. It does not receive the full vault, continuous memory synchronization, a global student directory or database write credentials. The UI labels this route **Your workstation**.

The cloud adapter is separately configured and disabled by default. Network loss never silently enables it. A paid provider route requires configured credentials and limits. The local and workstation routes remain usable without a ChatGPT subscription or cloud API account.

## 3. Local model and runtime setup contract

The default learner profile is Gemma 4 E4B with the selected official Google QAT model pack and an **8,192-token runtime context**. The compact profile is Ministral 3B at 8,192 tokens. The reference workstation uses Gemma 4 31B with 16,384 tokens initially; 32,768 is an explicitly evaluated profile after memory and quality checks. These are design choices. Exact model artifacts, licenses and hashes come from the project's model manifests.

Local semantic retrieval uses the selected Google EmbeddingGemma 2 270M BF16 pack, producing normalized 768-dimensional vectors. Its model ceiling is 8,192 tokens; ordinary document chunks start at 512 tokens and retain source/section identifiers. The embedding worker has no external network access, accepts only approved private IPC, supports BF16/F32 execution, and must reject FP16 conversion or fallback. Batched indexing pauses during generative inference to protect interactive responsiveness. SQLCipher plus sqlite-vec is the selected encrypted vector-store integration, with extension compatibility, finite outputs, retrieval quality and deletion behavior still requiring implementation tests. The model metadata is researched; it has not been downloaded or run here.

The generative runtime is llama.cpp, researched at commit bee23322f1baa3d2dd16b8339bed6aff4a8eb663. Its server README was retrieved at that same commit. It has not been compiled or used for inference in this specification task. The lock records this distinction.

The runtime is an unprivileged worker with read-only access to verified models and no access to the learner vault. An authenticated Commonstar wrapper exposes only health and chat-completion operations needed by the application. Disable the upstream web UI, built-in tools/agents, persistent prompt saving, slot inspection, network model fetching, external tunnels and request-content logging. Explicitly configure ports, one inference slot, context size and zero additional prompt-cache allocation; do not inherit changing upstream defaults.

The supervisor constructs an allowlisted environment. A pre-existing environment variable must not re-enable upstream tools, download paths, logging or network exposure. A protected key file authenticates backend calls; the webview never receives the raw inference key. Direct requests from unrelated browser origins are rejected. Killing or switching a learner session terminates the corresponding worker/request state before another learner's profile is opened.

The worker's network restriction denies **external outbound connections**, while retaining the configured private Unix/loopback request-and-response path. Do not deny all socket families and then expect a loopback HTTP server to function. A provider-profile Unix socket can terminate at the Commonstar gateway; that gateway calls the API-key-protected loopback llama worker. These are separate interfaces. Enforce outbound restrictions with verified OS process controls: binding to loopback and setting the upstream offline flag are not substitutes for an egress sandbox. If the required isolation is unavailable, refuse private-data inference with a clear diagnostic rather than silently allowing outside connections.

CPU inference is a supported execution path even when slow. GPU acceleration is an optional tested runtime package. A sandbox that hides all device nodes may block acceleration; permit only required GPU devices and verify that this does not grant access to storage, the vault or unrelated devices. Keep local navigation, reading, editing and retrieval responsive while generation loads or runs. Record latency and peak memory instead of inferring them from parameter count or weight-file size. [S5]

## 4. Full-install procedure

### Before writing an installation medium

Verify the actual release signature and checksums using the documented maintainer key identity. Confirm image version, architecture, model pack and support status. Back up anything needed from the intended laptop and independently verify the backup. The installer must show the exact target disk identity, capacity and affected partitions before any erase operation. Instructions for writing USB media must distinguish the USB device from the internal disk.

The live environment initially uses a disposable demonstration profile. Saving important work requires an explicitly provisioned encrypted persistent vault or an installed system. It must not present a temporary live filesystem as durable personal storage.

### Partition and boot policy

The reference layout is GPT with:

| Partition | Reference size | Contents and policy |
|---|---:|---|
| EFI System Partition | 512 MiB | Bootloader files; no learner data or unlock secret |
| Separate boot partition | 2,048 MiB | Kernel and boot artifacts; no plaintext vault or disk-unlock key |
| LUKS2 encrypted ext4 volume | Remaining approved space | System, private user state, documents, vault and any explicitly enabled disk swap |

Use calibrated Argon2id parameters supported by the tested installer and target machine. The initramfs unlocks root after the bootloader loads the kernel. Separating boot avoids requiring GRUB to decrypt an arbitrary LUKS2 configuration. The exact Calamares module configuration must be reviewed and boot-tested against the installed Calamares version.

Zram is the default swap policy. A disk swap option resides inside the encrypted boundary. Disable hibernation until encrypted resume, lock behavior and key handling are validated. Do not write plaintext prompts or documents to crash dumps, diagnostic archives, unencrypted temporary directories or external swap.

Retain upstream signed boot components where supported, and test Secure Boot on the actual device. This does not establish that every early-boot configuration or initramfs is authenticated. At-rest encryption protects a powered-off lost device; it does not make unlocked data invisible to malware, a privileged administrator or a compromised boot process. [S6–S7]

### First run

Choose adult self-test, household learner or authorized school deployment mode. The initial development test uses the adult owner's original material or synthetic student material. Create a local profile and recovery custody policy, verify its encrypted storage, install or verify the bundled model pack, and perform one offline learning interaction before configuring the workstation or backup.

The first-run application explains who can unlock or recover the profile, what backup destination was chosen, which inference route is active, and how to inspect/correct remembered information. It must not imply that a lost key can always be recovered. Existing files are imported only after the user selects them; importing a directory is not permission to crawl the whole device.

## 5. Workstation connection procedure

The files under distro/workstation/ are **reference templates, not installed configurations**. The client template deliberately uses an invalid hostname so it cannot accidentally connect. No existing account, private key, known-host entry, inference credential or server has been created by this document.

1. On the Ubuntu workstation, verify the exact model pack and runtime build. Start the service as an isolated unprivileged identity behind an authenticated gateway listening only on 127.0.0.1:18081.
2. Provision a dedicated commonstar-inference SSH identity and one authorized key for the learner device. Restrict it to local forwarding to that endpoint, with no shell, subsystem, TTY, agent, X11 or arbitrary destination access.
3. Independently obtain the workstation's SSH host-key fingerprint from the workstation. Verify it before installing the corresponding known-host entry. A fingerprint obtained only through the same unverified network connection is insufficient.
4. Review the supplied server fragment in the context of the actual SSH configuration. Validate syntax and the effective account policy before reload. Preserve an existing administrator session until a new test connection and negative cases succeed.
5. Configure the client's real host, protected private-key location and dedicated known-hosts file. Start the restricted local tunnel. The client binds 127.0.0.1:18082 and forwards to workstation loopback port 18081.
6. Provision a separate inference API key through protected local setup. The application's backend uses the tunneled endpoint and checks service/model identity. The user sees the destination and exact context policy.
7. Complete the successful request, wrong-key, wrong-host-key, blocked-shell, disallowed-destination and disconnected-workstation tests before using personal material.

Reference connection command after configuration:

~~~sh
ssh -F /absolute/path/to/the-configured-client-file -NT commonstar-workstation
~~~

The SSH server policy uses MaxSessions 0 to prevent shell/subsystem sessions while permitting the expressly allowed forwarding. It also uses AllowTcpForwarding local and PermitOpen for the specific model endpoint. A tunnel is encrypted transport; the inference gateway still needs authorization and bounded requests.

Neither router port forwarding nor a public tunnel is necessary for the initial LAN test. A later district service can use an authenticated TLS gateway, per-device credentials and admission control, while preserving local vault authority. No such school service is assumed to exist.

Disable workstation prompt/response logs and persistent conversation stores. Use encrypted storage/swap where any memory could spill, disable core dumps for inference processes, and inspect configured temp/cache/log locations with synthetic data. Clearing files is not a proof that no privileged observer could read process memory. [S8–S9]

## 6. Signed updates

Debian system packages come from authenticated Trixie repositories. Commonstar application packages require an independently maintained signed repository or a separately verified release-package flow. Model and content manifests identify exact version, origin, license and artifact hashes. Do not install executable updates from retrieved lesson text, model output or an unverified user-supplied package location.

Maintain development, candidate and stable channels. Promotion changes a reviewed release manifest, not a floating source branch. An update first verifies signatures/hashes, available space and compatibility, then stages files. Keep the working model until its replacement has loaded successfully. Keep the preceding bootable kernel. Automatic forced reboot during a session is prohibited.

Before a schema migration, take a consistent encrypted safety snapshot and verify recovery metadata. Apply database changes transactionally. A package rollback is allowed only when the old version supports the current schema; otherwise use the documented verified recovery procedure. An OS rollback must never silently overwrite a learner's newer history.

The initial distro uses conventional APT. It does **not** claim an immutable root, A/B slots or atomic OS rollback. Its recovery path is previous-kernel boot, a previous compatible application package, known-good recovery media and a validated vault restore. Any future snapshot system needs a separate decision and tests for boot artifacts, schema compatibility and data preservation.

Release keys have published identities, offline-protected or separately controlled private material, documented rotation/revocation and a response path for compromise. An artifact checksum alone is not publisher authentication. A valid signature does not establish that software is free of defects. [S10–S11]

## 7. Backup and clean-device recovery

Only one device actively writes a learner vault. Backups are versioned authenticated encrypted snapshots at one chosen destination. The remote store does not run retrieval, embeddings, memory consolidation or inference. Backup access credentials do not include the vault decryption key.

Create a consistent snapshot of the database and attachments, record schema/app/content versions and attachment hashes, encrypt before transfer, and confirm upload integrity. Show backup age and the last successful restore-check status. An interrupted upload must not destroy the previous complete snapshot. Removing live records must update live indexes and summaries; historic backup retention and deletion are separately disclosed and enforced.

Recovery on a replacement device verifies the image/application, installs the compatible runtime, obtains the encrypted snapshot, verifies authenticity and integrity, and unlocks with the chosen custodian's recovery mechanism. Restore into a new empty vault first. Inspect record counts, hashes, permissions, corrections and retrieval results before marking the replacement as the active writer. Overwriting an existing vault requires explicit confirmation. The old writer is retired or its writes are rejected according to the transfer protocol.

Loss of both the device and every valid recovery key can make a correctly encrypted backup unrecoverable. The product must explain this during setup and test the chosen custody procedure. A successful upload is not a successful recovery test.

## 8. Release gates and required evidence

All gates below are **unexecuted** for the implementation described here. A specification-format check is distinct from an installed-product check.

| Gate | Required evidence |
|---|---|
| REL-01 — provenance and rights | Exact source/dependency/model/content locks, SBOM, redistributed license/notices and verified upstream identities |
| REL-02 — actual build | Built packages and ISO, command logs, binary/image hashes, secret scan and independent rebuild comparison |
| REL-03 — boot and install | UEFI VM plus target-laptop live boot, encrypted install/reboot, recovery boot and actual Secure Boot result |
| REL-04 — storage protection | Synthetic sensitive records absent from unintended plaintext disk/temp/log/swap locations; tested lock/recovery behavior |
| REL-05 — complete local journey | Offline ingest, retrieval, explanation, independent practice, validated memory update, correction and rebooted continuity |
| REL-06 — model compatibility | Actual chosen artifacts loaded; tokenizer/template, context, structured output, latency, memory, cancellation and CPU/GPU paths measured |
| REL-07 — workstation boundary | Authorized request succeeds; wrong key/host/route/shell/destination denied; disconnect preserves local work and capability |
| REL-08 — network behavior | Captured traffic and process policy demonstrate selected routing, no silent cloud fallback or telemetry, no unauthorized vault exposure |
| REL-09 — recovery | Interrupted backup and clean-device restore with matching records, attachment hashes, permissions and correction semantics |
| REL-10 — update failure | Signature mismatch rejected; out-of-space/interrupted update and failed migration recover; previous data preserved |
| REL-11 — usable interface | Actual keyboard/screen-reader/math accessibility, narrow/desktop layouts, reduced motion, loading/error/offline and retry behavior |
| REL-12 — declared device scope | Wi-Fi, audio, keyboard, touchpad, suspend/resume, battery/thermal and storage tests per advertised hardware; distinct managed-ChromeOS policy result if claimed |

A release may advertise only the device/feature scope supported by its evidence. A successful Linux package test cannot be reported as a Chromebook install; a VM test cannot substitute for the target laptop's hardware result. Adult self-testing does not establish educational efficacy or authorize collection of children's records.

## 9. First owner-operated test

The decisive initial demonstration is two physical machines:

1. On the learner laptop, disconnect networking and import a small set of original learning documents, notes and deadlines.
2. Demonstrate local search, organization and a useful explanation with traceable source references.
3. Record one proposed memory update, validate it locally, inspect/edit it, restart the application and confirm continuity.
4. Connect the Ubuntu workstation through the verified tunnel. Run a task that benefits from the larger model and inspect exactly what left the laptop.
5. Disconnect the workstation during a request. Keep the previous committed work, show the failure clearly and continue locally.
6. Make and restore an encrypted backup on a clean profile, then confirm the history still works with a different approved model profile.

Record laptop/workstation hardware, installed OS and application hashes, runtime/model hashes, context setting, first-token time, generation rate, peak resident memory and selected route. Preserve failures as evidence to repair. No target hardware or inference results are claimed in this document.

## Sources

- **S1:** Debian 13.7 release, 12 September 2026 — https://www.debian.org/News/2026/20260912
- **S2:** Debian 13 architectures and software — https://www.debian.org/releases/trixie/release-notes/whats-new.html
- **S3:** Ubuntu current desktop/LTS distribution — https://ubuntu.com/download/desktop
- **S4:** Google managed ChromeOS Linux policy — https://support.google.com/chrome/a/answer/2657289?hl=en
- **S5:** llama.cpp server documentation at researched source revision — https://github.com/ggml-org/llama.cpp/blob/bee23322f1baa3d2dd16b8339bed6aff4a8eb663/tools/server/README.md
- **S6:** Debian installation and encrypted-volume behavior — https://www.debian.org/releases/trixie/amd64/ch06s03.en.html
- **S7:** Debian Secure Boot — https://wiki.debian.org/SecureBoot
- **S8:** OpenSSH server configuration — https://man.openbsd.org/sshd_config
- **S9:** OpenSSH client — https://man.openbsd.org/ssh
- **S10:** Debian image verification — https://www.debian.org/CD/verify.html
- **S11:** Debian security information — https://www.debian.org/security/

The selected Commonstar architecture and procedures are original engineering recommendations based on these upstream capabilities. Upstream documentation establishes available mechanisms; it does not establish that this Commonstar implementation has been built or tested.
