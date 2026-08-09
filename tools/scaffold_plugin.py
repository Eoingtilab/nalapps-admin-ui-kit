#!/usr/bin/env python3
"""Generate a WordPress plugin skeleton from a NalApps plugin profile."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from validate_profile import ROOT, load_json, validate_profile


def php_const_prefix(slug: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", slug.upper()).strip("_")


def namespace_suffix(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("-"))


def php_header(profile: dict, company: dict) -> str:
    slug = profile["slug"]
    plugin_uri = profile.get("plugin_uri") or company["plugin_uri_fallback"]
    update_uri = profile.get("update_uri") or plugin_uri
    requires_plugins = ", ".join(profile.get("requires_plugins", []))
    requires_line = f" * Requires Plugins: {requires_plugins}\n" if requires_plugins else ""
    return f'''<?php
/**
 * Plugin Name: {profile["plugin_name"]}
 * Plugin URI: {plugin_uri}
 * Description: {profile.get("description") or "NalApps WordPress plugin."}
 * Version: {profile.get("plugin_version", "0.1.0")}
 * Author: {company["author"]}
 * Author URI: {company["author_uri"]}
 * Text Domain: {slug}
 * Requires at least: {profile.get("requires_wp", "6.5")}
 * Requires PHP: {profile.get("requires_php", "7.4")}
{requires_line} * Update URI: {update_uri}
 * License: {profile.get("license", "GPLv2 or later")}
 * License URI: {profile.get("license_uri") or "https://www.gnu.org/licenses/gpl-2.0.html"}
 */

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

'''


def main_plugin(profile: dict, company: dict, standard_version: str) -> str:
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    ns = namespace_suffix(slug)
    version = profile.get("plugin_version", "0.1.0")
    header = php_header(profile, company)
    requires = ["includes/class-plugin.php"]
    for enabled, path in [
        (profile.get("external_api"), "includes/class-http-client.php"),
        (profile.get("database"), "includes/class-db-migrator.php"),
        (profile.get("cron"), "includes/class-cron-manager.php"),
        (profile.get("rest_api"), "includes/class-rest-controller.php"),
        (profile.get("file_upload"), "includes/class-upload-guard.php"),
        (profile.get("product_type") == "edd_paid", "includes/class-edd-config.php"),
    ]:
        if enabled:
            requires.append(path)
    require_lines = "\n".join(f"require_once __DIR__ . '/{path}';" for path in requires)
    return header + f'''define( '{prefix}_VERSION', '{version}' );
define( '{prefix}_STANDARD_VERSION', '{standard_version}' );
define( '{prefix}_FILE', __FILE__ );
define( '{prefix}_PATH', plugin_dir_path( __FILE__ ) );
define( '{prefix}_URL', plugin_dir_url( __FILE__ ) );

{require_lines}

add_action(
\t'plugins_loaded',
\tstatic function () {{
\t\t\\EOINGTI\\Plugins\\{ns}\\Plugin::instance();
\t}}
);
'''


def plugin_class(profile: dict, company: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    repo = company["repository_template"].replace("{plugin-slug}", slug)
    return f'''<?php
/**
 * Core plugin bootstrap.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class Plugin {{
\tprivate static $instance = null;

\tpublic static function instance() {{
\t\tif ( null === self::$instance ) {{
\t\t\tself::$instance = new self();
\t\t}}
\t\treturn self::$instance;
\t}}

\tprivate function __construct() {{
\t\tadd_filter( 'plugin_action_links_' . plugin_basename( dirname( __DIR__ ) . '/{slug}.php' ), array( $this, 'action_links' ) );
\t}}

\tpublic function action_links( $links ) {{
\t\t$links[] = '<a href="{company["developer_site"]}" target="_blank" rel="noopener noreferrer">Developer</a>';
\t\t$links[] = '<a href="{repo}" target="_blank" rel="noopener noreferrer">GitHub</a>';
\t\treturn $links;
\t}}
}}
'''


def http_client(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class Http_Client {{
\tpublic static function request( $url, $args = array() ) {{
\t\tif ( ! wp_http_validate_url( $url ) || 0 !== strpos( $url, 'https://' ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_invalid_remote_url', 'A valid HTTPS endpoint is required.' );
\t\t}}
\t\t$args = wp_parse_args( $args, array( 'timeout' => 15, 'sslverify' => true, 'redirection' => 3 ) );
\t\treturn wp_remote_request( $url, $args );
\t}}
}}
'''


def db_migrator(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    option = profile["slug"].replace("-", "_") + "_db_schema_version"
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class DB_Migrator {{
\tconst OPTION = '{option}';
\tconst TARGET = '1';

\tpublic static function maybe_migrate() {{
\t\t$current = (string) get_option( self::OPTION, '0' );
\t\tif ( version_compare( $current, self::TARGET, '>=' ) ) {{ return; }}
\t\tupdate_option( self::OPTION, self::TARGET, false );
\t}}
}}
'''


def cron_manager(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    hook = profile["slug"].replace("-", "_") + "_cron_tick"
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class Cron_Manager {{
\tconst HOOK = '{hook}';

\tpublic static function schedule() {{
\t\tif ( ! wp_next_scheduled( self::HOOK ) ) {{
\t\t\twp_schedule_event( time() + HOUR_IN_SECONDS, 'daily', self::HOOK );
\t\t}}
\t}}

\tpublic static function clear() {{
\t\twp_clear_scheduled_hook( self::HOOK );
\t}}
}}
'''


def rest_controller(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class Rest_Controller {{
\tpublic static function register() {{
\t\tregister_rest_route(
\t\t\t'{slug}/v1',
\t\t\t'/status',
\t\t\tarray(
\t\t\t\t'methods' => \\WP_REST_Server::READABLE,
\t\t\t\t'callback' => array( __CLASS__, 'status' ),
\t\t\t\t'permission_callback' => static function () {{ return current_user_can( 'manage_options' ); }},
\t\t\t)
\t\t);
\t}}

\tpublic static function status() {{
\t\treturn rest_ensure_response( array( 'status' => 'ok' ) );
\t}}
}}
'''


def upload_guard(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class Upload_Guard {{
\tpublic static function validate( $tmp_name, $file_name, $allowed_mimes ) {{
\t\tif ( ! current_user_can( 'upload_files' ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_upload_forbidden', 'Upload permission is required.' );
\t\t}}
\t\t$checked = wp_check_filetype_and_ext( $tmp_name, $file_name, $allowed_mimes );
\t\tif ( empty( $checked['ext'] ) || empty( $checked['type'] ) ) {{
\t\t\treturn new \\WP_Error( 'nalapps_upload_type', 'File type is not allowed.' );
\t\t}}
\t\treturn $checked;
\t}}
}}
'''


def edd_config(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    store = profile["edd_store_url"]
    item = int(profile["edd_download_id"])
    return f'''<?php
/** @package {ns} */
namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{ exit; }}

final class EDD_Config {{
\tconst STORE_URL = '{store}';
\tconst DOWNLOAD_ID = {item};

\tprivate function __construct() {{}}
}}
'''


def readme(profile: dict, company: dict, standard_version: str) -> str:
    repo = company["repository_template"].replace("{plugin-slug}", profile["slug"])
    return f'''# {profile["plugin_name"]}

{profile.get("description") or "NalApps WordPress plugin."}

## Development standard

Generated from **NalApps WordPress Plugin Standard v{standard_version}**.

- Developer: **{company["developer_name_en"]} / {company["developer_name_ko"]}**
- Website: {company["developer_site"]}
- Source: {repo}
- Telemetry: {profile.get("telemetry", company["telemetry_default"])}

## Requirements

- WordPress {profile.get("requires_wp", "6.5")}+
- PHP {profile.get("requires_php", "7.4")}+

## Security and privacy

Do not publish license keys, API keys, passwords, cookies, customer databases, backups, production dumps, or `.env` files. External services used by the product must be documented before release.

## Release policy

Version bump is the final release commit. CI must pass profile validation, PHP syntax, coding standards, secret scanning, package validation, and upgrade regression before a release is considered ready.
'''


def readme_txt(profile: dict) -> str:
    version = profile.get("plugin_version", "0.1.0")
    return f'''=== {profile["plugin_name"]} ===
Requires at least: {profile.get("requires_wp", "6.5")}
Requires PHP: {profile.get("requires_php", "7.4")}
Stable tag: {version}
License: {profile.get("license", "GPLv2 or later")}

{profile.get("description") or "NalApps WordPress plugin."}

== Changelog ==

= {version} =
* Initial scaffold generated from NalApps WordPress Plugin Standard.
'''


def quality_workflow(profile: dict) -> str:
    slug = profile["slug"]
    return f'''name: NalApps Plugin Quality Gate

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '7.4'
          tools: composer:v2
          coverage: none
      - name: PHP syntax
        run: find . -name '*.php' -not -path './vendor/*' -print0 | xargs -0 -n1 php -l
      - name: Public repository safety
        shell: bash
        run: |
          set -euo pipefail
          if git ls-files | grep -E '(^|/)(\\.env|id_rsa|id_ed25519|.*\\.pem|.*\\.p12|.*\\.pfx|.*\\.sql|.*\\.dump|.*\\.bak)$'; then exit 1; fi
          if git grep -nEI '(BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|ghp_[A-Za-z0-9]{{20,}}|github_pat_[A-Za-z0-9_]{{20,}}|AKIA[0-9A-Z]{{16}})'; then exit 1; fi
      - name: Package root contract
        run: test -f '{slug}.php' && test -f plugin-profile.json && test -f readme.txt
'''


def manifest(profile: dict, standard_version: str) -> dict:
    modules = ["admin_ui", "security", "compatibility", "lifecycle", "system_status", "release_gate"]
    for key, module in [
        ("database", "db_migration"), ("cron", "cron_manager"), ("rest_api", "rest_api"),
        ("external_api", "http_client"), ("file_upload", "upload_guard"), ("multisite", "multisite_policy"),
    ]:
        if profile.get(key):
            modules.append(module)
    if profile.get("product_type") == "edd_paid":
        modules.extend(["edd_license", "hybrid_updater", "release_asset"])
    return {
        "standard_version": standard_version,
        "slug": profile["slug"],
        "required_modules": modules,
        "release_gates": [
            "profile_schema", "php_syntax", "wpcs", "secret_scan", "dependency_audit",
            "package_root", "version_consistency", "upgrade_regression",
        ],
    }


def write_file(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold(profile_path: Path, output: Path, clean: bool = False) -> Path:
    profile = validate_profile(profile_path)
    company = load_json(ROOT / "profiles" / "company-profile.json")
    standard_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    target = output / profile["slug"]
    if target.exists():
        if not clean:
            raise SystemExit(f"Output already exists: {target}. Use --clean to replace it.")
        shutil.rmtree(target)
    target.mkdir(parents=True)

    write_file(target, f"{profile['slug']}.php", main_plugin(profile, company, standard_version))
    write_file(target, "includes/class-plugin.php", plugin_class(profile, company))
    if profile.get("external_api"):
        write_file(target, "includes/class-http-client.php", http_client(profile))
    if profile.get("database"):
        write_file(target, "includes/class-db-migrator.php", db_migrator(profile))
    if profile.get("cron"):
        write_file(target, "includes/class-cron-manager.php", cron_manager(profile))
    if profile.get("rest_api"):
        write_file(target, "includes/class-rest-controller.php", rest_controller(profile))
    if profile.get("file_upload"):
        write_file(target, "includes/class-upload-guard.php", upload_guard(profile))
    if profile.get("product_type") == "edd_paid":
        write_file(target, "includes/class-edd-config.php", edd_config(profile))

    write_file(target, "README.md", readme(profile, company, standard_version))
    write_file(target, "readme.txt", readme_txt(profile))
    write_file(target, "CHANGELOG.md", f"# Changelog\n\n## {profile.get('plugin_version', '0.1.0')}\n- Initial NalApps standard scaffold.\n")
    write_file(target, "SECURITY.md", "# Security\n\nReport vulnerabilities privately to the repository owner. Never post credentials or customer data in public issues.\n")
    write_file(target, "CONTRIBUTING.md", "# Contributing\n\nChanges must preserve plugin-profile.json, pass the NalApps quality gate, and update tests/documentation when behavior changes.\n")
    write_file(target, "plugin-profile.json", json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    write_file(target, "nalapps-standard-manifest.json", json.dumps(manifest(profile, standard_version), ensure_ascii=False, indent=2) + "\n")
    write_file(target, ".github/workflows/quality.yml", quality_workflow(profile))
    write_file(target, ".gitignore", ".env\n.env.*\nvendor/\nbuild/\n*.zip\n*.sql\n*.dump\n*.bak\n")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", default=Path("build/scaffold"), type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    target = scaffold(args.profile, args.output, args.clean)
    print(f"PASS scaffold={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
