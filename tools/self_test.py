#!/usr/bin/env python3
"""Generate representative plugins and assert the complete standard is self-consistent."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from scaffold_complete import complete_scaffold
from scaffold_plugin import ROOT

BUILD = ROOT / "build" / "self-test"
PROFILES = ROOT / "build" / "self-test-profiles"

CASES = {
    "free-basic": {
        "plugin_name": "NalApps Free Basic",
        "slug": "nalapps-free-basic",
        "description": "Synthetic free plugin used to validate the standard.",
        "plugin_version": "0.1.0",
        "product_type": "free",
        "frontend": True,
        "database": False,
        "cron": False,
        "rest_api": False,
        "external_api": False,
        "file_upload": False,
        "multisite": False,
        "telemetry": "off",
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
        "requires_plugins": [],
    },
}

EXPECTED = {
    "free-basic": [],
    "paid-api": ["includes/class-http-client.php", "includes/class-edd-config.php"],
    "full-capability": [
        "includes/class-http-client.php",
        "includes/class-db-migrator.php",
        "includes/class-cron-manager.php",
        "includes/class-rest-controller.php",
        "includes/class-upload-guard.php",
    ],
}


def assert_no_placeholders(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".php", ".md", ".txt", ".json", ".yml", ".xml"}:
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
        target = complete_scaffold(profile_path, BUILD, clean=True)

        required = [
            target / f"{profile['slug']}.php",
            target / "plugin-profile.json",
            target / "nalapps-standard-manifest.json",
            target / "README.md",
            target / "readme.txt",
            target / "SECURITY.md",
            target / "composer.json",
            target / "phpcs.xml.dist",
            target / "docs/RELEASE-ACCEPTANCE.md",
            target / ".github/workflows/quality.yml",
            target / ".github/workflows/release.yml",
        ]
        for path in required:
            if not path.is_file():
                raise AssertionError(f"Missing scaffold output: {path}")
        for relative in EXPECTED[name]:
            if not (target / relative).is_file():
                raise AssertionError(f"Missing conditional module: {relative}")

        manifest = json.loads((target / "nalapps-standard-manifest.json").read_text(encoding="utf-8"))
        if manifest["standard_version"] != standard_version:
            raise AssertionError(f"Standard version mismatch for {name}")
        if profile["product_type"] == "free" and "edd_license" in manifest["required_modules"]:
            raise AssertionError("Free profile incorrectly selected EDD module")
        if profile["product_type"] == "edd_paid" and "hybrid_updater" not in manifest["required_modules"]:
            raise AssertionError("Paid profile did not select hybrid updater")
        assert_no_placeholders(target)

    print(f"PASS self_test cases={len(CASES)} standard={standard_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
