#!/usr/bin/env python3
"""Fail when the standard's canonical files or cross-references drift."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "VERSION",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "profiles/company-profile.json",
    "profiles/plugin-profile.schema.json",
    "docs/MASTER-STANDARD.md",
    "docs/WORDPRESS-PLUGIN-STANDARD.md",
    "docs/ENGINEERING-CONTRACTS-V3.md",
    "docs/PUBLIC-REPOSITORY-SAFETY.md",
    "docs/EDD-LICENSE-AND-UPDATES.md",
    "docs/ACCEPTANCE-CHECKLIST.md",
    "tools/validate_profile.py",
    "tools/scaffold_plugin.py",
    "tools/self_test.py",
    "tools/public_repo_guard.sh",
    "composer.json",
    "phpcs.xml.dist",
    ".github/workflows/quality-gate.yml",
    ".github/workflows/tag-version.yml",
]


def fail(message: str) -> None:
    raise SystemExit(f"AUDIT_FAIL {message}")


def main() -> int:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"missing {relative}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?", version):
        fail("invalid VERSION")

    company = json.loads((ROOT / "profiles/company-profile.json").read_text(encoding="utf-8"))
    expected = {
        "developer_name_en": "EOINGTI Lab",
        "author": "EOINGTI Lab",
        "author_uri": "https://eoingti.com/",
        "github_org": "Eoingtilab",
        "telemetry_default": "off",
        "uninstall_data_policy_default": "preserve",
    }
    for key, value in expected.items():
        if company.get(key) != value:
            fail(f"company profile drift: {key}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for token in [
        "Eoingtilab/nalapps-wordpress-plugin-standard",
        "https://eoingti.com/",
        "Plugin Profile",
        "Public Repository Safety",
        "Testing / CI / Release",
    ]:
        if token not in readme:
            fail(f"README missing canonical token: {token}")

    schema = json.loads((ROOT / "profiles/plugin-profile.schema.json").read_text(encoding="utf-8"))
    if schema.get("additionalProperties") is not False:
        fail("plugin profile schema must fail closed on unknown fields")

    print(f"PASS standard_audit version={version} required_files={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
