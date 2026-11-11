# Lone Star OS — Working-OS-first parallel build brief

**Decision date:** 2026-11-10 (America/Chicago)  
**Repository:** `corgi-verse/lone-star-os`, branch `main`  
**Status:** Implementation plan, **not** evidence of a built app or bootable ISO.  
**Priority:** Ship a usable local learning computer **while** Codex Astra completes the K–12 corpus. Defer deep educational/editorial review without pretending draft content is school-ready.

## 1. Read this before implementing

Read the nearest `AGENTS.md`, `README.md`, `STATUS.md`, `distro/BUILD_CONTRACT.md`, `contracts/README.md`, `contracts/content-pack.schema.json`, `api/README.md`, and only the relevant parts of `SPECIFICATION.md`. Do not begin another specification rewrite. The current `main` contains contracts, tests, and image-build requirements, but **no executable Commonstar app, .deb, or bootable ISO** as of this decision. Existing document references to `commonstar-learning-os` are historical: the active GitHub repository resolves as `corgi-verse/lone-star-os`.

Product naming: the user calls this **Lone Star OS**. Existing `commonstar-*` package IDs, schema URNs, API contracts, and source names are technical compatibility identifiers. **Do not bulk-rename them** as part of the first boot; expose the agreed outward Lone Star identity using actual approved assets when available. Record an explicit identity migration decision later. Keep upstream licenses and legal notices intact.

The user's current Codex Astra curriculum work has reportedly reached Grade 4. Those files were **not present in this repository's `main`** at this check. Do not infer that work was lost, invent its format, or regenerate K–4. Discover its actual local worktree, repository, ownership and output before integrating. Keep the curriculum's working area independent.

## 2. The two lanes and ownership

| Lane | Owner / source of truth | May change | Must not change |
| --- | --- | --- | --- |
| Curriculum | Active Astra corpus worktree | K–12 source units, lessons, exercises, coverage manifest, draft provenance, content exports | OS application, local vault schema, privileged API, installer, release policy |
| OS and lesson player | One Codex implementation worktree in this repo, e.g. `build/working-os-first` | App, importer, trusted core, tests, distro/live image, desktop branding, release automation | Astra's source curriculum or authoritative review status |
| Review/repair (optional) | At most one independent review lane | Test/repair evidence and tightly scoped fixes | Duplicate competing implementation |

**Integration boundary:** Curriculum publishes immutable, versioned **content-pack inputs**. OS consumes them through an importer. Never have both builders edit the same lesson tree, manifest, generated OpenAPI or schema files concurrently. A schema change requires a small, explicit compatibility proposal and fixtures before either builder relies on it.

Create commits and checkpoints at runnable gates. Rebase/sync only after checking both worktrees and uncommitted work. The `main` branch is the integration destination, not a reason to run unfinished multiple-lane experiments directly on it.

## 3. The first tangible goal

**A disposable x86_64 VM boots Lone Star OS; a user launches the learner workspace, opens a real imported draft lesson, answers one deterministic exercise, exits/reopens, and can see the saved progress. The same app can first be exercised as an ordinary Debian/Ubuntu package.**

There must be **no fake cloud chat, simulated lesson save, screenshot-only desktop, or fabricated content coverage**. The earliest bootable preview may show "Local tutor not installed/ready" rather than claiming AI works. The final local-tutor gate later requires actual offline inference, not a mock.

First-run flow:

1. Boot the live OS in QEMU/KVM with UEFI and see a properly branded desktop and launchable learner app. Live-session changes must visibly say **temporary**.
2. Install to a **disposable virtual disk** with visible destructive-action confirmation, then reboot. Use LUKS2, per `distro/profiles/commonstar-amd64.json`, before claiming an installable alpha.
3. Create a local adult engineering-test profile, no account/network requirement. For the initial dev app milestone, use real persisted user state with explicitly documented data-at-rest limitations until the encrypted vault is operational.
4. Browse a Grade 4 (or other actually available) unit and a lesson imported from Astra's real output. If none is exported yet, one existing synthetic repo fixture may be used as a clearly labeled temporary test fixture; never pass a fixture off as completed K–4 curriculum.
5. Read a lesson, submit an answer checked by approved deterministic local code, save a note, close and reopen. The attempt, note, source reference and progress survive application restart and installed-system reboot.
6. In the development preview, show the content status as **Draft / not educator-reviewed**. Do not permit draft content to enter school mode, claim a grade, or silently create a permanent evaluation record from model text.
7. Show actual offline/AI state, including model loading or unavailable status; no implicit provider route or cloud API costs.

No data from a real child is needed for this first run. All test profiles, vaults, content and screenshots must be synthetic or an explicitly authorized adult's own test material.

## 4. Vertical build gates (in order)

### Gate A — Executable learning loop on an existing Linux OS

- Create the Tauri 2 + React/TypeScript learner workspace and Rust core under a coherent source layout consistent with `distro/package-boundaries.json`.
- First slices: first run, Today, Learn, Library, simple notes, lesson attempt, resume, clear empty/error states. A calm, distinctive, accessible desktop UI, not just a chat window.
- Implement a **real local persistence path**. Prefer the specified SQLCipher design from the start; if an early plaintext test store is unavoidable, gate it as disposable developer-only data and never call it a private/student release.
- Import the actual Astra export through a **separate adapter**; read-only content at rest, revision-aware IDs, deterministic answer checking through pre-approved implementations.
- Provide runnable local dev instructions, integration tests, restart test, and a distributable `.deb` built for the exact tested Linux ABI.
- **Acceptance:** independently launch the built app on Linux, complete an actual lesson and confirm persistence after restart. Record screenshots and exact commands/results.

### Gate B — Bootable image rather than a branded mock

- Implement `distro/live/` using Debian 13 Trixie `live-build` and reviewed stock signed boot/kernel packages. KDE/Wayland is the maintained platform. Package the **same app** produced at Gate A; do not build a separate web-only OS facsimile.
- Integrate startup, display/login appearance, app launcher, desktop defaults, offline starter content, and original approved visual archive assets when found. Do not remove license attribution or assume a proprietary replacement kernel.
- Make and verify a real `amd64` ISO-hybrid build. Boot it with QEMU/KVM + OVMF, inspect the desktop, run the lesson flow. Then test Calamares on a disposable virtual disk with explicit target selection.
- **Acceptance:** actual UEFI boot screenshot, installed VM reboot, lesson progress retained after installed reboot. Keep evidence of failed tests too. A successful `lb build` alone is not boot proof.

### Gate C — Real offline local intelligence and private learning memory

- Implement the specified Rust orchestrator and local trust boundary before enabling personal-data inference. Use SQLCipher, closed model proposal contracts, local source/provenance mapping, correction and deletion, no model direct writes.
- Package and verify pinned `llama.cpp` runtime and exact approved model files **by actual checksum**. Model identities in `models/catalog.json` are metadata, not proof of downloaded/runtime-tested weights.
- Actual disconnected generation: ask a new question about the imported content and receive grounded answer + valid source references. The OS must distinguish "This device", "Your workstation", and "Cloud" based on reality.
- If workstation routing is implemented, use explicit approval, authenticated private transport, minimized request context, and a disabled-by-default paid cloud adapter. Do not assume a ChatGPT subscription grants API access.
- **Acceptance:** airplane-mode local inference and correction survives reboot; no surprise network fallback; killed worker / missing model / failure states preserve the lesson and notes.

### Gate D — Privacy, recovery and release candidate

- Finish local encryption, versioned vault snapshots, one selected encrypted backup destination and clean-profile restore. Test wrong-key/corrupt/interrupted restores and schema migration recovery.
- Verify installed-system encrypted boot/reboot, disk selection, previous-kernel/package recovery, software/source/model license manifest and hashes.
- Test keyboard, screen reader, focus, 200% text zoom, reduced motion and narrow-window layouts. Confirm actual hardware separately from VM.
- **Acceptance:** clean VM restore of a committed learner record; repeatable image and package build with exact source commit, input lock, SBOM, checksums, observed results. Only then describe the output as a release candidate.

### Gate E — All grades and educator review

- As Astra produces Grades 5–12, import the updated packs, perform automatic structural/asset/prerequisite/answer-format checks, and display **actual coverage** by grade/subject/status; do not put placeholder material behind a "complete" badge.
- Deep editorial/factual/TEKS alignment, educator review, translations, child usability, accessibility studies, physical Chromebook certification and academic learning outcomes are **later dedicated acceptance gates**, not invented results.
- Draft packs are available only in clearly disclosed adult engineering/test mode. School mode accepts only the existing reviewed/signed policy conditions.

## 5. Curriculum → OS import interface (minimize Astra spending)

**Do not redesign `contracts/content-pack.schema.json` merely to accommodate raw authoring files.** This existing v1 JSON Schema already models pack ID/version, rights, assets with SHA-256/length, objectives and prerequisites, lessons, exercises, answer/checker specifications, accessibility references, authors, review state and optional signature.

Implement a **one-way export/import converter** from Astra's actual files to a conforming pack:

- Preserve original source path + source Git commit + generator/source revision and license/attribution. Store a mapping `source_reference → pack_id/version/lesson_id` so content can be corrected without destroying historical learner attempts.
- Add an **external curriculum catalog/index** (not an unreviewed schema change) mapping each pack to grade, subject, units, expected lessons, actual completed lessons, status, origin and last successful import; never fabricate counts.
- Import is idempotent. Reimporting the same pack hash changes nothing. A new pack version preserves attempts attached to the earlier version and offers explicit rebase/migration logic if lesson IDs change.
- Validate JSON Schema plus actual bytes, duplicate IDs, asset existence/paths, graph cycles, deterministic checker compatibility, accessibility assets, manifest hashes, and approved rights. Do **not** execute code carried in content packs.
- Unsupported lesson shapes should produce an inspectable per-lesson error and a valid partial catalog, not corrupt the vault or stop the entire app. Keep failed inputs quarantined.
- Persist grade/subject selection in the learner application; **do not** hardwire the UI to whichever grade Astra has most recently generated.
- Generate a machine-readable import report with source paths, counts, accepted/rejected packs, lesson IDs, error reasons and package hash. This becomes the "handoff receipt" between lanes.

**What Astra needs to know:** continue producing grades using its current harness and source structure; export canonical IDs, lesson text, exercises/answers, provenance and coverage regularly. No requirement to polish, audit, or reauthor completed K–4 solely for OS integration.

## 6. Credit and execution discipline

- Keep Astra focused on finishing the full K–12 source corpus. Do not spend those expensive turns on installer setup, Debian trivia, CSS changes or re-checking previously verified specs.
- Build the OS in another Codex session/worktree, using the **smallest effective reasoning effort for ordinary implementation**, reserving more expensive effort for trust boundaries, thorny integration and meaningful failures.
- One main builder and at most one repair/review lane within this repository. Avoid simultaneous full-repo agent explorations.
- Every coding session reads this document and `STATUS.md`, checks the actual worktree/branch, then resumes from the **first unmet runnable gate**, instead of regenerating plans.
- After each gate, save reproducible artifact identity, README run instructions, test results, failure evidence and current blockers to `STATUS.md` and `verification/`. Do not mark app, image or model tests passed until they have actually run.
- No purchases, paid cloud inference, public deployment, school/student upload or destructive disk operation. Use disposable VM disks only until separately authorized.

## 7. The next Codex assignment

> Work in `corgi-verse/lone-star-os`. Read AGENTS.md, STATUS.md and docs/BUILD_WHILE_CURRICULUM_GROWS.md first. Verify GitHub owner, current branch, existing worktrees and implementation; preserve Astra's separate curriculum lane. Do not rewrite the specification. Implement **Gate A**, end to end, using Tauri 2 + React/TypeScript + Rust and the existing contracts. Locate the actual K–4 Astra export if it is available without interfering with its active work; otherwise use one clearly labeled synthetic fixture, with a stable import adapter designed for later real packs. Make profile, grade/lesson browsing, deterministic exercise attempt, note, save/restart/reopen, draft watermark, empty/error/recovery states actually work. Build and launch the app in a real Linux session, exercise and document the learner path, produce a Debian package if build dependencies permit, commit exact verification evidence. If Gate A completes and the environment supports it, continue directly to **Gate B**, building and booting the live ISO in a disposable UEFI VM. Do not end at scaffolding, a passing compile, a mocked UI or a plan. Only claim what you executed. Checkpoint runnable progress to a reviewable branch and integrate to main when verified; do not duplicate another builder's lane.

## 8. Done means observed behavior

A milestone is **complete** only if it has: (1) a source commit and reproducible commands, (2) a runnable artifact, (3) an observed user path, (4) persistence and failure/recovery evidence relevant to that gate, and (5) an honest `STATUS.md` update. No launch means no "working OS" claim. A spec-test success, successful package build or simulated screen does not replace the actual end-to-end run.

**First visible destination:** boot the OS in a window on the Ubuntu workstation, select an imported Grade 4 draft lesson, do the exercise, and reopen the saved work. **Later destination:** complete K–12 coverage and separate evidence-based curriculum review, without rebuilding the OS for each grade.
