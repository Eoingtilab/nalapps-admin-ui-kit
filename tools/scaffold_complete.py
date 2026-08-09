#!/usr/bin/env python3
"""Create a complete NalApps WordPress plugin project with enforced CI/release gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scaffold_plugin import scaffold, write_file
from validate_profile import validate_profile


def composer_json(profile: dict) -> str:
    package = f"eoingtilab/{profile['slug']}"
    data = {
        "name": package,
        "description": profile.get("description") or "NalApps WordPress plugin.",
        "type": "wordpress-plugin",
        "license": "GPL-2.0-or-later",
        "require-dev": {
            "dealerdirect/phpcodesniffer-composer-installer": "^1.0",
            "wp-coding-standards/wpcs": "^3.4",
        },
        "config": {
            "allow-plugins": {"dealerdirect/phpcodesniffer-composer-installer": True},
            "sort-packages": True,
        },
        "scripts": {
            "phpcs": "phpcs --standard=phpcs.xml.dist",
            "audit": "composer audit",
        },
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def phpcs_xml() -> str:
    return '''<?xml version="1.0"?>
<ruleset name="NalApps Plugin">
  <description>NalApps WordPress Coding Standards gate.</description>
  <file>.</file>
  <arg name="extensions" value="php" />
  <arg value="ps" />
  <exclude-pattern>*/vendor/*</exclude-pattern>
  <exclude-pattern>*/build/*</exclude-pattern>
  <rule ref="WordPress-Core">
    <exclude name="WordPress.WP.I18n" />
  </rule>
  <rule ref="WordPress-Extra">
    <exclude name="WordPress.WP.I18n" />
  </rule>
</ruleset>
'''


def quality_workflow(profile: dict) -> str:
    slug = profile["slug"]
    return f'''name: NalApps Plugin Quality Gate

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          tools: composer:v2
          coverage: none
      - name: Install quality dependencies
        run: composer update --no-interaction --prefer-dist --no-progress
      - name: Dependency security audit
        run: composer audit
      - name: PHP syntax
        run: find . -name '*.php' -not -path './vendor/*' -not -path './build/*' -print0 | xargs -0 -r -n1 php -l
      - name: WordPress Coding Standards
        run: vendor/bin/phpcs --standard=phpcs.xml.dist
      - name: Public repository safety
        shell: bash
        run: |
          set -euo pipefail
          if git ls-files | grep -E '(^|/)(\\.env|\\.env\\..+|id_rsa|id_ed25519|.*\\.pem|.*\\.p12|.*\\.pfx|.*\\.sql|.*\\.dump|.*\\.sqlite|.*\\.bak)$'; then exit 1; fi
          if git grep -nEI '(BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|ghp_[A-Za-z0-9]{{20,}}|github_pat_[A-Za-z0-9_]{{20,}}|AKIA[0-9A-Z]{{16}}|xox[baprs]-[A-Za-z0-9-]{{10,}})'; then exit 1; fi
      - name: Profile and version consistency
        shell: bash
        run: |
          set -euo pipefail
          python3 -m json.tool plugin-profile.json >/dev/null
          version="$(sed -n 's/^ \\* Version: \\(.*\\)$/\\1/p' {slug}.php | head -n1 | tr -d '\\r')"
          grep -q "Stable tag: $version" readme.txt
          grep -q '"slug": "{slug}"' plugin-profile.json
      - name: Package contract
        run: test -f '{slug}.php' && test -f README.md && test -f readme.txt && test -f SECURITY.md && test -f nalapps-standard-manifest.json

  php-matrix:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        php: ['7.4', '8.1', '8.3', '8.4', '8.5']
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: ${{{{ matrix.php }}}}
          coverage: none
      - run: find . -name '*.php' -not -path './vendor/*' -not -path './build/*' -print0 | xargs -0 -r -n1 php -l
'''


def release_workflow(profile: dict) -> str:
    slug = profile["slug"]
    name = profile["plugin_name"].replace('"', '')
    mode = profile.get("release_mode", "manual")
    if mode == "auto_on_version_bump":
        trigger = f'''on:
  push:
    branches: [main]
    paths:
      - '{slug}.php'
      - 'readme.txt'
  workflow_dispatch:
'''
    else:
        trigger = '''on:
  workflow_dispatch:
'''
    return f'''name: Validate and Build Plugin Release

{trigger}
permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Read version and immutable tag state
        id: version
        shell: bash
        run: |
          set -euo pipefail
          version="$(sed -n 's/^ \\* Version: \\(.*\\)$/\\1/p' {slug}.php | head -n1 | tr -d '\\r')"
          test -n "$version"
          tag="v$version"
          if git rev-parse "$tag" >/dev/null 2>&1; then is_new=false; else is_new=true; fi
          echo "version=$version" >> "$GITHUB_OUTPUT"
          echo "tag=$tag" >> "$GITHUB_OUTPUT"
          echo "is_new=$is_new" >> "$GITHUB_OUTPUT"
      - name: Existing release is immutable
        if: steps.version.outputs.is_new != 'true'
        run: echo "${{{{ steps.version.outputs.tag }}}} exists; no rebuild or asset overwrite is allowed."
      - uses: shivammathur/setup-php@v2
        if: steps.version.outputs.is_new == 'true'
        with:
          php-version: '8.3'
          tools: composer:v2
          coverage: none
      - name: Install and audit quality dependencies
        if: steps.version.outputs.is_new == 'true'
        run: |
          composer update --no-interaction --prefer-dist --no-progress
          composer audit
      - name: Validate source
        if: steps.version.outputs.is_new == 'true'
        shell: bash
        run: |
          set -euo pipefail
          find . -name '*.php' -not -path './vendor/*' -not -path './build/*' -print0 | xargs -0 -r -n1 php -l
          vendor/bin/phpcs --standard=phpcs.xml.dist
          version="${{{{ steps.version.outputs.version }}}}"
          grep -q "Stable tag: $version" readme.txt
          grep -q '"slug": "{slug}"' plugin-profile.json
      - name: Prepare production dependencies
        if: steps.version.outputs.is_new == 'true'
        shell: bash
        run: |
          set -euo pipefail
          runtime_count="$(php -r '$c=json_decode(file_get_contents("composer.json"), true); echo count($c["require"] ?? []);')"
          if [ "$runtime_count" -gt 0 ]; then
            composer install --no-dev --prefer-dist --optimize-autoloader --no-interaction --no-progress
          else
            rm -rf vendor
          fi
      - name: Build immutable distribution
        if: steps.version.outputs.is_new == 'true'
        shell: bash
        run: |
          set -euo pipefail
          version="${{{{ steps.version.outputs.version }}}}"
          rm -rf build
          mkdir -p build/{slug}
          rsync -a ./ build/{slug}/ \\
            --exclude '.git/' --exclude '.github/' --exclude 'build/' --exclude 'tests/' \\
            --exclude '*.zip' --exclude 'phpcs.xml.dist'
          test -f build/{slug}/{slug}.php
          cd build
          zip -qr "{slug}-$version.zip" {slug}
          test "$(unzip -Z1 "{slug}-$version.zip" | head -n1)" = "{slug}/"
          sha256sum "{slug}-$version.zip" > "{slug}-$version.zip.sha256"
      - name: Create tag after validation
        if: steps.version.outputs.is_new == 'true'
        env:
          TAG: ${{{{ steps.version.outputs.tag }}}}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git tag -a "$TAG" -m "{name} $TAG"
          git push origin "$TAG"
      - name: Create GitHub Release
        if: steps.version.outputs.is_new == 'true'
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        run: |
          version="${{{{ steps.version.outputs.version }}}}"
          gh release create "${{{{ steps.version.outputs.tag }}}}" \\
            "build/{slug}-$version.zip" \\
            "build/{slug}-$version.zip.sha256" \\
            --title "{name} v$version" --generate-notes
'''


def acceptance_md(profile: dict) -> str:
    lines = [
        "# NalApps Release Acceptance",
        "",
        "Release is PASS only when all applicable items are verified.",
        "",
        "- [ ] plugin-profile.json validates against the canonical schema.",
        "- [ ] Author/Author URI/GitHub metadata matches EOINGTI Lab defaults.",
        "- [ ] Capability + nonce protect every mutation.",
        "- [ ] Input validation/sanitization and output escaping are applied.",
        "- [ ] PHP syntax and WPCS CI pass.",
        "- [ ] Public repository secret/customer-data gate passes.",
        "- [ ] Version header, readme Stable tag, Git tag, release and store metadata agree.",
        "- [ ] Existing settings/data survive the supported upgrade path.",
        "- [ ] Release ZIP root equals the canonical plugin slug.",
    ]
    if profile.get("product_type") == "edd_paid":
        lines += [
            "- [ ] EDD license activation/deactivation is verified.",
            "- [ ] WordPress Plugins screen and internal updater both detect a newer release.",
            "- [ ] Production Release ZIP contains every runtime dependency required by the updater.",
        ]
    if profile.get("database"):
        lines.append("- [ ] Database migration is forward-only, idempotent and regression-tested.")
    if profile.get("cron"):
        lines.append("- [ ] Cron scheduling is duplicate-safe and cleared on deactivation when appropriate.")
    return "\n".join(lines) + "\n"


def normalize_generated_php(target: Path) -> None:
    replacements = {
        "if ( ! defined( 'ABSPATH' ) ) { exit; }": "if ( ! defined( 'ABSPATH' ) ) {\n\texit;\n}",
        "if ( version_compare( $current, self::TARGET, '>=' ) ) { return; }": "if ( version_compare( $current, self::TARGET, '>=' ) ) {\n\t\t\treturn;\n\t\t}",
        "private function __construct() {}": "private function __construct() {\n\t}",
    }
    for path in target.rglob("*.php"):
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def complete_scaffold(profile_path: Path, output: Path, clean: bool = False) -> Path:
    profile = validate_profile(profile_path)
    target = scaffold(profile_path, output, clean=clean)
    normalize_generated_php(target)
    write_file(target, "composer.json", composer_json(profile))
    write_file(target, "phpcs.xml.dist", phpcs_xml())
    write_file(target, ".github/workflows/quality.yml", quality_workflow(profile))
    write_file(target, ".github/workflows/release.yml", release_workflow(profile))
    write_file(target, "docs/RELEASE-ACCEPTANCE.md", acceptance_md(profile))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", default=Path("build/scaffold"), type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    target = complete_scaffold(args.profile, args.output, args.clean)
    print(f"PASS complete_scaffold={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
