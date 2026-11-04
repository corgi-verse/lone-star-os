# Verification record

The specification has several different evidence levels. Keep them distinct.

## Checks available in this repository

- `tests/validate_contracts.py`: JSON Schema meta-schema validation, valid fixtures, expected structural rejections and expected semantic rejections using synthetic trusted contexts.
- `tests/validate_repository.py`: document links, required files, JSON syntax, distro schema, model metadata shape, runtime policy consistency and a bounded publication preflight.
- `tests/validate_openapi.py`: OpenAPI 3.1 validation, embedded-contract identity, authentication/idempotency coverage, resolved local references and unsafe-request rejection.
- `distro/verification-report.json`: distro profile and SSH client template checks with checked-file hashes.

Detailed local run results are in [local-checks.json](local-checks.json); their original source identities are in [source-manifest.json](source-manifest.json). Those files preserve the authoring evidence. The current [publication manifest](publication-manifest.json) records source identities after publication-metadata updates. Model catalog digests are upstream metadata; a syntax check of a digest does not verify the model binary.

The GitHub Actions workflow runs the three specification validators with read-only repository permission. Its checkout action is pinned to the upstream v7.0.1 commit. The first public run passed all three validators; [github-publication.json](github-publication.json) records its exact commit, tree, run URL and job conclusions. Later commits have their own runs on the repository's [Actions page](https://github.com/corgi-verse/commonstar-learning-os/actions).

## Not established by these checks

No application implementation, bootable image, local or remote model inference, cloud API call, physical hardware performance, encrypted storage, process sandbox, backup restore, school authorization, accessibility acceptance or learning improvement is established by the specification check suite.

Future evidence should identify the exact source commit, build and model identities, environment, test input, expected/observed result and material limitations. Use synthetic or appropriately authorized data and keep private evidence outside public Git history.
