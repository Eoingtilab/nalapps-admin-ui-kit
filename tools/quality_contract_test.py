#!/usr/bin/env python3
"""High-value regression tests for NalApps standard contracts.

These tests complement scaffold smoke tests with boundary/negative cases inspired by
ISO/IEC/IEEE 29119 test design and ISO/IEC 25010 product quality evaluation.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from nalapps_plugin import create_project
from scaffold_plugin import ROOT
from scaffold_product import product_scaffold
from validate_profile import validate_profile

TMP = ROOT / "build" / "quality-contract"


def write_profile(name: str, data: dict) -> Path:
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / f"{name}.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def expect_profile_fail(name: str, data: dict) -> None:
    path = write_profile(name, data)
    try:
        validate_profile(path)
    except SystemExit as exc:
        if exc.code != 2:
            raise AssertionError(f"{name}: expected validation exit 2, got {exc.code}") from exc
        return
    raise AssertionError(f"{name}: invalid profile unexpectedly passed")


def base_profile() -> dict:
    return {
        "plugin_name": "Contract Fixture",
        "slug": "contract-fixture",
        "description": "Synthetic contract fixture.",
        "plugin_version": "1.0.0",
        "product_type": "free",
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
    }


def main() -> int:
    shutil.rmtree(TMP, ignore_errors=True)

    legacy_free = base_profile()
    normalized = validate_profile(write_profile("legacy-free", legacy_free))
    if normalized.get("license_mode") != "free_download" or normalized.get("license_required") is not False:
        raise AssertionError("Legacy free profile must normalize to free_download / license_required=false")

    explicit_free = dict(legacy_free)
    explicit_free.update({"license_mode": "free_download", "license_required": False})
    validate_profile(write_profile("valid-free-download", explicit_free))

    free_download_requires_key = dict(explicit_free)
    free_download_requires_key["license_required"] = True
    expect_profile_fail("free-download-license-required-true", free_download_requires_key)

    free_registered_missing = dict(legacy_free)
    free_registered_missing.update(
        {
            "license_mode": "free_registered",
            "license_required": True,
            "external_api": True,
        }
    )
    expect_profile_fail("free-registered-missing-edd-metadata", free_registered_missing)

    free_registered_false = dict(free_registered_missing)
    free_registered_false["license_required"] = False
    expect_profile_fail("free-registered-license-required-false", free_registered_false)

    unknown = dict(explicit_free)
    unknown["unexpected_field"] = True
    expect_profile_fail("unknown-field", unknown)

    bad_slug = dict(explicit_free)
    bad_slug["slug"] = "Bad Slug"
    expect_profile_fail("bad-slug", bad_slug)

    telemetry = dict(explicit_free)
    telemetry["telemetry"] = "opt_in"
    expect_profile_fail("telemetry-without-external-api", telemetry)

    paid_missing = dict(legacy_free)
    paid_missing.update(
        {
            "product_type": "edd_paid",
            "license_mode": "paid",
            "license_required": True,
            "external_api": True,
        }
    )
    expect_profile_fail("paid-missing-edd-metadata", paid_missing)

    paid_as_free = dict(paid_missing)
    paid_as_free["product_type"] = "free"
    paid_as_free["edd_download_id"] = 123
    paid_as_free["edd_store_url"] = "https://example.com/"
    expect_profile_fail("free-product-cannot-use-paid-license-mode", paid_as_free)

    github_missing_repo = dict(explicit_free)
    github_missing_repo["update_source"] = "github_releases"
    expect_profile_fail("github-update-source-missing-repository", github_missing_repo)

    sensitive_backup = dict(explicit_free)
    sensitive_backup["data_contract"] = {"options": ["contract_fixture_api_key"]}
    expect_profile_fail("sensitive-backup-option", sensitive_backup)

    paid = dict(legacy_free)
    paid.update(
        {
            "plugin_name": "Hyphenated Paid Fixture",
            "slug": "hyphenated-paid-fixture",
            "product_type": "edd_paid",
            "license_mode": "paid",
            "license_required": True,
            "external_api": True,
            "edd_download_id": 123,
            "edd_store_url": "https://example.com/",
            "update_uri": "https://example.com/",
        }
    )
    paid_path = write_profile("paid", paid)
    paid_target = product_scaffold(paid_path, TMP / "paid-out", clean=True)
    paid_license_text = (paid_target / "includes/class-license.php").read_text(encoding="utf-8")
    updater_text = (paid_target / "includes/class-update-manager.php").read_text(encoding="utf-8")
    main_text = (paid_target / f"{paid['slug']}.php").read_text(encoding="utf-8")
    composer = json.loads((paid_target / "composer.json").read_text(encoding="utf-8"))

    if "hyphenated-paid-fixture_license_key" not in paid_license_text:
        raise AssertionError("EDD SDK license-key option must preserve canonical hyphenated slug")
    if "hyphenated_paid_fixture_license_key" in paid_license_text:
        raise AssertionError("Legacy underscore-transformed EDD option name reintroduced")
    if not re.search(r"['\"]id['\"]\s*=>\s*['\"]hyphenated-paid-fixture['\"]", main_text):
        raise AssertionError("EDD SDK registry id does not match canonical slug")
    if re.search(r"if\s*\([^\n]*(?:license|serial)[^\n]*\)\s*\{?\s*return\b", main_text, re.IGNORECASE):
        raise AssertionError("Public plugin runtime must not return early based on license/serial state")
    if "easy-digital-downloads/edd-sl-sdk" not in composer.get("require", {}):
        raise AssertionError("EDD paid scaffold omitted runtime SDK dependency")
    if "package_url" not in updater_text or "$info['package']" not in updater_text:
        raise AssertionError("EDD hybrid updater must consume the canonical package field")
    if "elseif ( ! empty( $info['download_link'] ) )" not in updater_text:
        raise AssertionError("EDD hybrid updater must retain download_link only as compatibility fallback")
    if "'package'     => $this->package_url( $info )" not in updater_text:
        raise AssertionError("WordPress update transient must receive the executable package URL")

    registered = dict(legacy_free)
    registered.update(
        {
            "plugin_name": "Registered Free Fixture",
            "slug": "registered-free-fixture",
            "license_mode": "free_registered",
            "license_required": True,
            "external_api": True,
            "edd_download_id": 456,
            "edd_store_url": "https://example.com/",
            "update_uri": "https://example.com/",
        }
    )
    registered_path = write_profile("registered-free", registered)
    registered_target = create_project(registered_path, TMP / "registered-out", clean=True)
    registered_license = (registered_target / "includes/class-license.php").read_text(encoding="utf-8")
    registered_main = (registered_target / "registered-free-fixture.php").read_text(encoding="utf-8")
    registered_manifest = json.loads((registered_target / "nalapps-standard-manifest.json").read_text(encoding="utf-8"))
    for token in ("무료 (라이선스 등록)", "Serial key", "activate_license", "deactivate_license"):
        if token not in registered_license:
            raise AssertionError(f"Registered-free UI missing: {token}")
    for token in ("class-edd-config.php", "edd_sl_sdk_registry", "Update_Manager"):
        if token not in registered_main:
            raise AssertionError(f"Registered-free runtime missing: {token}")
    if "free_registered_license" not in registered_manifest["required_modules"]:
        raise AssertionError("Registered-free manifest module is missing")

    print(
        "PASS quality_contract_test cases=12 edd_regression=3 privacy_regression=1 "
        "license_modes=paid,free_registered,free_download legacy_inference=1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
