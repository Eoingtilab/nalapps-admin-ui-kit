#!/usr/bin/env python3
"""Generate deterministic file hashes for a built plugin package directory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("release-provenance.json"))
    parser.add_argument("--version", default="")
    parser.add_argument("--commit", default="")
    args = parser.parse_args()

    root = args.package_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"Package root does not exist: {root}")

    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        files.append({"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size})

    payload = {
        "schema_version": "1.0",
        "version": args.version,
        "commit": args.commit,
        "package_root": root.name,
        "file_count": len(files),
        "files": files,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS release_manifest files={len(files)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
