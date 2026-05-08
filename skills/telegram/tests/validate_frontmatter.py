"""Validate that every slash-command file has valid YAML frontmatter.

Exits non-zero on any error. Run from repo root:
    python tests/validate_frontmatter.py
"""

from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("Install pyyaml: pip install pyyaml")
    sys.exit(2)


def main() -> int:
    errors: list[str] = []
    commands_dir = pathlib.Path(".claude/commands")
    if not commands_dir.exists():
        print(f"Directory not found: {commands_dir}")
        return 1

    for path in sorted(commands_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            errors.append(f"{path}: no frontmatter")
            continue

        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as err:
            errors.append(f"{path}: invalid YAML — {err}")
            continue

        if not isinstance(frontmatter, dict):
            errors.append(f"{path}: frontmatter not a mapping")
            continue

        if "description" not in frontmatter:
            errors.append(f"{path}: missing 'description' field")

    if errors:
        print("\n".join(errors))
        return 1

    print(f"All {len(list(commands_dir.glob('*.md')))} command files have valid frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
