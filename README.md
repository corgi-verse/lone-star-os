# Commonstar Learning OS

**An open learning computer with private local memory and intelligence.**

Canonical public repository: [corgi-verse/commonstar-learning-os](https://github.com/corgi-verse/commonstar-learning-os). [Specification checks](https://github.com/corgi-verse/commonstar-learning-os/actions/workflows/specification.yml).

Commonstar is an independently developed Linux education project initiated by Hayden Lindley. It is designed for Texas public education and for anyone organizing a serious life of learning. Its authoritative learning record stays on the learner's device. A local model tutors and organizes offline; a paired Ubuntu workstation or an explicitly enabled cloud API can add intelligence without taking over the record.

## Current release

**Specification v1.0 — 4 November 2026.** This repository contains the complete distribution specification, researched model/runtime identities, machine-readable contracts, synthetic fixtures, and installation/release acceptance requirements. It does not yet contain a bootable Commonstar image or the implemented learning application. Actual verification is recorded in [STATUS.md](STATUS.md).

Start with the [complete specification](SPECIFICATION.md). It defines installation, local intelligence, memory, retrieval, orchestration, the workstation bridge, optional OpenAI integration, recovery, accessibility, curriculum, security, licensing and the evidence required for a release.

## Concrete technical decisions

| Responsibility | Selection |
| --- | --- |
| Learner distro | Debian 13 Trixie, KDE Plasma/Wayland, encrypted installation |
| Local tutor and organizer | Gemma 4 E4B, official QAT Q4_0 GGUF; 4.5B effective / 8B including embeddings |
| Compact local installation | Ministral 3 3B Instruct Q4_K_M |
| Local semantic search | EmbeddingGemma 2 text backbone, BF16, 768-dimensional vectors |
| Ubuntu workstation | Gemma 4 31B QAT Q4_0 over authenticated private transport |
| Private memory | SQLCipher, FTS5, local vector retrieval, source and revision tracking |
| Application | Tauri 2, React/TypeScript, Rust services |
| Backup | One destination with versioned encrypted snapshots and tested recovery |
| Optional cloud | OpenAI API adapter, disabled until configured and policy-approved |

Model files and runtime memory are different quantities. Exact upstream metadata and evidence limits are in [model decisions](docs/MODEL_DECISIONS.md) and the [model catalog](models/catalog.json). No hardware throughput or educational superiority is claimed by these selections.

## The first test

On a learner laptop, disconnect the internet and workstation. Import an original learning document, ask a new question, obtain an actual local-model answer with usable source references, accept a study plan or note, reboot, and resume it. Then pair an Ubuntu workstation, inspect the selected outgoing context, run a deeper request, disconnect again, and continue locally. Finally restore the encrypted vault into a clean profile.

The public repository uses synthetic records. A real adult self-test vault belongs outside this checkout. Child deployment, actual Chromebook compatibility and learning outcomes each require their own acceptance evidence.

## Repository guide

- [SPECIFICATION.md](SPECIFICATION.md): complete normative product and distro specification.
- [For Texas educators](docs/FOR_TEXAS_EDUCATORS.md): public purpose, current status and useful collaboration.
- [Installation and release](docs/INSTALLATION_AND_RELEASE.md): package, ISO, workstation, update and recovery contract.
- [Model decisions](docs/MODEL_DECISIONS.md): selected checkpoints, parameter accounting, provenance and evaluation requirements.
- [Distro assets](distro/README.md): declarative platform profile, source-read runtime lock and SSH examples.
- [Contracts](contracts/README.md): versioned schemas for memory, untrusted proposals, context, providers, tutor responses and content.
- [Local API](api/README.md): self-contained OpenAPI 3.1 contract, native session boundaries, durable jobs and recovery operations.
- [Synthetic examples](examples/README.md): positive and negative fixtures with explicit trusted test contexts.
- [Verification](verification/README.md): exact checks performed and limits of those results.
- [Licensing](LICENSING.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md) and [working instructions](AGENTS.md).

## Run the specification checks

These checks validate contracts and specification consistency. They do not start a model or prove a runtime security boundary.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r api/verification-requirements.txt
python tests/validate_contracts.py
python tests/validate_openapi.py
python tests/validate_repository.py
```

The model runtime, weights, installer and operating-system packages have their own acceptance gates before an executable release. Downloaded weights do not belong in ordinary Git history.

## Data and public ownership

The learner's record remains understandable and exportable when a model changes. Model output is a proposal; trusted local code controls identity, permissions and durable writes. A remote model receives an approved context capsule, never a student ID that grants access to the vault.

Remote personalized inference still processes selected data outside the laptop. **This device**, **Your workstation** and **Cloud** are explicit modes. Slow local computation cannot silently trigger a remote or paid route.

Original code and machine-readable contracts use **AGPL-3.0-or-later**. Original prose uses **CC-BY-SA-4.0**. Upstream packages and model weights keep their own licenses. No source license grants rights to a learner's private records. See [LICENSING.md](LICENSING.md).

Commonstar is not an official Texas Education Agency product and has no claimed school, candidate or model-provider endorsement. The mission is independent learning, useful continuity and support for educators.
