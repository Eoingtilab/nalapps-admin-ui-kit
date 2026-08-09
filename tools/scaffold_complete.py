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
      - 'plugin-profile.json'
      - '.github/workflows/release.yml'
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

      - name: Read version and release asset state
        id: version
        shell: bash
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        run: |
          set -euo pipefail
          version="$(sed -n 's/^ \\* Version: \\(.*\\)$/\\1/p' {slug}.php | head -n1 | tr -d '\\r')"
          test -n "$version"
          tag="v$version"
          zip_name="{slug}-$version.zip"
          sha_name="$zip_name.sha256"
          if git rev-parse "$tag" >/dev/null 2>&1; then tag_exists=true; else tag_exists=false; fi
          if gh release view "$tag" >/dev/null 2>&1; then
            release_exists=true
            assets="$(gh release view "$tag" --json assets --jq '.assets[].name' 2>/dev/null || true)"
          else
            release_exists=false
            assets=""
          fi
          if printf '%s\\n' "$assets" | grep -Fxq "$zip_name"; then zip_exists=true; else zip_exists=false; fi
          if printf '%s\\n' "$assets" | grep -Fxq "$sha_name"; then sha_exists=true; else sha_exists=false; fi
          if [ "$release_exists" = true ] && [ "$zip_exists" = true ] && [ "$sha_exists" = true ]; then needs_assets=false; else needs_assets=true; fi
          echo "version=$version" >> "$GITHUB_OUTPUT"
          echo "tag=$tag" >> "$GITHUB_OUTPUT"
          echo "zip_name=$zip_name" >> "$GITHUB_OUTPUT"
          echo "sha_name=$sha_name" >> "$GITHUB_OUTPUT"
          echo "tag_exists=$tag_exists" >> "$GITHUB_OUTPUT"
          echo "release_exists=$release_exists" >> "$GITHUB_OUTPUT"
          echo "needs_assets=$needs_assets" >> "$GITHUB_OUTPUT"

      - name: Existing verified release is immutable
        if: steps.version.outputs.needs_assets != 'true'
        run: echo "${{{{ steps.version.outputs.tag }}}} already has verified ZIP and SHA256 assets; no overwrite is allowed."

      - name: Pin recovery build to existing tag
        if: steps.version.outputs.needs_assets == 'true' && steps.version.outputs.tag_exists == 'true'
        shell: bash
        run: |
          set -euo pipefail
          git checkout --detach "${{{{ steps.version.outputs.tag }}}}"
          test "$(sed -n 's/^ \\* Version: \\(.*\\)$/\\1/p' {slug}.php | head -n1 | tr -d '\\r')" = "${{{{ steps.version.outputs.version }}}}"

      - uses: shivammathur/setup-php@v2
        if: steps.version.outputs.needs_assets == 'true'
        with:
          php-version: '8.3'
          tools: composer:v2
          coverage: none

      - name: Install and audit quality dependencies
        if: steps.version.outputs.needs_assets == 'true'
        run: |
          composer update --no-interaction --prefer-dist --no-progress
          composer audit

      - name: Validate source
        if: steps.version.outputs.needs_assets == 'true'
        shell: bash
        run: |
          set -euo pipefail
          find . -name '*.php' -not -path './vendor/*' -not -path './build/*' -print0 | xargs -0 -r -n1 php -l
          vendor/bin/phpcs --standard=phpcs.xml.dist
          version="${{{{ steps.version.outputs.version }}}}"
          grep -q "Stable tag: $version" readme.txt
          grep -q '"slug": "{slug}"' plugin-profile.json

      - name: Prepare production dependencies
        if: steps.version.outputs.needs_assets == 'true'
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
        if: steps.version.outputs.needs_assets == 'true'
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

      - name: Create immutable tag after successful build validation
        if: steps.version.outputs.needs_assets == 'true' && steps.version.outputs.tag_exists != 'true'
        env:
          TAG: ${{{{ steps.version.outputs.tag }}}}
        run: |
          set -euo pipefail
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git tag -a "$TAG" -m "{name} $TAG"
          git push origin "$TAG"

      - name: Create release or backfill missing assets
        if: steps.version.outputs.needs_assets == 'true'
        shell: bash
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        run: |
          set -euo pipefail
          version="${{{{ steps.version.outputs.version }}}}"
          tag="${{{{ steps.version.outputs.tag }}}}"
          zip_path="build/{slug}-$version.zip"
          sha_path="$zip_path.sha256"
          if ! gh release view "$tag" >/dev/null 2>&1; then
            gh release create "$tag" --title "{name} v$version" --generate-notes
          fi
          assets="$(gh release view "$tag" --json assets --jq '.assets[].name' 2>/dev/null || true)"
          if ! printf '%s\\n' "$assets" | grep -Fxq "$(basename "$zip_path")"; then gh release upload "$tag" "$zip_path"; fi
          if ! printf '%s\\n' "$assets" | grep -Fxq "$(basename "$sha_path")"; then gh release upload "$tag" "$sha_path"; fi
          final_assets="$(gh release view "$tag" --json assets --jq '.assets[].name')"
          printf '%s\\n' "$final_assets" | grep -Fxq "$(basename "$zip_path")"
          printf '%s\\n' "$final_assets" | grep -Fxq "$(basename "$sha_path")"

      - name: Upload verified install package
        if: steps.version.outputs.needs_assets == 'true'
        uses: actions/upload-artifact@v4
        with:
          name: {slug}-${{{{ steps.version.outputs.version }}}}-install-package
          path: |
            build/{slug}-${{{{ steps.version.outputs.version }}}}.zip
            build/{slug}-${{{{ steps.version.outputs.version }}}}.zip.sha256
          if-no-files-found: error
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
        "- [ ] Version header, readme Stable tag, Git tag, Release, ZIP filename and store metadata agree.",
        "- [ ] Existing settings/data survive the supported upgrade path.",
        "- [ ] Release ZIP root equals the canonical plugin slug.",
        "- [ ] Release ZIP and SHA256 assets exist; source-code archive alone is not accepted.",
        "- [ ] Existing release assets were not overwritten.",
        "- [ ] Missing release assets can be backfilled only from the immutable version tag.",
    ]
    if profile.get("product_type") == "edd_paid":
        lines += [
            "- [ ] Product-native serial entry, activation, check and deactivation UI is available.",
            "- [ ] No bootstrap deadlock exists where a license is required for update but cannot be entered.",
            "- [ ] Existing core product runtime is not license-gated unless explicitly required by product policy.",
            "- [ ] EDD license activation/deactivation is verified.",
            "- [ ] WordPress Plugins screen and internal updater both detect a newer release.",
            "- [ ] get_version returns an installable package/download URL, not only new_version.",
            "- [ ] Production Release ZIP contains every runtime dependency required by the updater.",
            "- [ ] EDD Update File points to the verified Release Asset, not Release Source Code.",
            "- [ ] A real N-1 to N WordPress update succeeds and preserves existing data/settings.",
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
