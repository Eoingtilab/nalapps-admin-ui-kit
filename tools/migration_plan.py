#!/usr/bin/env python3
"""Generate a read-only NalApps migration plan from an explicit repository inventory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_ARCH = {"standalone", "commerce_family", "specialized"}
ALLOWED_ROLES = {"plugin", "core", "addon", "server_bridge", "security", "credential_sensitive", "data_sensitive"}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "blocked", "reason": reason}


def classify(repo: dict[str, Any]) -> dict[str, Any]:
    required = (
        "repository", "wordpress_plugin", "architecture", "role", "slug", "main_file",
        "current_version", "control_plane", "data_contract_reviewed", "credential_sensitive",
        "release_contract_known",
    )
    missing = [key for key in required if key not in repo]
    if missing:
        return _blocked("missing_required_fields:" + ",".join(missing))
    if not repo["wordpress_plugin"]:
        return {"status": "excluded", "reason": "not_wordpress_plugin"}
    if repo["architecture"] not in ALLOWED_ARCH or repo["role"] not in ALLOWED_ROLES:
        return _blocked("unknown_architecture_or_role")
    if repo["control_plane"] == "unknown":
        return _blocked("control_plane_unknown")
    if not repo["data_contract_reviewed"]:
        return _blocked("data_contract_not_reviewed")
    if not repo["release_contract_known"]:
        return _blocked("release_contract_unknown")

    architecture = repo["architecture"]
    role = repo["role"]
    base = {
        "repository": repo["repository"],
        "architecture": architecture,
        "role": role,
        "preserve": ["slug", "plugin_basename", "data_contract", "frontend_behavior"],
        "forbidden": ["direct_main_write", "existing_release_overwrite", "secret_commit"],
    }

    if architecture == "standalone":
        if role != "plugin":
            return _blocked("standalone_requires_plugin_role")
        base.update({
            "status": "adapter_ready",
            "adapter": "standalone",
            "lifecycle_owner": "plugin",
            "allowed_modules": ["admin_ui", "license", "update", "backup_restore", "system_info", "verified_rollback"],
            "preconditions": ["product_specific_regression_tests", "edd_mapping_if_paid"],
        })
        return base

    if architecture == "commerce_family":
        if role not in {"core", "addon"}:
            return _blocked("commerce_family_requires_core_or_addon")
        base.update({
            "status": "adapter_review_required",
            "adapter": "commerce_core" if role == "core" else "commerce_addon",
            "lifecycle_owner": "commerce_core",
            "allowed_modules": ["admin_ui", "system_info"],
            "conditional_modules": ["license", "update", "backup_restore", "verified_rollback"],
            "forbidden": base["forbidden"] + ["parallel_lifecycle_control_plane"],
            "preconditions": ["commerce_core_contract_review", "delegation_contract_verified"],
        })
        return base

    # specialized
    allowed = ["admin_ui", "system_info"]
    forbidden = base["forbidden"] + ["replace_existing_signature_verification", "generic_secret_backup"]
    preconditions = ["product_specific_security_review"]
    if repo["credential_sensitive"]:
        preconditions.append("credential_storage_contract_review")
    base.update({
        "status": "adapter_review_required",
        "adapter": "specialized",
        "lifecycle_owner": repo["control_plane"],
        "allowed_modules": allowed,
        "conditional_modules": ["license", "update", "backup_restore", "verified_rollback"],
        "forbidden": forbidden,
        "preconditions": preconditions,
    })
    return base


def build_plan(inventory: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(inventory, dict) or not isinstance(inventory.get("repositories"), list):
        raise ValueError("inventory must contain a repositories array")
    plans = [classify(item) for item in inventory["repositories"]]
    counts: dict[str, int] = {}
    for plan in plans:
        counts[plan["status"]] = counts.get(plan["status"], 0) + 1
    return {
        "standard_version": inventory.get("standard_version", "unknown"),
        "mode": "read_only_plan",
        "mutations_performed": False,
        "summary": counts,
        "repositories": plans,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    plan = build_plan(data)
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
