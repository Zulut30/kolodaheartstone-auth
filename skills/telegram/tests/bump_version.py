"""Bump version across VERSION, plugin.json, and CHANGELOG scaffolding.

Usage:
    python tests/bump_version.py patch      # 1.5.0 → 1.5.1
    python tests/bump_version.py minor      # 1.5.0 → 1.6.0
    python tests/bump_version.py major      # 1.5.0 → 2.0.0
    python tests/bump_version.py 1.7.2      # explicit

Prints new version. Does NOT commit or tag — intentional, so you can review.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys


def current() -> tuple[int, int, int]:
    raw = pathlib.Path("VERSION").read_text(encoding="utf-8").strip()
    parts = [int(p) for p in raw.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])  # type: ignore[return-value]


def bump(level: str) -> tuple[int, int, int]:
    major, minor, patch = current()
    match level:
        case "major":
            return (major + 1, 0, 0)
        case "minor":
            return (major, minor + 1, 0)
        case "patch":
            return (major, minor, patch + 1)
        case _:
            if re.fullmatch(r"\d+\.\d+\.\d+", level):
                return tuple(int(p) for p in level.split("."))  # type: ignore[return-value]
            raise SystemExit(f"unknown level: {level!r} (use major|minor|patch|X.Y.Z)")


def write_version_file(v: tuple[int, int, int]) -> None:
    pathlib.Path("VERSION").write_text(".".join(map(str, v)) + "\n", encoding="utf-8")


def update_plugin_manifest(v: tuple[int, int, int]) -> None:
    path = pathlib.Path(".claude-plugin/plugin.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["version"] = ".".join(map(str, v))
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


#: Human-readable version strings shaped as `**Version:** X.Y.Z` that should
#: track VERSION. Files using a shorter `v{major}.{minor}` label (system_prompt,
#: cursor rules, codex/AGENTS.md) stay on the minor line by convention.
_VERSION_HEADER_RE = re.compile(
    r"^(\*\*Version:\*\*\s*)\d+\.\d+\.\d+", re.MULTILINE
)
_VERSION_HEADER_TARGETS: tuple[pathlib.Path, ...] = (
    pathlib.Path(".claude/skills/botforge/SKILL.md"),
    pathlib.Path("SKILL.md"),
)


def update_skill_md_version(v: tuple[int, int, int]) -> list[pathlib.Path]:
    """Patch `**Version:** X.Y.Z` lines in SKILL.md files to the new version."""
    new_str = ".".join(map(str, v))
    patched: list[pathlib.Path] = []
    for path in _VERSION_HEADER_TARGETS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = _VERSION_HEADER_RE.subn(
            rf"\g<1>{new_str}", text, count=1
        )
        if n and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            patched.append(path)
    return patched


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    level = sys.argv[1]
    new = bump(level)
    new_str = ".".join(map(str, new))

    write_version_file(new)
    update_plugin_manifest(new)
    patched = update_skill_md_version(new)

    print(f"Bumped to {new_str}")
    for p in patched:
        print(f"  patched header in {p}")
    print("Remember to:")
    print(f"  1. Prepend a new section to docs/CHANGELOG.md: ## v{new_str} — YYYY-MM-DD")
    print("  2. Commit: git commit -am 'chore: bump version to " f"{new_str}'")
    print(f"  3. Tag:    git tag v{new_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
