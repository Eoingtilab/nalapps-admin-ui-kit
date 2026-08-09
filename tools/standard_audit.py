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
    "profiles/example-free.plugin-profile.json",
    "profiles/example-edd-paid.plugin-profile.json",
    "docs/MASTER-STANDARD.md",
    "docs/WORDPRESS-PLUGIN-STANDARD.md",
    "docs/ENGINEERING-CONTRACTS-V3.md",
    "docs/AUTOMATION-AND-SCAFFOLDING.md",
    "docs/ROLLBACK-BACKUP-DATA-LIFECYCLE.md",
    "docs/PUBLIC-REPOSITORY-SAFETY.md",
    "docs/EDD-LICENSE-AND-UPDATES.md",
    "docs/ACCEPTANCE-CHECKLIST.md",
    "docs/ISO-29119-25010-TEST-PLAN.md",
    "tools/validate_profile.py",
    "tools/scaffold_plugin.py",
    "tools/scaffold_complete.py",
    "tools/scaffold_product.py",
    "tools/scaffold_maintenance.py",
    "tools/nalapps_plugin.py",
    "tools/self_test.py",
    "tools/quality_contract_test.py",
    "tools/standard_audit.py",
    "tools/public_repo_guard.sh",
    "tools/release_manifest.py",
    "requirements-dev.txt",
    "composer.json",
    "phpcs.xml.dist",
    ".github/workflows/quality-gate.yml",
    ".github/workflows/plugin-check-free.yml",
    ".github/workflows/tag-version.yml",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
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
        "EDD Software Licensing SDK",
        "Rollback / Backup / Data Lifecycle",
    ]:
        if token not in readme:
            fail(f"README missing canonical token: {token}")

    schema = json.loads((ROOT / "profiles/plugin-profile.schema.json").read_text(encoding="utf-8"))
    if schema.get("additionalProperties") is not False:
        fail("plugin profile schema must fail closed on unknown fields")
    for key in ("release_mode", "uninstall_policy", "data_contract"):
        if key not in schema.get("properties", {}):
            fail(f"plugin profile schema must define {key}")
    if not any(item.get("if", {}).get("properties", {}).get("product_type", {}).get("const") == "edd_paid" for item in schema.get("allOf", [])):
        fail("plugin profile schema must require EDD fields for paid products")

    product_scaffold = (ROOT / "tools/scaffold_product.py").read_text(encoding="utf-8")
    for token in [
        "easy-digital-downloads/edd-sl-sdk",
        "edd_sl_sdk_registry",
        "class-license.php",
        "class-update-manager.php",
        "pre_set_site_transient_update_plugins",
    ]:
        if token not in product_scaffold:
            fail(f"product scaffold missing EDD contract: {token}")

    maintenance = (ROOT / "tools/scaffold_maintenance.py").read_text(encoding="utf-8")
    for token in [
        "upgrader_pre_install",
        "overwrite_package",
        "nalapps-data-backup-v1",
        "debug_information",
        "delete_all",
        "class-data-portability.php",
        "class-rollback-manager.php",
    ]:
        if token not in maintenance:
            fail(f"maintenance scaffold missing contract: {token}")

    contract_test = (ROOT / "tools/quality_contract_test.py").read_text(encoding="utf-8")
    for token in [
        "hyphenated-paid-fixture_license_key",
        "telemetry-without-external-api",
        "paid-missing-edd-metadata",
        "sensitive-backup-option",
    ]:
        if token not in contract_test:
            fail(f"quality contract regression missing: {token}")

    cli = (ROOT / "tools/nalapps_plugin.py").read_text(encoding="utf-8")
    for token in [
        "wordpress/plugin-check-action@v1",
        "dependabot.yml",
        "CODEOWNERS",
        "ISSUE_TEMPLATE",
        "tests/README.md",
        "add_maintenance_runtime",
    ]:
        if token not in cli:
            fail(f"canonical CLI missing governance contract: {token}")

    codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
    if "@Eoingtilab" not in codeowners:
        fail("EOINGTI Lab CODEOWNERS entry is missing")

    quality = (ROOT / ".github/workflows/quality-gate.yml").read_text(encoding="utf-8")
    for token in [
        "quality_contract_test.py",
        "wordpress/plugin-check-action@v1",
        "cache-dependency-path: requirements-dev.txt",
        "nalapps-paid-api",
    ]:
        if token not in quality:
            fail(f"primary quality gate missing contract: {token}")

    free_plugin_check = (ROOT / ".github/workflows/plugin-check-free.yml").read_text(encoding="utf-8")
    if "nalapps-free-basic" not in free_plugin_check or "wordpress/plugin-check-action@v1" not in free_plugin_check:
        fail("isolated free-plugin official Plugin Check is missing")

    tag_workflow = (ROOT / ".github/workflows/tag-version.yml").read_text(encoding="utf-8")
    for token in [
        "Create immutable standard tag after validation",
        "quality_contract_test.py",
        "cache-dependency-path: requirements-dev.txt",
        "nalapps-paid-api",
    ]:
        if token not in tag_workflow:
            fail(f"standard tag workflow missing gate contract: {token}")

    print(f"PASS standard_audit version={version} required_files={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
