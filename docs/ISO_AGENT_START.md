# Build Lone Star OS: start here

This assignment is agent-neutral. Use the existing repository and Ubuntu workspace, not a new competing OS project.

## Job

Build the real `amd64` UEFI Lone Star OS ISO described in [ISO_AGENT_BUILD_SPEC.md](ISO_AGENT_BUILD_SPEC.md). The target is an **offline engineering alpha** that installs to a disposable virtual disk, runs a real lesson and local tutor, saves private learning state, survives reboot and restores a backup. A mock desktop, source-only scaffold, successful compile or unbooted ISO is not completion.

Canonical repository: `https://github.com/corgi-verse/lone-star-os`.

Read the local `AGENTS.md`, `STATUS.md`, current implementation and the build spec before edits. Confirm owner/remotes, branch, dirty files, worktrees and any active build lane. A local checkout may be ahead of GitHub. Reuse that work; do not reset it or start a duplicate builder. Keep one implementation lane and at most one independent repair/review lane.

**The corpus is not verified complete.** The user suspects Astra paused; Dots will audit it later. Locate its actual source/export, preserve it, and use a read-only versioned snapshot. Do not resume generation, regenerate K-4/K-12, invent missing lessons, conduct the full educational review, or force the authoring tree into a new format. Adapt to the existing content-pack v1 contract and add a separate course catalog only where needed. Partial/unknown coverage must work. Later packs must install without an OS rebuild.

Retain Debian Trixie, KDE/Wayland, Tauri/React/Rust, the private vault and local-model architecture unless actual local implementation/evidence requires a documented compatibility correction. Keep internal Commonstar identifiers compatible while presenting Lone Star OS. Locate the approved visual assets; the two supplied reference boards are not the complete production artwork or evidence of a working UI.

## Execute, in order

1. Discover existing work, snapshot inputs, run baseline checks and record exact blockers.
2. Finish one real lesson/attempt/note/resume path and package the app.
3. Build and boot a first ISO early; continue rather than declaring that preview complete.
4. Install onto an expendable virtual disk, eject the ISO, reboot and prove persistence/encryption.
5. Finish actual offline inference, available-corpus import, identity, privacy, error/recovery behavior and the required acceptance cases against the final image.
6. Deliver the tested ISO, full SHA-256, packages, input lock, corpus report and evidence; checkpoint code and update STATUS.md. Integrate verified work through the established repository path.

Use the script interfaces and ISO-01 through ISO-30 in the main spec. Keep every acceptance result `not_run`, `blocked` or `failed` until observed evidence supports `passed`. Preserve tests and failure evidence. Run real native UI/VM journeys as well as software tests.

No API key, paid runtime service, public endpoint, cloud fallback, physical-disk formatting or student-data upload is authorized. Build inside isolated/disposable storage; retain the Ubuntu host. No full-corpus review is required for the adult engineering alpha, but draft status, integrity and safe execution are required.

Continue through all independently executable work. Stop only for a genuine credential, license, privilege, hardware or irreconcilable source dependency. Leave the exact failing command, completed artifacts, first unmet gate and smallest necessary owner action. Do not return another plan in place of a build.
