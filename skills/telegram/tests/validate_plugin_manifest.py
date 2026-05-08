"""Validate plugin.json: required fields + every referenced file exists.

Exits non-zero on any error. Run from repo root:
    python tests/validate_plugin_manifest.py
"""

from __future__ import annotations

import json
import pathlib
import sys

REQUIRED_FIELDS = {"name", "version", "description", "skills", "commands"}


def main() -> int:
    manifest_path = pathlib.Path(".claude-plugin/plugin.json")
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        print(f"Invalid JSON: {err}")
        return 1

    missing = REQUIRED_FIELDS - manifest.keys()
    if missing:
        print(f"Missing required fields: {sorted(missing)}")
        return 1

    errors: list[str] = []

    for entry in manifest["commands"]:
        if not pathlib.Path(entry["path"]).exists():
            errors.append(f"command not found: {entry['path']}")

    for entry in manifest["skills"]:
        if not pathlib.Path(entry["path"]).exists():
            errors.append(f"skill not found: {entry['path']}")

    for path in manifest.get("references", []):
        if not pathlib.Path(path).exists():
            errors.append(f"reference not found: {path}")

    if errors:
        print("\n".join(errors))
        return 1

    n_cmd = len(manifest["commands"])
    n_skill = len(manifest["skills"])
    n_ref = len(manifest.get("references", []))
    print(f"plugin.json OK: {n_cmd} commands, {n_skill} skills, {n_ref} references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
