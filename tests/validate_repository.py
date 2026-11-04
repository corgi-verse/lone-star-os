#!/usr/bin/env python3
"""Validate the specification package; does not implement or test the product.

SPDX-License-Identifier: AGPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "__pycache__", "node_modules", "target", "build", "dist"}


def source_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(ROOT).parts))


def run():
    checks = []
    errors = []
    files = source_files()

    def check(name, action):
        try:
            detail = action()
            checks.append({"name": name, "status": "passed", "detail": detail})
        except (AssertionError, ValueError, KeyError, OSError, jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as exc:
            errors.append(f"{name}: {exc}")
            checks.append({"name": name, "status": "failed", "detail": str(exc)})

    def required_files():
        required = ["README.md", "SPECIFICATION.md", "STATUS.md", "AGENTS.md", "LICENSE", "LICENSING.md", "LICENSES/CC-BY-SA-4.0.txt", "SECURITY.md", "CONTRIBUTING.md", "docs/INSTALLATION_AND_RELEASE.md", "docs/MODEL_DECISIONS.md", "models/catalog.json", "distro/runtime-lock.json", "distro/profiles/commonstar-amd64.json", "contracts/README.md", "examples/manifest.json", "tests/validate_contracts.py", "api/openapi.json", "api/build_openapi.py", "api/README.md", "tests/validate_openapi.py", ".github/workflows/specification.yml"]
        missing = [name for name in required if not (ROOT / name).is_file()]
        assert not missing, f"Missing: {missing}"
        return f"{len(required)} required files exist"

    def parse_json():
        paths = [p for p in files if p.suffix == ".json"]
        for path in paths:
            json.loads(path.read_text())
        return f"{len(paths)} JSON documents parsed"

    def distro_schema():
        schema = json.loads((ROOT / "distro/schemas/distro-profile.schema.json").read_text())
        profile = json.loads((ROOT / "distro/profiles/commonstar-amd64.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(profile)
        return "Distro profile matches its Draft 2020-12 schema"

    def catalog_metadata():
        catalog = json.loads((ROOT / "models/catalog.json").read_text())
        artifacts = catalog["artifacts"]
        roles = set()
        for item in artifacts:
            assert re.fullmatch(r"[0-9a-f]{40}", item["revision"]), item["role"] + " revision"
            assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), item["role"] + " digest"
            assert isinstance(item["size_bytes"], int) and item["size_bytes"] > 0
            assert item["role"] not in roles, "Duplicate model role"
            roles.add(item["role"])
            assert item["license"] == "Apache-2.0", "Selected model license changed; review required"
            assert item["filename"].endswith(".gguf") and "/" not in item["filename"]
            assert item["binary_verification"] == "not_downloaded_or_recomputed", "Do not promote metadata to binary verification here"
            assert item["revision"] in item["metadata_pointer_url"]
        for role in ["client_default", "client_compact", "workstation_default"]:
            assert role in roles, "Missing required inference role: " + role
        assert any("embeddinggemma-2-BF16.gguf" == x["filename"] for x in artifacts)
        return f"{len(artifacts)} artifact identities structurally complete; binaries NOT verified"

    def runtime_boundary():
        runtime = json.loads((ROOT / "distro/runtime-lock.json").read_text())
        p = runtime["policy"]
        assert p["api_key_required"] is True
        assert p["direct_vault_access"] is False
        assert p["built_in_tools"] is False
        assert p["public_tunnel"] is False
        assert p["cloud_fallback"] is False
        assert p["request_content_logging"] is False
        assert p["persistent_prompt_cache"] is False
        assert runtime["upstream"]["compiled"] is False
        assert runtime["upstream"]["model_loading_tested"] is False
        assert re.fullmatch(r"[0-9a-f]{40}", runtime["upstream"]["commit"])
        roles = {x["id"]: x for x in runtime["profiles"]}
        assert roles["learner-flagship"]["context_tokens"] == 8192
        assert roles["workstation-reference"]["port"] != roles["workstation-reference"]["tunnel_client_port"]
        return "Research runtime lock retains the specified boundaries and unexecuted status"

    def markdown_links():
        count = 0
        for path in (p for p in files if p.suffix == ".md"):
            for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                target = target.strip().split(" \"")[0]
                if "://" in target or target.startswith(("#", "mailto:", "urn:")):
                    continue
                target = unquote(target.split("#", 1)[0])
                if target:
                    resolved = (path.parent / target).resolve()
                    assert resolved.is_relative_to(ROOT), f"Link escapes repository: {path.relative_to(ROOT)} -> {target}"
                    assert resolved.exists(), f"Broken link: {path.relative_to(ROOT)} -> {target}"
                    count += 1
        return f"{count} relative documentation links resolve"

    def publication_scan():
        forbidden_ext = {".gguf", ".safetensors", ".iso", ".img", ".db", ".sqlite", ".sqlite3", ".key", ".pem"}
        patterns = [r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", r"\bsk-proj-[A-Za-z0-9_-]{30,}\b"]
        scanned = 0
        for path in files:
            rel = path.relative_to(ROOT)
            assert not path.is_symlink(), "Symlink must be reviewed before publication: " + str(rel)
            assert path.suffix not in forbidden_ext, "Private/binary artifact excluded from source: " + str(rel)
            assert path.name != ".env", "Environment secret file excluded"
            assert not any(x in {"vaults", "private-data", "recovery-secrets"} for x in rel.parts)
            if path == Path(__file__).resolve():
                continue  # This file intentionally contains the detection expressions.
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                assert not re.search(pattern, text), "Possible secret pattern in " + str(rel)
            scanned += 1
        return f"{scanned} text files checked for prohibited binary/private paths and selected credential patterns; not an exhaustive data audit"

    for name, action in [("Required deliverables", required_files), ("JSON syntax", parse_json), ("Distro schema", distro_schema), ("Model metadata", catalog_metadata), ("Runtime boundary consistency", runtime_boundary), ("Documentation links", markdown_links), ("Publication preflight", publication_scan)]:
        check(name, action)
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "scope": "Specification consistency only; no application, model, crypto, OS sandbox, installer, device or educational evaluation", "checks": checks, "passed": not errors, "errors": errors}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for row in result["checks"]:
            print(f'{row["status"].upper()}: {row["name"]}: {row["detail"]}')
        print("Product/runtime tests were not performed by this verifier.")
    sys.exit(0 if result["passed"] else 1)
