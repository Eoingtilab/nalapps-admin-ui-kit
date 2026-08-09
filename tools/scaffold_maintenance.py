#!/usr/bin/env python3
"""Add common NalApps rollback, portability, diagnostics and uninstall runtime."""
from __future__ import annotations

import json
from pathlib import Path

from maintenance_data import data_portability_class
from maintenance_rollback import rollback_manager_class
from maintenance_system import maintenance_page_class, system_info_class
from maintenance_uninstall import uninstall_php
from scaffold_plugin import ROOT, namespace_suffix, php_const_prefix, write_file


def augment_main(target: Path, profile: dict) -> None:
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    ns = namespace_suffix(slug)
    path = target / f"{slug}.php"
    text = path.read_text(encoding="utf-8")
    marker = "// NalApps common maintenance runtime."
    if marker in text:
        return
    block = f'''\n\n{marker}\nrequire_once {prefix}_PATH . 'includes/class-data-portability.php';\nrequire_once {prefix}_PATH . 'includes/class-rollback-manager.php';\nrequire_once {prefix}_PATH . 'includes/class-system-info.php';\nrequire_once {prefix}_PATH . 'includes/class-maintenance-page.php';\nnew \\EOINGTI\\Plugins\\{ns}\\Data_Portability();\nnew \\EOINGTI\\Plugins\\{ns}\\Rollback_Manager();\nnew \\EOINGTI\\Plugins\\{ns}\\System_Info();\nnew \\EOINGTI\\Plugins\\{ns}\\Maintenance_Page();\n'''
    path.write_text(text + block, encoding="utf-8")


def augment_manifest(target: Path) -> None:
    path = target / "nalapps-standard-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for module in ("rollback", "data_portability", "safe_uninstall", "system_info", "refined_admin_ui"):
        if module not in data["required_modules"]:
            data["required_modules"].append(module)
    for gate in ("rollback_backup_contract", "data_backup_import_export", "uninstall_delete_gate", "system_info_redaction", "admin_ui_contract"):
        if gate not in data["release_gates"]:
            data["release_gates"].append(gate)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_maintenance_php(target: Path) -> None:
    replacements = {
        "array( 'timeout' => 15, 'sslverify' => true, 'redirection' => 3 )": (
            "array(\n"
            "\t\t\t\t'timeout'     => 15,\n"
            "\t\t\t\t'sslverify'   => true,\n"
            "\t\t\t\t'redirection' => 3,\n"
            "\t\t\t)"
        ),
        "$wpdb = $GLOBALS['wpdb'];": "global $wpdb;",
        "$tmp_name = (string) $_FILES['nalapps_backup']['tmp_name']; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized\n\t\t$size     =": (
            "$tmp_name = (string) $_FILES['nalapps_backup']['tmp_name']; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized\n\n\t\t$size ="
        ),
        "$size = (int) $_FILES['nalapps_backup']['size'];\n\t\t$name     =": (
            "$size = (int) $_FILES['nalapps_backup']['size'];\n\n\t\t$name ="
        ),
        "$raw = file_get_contents( $tmp_name ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents\n\t\tif": (
            "$raw = file_get_contents( $tmp_name ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents\n\n\t\tif"
        ),
        "$payload = json_decode( $raw, true );\n\t\tif": "$payload = json_decode( $raw, true );\n\n\t\tif",
        "$snapshot = self::create_snapshot( 'pre-import' );\n\t\tif": "$snapshot = self::create_snapshot( 'pre-import' );\n\n\t\tif",
        "$post_id  =": "$post_id   =",
        "$args     =": "$args      =",
        "$existing = $post_id ?": "$existing  = $post_id ?",
        "$saved  = wp_insert_post": "$saved = wp_insert_post",
    }
    for path in target.rglob("*.php"):
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def add_maintenance_runtime(target: Path, profile: dict) -> Path:
    write_file(target, "includes/class-data-portability.php", data_portability_class(profile))
    write_file(target, "includes/class-rollback-manager.php", rollback_manager_class(profile))
    write_file(target, "includes/class-system-info.php", system_info_class(profile))
    write_file(target, "includes/class-maintenance-page.php", maintenance_page_class(profile))
    write_file(target, "assets/css/nalapps-admin-ui.css", (ROOT / "assets/css/nalapps-admin-ui.css").read_text(encoding="utf-8"))
    write_file(target, "assets/css/nalapps-admin-typography.css", (ROOT / "assets/css/nalapps-admin-typography.css").read_text(encoding="utf-8"))
    write_file(target, "uninstall.php", uninstall_php(profile))
    augment_main(target, profile)
    augment_manifest(target)
    normalize_maintenance_php(target)
    return target
