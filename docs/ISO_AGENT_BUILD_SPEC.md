# Lone Star OS: agent-neutral ISO implementation specification

Version 1.0 | 12 November 2026 | Target: a working offline engineering ISO

**This is a build assignment, not a claim that an ISO exists.** The curriculum may have paused before completion. Its current completeness is **unknown pending the Ubuntu/Dots audit**. Build against the material actually available; do not wait for that audit, regenerate the curriculum, or declare K-12 complete.

## 1. Deliverable and scope

Produce an actual `amd64` UEFI-bootable, installable Lone Star OS ISO. It must contain the real learning application, persistent private learning state, verified local inference, the available admissible curriculum snapshot, offline help, and the approved product identity. Install it onto a disposable virtual disk, eject the ISO, reboot, and repeat the learning journey without networking. Deliver the exact tested image, its SHA-256, package set, input lock, coverage report, and test evidence.

The ordinary journey is:

**Boot -> install or try temporarily -> create/unlock a local profile -> choose an available course -> read -> attempt/check or save a response -> ask the local tutor -> save a note -> shut down -> resume the same work.**

Three labels are distinct:

| Artifact label | What it establishes |
| --- | --- |
| `boot-preview` | The actual ISO boots and has a launchable application. Missing runtime, content or branding is disclosed. This is a checkpoint, not completion of this assignment. |
| `offline-engineering-alpha` | The installed image performs the complete journey, with real local inference, encryption, reboot persistence and recovery. Draft material is permitted in adult engineering use. This is the requested build target. |
| `managed/student release` | The additional family/school enforcement, safeguarding, content approval, device and participant gates have passed. This assignment must not claim those outcomes from an adult engineering alpha. |

Academic/editorial review is deferred. Structural validity, data integrity, safe installation, security boundaries and honest status are not deferred. Generating an answer, passing a schema, completing a lesson and demonstrating mastery remain different facts.

The approved broader product requirements remain in force as the product roadmap. Do not erase Family Center, Classroom, adult refresher pathways, accessibility, the ordinary desktop, or recovery from the design merely because the first image is an engineering alpha. Keep unimplemented managed modes unavailable rather than presenting decorative controls as enforced protection.

## 2. Source of truth and preflight

Canonical repository: `https://github.com/corgi-verse/lone-star-os`.

The live GitHub baseline inspected for this brief was `main` at `78a4df27ce284ef09fb9b1ddfb1b0e5406497af0`. Only `main` and no open pull requests were returned. That baseline contains specifications and validators, not the actual Astra curriculum or a bootable product. A local Ubuntu worktree may be substantially ahead. **Inspect it before scaffolding anything.**

Read root/nearest `AGENTS.md`, `STATUS.md`, `README.md`, this document, `distro/BUILD_CONTRACT.md`, the selected distro profile, `distro/package-boundaries.json`, `contracts/README.md`, `contracts/content-pack.schema.json`, `api/README.md`, and the relevant portions of `SPECIFICATION.md`. Reuse the current application, importer and image tooling when present. Do not rewrite the whole specification.

Before writes, record the repository owner, remotes, branch, HEAD, dirty state, worktrees and active build owner. Use one implementation branch/worktree, preferably `build/iso-offline-alpha`, unless an existing lane already owns the job. Never reset, clean, rebase or overwrite another agent's uncommitted work. Integrate verified work into `main` through the repository's normal review path; a branch is not a reason to leave a verified result stranded.

Locate curriculum and artwork in the user's known project workspaces and supplied archives. Accept explicit `CORPUS_ROOT` and `BRAND_ROOT` overrides. Do not crawl unrelated personal folders or assume the corpus is in this repository. Treat earlier chat claims and archive/branch names as discovery hints, not proof of available files. The original production-art archive still needs local discovery; the downloadable handoff includes two reference boards, not the complete asset family.

Write `verification/iso/<build-id>/discovery.json` with source identities, discovered entry points, existing tests, missing inputs and decisions. Do not publish private absolute paths, personal vaults or raw learner data. A source commit plus a sanitized relative path and snapshot hash is sufficient in public evidence. An unavailable corpus blocks real-corpus acceptance, not independent application/image implementation.

## 3. Platform decisions

| Layer | Required approach |
| --- | --- |
| Build host | The existing Ubuntu workstation; inspect the actual release, architecture, privileges, storage and virtualization support. Do not upgrade or replace its OS. |
| Image build environment | A disposable Debian Trixie amd64 VM. An already-working isolated builder may be reused if equivalent privileges and inputs are documented. Never require privileged access to the user's physical disks. |
| Learner OS | Debian 13 Trixie, maintained stock kernel, KDE Plasma/Wayland, SDDM, GRUB/UEFI and Plymouth. Preserve Debian security updates and truthful upstream attribution. |
| Image tooling | Debian `live-build`, SquashFS and ISO-hybrid output; actual Calamares installer configuration for the installed Calamares version. |
| Learner app | Existing Tauri 2 + React/TypeScript + Rust design. Build the same application into `.deb` packages and the ISO; no separate website pretending to be an OS. |
| Private state | Rust-controlled SQLCipher vault and protected attachments/derivatives; full-disk encryption for the installed system. |
| Local inference | The approved model catalog plus a pinned, actually tested runtime. Portable CPU execution is mandatory; GPU acceleration is additive. |
| Content | Read-only, versioned packs plus a derived course catalog; authoritative attempts and notes remain in the learner vault. |

Pin the suite as `trixie`, not the moving alias `stable`. Resolve and record actual package versions and signed metadata. Historical point-release strings in earlier documents are not a lock. Keep build-source snapshots separate from the installed machine's supported security-update configuration. Do not disable repository authentication to make a build pass. [U1-U3]

Build the application for the actual target Debian ABI. A binary built on Ubuntu is not automatically compatible with Debian, and vice versa. Test an Ubuntu companion package separately when produced; it must never rebrand the Ubuntu host. Tauri's Debian packaging documentation explicitly distinguishes dependency and older-system compatibility. [U4]

For planning, start VM testing with 4 virtual CPUs, 16 GiB RAM and an 80 GiB expandable virtual disk, then adjust from measured image/model/storage requirements. These are test allocations, not claimed minimum hardware requirements. Run a separate compact-model/low-memory profile. `doctor` must calculate headroom for package caches, unpacked filesystems, model copies, image output and test disks before downloads/builds. Do not assume a nominal 500 GB drive has sufficient free space.

## 4. Build order: get a real image early

### Gate 0: reconcile, snapshot and lock

Recover existing local implementation instead of creating a rival. Inventory the corpus without judging its educational accuracy. Make an immutable, hash-identified content snapshot, find approved artwork, identify model/runtime inputs and record exact missing dependencies. Run existing baseline tests and retain failures rather than weakening them.

### Gate 1: one working learning journey

Implement or complete local profile creation/unlock, course navigation, lesson rendering, one supported exercise type, notes, exact resume and draft labeling. Use actual corpus material as soon as it is accessible. Before that, a separately named synthetic fixture may exercise the path; it must never be counted as authored curriculum. Produce and launch a real Debian package. Reading, notes and saving must work with the generator stopped.

### Gate 2: boot the first ISO

Package that same app and a bounded content snapshot into the live filesystem. Build a real ISO, boot through UEFI firmware, inspect the desktop, launch the app and exercise Gate 1. An early boot preview may disclose an unavailable model; it is not the completed offline alpha. Do not wait for every dashboard or future school integration before proving the boot/install pipeline.

### Gate 3: installation and persistence

Configure the real installer, install onto an expendable virtual disk, eject the ISO and reboot. Prove encryption unlock, a fresh local account, saved attempts/notes and recovery. A live RAM session must not masquerade as durable storage. Finish the installed-system path before polishing nonessential screens.

### Gate 4: complete offline alpha

Integrate verified local generation and embeddings, import all eligible packs in the selected snapshot, finish branded ordinary-use surfaces, missing/error/recovery states, privacy boundaries and backups. Run all engineering acceptance cases against the final image. Produce the evidence/artifact bundle. Continue across checkpoints until this gate passes or a genuine dependency blocks it.

No milestone is finished merely because compilation, unit tests, a package build or `lb build` succeeds. Keep checkpoints usable while continuing toward the whole image.

## 5. Product experience and visual identity

The learner is the lone star. Preserve the existing friendly yellow star and calm pastel/ivory/indigo identity. Reuse approved original assets; do not generate a rival mascot, replace the identity with a Texas seal, or use a reference-board screenshot as a wallpaper or installer UI. Text, buttons, progress and authentication remain native/live controls.

Product-owned surfaces include ISO naming/volume label, boot menu, Plymouth boot/shutdown/unlock, live welcome, Calamares, SDDM, session splash, Plasma lock screen, wallpaper/panel/launcher, notifications, app chrome, ordinary settings, help and recovery. Cover English/Spanish UI, readable focus, 200% text zoom, high DPI, reduced motion, keyboard navigation and actual screen-reader behavior. Preserve upstream application names and technical/legal credits.

Package the derivative identity through an update-safe mechanism. Use genuine Lone Star `NAME`, `PRETTY_NAME` and product ID, with truthful Debian `ID_LIKE`. Do not blind-edit every occurrence of Debian, Linux, KDE or Commonstar. Preserve `commonstar-*` package/IPC/schema identifiers until a deliberate migration is required. Existing identifiers are compatibility interfaces, not unwanted branding. The standard `os-release` format supports this distinction. [U5]

One coherent workspace should expose **Today, Study, Library, Notebook, Projects and Progress**, with contextual Practice/Math Lab and Device/Privacy/Recovery controls. Today resumes the exact lesson, source position and scratch work without inventing an AI summary. Grade choice is an academic setting, not an age or authority setting. An adult may open elementary or high-school material without entering a child account.

Use the agreed companion-app portfolio: Firefox ESR, LibreOffice, Dolphin, Okular, Gwenview, Haruna, Ark, Spectacle and KCalc, with Kate/Konsole as owner/advanced tools. Resolve actual packages and dependencies; preserve accessibility and necessary platform services. Do not inherit unrelated mail/calendar stacks, extra players, games, telemetry, cloud enrollment or remote-support servers accidentally from a large desktop metapackage.

Device Center must show actual model, storage, persistence, corpus snapshot, update, backup and connectivity states. It may invoke maintained native settings with coherent styling; do not reimplement a network stack or browser engine. Unsupported managed features must say unavailable and remain disabled. A hidden terminal icon is not parental-control enforcement.

If the production artwork cannot be located, continue with a plainly labeled functional preview and record the exact missing asset inputs. Do not label the visual acceptance gate passed from the reference boards alone.

## 6. Corpus compatibility contract

### 6.1 Never mutate the authoring source

The OS consumes the corpus. It does not take ownership of generation, resume Astra, rewrite lessons, invent missing units, change answer keys, or perform the later educational audit. Preserve original files, IDs, provenance, licenses and review records. A paused run and a complete run must both be importable.

Snapshot a committed revision when possible. For an uncommitted export, create a read-only staged snapshot with a sorted per-file SHA-256 inventory and record dirty/source status. Detect files changing during capture; retry or reject the snapshot instead of publishing a mixture of revisions. Never freeze or terminate another builder to obtain a snapshot.

Report three independent dimensions:

- **Generation coverage:** unknown, partial, author-reported complete, or structurally checked against an identified expected inventory.
- **Engineering usability:** renderable, exercise/checker supported, dependencies resolved, imported or quarantined.
- **Educational review:** the existing pack review state, plus separately evidenced later reviews. Structural checks do not upgrade it.

Do not calculate completion percentages without an authoritative expected inventory. A directory named Grade 12, an agent's summary, or a zero exit status is not evidence that every course is complete. Unknown denominators stay `null`, not zero or 100 percent.

### 6.2 Reuse the existing v1 pack schema

The canonical runtime pack contract remains `contracts/content-pack.schema.json`, schema version `1.0`, ID `urn:commonstar:schema:content-pack:1`, with references resolved through the existing schema registry.

It already models pack identity/version, rights, languages, audiences, assets and hashes, objectives/prerequisites, lessons, authors, exercises, checkers, accessibility assets, review and signature. `review.status` is `draft` or `educator_reviewed`. The schema is closed; do not slip grade, course or generation fields into its objects. Do not rename its URNs or weaken existing negative fixtures.

Authoring format is currently unverified. Detect it on Ubuntu and implement a separate adapter. If it already conforms, use a verified pass-through. If it is Markdown/JSON/YAML or another established export, convert deterministically outside the authoring tree. Preserve originals and explain every field mapping. Malformed or unsupported records produce actionable diagnostics, not fabricated values.

Preserve supplied stable IDs. Where an ID is genuinely absent, assign it once in a persistent source-to-ID mapping and retain that mapping across edits/moves. Do not make lesson identity depend on mutable title, order or content hash. Content hashes identify versions/bytes, not the learner's enduring lesson identity.

### 6.3 Derived course catalog, not a new corpus format

Implement a versioned OS-side course catalog as a separate schema. Prefer a compatible existing local course/route contract if one is already implemented; otherwise create `course-catalog.v1` with fixtures and migration policy. This document specifies required semantics, not an assertion that that file already exists.

The catalog must contain:

| Object | Required information |
| --- | --- |
| Snapshot | Format version, snapshot ID, source repository/revision when available, sorted inventory hash, adapter version, creation time and generation-coverage evidence. |
| Course | Stable course ID/title, language, grade/level and subject as known, ordered units, declared routes/prerequisites and links to exact pack versions/hashes. Unknown metadata stays unknown. |
| Unit | Stable ID/title and ordered lesson references; planned items are distinguished from importable items. |
| Lesson reference | Existing pack ID, version, manifest digest and lesson ID; availability and supported activity capabilities are derived from actual files/runtime. |
| Coverage | Expected count/inventory reference or null, discovered/imported/quarantined counts, explicit missing IDs and reasons, separate reviewed counts and supported-practice counts. |
| Source mapping | Original relative source identity/revision -> stable course/unit/lesson IDs -> generated pack identities. No private learner records. |

Grade/level metadata must not be inferred from `audiences`; adult/13-plus/under-13 eligibility is not academic level. Keep English and Spanish coverage separate. Derive navigation from installed catalog records, not thirteen hard-coded fake course cards. Planned/unavailable entries may be shown with truthful states and no pretend lesson content.

If the source contains only readable lessons with no exercises, expose reading and notes. Preserve a missing-practice status. Do not generate scored exercises just to make an import pass. Existing v1 schema permits some empty exercise/accessibility arrays; structural validity alone is not course completeness.

### 6.4 Import pipeline and atomicity

Implement `discover -> snapshot -> map -> validate -> stage -> activate -> report`.

Validate actual bytes, declared lengths and SHA-256 values, schema, duplicate IDs, all local references, prerequisite graphs, content rights, checker compatibility and safe paths. Reject traversal, absolute paths, links escaping the staging tree, device files, oversized decompression and executable/script-bearing content that could reach privileged IPC. Never run code from a pack. Sanitize Markdown/HTML and do not load remote resources while rendering an offline lesson.

A failed pack is quarantined as a whole; do not activate a half-validated pack. Other independently valid packs may still import. At image build time, every pack declared required in the locked selected snapshot must pass or the build fails. Missing optional/planned material is listed, not silently substituted. Keep the working installation until its replacement is validated and activated transactionally.

Reimporting identical identity/version/bytes is a no-op. The same pack ID/version with different bytes is a conflict, not an overwrite. A new version installs alongside the previous version while referenced learner history exists. Removing a content pack cannot delete notes or attempts. Updates and withdrawals preserve historic provenance and do not silently regrade old work.

Unsigned local draft packs can be used only through explicit adult engineering admission. A valid hash establishes byte integrity, not publisher authenticity or educational correctness. Reviewed/signed school admission keeps its existing stricter policy. Never generate a reviewer identity or claim a signature is verified because its field has the right shape. Before implementing signed packs, specify the canonical bytes covered by the signature, trusted key resolution and revocation tests; do not hash an envelope including its own signature recursively.

### 6.5 Curriculum can arrive after the ISO

Support local folder/archive import through native file selection and a bounded importer. Later material can be installed without rebuilding or reinstalling the OS. Source discovery remains read-only; importing never edits Astra's authoring tree. The packaged starter snapshot is one versioned input, not a permanent upper limit on grades.

Write `corpus-import-report.json` and `corpus-coverage.json` with exact source/snapshot identities, adapter version, accepted/rejected packs and reasons, counts and missing metadata. Show those statuses in the app. Preserve enough provenance for Dots' later audit and the future editorial pass to locate an issue without regenerating everything.

## 7. Learner behavior, persistence and review later

Use the existing memory/proposal/API contracts. Add any course, enrollment and attempt extensions deliberately with fixtures; do not loosen closed envelopes. Bind each attempt to the active profile, exact pack/version/manifest hash, course, lesson, exercise instance, submitted response, checker/version and assistance history. A teacher grade and a model suggestion must not share authority.

Implement numeric and choice checking first using approved deterministic code. For an unreviewed answer key, label the result **checked against a draft key**, not verified educational truth. Unsupported expressions, proofs or rubrics retain the submitted response with `pending/unsupported` feedback rather than guessing correct or incorrect. Never use arbitrary `eval` on educational expressions. A mathematically supported checker needs bounded parsing, domain/unit/tolerance rules and tests before it is advertised.

Store notes, lesson position, scratchpad, attempts, chosen route and pending work transactionally in the private vault. Save works without inference. Cancellation, full disk, a killed worker or application restart cannot silently discard a committed attempt or write partial generated text as an accepted record. Profile switch/lock revokes the old session and clears private visible/worker state.

The later review pass needs a useful foothold now: attach issue flags to exact content versions and source locators, allow a learner to mark a suspected error, preserve proposed corrections separately from original content, and support withdrawal/replacement without destroying history. Do not require factual review of every lesson to ship this adult engineering image.

## 8. Offline intelligence and privacy

Read `models/catalog.json`, `distro/runtime-lock.json` and model decisions. Verify that selected files actually exist, their license/terms allow the planned use, their bytes match the locked identities, and the pinned runtime can load and generate with them. Historical upstream hashes are observations until verified against downloaded bytes. Do not invent a model, checksum, throughput or release pin.

The complete offline image follows the approved standard tutor, compact tutor and embedding-model design. The large optional workstation model is not bundled by default. Keep all required local tokenizer/template/auxiliary files with the locked models. Use a portable CPU build; a CUDA-only workstation build does not satisfy an ordinary learner laptop. Do not claim a smaller or missing-model preview is the complete offline alpha. A justified model/runtime substitution needs a recorded compatibility/license decision and executed tests, not a silent swap.

Test a fresh grounded question with the VM's network interface absent. Require an actual locally generated answer, openable source references, visible model identity, cancellation and failure recovery. Measure load time, memory and response performance on the recorded VM/profile; do not infer them from file size. Model switching preserves the vault and versioned retrieval provenance.

Inference/extraction workers are unprivileged, cannot read the vault directly, and cannot invoke arbitrary shell/SQL tools. Keep secrets out of the webview. Use scoped native IPC or authenticated private endpoints with tested isolation. Loopback binding alone is not authorization. An unavailable worker leaves reading, notes, practice and help usable.

Cloud routes remain disabled. Do not require an API key, paid service or commercial account to boot or learn. Workstation pairing is optional and explicit; network loss never silently enables another provider. The build agent's model/subscription is unrelated to the runtime tutor or its cost.

Encrypt installed private state and attachments; exclude vault/staging data from desktop indexing, persistent clipboard history, thumbnails, crash logs and lock-screen previews. Do not claim encryption protects an unlocked endpoint from malicious root. Managed child free-form generation stays disabled unless the required local safety and policy controls are implemented and evaluated. Adult testing does not establish child suitability.

## 9. Actual image and installer implementation

Use `distro/live/` as already specified. Include `auto/config`, package lists, local package inputs, file includes, version-appropriate hooks, Calamares configuration/branding and boot themes. If local tooling already owns these, extend it instead of creating a second build system.

Select Debian mode, suite, architecture, image type and bootloader explicitly; validate option names against the pinned tool version. Do not let an Ubuntu host select Ubuntu mode by default. Put built product packages in `config/packages.chroot/` or an equivalent verified package source. Use package lists, `includes.chroot` and documented hooks rather than cloning a moving branch from a privileged hook. Calamares is the selected installer; adding Debian Installer is not a substitute for implementing it. [U1-U3]

Build packages in an unprivileged preparation stage where possible. Restrict privileged filesystem assembly to the disposable build VM. Require immutable inputs before `lb build`; download caches must validate hashes rather than silently reusing stale files. Logs must preserve failing command and exit status. A rerun cannot mark a failed earlier run successful or delete unrelated data.

### Installed disk contract

Use GPT/UEFI with a FAT32 EFI partition, separate unencrypted `/boot`, and LUKS2-encrypted root/data. Start from the existing profile's 512 MiB EFI and 2 GiB `/boot` allocations, validating actual space requirements. Initramfs unlocks root; do not depend on GRUB supporting a particular LUKS2 key derivation. Use the documented Argon2id policy where supported and inspect the actual resulting LUKS metadata. Never silently downgrade encryption to make installation pass.

Generate correct `crypttab`, `fstab`, bootloader and initramfs configuration for the target. No plaintext unlock key in `/boot`, ISO, Git or evidence. Installer summary must identify the exact expendable target and destructive changes before writing. Installation to a physical disk requires separate explicit authorization.

Live mode is a temporary demonstration with a conspicuous persistence warning. Do not automatically migrate live-demo state into a real account. Installed mode creates fresh identity/key material; remove the live account, autologin, build-time tokens, shared machine identity and other temporary artifacts. Never ship a universal installed administrator password. Use zram by default; do not enable unencrypted disk swap or hibernation casually.

Retain signed upstream boot components where possible. Test ordinary UEFI and Secure Boot as separate claims. An OVMF boot with Secure Boot off is not Secure Boot evidence; nor does a signed kernel prove every early-boot byte is authenticated. Physical laptop/Chromebook and Apple Silicon compatibility remain separate hardware tests.

### Repeatable operator commands

Provide the following script responsibilities or documented equivalents, with `--help`, bounded paths, clear exit statuses and logs. These names are requirements to implement, not commands claimed to exist today.

| Command | Contract |
| --- | --- |
| `scripts/iso/doctor` | Read-only host/input preflight; report missing packages, KVM/UEFI support, disk/memory budget and exact blockers. No automatic sudo changes. |
| `scripts/iso/prepare --config <file>` | Snapshot/verify inputs, resolve locks and build packages in the declared isolated environment. Never mutate the corpus. |
| `scripts/iso/build --lock <file>` | Assemble the selected ISO from locked inputs in the disposable builder; emit actual image/package manifests and hashes. |
| `scripts/iso/vm --iso <file> --offline` | Boot through UEFI using private firmware-variable storage and regular-file virtual disks; no raw devices, host-home mounts or networking. |
| `scripts/iso/verify --run-dir <dir>` | Run implemented acceptance checks; preserve failed/not-run cases; do not equate a checklist parser with runtime acceptance. |
| `scripts/iso/evidence --run-dir <dir>` | Collect sanitized logs/screenshots/manifests and bind every result to the exact source and image hash. |

Use a persistent qcow2 disk for install/reboot tests; QEMU's ephemeral snapshot mode must not make persistence look successful within one session. Boot the final ISO through firmware, not only a directly supplied kernel. A networked build VM and a disconnected acceptance VM are separate environments. [U6]

## 10. Acceptance and evidence

For every case record `not_run`, `passed`, `failed` or `blocked`, the exact command/action, observation, environment, timestamp, source commit, ISO SHA-256 and evidence paths. No empty result is a pass. Some cases require software tests plus actual UI/VM observation; record those separately. The final image's hashes must match the image tested, including after reassembly or last-minute visual changes.

| ID | Required observation |
| --- | --- |
| ISO-01 | Build from documented locked inputs and emit a real ISO, not a renamed archive or pre-existing image. |
| ISO-02 | Firmware boots final ISO to branded usable desktop; app opens without internet. |
| ISO-03 | Live session explains temporary state; no host disk is automatically mounted/written. |
| ISO-04 | Installer selects only the expendable disk and shows encryption/destructive summary. |
| ISO-05 | Eject ISO; installed disk boots, unlocks and reaches a fresh local account. |
| ISO-06 | Actual disk metadata confirms the declared encryption layout; wrong unlock fails safely. |
| ISO-07 | Attempt, note, position and scratch work survive clean shutdown and a new VM process. |
| ISO-08 | Available real corpus imports; count/report matches the selected snapshot, not agent prose. |
| ISO-09 | A partial snapshot works; unknown/planned grades and unknown denominators remain truthful. |
| ISO-10 | Same input is a no-op; same ID/version with altered bytes rejects; newer version preserves old history. |
| ISO-11 | Corrupt hash, traversal, escaping link, duplicate ID and invalid dependency/checker inputs are rejected without damaging valid packs. |
| ISO-12 | Draft labels persist in navigation, lesson and results; review/grade authority cannot be forged. |
| ISO-13 | Add a later valid pack from local media without reinstalling/rebuilding the OS. |
| ISO-14 | Supported numeric/choice checks handle correct, incorrect and boundary values; unsupported work is saved without a fabricated grade. |
| ISO-15 | With no network interface, a fresh grounded question generates locally and cites an openable source. |
| ISO-16 | Missing/corrupt model, killed runtime, cancellation and low memory preserve work and never invoke cloud. |
| ISO-17 | Stopped inference does not prevent reading, notes, manual planning, supported practice or help. |
| ISO-18 | Two profiles cannot access one another's records; lock/switch invalidates previous sessions and sensitive UI state. |
| ISO-19 | Synthetic private canaries do not appear in unintended logs, indexes, clipboard history, thumbnails or lock-screen previews. |
| ISO-20 | Untrusted content/model text cannot invoke shell, arbitrary SQL, native privileges, provider setup or review approval. |
| ISO-21 | One versioned encrypted backup restores into a clean profile; wrong key/corrupt/interrupted restore preserves existing work. |
| ISO-22 | A restore cannot silently revive revoked sharing/provider/authority permissions. |
| ISO-23 | Interrupted import, full disk and failed migration/update recover without deleting the prior usable state. |
| ISO-24 | Keyboard/focus, screen reader, 200% zoom and reduced motion work in the native app, installer and authentication paths. |
| ISO-25 | English/Spanish UI and declared offline assets work; untranslated curriculum is labeled accurately. |
| ISO-26 | Ordinary boot/install/login/lock/settings/recovery match approved identity; genuine upstream app/technical credits remain. |
| ISO-27 | Fresh account and normal update retain defaults without overwriting a user's deliberate preferences. |
| ISO-28 | Exported image/package/source manifests match actual installed contents; no credentials or real learner data are shipped. |
| ISO-29 | Delivered or reassembled ISO hash equals the tested hash; package/input/model/content identities are included. |
| ISO-30 | Capability report distinguishes adult engineering alpha from unverified managed, Secure Boot and hardware claims. |

All ISO-01 through ISO-30 are required for the offline engineering-alpha target. A blocked required case means a partial deliverable, with usable completed artifacts still retained. Managed/student release also requires the original specification's applicable A/REL gates and the adopted product review's managed-policy, safeguarding and participant gates. Those are not waived by this table.

Test representative desktop and narrow app layouts, at least 1366x768 and a 720-pixel-wide window, plus the actual native screen-reader flow. Browser/DOM checks are useful but cannot stand in for Tauri/WebKit, SDDM, Calamares or Plymouth testing. Physical hardware and human participation remain explicitly unverified unless actually performed.

## 11. Artifact bundle and stopping rules

Deliver locally under an ignored `dist/<build-id>/` or established equivalent:

- `lone-star-os-<version>-amd64.iso`, `SHA256SUMS`, package artifacts and `BUILD_INFO.json`.
- `build-input-lock.json`, actual installed-package inventory, runtime/model manifests, license/source notices and SBOM.
- Corpus catalog, source/adapter mapping, import report and coverage report with explicit unknowns.
- `acceptance-results.json`, sanitized command logs, final-image screenshots and failure/blocker evidence.
- VM launch/install/recovery instructions, known limitations and a concise continuation note identifying the first unmet gate.

The input lock names exact source revision/dirty state, builder identity/toolchains, Debian metadata and package versions, runtime commit/build flags, model identities/byte hashes/licenses, content snapshot/pack hashes and asset identities. Never fill a missing identity with an example checksum. Keep weights, images, vaults and private keys out of normal Git history.

A repeatable recipe is mandatory. Bit-for-bit reproducibility may only be claimed after independent builds actually match; record remaining nondeterminism. Checksums are mandatory. Publisher signatures require a real maintainer-controlled key and verification; missing signing authority blocks authenticated public-release claims, not a clearly identified local engineering artifact.

Do not create hosting, paid services or public releases without authorization. If later authorized delivery requires splitting the ISO, use numbered parts, per-part hashes, deterministic reassembly and a full-image hash verification. GitHub's documented release-asset limit is below 2 GiB per file; verify the applicable limits before publication. Do not remove offline models just to fit one asset. [U7]

Checkpoint meaningful progress and update `STATUS.md` and `verification/`. Continue through implementation, packaging, real boot, installation, offline use and recovery instead of handing back another plan. Stop only for a real missing credential/license acceptance, unavailable privilege/hardware, unsafe physical-disk operation, or material unresolvable source conflict. Complete independent work and state the smallest exact remaining action. Never report a preview as the finished target.

## 12. References and evidence boundaries

Repository references are authoritative project inputs, not proof of implementation:

- `AGENTS.md`, `STATUS.md`, `README.md`, `SPECIFICATION.md`.
- `distro/BUILD_CONTRACT.md`, `distro/profiles/commonstar-amd64.json`, `distro/package-boundaries.json`, `distro/runtime-lock.json`.
- `contracts/content-pack.schema.json`, `contracts/memory-record.schema.json`, existing API and fixture validators.
- `docs/BUILD_WHILE_CURRICULUM_GROWS.md`: earlier parallel-build brief. This assignment supersedes its assumed K-4 state and supplies the current ISO endpoint; preserve its non-conflict principles.
- Supplied product design review v1.1: full custom experience, adult/managed distinctions and later release gates. Its earlier coding-agent/model designation does not constrain this agent-neutral assignment.
- The original Lone Star visual archive when available. The handoff's two unchanged PNG boards are visual references only, not tested screenshots or complete production assets.

Primary technical references checked for this brief:

- **U1:** Debian Live package customization: https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html
- **U2:** Debian Live includes/hooks: https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-contents.en.html
- **U3:** Debian live images and Calamares: https://www.debian.org/CD/live/
- **U4:** Tauri Debian packaging/ABI guidance: https://v2.tauri.app/distribute/debian/
- **U5:** OS identity and derivative ancestry: https://www.freedesktop.org/software/systemd/man/256/os-release.html
- **U6:** QEMU firmware, drives and snapshot behavior: https://www.qemu.org/docs/master/system/invocation.html
- **U7:** GitHub release artifacts: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases

These sources establish upstream mechanisms. Every Lone Star capability above remains an implementation requirement until its own evidence exists.
