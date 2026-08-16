#!/usr/bin/env python3
"""Add the canonical registered-free EDD license runtime to NalApps plugins."""
from __future__ import annotations

import json
from pathlib import Path

from scaffold_plugin import edd_config, php_const_prefix, write_file
from scaffold_product import augment_composer, augment_main, license_class, update_manager_class


def augment_edd_config_require(target: Path, profile: dict) -> None:
    slug = profile["slug"]
    prefix = php_const_prefix(slug)
    path = target / f"{slug}.php"
    text = path.read_text(encoding="utf-8")
    marker = "// NalApps registered-license EDD config runtime."
    if marker in text:
        return
    block = f"\n\n{marker}\nrequire_once {prefix}_PATH . 'includes/class-edd-config.php';\n"
    path.write_text(text + block, encoding="utf-8")


def augment_manifest(target: Path) -> None:
    path = target / "nalapps-standard-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    modules = data.setdefault("required_modules", [])
    gates = data.setdefault("release_gates", [])
    for module in ("edd_license", "product_native_license_ui", "hybrid_updater", "release_asset", "free_registered_license"):
        if module not in modules:
            modules.append(module)
    for gate in ("license_activation_ui", "registered_license_activation", "license_update_entitlement"):
        if gate not in gates:
            gates.append(gate)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_registered_license_runtime(target: Path, profile: dict) -> None:
    """Install the same EDD registration runtime for free_registered products.

    The product price is free, but the site must register/activate a license key.
    """
    if profile.get("license_mode") != "free_registered":
        return
    if profile.get("license_required") is not True:
        raise ValueError("free_registered must declare license_required=true")
    if not profile.get("edd_download_id") or not profile.get("edd_store_url"):
        raise ValueError("free_registered requires EDD licensing metadata")

    augment_composer(target)
    write_file(target, "includes/class-edd-config.php", edd_config(profile))
    augment_edd_config_require(target, profile)
    write_file(target, "includes/class-license.php", license_class(profile))
    write_file(target, "includes/class-update-manager.php", update_manager_class(profile))
    augment_main(target, profile)
    augment_manifest(target)
