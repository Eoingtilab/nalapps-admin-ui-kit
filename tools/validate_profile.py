#!/usr/bin/env python3
"""Validate a NalApps plugin profile against the canonical JSON schema."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "profiles" / "plugin-profile.schema.json"
SENSITIVE_OPTION_PATTERN = re.compile(
    r"(?:password|passwd|secret|token|api[_-]?key|license[_-]?key|private[_-]?key|credential|auth[_-]?key)",
    re.IGNORECASE,
)
LICENSE_MODES = {"paid", "free_registered", "free_download"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def normalize_license_contract(profile: dict) -> dict:
    """Normalize legacy profiles into the canonical three-mode license contract."""
    product_type = profile.get("product_type")
    mode = profile.get("license_mode")

    if not mode:
        if product_type == "edd_paid":
            mode = "paid"
        elif profile.get("license_required") is True:
            mode = "free_registered"
        else:
            mode = "free_download"
        profile["license_mode"] = mode

    if mode not in LICENSE_MODES:
        print(f"PROFILE_ERROR license_mode: unsupported license mode: {mode}", file=sys.stderr)
        raise SystemExit(2)

    required = mode in {"paid", "free_registered"}
    if "license_required" not in profile:
        profile["license_required"] = required
    elif bool(profile["license_required"]) != required:
        print(
            f"PROFILE_ERROR license_required: {mode} requires license_required={str(required).lower()}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if product_type == "edd_paid" and mode != "paid":
        print("PROFILE_ERROR license_mode: edd_paid products must use paid", file=sys.stderr)
        raise SystemExit(2)
    if product_type == "free" and mode == "paid":
        print("PROFILE_ERROR license_mode: free products cannot use paid", file=sys.stderr)
        raise SystemExit(2)

    if required:
        if not profile.get("edd_download_id") or not profile.get("edd_store_url"):
            print(
                f"PROFILE_ERROR {mode} requires edd_download_id and edd_store_url",
                file=sys.stderr,
            )
            raise SystemExit(2)
        profile.setdefault("update_source", "edd")
    elif mode == "free_download":
        profile.setdefault("update_source", "github_releases" if profile.get("update_repository") else "github_releases")

    if profile.get("update_source") == "github_releases" and not profile.get("update_repository"):
        # Keep legacy profiles valid when they have not opted into an updater yet.
        # Once update_repository is supplied, scaffold/update tooling can enforce the installable asset contract.
        profile.pop("update_source", None)

    return profile


def validate_profile(path: Path) -> dict:
    schema = load_json(SCHEMA_PATH)
    profile = load_json(path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(profile), key=lambda error: list(error.absolute_path))
    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            print(f"PROFILE_ERROR {location}: {error.message}", file=sys.stderr)
        raise SystemExit(2)

    profile = normalize_license_contract(profile)

    if profile.get("telemetry", "off") == "opt_in" and not profile.get("external_api"):
        print("PROFILE_ERROR telemetry opt_in requires external_api=true", file=sys.stderr)
        raise SystemExit(2)

    data_contract = profile.get("data_contract") or {}
    for field in ("options", "site_options"):
        for option_name in data_contract.get(field, []):
            if SENSITIVE_OPTION_PATTERN.search(option_name):
                print(
                    f"PROFILE_ERROR data_contract.{field}: sensitive option cannot be exported automatically: {option_name}",
                    file=sys.stderr,
                )
                raise SystemExit(2)

    return profile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    profile = validate_profile(args.profile)
    print(
        f"PASS profile={profile['slug']} type={profile['product_type']} "
        f"license_mode={profile['license_mode']} license_required={str(profile['license_required']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
