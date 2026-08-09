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


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


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

    if profile.get("telemetry", "off") == "opt_in" and not profile.get("external_api"):
        print("PROFILE_ERROR telemetry opt_in requires external_api=true", file=sys.stderr)
        raise SystemExit(2)

    if profile.get("product_type") == "edd_paid":
        if not profile.get("edd_download_id") or not profile.get("edd_store_url"):
            print("PROFILE_ERROR edd_paid requires edd_download_id and edd_store_url", file=sys.stderr)
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
    print(f"PASS profile={profile['slug']} type={profile['product_type']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
