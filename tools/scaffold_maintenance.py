#!/usr/bin/env python3
"""Add common NalApps rollback, portability, diagnostics and uninstall runtime."""
from __future__ import annotations

import json
from pathlib import Path

from maintenance_data import data_portability_class
from maintenance_rollback import rollback_manager_class
from maintenance_system import maintenance_page_class, system_info_class
from maintenance_uninstall import uninstall_php
from scaffold_plugin import namespace_suffix, php_const_prefix, write_file


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
    for module in ("rollback", "data_portability", "safe_uninstall", "system_info"):
        if module not in data["required_modules"]:
            data["required_modules"].append(module)
    for gate in ("rollback_backup_contract", "data_backup_import_export", "uninstall_delete_gate", "system_info_redaction"):
        if gate not in data["release_gates"]:
            data["release_gates"].append(gate)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_maintenance_runtime(target: Path, profile: dict) -> Path:
    write_file(target, "includes/class-data-portability.php", data_portability_class(profile))
    write_file(target, "includes/class-rollback-manager.php", rollback_manager_class(profile))
    write_file(target, "includes/class-system-info.php", system_info_class(profile))
    write_file(target, "includes/class-maintenance-page.php", maintenance_page_class(profile))
    write_file(target, "uninstall.php", uninstall_php(profile))
    augment_main(target, profile)
    augment_manifest(target)
    return target
