#!/usr/bin/env python3
"""Self-test for migration adapter classification."""
from migration_plan import build_plan


def repo(**overrides):
    base = {
        "repository": "Eoingtilab/example",
        "wordpress_plugin": True,
        "architecture": "standalone",
        "role": "plugin",
        "slug": "example",
        "main_file": "example.php",
        "current_version": "1.0.0",
        "control_plane": "self",
        "data_contract_reviewed": True,
        "credential_sensitive": False,
        "release_contract_known": True,
    }
    base.update(overrides)
    return base


def main():
    cases = [
        repo(),
        repo(repository="Eoingtilab/core", architecture="commerce_family", role="core", control_plane="self"),
        repo(repository="Eoingtilab/addon", architecture="commerce_family", role="addon", control_plane="commerce_core"),
        repo(repository="Eoingtilab/bridge", architecture="specialized", role="server_bridge", control_plane="server_side"),
        repo(repository="Eoingtilab/unknown", control_plane="unknown"),
        repo(repository="Eoingtilab/unreviewed", data_contract_reviewed=False),
        repo(repository="Eoingtilab/windows", wordpress_plugin=False),
    ]
    plan = build_plan({"standard_version": "4.6.0", "repositories": cases})
    statuses = [item["status"] for item in plan["repositories"]]
    assert statuses == [
        "adapter_ready",
        "adapter_review_required",
        "adapter_review_required",
        "adapter_review_required",
        "blocked",
        "blocked",
        "excluded",
    ], statuses
    standalone = plan["repositories"][0]
    assert standalone["adapter"] == "standalone"
    assert "verified_rollback" in standalone["allowed_modules"]
    addon = plan["repositories"][2]
    assert addon["lifecycle_owner"] == "commerce_core"
    assert "parallel_lifecycle_control_plane" in addon["forbidden"]
    specialized = plan["repositories"][3]
    assert "replace_existing_signature_verification" in specialized["forbidden"]
    assert plan["mutations_performed"] is False
    print("PASS migration adapter contracts")


if __name__ == "__main__":
    main()
