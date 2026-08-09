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

    valid = base_profile()
    validate_profile(write_profile("valid-free", valid))

    unknown = dict(valid)
    unknown["unexpected_field"] = True
    expect_profile_fail("unknown-field", unknown)

    bad_slug = dict(valid)
    bad_slug["slug"] = "Bad Slug"
    expect_profile_fail("bad-slug", bad_slug)

    telemetry = dict(valid)
    telemetry["telemetry"] = "opt_in"
    expect_profile_fail("telemetry-without-external-api", telemetry)

    paid_missing = dict(valid)
    paid_missing["product_type"] = "edd_paid"
    paid_missing["external_api"] = True
    expect_profile_fail("paid-missing-edd-metadata", paid_missing)

    sensitive_backup = dict(valid)
    sensitive_backup["data_contract"] = {"options": ["contract_fixture_api_key"]}
    expect_profile_fail("sensitive-backup-option", sensitive_backup)

    paid = dict(valid)
    paid.update(
        {
            "plugin_name": "Hyphenated Paid Fixture",
            "slug": "hyphenated-paid-fixture",
            "product_type": "edd_paid",
            "external_api": True,
            "edd_download_id": 123,
            "edd_store_url": "https://example.com/",
            "update_uri": "https://example.com/",
        }
    )
    paid_path = write_profile("paid", paid)
    target = product_scaffold(paid_path, TMP / "out", clean=True)
    license_text = (target / "includes/class-license.php").read_text(encoding="utf-8")
    main_text = (target / f"{paid['slug']}.php").read_text(encoding="utf-8")
    composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))

    if "hyphenated-paid-fixture_license_key" not in license_text:
        raise AssertionError("EDD SDK license-key option must preserve canonical hyphenated slug")
    if "hyphenated_paid_fixture_license_key" in license_text:
        raise AssertionError("Legacy underscore-transformed EDD option name reintroduced")
    if not re.search(r"['\"]id['\"]\s*=>\s*['\"]hyphenated-paid-fixture['\"]", main_text):
        raise AssertionError("EDD SDK registry id does not match canonical slug")
    if "easy-digital-downloads/edd-sl-sdk" not in composer.get("require", {}):
        raise AssertionError("EDD paid scaffold omitted runtime SDK dependency")
    if not (target / "includes/class-update-manager.php").is_file():
        raise AssertionError("EDD paid scaffold omitted hybrid updater")

    print("PASS quality_contract_test cases=7 edd_regression=1 privacy_regression=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
