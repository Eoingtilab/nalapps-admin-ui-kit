#!/usr/bin/env python3
"""Fail when the standard's canonical files or cross-references drift."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md", "VERSION", "LICENSE", "SECURITY.md", "CONTRIBUTING.md",
    "profiles/company-profile.json", "profiles/plugin-profile.schema.json",
    "profiles/example-free.plugin-profile.json", "profiles/example-edd-paid.plugin-profile.json",
    "docs/MASTER-STANDARD.md", "docs/WORDPRESS-PLUGIN-STANDARD.md",
    "docs/ENGINEERING-CONTRACTS-V3.md", "docs/AUTOMATION-AND-SCAFFOLDING.md",
    "docs/ROLLBACK-BACKUP-DATA-LIFECYCLE.md", "docs/PUBLIC-REPOSITORY-SAFETY.md",
    "docs/EDD-LICENSE-AND-UPDATES.md", "docs/ACCEPTANCE-CHECKLIST.md",
    "docs/ISO-29119-25010-TEST-PLAN.md", "tools/validate_profile.py",
    "tools/scaffold_plugin.py", "tools/scaffold_complete.py", "tools/scaffold_product.py",
    "tools/scaffold_maintenance.py", "tools/maintenance_data.py", "tools/maintenance_license.py",
    "tools/maintenance_rollback.py", "tools/maintenance_system.py", "tools/maintenance_uninstall.py",
    "tools/nalapps_plugin.py", "tools/self_test.py", "tools/quality_contract_test.py", "tools/standard_audit.py",
    "tools/public_repo_guard.sh", "tools/release_manifest.py", "requirements-dev.txt",
    "composer.json", "phpcs.xml.dist", ".github/workflows/quality-gate.yml",
    ".github/workflows/plugin-check-free.yml", ".github/workflows/tag-version.yml",
    ".github/dependabot.yml", ".github/CODEOWNERS",
    "assets/css/nalapps-admin-ui.css", "assets/css/nalapps-admin-typography.css",
    "wordpress/class-nalapps-admin-ui-adapter.php",
    "wordpress/edd/github-actions-release-template.yml",
]


def fail(message: str) -> None:
    raise SystemExit(f"AUDIT_FAIL {message}")


def require_tokens(text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        if token not in text:
            fail(f"{label} missing contract: {token}")


def main() -> int:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"missing {relative}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?", version):
        fail("invalid VERSION")

    company = json.loads((ROOT / "profiles/company-profile.json").read_text(encoding="utf-8"))
    expected = {
        "developer_name_en": "EOINGTI Lab", "author": "EOINGTI Lab",
        "author_uri": "https://eoingti.com/", "github_org": "Eoingtilab",
        "telemetry_default": "off", "uninstall_data_policy_default": "preserve",
    }
    for key, value in expected.items():
        if company.get(key) != value:
            fail(f"company profile drift: {key}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require_tokens(
        readme,
        [
            "Eoingtilab/nalapps-wordpress-plugin-standard", "https://eoingti.com/", "Plugin Profile",
            "Public Repository Safety", "Testing / CI / Release", "EDD Software Licensing SDK",
            "Rollback / Backup / Data Lifecycle",
        ],
        "README",
    )

    schema = json.loads((ROOT / "profiles/plugin-profile.schema.json").read_text(encoding="utf-8"))
    if schema.get("additionalProperties") is not False:
        fail("plugin profile schema must fail closed on unknown fields")
    for key in ("release_mode", "uninstall_policy", "data_contract"):
        if key not in schema.get("properties", {}):
            fail(f"plugin profile schema must define {key}")
    if not any(item.get("if", {}).get("properties", {}).get("product_type", {}).get("const") == "edd_paid" for item in schema.get("allOf", [])):
        fail("plugin profile schema must require EDD fields for paid products")

    product_scaffold = (ROOT / "tools/scaffold_product.py").read_text(encoding="utf-8")
    require_tokens(
        product_scaffold,
        [
            "easy-digital-downloads/edd-sl-sdk", "edd_sl_sdk_registry", "class-license.php",
            "class-update-manager.php", "pre_set_site_transient_update_plugins", "install_update",
            "Plugin_Upgrader", "Update now", "package_url",
        ],
        "product scaffold executable EDD updater",
    )

    maintenance = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            "tools/scaffold_maintenance.py", "tools/maintenance_data.py", "tools/maintenance_license.py",
            "tools/maintenance_rollback.py", "tools/maintenance_system.py", "tools/maintenance_uninstall.py",
        ]
    )
    require_tokens(
        maintenance,
        [
            "upgrader_pre_install", "overwrite_package", "nalapps-data-backup-v1", "debug_information",
            "delete_all", "class-data-portability.php", "class-rollback-manager.php",
            "nalapps-switch", "nalapps-admin-ui.css", "refined_admin_ui",
            "product_native_license_ui", "license_activation_ui", "activate_license",
            "check_license", "deactivate_license", "Serial key",
            "list_release_versions", "release_rollback", "RELEASES_API",
            "browser_download_url", "prerelease", "Rollback to selected version",
            "Local safety backups",
        ],
        "maintenance scaffold",
    )

    rollback_doc = (ROOT / "docs/ROLLBACK-BACKUP-DATA-LIFECYCLE.md").read_text(encoding="utf-8")
    require_tokens(
        rollback_doc,
        [
            "Verified Release Version Rollback", "Release Asset", "Source code", "N → N-1",
            "Update Center contract", "지금 업데이트", "로컬 안전 백업",
        ],
        "rollback lifecycle",
    )

    acceptance = (ROOT / "docs/ACCEPTANCE-CHECKLIST.md").read_text(encoding="utf-8")
    require_tokens(
        acceptance,
        [
            "N →", "실제 버전 롤백", "Update Center", "즉시 업데이트 버튼",
            "list_release_versions", "release_rollback", "Source Code archive",
        ],
        "acceptance gate",
    )

    release_tokens = [
        "Existing verified release is immutable",
        "Pin recovery build to existing tag",
        "Create immutable tag after successful build validation",
        "Create release or backfill missing assets",
        "sha256sum",
        "unzip -Z1",
        "gh release upload",
        "needs_assets",
    ]
    release_template = (ROOT / "wordpress/edd/github-actions-release-template.yml").read_text(encoding="utf-8")
    require_tokens(release_template, release_tokens, "EDD release template immutable/recovery")
    if "--clobber" in release_template:
        fail("EDD release template must never overwrite an existing release asset")

    complete_scaffold = (ROOT / "tools/scaffold_complete.py").read_text(encoding="utf-8")
    require_tokens(complete_scaffold, release_tokens, "generated product release workflow immutable/recovery")
    require_tokens(
        complete_scaffold,
        ["Release Source Code", "bootstrap deadlock", "N-1 to N", "package/download URL"],
        "generated release acceptance commercial lifecycle",
    )
    if "--clobber" in complete_scaffold:
        fail("generated product release workflow must never overwrite an existing release asset")

    edd_docs = (ROOT / "docs/EDD-LICENSE-AND-UPDATES.md").read_text(encoding="utf-8")
    require_tokens(
        edd_docs,
        [
            "bootstrap deadlock", "Release Source Code", "N-1 → N", "missing-asset backfill",
            "Update File", "package", "download_link",
        ],
        "EDD commercial lifecycle",
    )

    ui_css = (ROOT / "assets/css/nalapps-admin-ui.css").read_text(encoding="utf-8")
    require_tokens(
        ui_css,
        ["nalapps-page-actions", "nalapps-switch", "nalapps-danger-zone", "nalapps-nav a.is-active:after"],
        "refined admin UI",
    )

    adapter = (ROOT / "wordpress/class-nalapps-admin-ui-adapter.php").read_text(encoding="utf-8")
    require_tokens(adapter, ["백업/복구", "시스템 정보", "nalapps-page-actions", "updates", "maintenance"], "admin UI adapter")

    contract_test = (ROOT / "tools/quality_contract_test.py").read_text(encoding="utf-8")
    require_tokens(
        contract_test,
        ["hyphenated-paid-fixture_license_key", "telemetry-without-external-api", "paid-missing-edd-metadata", "sensitive-backup-option"],
        "quality contract regression",
    )

    cli = (ROOT / "tools/nalapps_plugin.py").read_text(encoding="utf-8")
    require_tokens(
        cli,
        ["wordpress/plugin-check-action@v1", "dependabot.yml", "CODEOWNERS", "ISSUE_TEMPLATE", "tests/README.md", "add_maintenance_runtime"],
        "canonical CLI governance",
    )

    if "@Eoingtilab" not in (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8"):
        fail("EOINGTI Lab CODEOWNERS entry is missing")

    quality = (ROOT / ".github/workflows/quality-gate.yml").read_text(encoding="utf-8")
    require_tokens(
        quality,
        ["quality_contract_test.py", "wordpress/plugin-check-action@v1", "cache-dependency-path: requirements-dev.txt", "nalapps-paid-api"],
        "primary quality gate",
    )

    free_plugin_check = (ROOT / ".github/workflows/plugin-check-free.yml").read_text(encoding="utf-8")
    if "nalapps-free-basic" not in free_plugin_check or "wordpress/plugin-check-action@v1" not in free_plugin_check:
        fail("isolated free-plugin official Plugin Check is missing")

    tag_workflow = (ROOT / ".github/workflows/tag-version.yml").read_text(encoding="utf-8")
    require_tokens(
        tag_workflow,
        ["Create immutable standard tag after validation", "quality_contract_test.py", "cache-dependency-path: requirements-dev.txt", "nalapps-paid-api"],
        "standard tag workflow",
    )

    print(f"PASS standard_audit version={version} required_files={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
