#!/usr/bin/env python3
"""Generate representative plugins and assert the complete standard is self-consistent."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from nalapps_plugin import create_project
from scaffold_plugin import ROOT
from scaffold_product import EDD_SDK_PACKAGE, EDD_SDK_VERSION

BUILD = ROOT / "build" / "self-test"
PROFILES = ROOT / "build" / "self-test-profiles"

CASES = {
    "free-basic": {
        "plugin_name": "NalApps Free Basic",
        "slug": "nalapps-free-basic",
        "description": "Synthetic free plugin used to validate the standard.",
        "plugin_version": "0.1.0",
        "product_type": "free",
        "license_required": False,
        "frontend": True,
        "database": False,
        "cron": False,
        "rest_api": False,
        "external_api": False,
        "file_upload": False,
        "multisite": False,
        "telemetry": "off",
        "release_mode": "manual",
        "uninstall_policy": "preserve",
        "requires_plugins": [],
    },
    "paid-api": {
        "plugin_name": "NalApps Paid API",
        "slug": "nalapps-paid-api",
        "description": "Synthetic paid plugin used to validate EDD and remote-service selection.",
        "plugin_version": "0.1.0",
        "product_type": "edd_paid",
        "frontend": True,
        "database": False,
        "cron": False,
        "rest_api": False,
        "external_api": True,
        "file_upload": False,
        "multisite": False,
        "telemetry": "off",
        "release_mode": "manual",
        "uninstall_policy": "preserve",
        "edd_download_id": 999999,
        "edd_store_url": "https://example.com/",
        "update_uri": "https://example.com/",
        "requires_plugins": [],
    },
    "full-capability": {
        "plugin_name": "NalApps Full Capability",
        "slug": "nalapps-full-capability",
        "description": "Synthetic all-capability plugin used to validate conditional module generation.",
        "plugin_version": "0.1.0",
        "product_type": "private",
        "frontend": True,
        "database": True,
        "cron": True,
        "rest_api": True,
        "external_api": True,
        "file_upload": True,
        "multisite": True,
        "telemetry": "off",
        "release_mode": "manual",
        "uninstall_policy": "preserve",
        "data_contract": {
            "options": ["nalapps_full_capability_settings"],
            "site_options": ["nalapps_full_capability_network"],
            "post_types": ["nalapps_record"],
            "custom_tables": ["nalapps_records"],
        },
        "requires_plugins": [],
    },
}

EXPECTED = {
    "free-basic": [
        "includes/class-license.php",
    ],
    "paid-api": [
        "includes/class-http-client.php",
        "includes/class-edd-config.php",
        "includes/class-license.php",
        "includes/class-update-manager.php",
    ],
    "full-capability": [
        "includes/class-http-client.php",
        "includes/class-db-migrator.php",
        "includes/class-cron-manager.php",
        "includes/class-rest-controller.php",
        "includes/class-upload-guard.php",
    ],
}

COMMON_MAINTENANCE = [
    "includes/class-data-portability.php",
    "includes/class-rollback-manager.php",
    "includes/class-system-info.php",
    "includes/class-maintenance-page.php",
    "uninstall.php",
]


def assert_no_placeholders(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".php", ".md", ".txt", ".json", ".yml", ".yaml", ".xml"}:
            continue
        text = path.read_text(encoding="utf-8")
        if "YOUR_API_KEY" in text:
            raise AssertionError(f"Unresolved placeholder in {path}")


def main() -> int:
    shutil.rmtree(BUILD, ignore_errors=True)
    shutil.rmtree(PROFILES, ignore_errors=True)
    BUILD.mkdir(parents=True)
    PROFILES.mkdir(parents=True)
    standard_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

    for name, profile in CASES.items():
        profile_path = PROFILES / f"{name}.json"
        profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        target = create_project(profile_path, BUILD, clean=True)

        required = [
            target / f"{profile['slug']}.php",
            target / "includes/class-plugin.php",
            target / "includes/class-system-status.php",
            target / "plugin-profile.json",
            target / "nalapps-standard-manifest.json",
            target / "README.md",
            target / "readme.txt",
            target / "SECURITY.md",
            target / "composer.json",
            target / "phpcs.xml.dist",
            target / "docs/RELEASE-ACCEPTANCE.md",
            target / "tests/README.md",
            target / ".distignore",
            target / ".github/workflows/quality.yml",
            target / ".github/workflows/release.yml",
            target / ".github/workflows/plugin-check.yml",
            target / ".github/dependabot.yml",
            target / ".github/CODEOWNERS",
            target / ".github/ISSUE_TEMPLATE/bug_report.yml",
            target / ".github/ISSUE_TEMPLATE/feature_request.yml",
            target / ".github/pull_request_template.md",
        ]
        required += [target / relative for relative in COMMON_MAINTENANCE]
        for path in required:
            if not path.is_file():
                raise AssertionError(f"Missing scaffold output: {path}")
        for relative in EXPECTED[name]:
            if not (target / relative).is_file():
                raise AssertionError(f"Missing conditional module: {relative}")

        manifest = json.loads((target / "nalapps-standard-manifest.json").read_text(encoding="utf-8"))
        if manifest["standard_version"] != standard_version:
            raise AssertionError(f"Standard version mismatch for {name}")
        for module in ("rollback", "data_portability", "safe_uninstall", "system_info", "refined_admin_ui"):
            if module not in manifest["required_modules"]:
                raise AssertionError(f"Common maintenance module missing: {module}")
        if profile["product_type"] == "free":
            if "edd_license" in manifest["required_modules"]:
                raise AssertionError("Free profile incorrectly selected EDD module")
            for module in ("free_license_display", "free_license_always_active"):
                if module not in manifest["required_modules"]:
                    raise AssertionError(f"Free profile missing required module: {module}")
            for gate in ("free_license_ui", "free_license_always_active"):
                if gate not in manifest["release_gates"]:
                    raise AssertionError(f"Free profile missing release gate: {gate}")
            free_license_text = (target / "includes/class-license.php").read_text(encoding="utf-8")
            for token in ("return 'free';", "return true;", "라이선스: 무료", "현재 상태: 활성"):
                if token not in free_license_text:
                    raise AssertionError(f"Free license runtime missing: {token}")
            for forbidden in ("activate_license", "deactivate_license", "license_key", "Serial key"):
                if forbidden in free_license_text:
                    raise AssertionError(f"Free license runtime must not include activation flow: {forbidden}")
            main_text = (target / f"{profile['slug']}.php").read_text(encoding="utf-8")
            if "canonical free-license runtime" not in main_text or "new \\EOINGTI\\Plugins\\NalappsFreeBasic\\License();" not in main_text:
                raise AssertionError("Free license runtime was not wired into the generated plugin")
        if profile["product_type"] == "edd_paid":
            for module in ("hybrid_updater", "product_native_license_ui"):
                if module not in manifest["required_modules"]:
                    raise AssertionError(f"Paid profile missing required module: {module}")
            if "license_activation_ui" not in manifest["release_gates"]:
                raise AssertionError("Paid profile missing license activation UI release gate")
            composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))
            if composer.get("require", {}).get(EDD_SDK_PACKAGE) != EDD_SDK_VERSION:
                raise AssertionError("Paid scaffold did not include the EDD SDK runtime dependency")
            main_text = (target / f"{profile['slug']}.php").read_text(encoding="utf-8")
            if "edd_sl_sdk_registry" not in main_text or "Update_Manager" not in main_text or "new \\EOINGTI\\Plugins\\NalappsPaidApi\\License();" not in main_text:
                raise AssertionError("Paid scaffold did not wire SDK, updater and product-native License runtime")
            license_text = (target / "includes/class-license.php").read_text(encoding="utf-8")
            for token in ("Serial key", "activate_license", "check_license", "deactivate_license", "admin_post_nalapps_paid_api_activate_license"):
                if token not in license_text:
                    raise AssertionError(f"Paid product-native license UI missing: {token}")
            updater_text = (target / "includes/class-update-manager.php").read_text(encoding="utf-8")
            for token in ("Update now", "install_update", "Plugin_Upgrader", "package_url"):
                if token not in updater_text:
                    raise AssertionError(f"Paid executable updater contract missing: {token}")

        main_text = (target / f"{profile['slug']}.php").read_text(encoding="utf-8")
        for class_name in ("Data_Portability", "Rollback_Manager", "System_Info", "Maintenance_Page"):
            if class_name not in main_text:
                raise AssertionError(f"Common maintenance runtime not wired: {class_name}")
        uninstall_text = (target / "uninstall.php").read_text(encoding="utf-8")
        if "delete_all" not in uninstall_text or "preserve" not in uninstall_text:
            raise AssertionError("Uninstall preserve/delete-all gate is missing")
        portability_text = (target / "includes/class-data-portability.php").read_text(encoding="utf-8")
        if "nalapps-data-backup-v1" not in portability_text or "pre-import" not in portability_text:
            raise AssertionError("Data portability/snapshot contract is missing")
        rollback_text = (target / "includes/class-rollback-manager.php").read_text(encoding="utf-8")
        for token in (
            "upgrader_pre_install",
            "overwrite_package",
            "list_release_versions",
            "release_rollback",
            "browser_download_url",
            "prerelease",
        ):
            if token not in rollback_text:
                raise AssertionError(f"Pre-update/verified rollback contract is missing: {token}")
        system_info_text = (target / "includes/class-system-info.php").read_text(encoding="utf-8")
        if "debug_information" not in system_info_text:
            raise AssertionError("Site Health system information integration is missing")
        maintenance_text = (target / "includes/class-maintenance-page.php").read_text(encoding="utf-8")
        for token in (
            "Download data backup",
            "Restore backup",
            "Version rollback",
            "Rollback to selected version",
            "Local safety backups",
            "Delete all plugin data on uninstall",
        ):
            if token not in maintenance_text:
                raise AssertionError(f"Visible maintenance UI missing: {token}")

        if name == "full-capability":
            if "nalapps_full_capability_settings" not in portability_text or "nalapps_record" not in portability_text:
                raise AssertionError("Declared data contract was not embedded into portability runtime")
            if "nalapps_records" not in uninstall_text:
                raise AssertionError("Declared custom table was not embedded into delete-all runtime")

        release_workflow = (target / ".github/workflows/release.yml").read_text(encoding="utf-8")
        if profile.get("release_mode", "manual") == "manual" and "workflow_dispatch" not in release_workflow:
            raise AssertionError("Manual release mode lost workflow_dispatch")
        plugin_check = (target / ".github/workflows/plugin-check.yml").read_text(encoding="utf-8")
        if "wordpress/plugin-check-action@v1" not in plugin_check:
            raise AssertionError("Official WordPress Plugin Check action is missing")
        if "@Eoingtilab" not in (target / ".github/CODEOWNERS").read_text(encoding="utf-8"):
            raise AssertionError("EOINGTI Lab CODEOWNERS policy is missing")
        assert_no_placeholders(target)

    print(f"PASS self_test cases={len(CASES)} standard={standard_version} maintenance=6 paid_license_ui=1 free_license_ui=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
