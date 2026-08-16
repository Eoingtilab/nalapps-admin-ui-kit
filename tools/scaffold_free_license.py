#!/usr/bin/env python3
"""Add the canonical always-active free-license runtime to free NalApps plugins."""
from __future__ import annotations

import json
from pathlib import Path

from scaffold_plugin import namespace_suffix, php_const_prefix, write_file


def free_license_class(profile: dict) -> str:
    ns = namespace_suffix(profile["slug"])
    slug = profile["slug"]
    page_slug = f"{slug}-license"
    return f'''<?php
/**
 * Canonical free-license status adapter.
 *
 * Free products never require a serial key or remote activation.
 * Their license state is always active while the plugin is installed.
 *
 * @package {ns}
 */

namespace EOINGTI\\Plugins\\{ns};

if ( ! defined( 'ABSPATH' ) ) {{
\texit;
}}

final class License {{
\tpublic function __construct() {{
\t\tadd_action( 'admin_menu', array( $this, 'register_page' ) );
\t}}

\tpublic static function key() {{
\t\treturn '';
\t}}

\tpublic static function status() {{
\t\treturn 'free';
\t}}

\tpublic static function is_valid() {{
\t\treturn true;
\t}}

\tpublic function register_page() {{
\t\tadd_options_page(
\t\t\t'{profile["plugin_name"]} License',
\t\t\t'{profile["plugin_name"]} License',
\t\t\t'manage_options',
\t\t\t'{page_slug}',
\t\t\tarray( $this, 'render_page' )
\t\t);
\t}}

\tpublic function render_page() {{
\t\tif ( ! current_user_can( 'manage_options' ) ) {{
\t\t\twp_die( esc_html( 'Insufficient permissions.' ) );
\t\t}}
\t\techo '<div class="wrap"><h1>' . esc_html( '{profile["plugin_name"]} License' ) . '</h1>';
\t\techo '<p><strong>' . esc_html( '라이선스: 무료 (Free)' ) . '</strong></p>';
\t\techo '<p><strong>' . esc_html( '현재 상태: 활성 (Active)' ) . '</strong></p>';
\t\techo '<p>' . esc_html( '무료 제품은 시리얼 키 입력, 원격 활성화 또는 비활성화 절차가 필요하지 않습니다.' ) . '</p>';
\t\techo '</div>';
\t}}
}}
'''


def augment_main(target: Path, profile: dict) -> None:
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    ns = namespace_suffix(slug)
    path = target / f"{slug}.php"
    text = path.read_text(encoding="utf-8")
    marker = "// NalApps canonical free-license runtime."
    if marker in text:
        return
    block = f'''\n\n{marker}\nrequire_once {prefix}_PATH . 'includes/class-license.php';\nnew \\EOINGTI\\Plugins\\{ns}\\License();\n'''
    path.write_text(text + block, encoding="utf-8")


def augment_manifest(target: Path) -> None:
    path = target / "nalapps-standard-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    modules = data.setdefault("required_modules", [])
    gates = data.setdefault("release_gates", [])
    for module in ("free_license_display", "free_license_always_active"):
        if module not in modules:
            modules.append(module)
    for gate in ("free_license_ui", "free_license_always_active"):
        if gate not in gates:
            gates.append(gate)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_free_license_runtime(target: Path, profile: dict) -> None:
    if profile.get("product_type") != "free":
        return
    if profile.get("license_required") is not False:
        raise ValueError("Free products must declare license_required=false")
    write_file(target, "includes/class-license.php", free_license_class(profile))
    augment_main(target, profile)
    augment_manifest(target)
