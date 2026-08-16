#!/usr/bin/env python3
"""Canonical CLI for creating and validating NalApps WordPress plugin projects."""
from __future__ import annotations

import argparse
from pathlib import Path

from scaffold_free_license import add_free_license_runtime
from scaffold_maintenance import add_maintenance_runtime
from scaffold_plugin import ROOT, write_file
from scaffold_product import product_scaffold
from validate_profile import validate_profile


def plugin_check_workflow() -> str:
    return '''name: WordPress Plugin Check

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  plugin-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Official WordPress Plugin Check
        uses: wordpress/plugin-check-action@v1
        with:
          build-dir: './'
          categories: |
            security
            performance
            accessibility
'''


def dependabot_config() -> str:
    return '''version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
  - package-ecosystem: composer
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
'''


def bug_report_template() -> str:
    return '''name: Bug report
description: Report a reproducible problem.
title: "[Bug] "
labels: [bug]
body:
  - type: markdown
    attributes:
      value: Never include passwords, license keys, API keys, tokens, cookies, customer data, or private logs.
  - type: input
    id: plugin-version
    attributes:
      label: Plugin version
    validations:
      required: true
  - type: input
    id: wp-version
    attributes:
      label: WordPress version
    validations:
      required: true
  - type: input
    id: php-version
    attributes:
      label: PHP version
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Reproduction steps
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
    validations:
      required: true
'''


def feature_request_template() -> str:
    return '''name: Feature request
description: Suggest a product improvement.
title: "[Feature] "
labels: [enhancement]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem or use case
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed behavior
    validations:
      required: true
  - type: textarea
    id: compatibility
    attributes:
      label: Compatibility or migration considerations
'''


def pull_request_template() -> str:
    return '''## Summary

Describe the change and why it is needed.

## NalApps Standard Gate

- [ ] Product profile still matches the implementation.
- [ ] Security/capability/nonce implications were reviewed.
- [ ] Existing data and upgrade compatibility were considered.
- [ ] Rollback/data backup/uninstall behavior was considered.
- [ ] Tests or reproducible verification were added/updated.
- [ ] Documentation/changelog was updated when behavior changed.
- [ ] No secret, credential, customer data, private dump, or production backup is included.
- [ ] Version was not bumped early; release version bump remains the final release commit.
'''


def tests_contract(profile: dict) -> str:
    conditional = []
    if profile.get("database"):
        conditional.append("- Database migration idempotency and upgrade fixture tests.")
    if profile.get("cron"):
        conditional.append("- Cron duplicate scheduling and deactivation cleanup tests.")
    if profile.get("rest_api"):
        conditional.append("- REST unauthorized/authorized permission tests and schema validation tests.")
    if profile.get("file_upload"):
        conditional.append("- Upload capability, extension/MIME, size, nonce and rejected-file tests.")
    if profile.get("external_api"):
        conditional.append("- Remote timeout/error/cache/redaction tests without live production credentials.")
    if profile.get("product_type") == "free":
        conditional.append("- Free-license UI must show Free/무료 and Active/활성 without a serial-key or activation flow.")
        conditional.append("- Free-license runtime must always report is_valid()=true and must not depend on a remote licensing server.")
    if profile.get("product_type") == "edd_paid":
        conditional.append("- EDD license state fixtures plus WordPress Plugins/internal updater detection tests.")
        conditional.append("- Human E2E for real activation/deactivation and version upgrade before release.")
    extra = "\n".join(conditional) if conditional else "- No additional profile-specific suite is required until product behavior is added."
    return f'''# Product Test Contract

Generated from `plugin-profile.json`. Generic static checks do not replace product behavior tests.

## Always required

- Activation, deactivation and reactivation smoke test.
- Capability/nonce failure tests for every mutation.
- Existing settings/data preservation during supported upgrades.
- Pre-update code backup and rollback package validation.
- Data export/import round-trip validation for every declared data contract.
- Uninstall policy tests for both preserve and explicit delete-all paths.
- System information redaction check: no credentials, license keys, absolute secrets or customer data.
- Admin/front-end regression tests for product-critical behavior.
- Public repository secret/customer-data regression check.
- Release package root and runtime dependency verification.

## Profile-specific

{extra}

## Human release gate

The final supported old-version → new-version upgrade path must be exercised on a disposable WordPress test site before a production release. Code rollback and data restore must be tested separately when migrations or schema changes are involved.
'''


def distignore() -> str:
    return '''/.git
/.github
/build
/tests
/.env
/.env.*
/phpcs.xml.dist
/*.zip
/*.sql
/*.dump
/*.bak
'''


def enrich_project(target: Path, profile: dict) -> None:
    write_file(target, ".github/workflows/plugin-check.yml", plugin_check_workflow())
    write_file(target, ".github/dependabot.yml", dependabot_config())
    write_file(target, ".github/CODEOWNERS", "* @Eoingtilab\n")
    write_file(target, ".github/ISSUE_TEMPLATE/bug_report.yml", bug_report_template())
    write_file(target, ".github/ISSUE_TEMPLATE/feature_request.yml", feature_request_template())
    write_file(target, ".github/pull_request_template.md", pull_request_template())
    write_file(target, "tests/README.md", tests_contract(profile))
    write_file(target, ".distignore", distignore())


def create_project(profile_path: Path, output: Path, clean: bool = False) -> Path:
    profile = validate_profile(profile_path)
    target = product_scaffold(profile_path, output, clean=clean)
    add_free_license_runtime(target, profile)
    add_maintenance_runtime(target, profile)
    enrich_project(target, profile)
    return target


def command_create(args: argparse.Namespace) -> int:
    target = create_project(args.profile, args.output, args.clean)
    print(f"PASS nalapps_create={target}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    profile = validate_profile(args.profile)
    print(f"PASS nalapps_validate={profile['slug']}")
    return 0


def command_version(_: argparse.Namespace) -> int:
    print((ROOT / "VERSION").read_text(encoding="utf-8").strip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a complete NalApps WordPress plugin project.")
    create.add_argument("--profile", required=True, type=Path)
    create.add_argument("--output", default=Path("build/scaffold"), type=Path)
    create.add_argument("--clean", action="store_true")
    create.set_defaults(func=command_create)

    validate = subparsers.add_parser("validate", help="Validate a plugin profile against the canonical schema.")
    validate.add_argument("--profile", required=True, type=Path)
    validate.set_defaults(func=command_validate)

    version = subparsers.add_parser("version", help="Print the current NalApps standard version.")
    version.set_defaults(func=command_version)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
