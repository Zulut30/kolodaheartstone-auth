"""Verify VERSION matches plugin.json, CHANGELOG, and SKILL.md headers.

Single source of truth: VERSION.
Exits non-zero if any of the tracked places disagree.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


_SKILL_HEADER_RE = re.compile(r"^\*\*Version:\*\*\s*(\d+\.\d+\.\d+)", re.MULTILINE)
_SKILL_HEADER_FILES = (
    pathlib.Path(".claude/skills/botforge/SKILL.md"),
    pathlib.Path("SKILL.md"),
)


def _skill_header_version(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    m = _SKILL_HEADER_RE.search(path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def main() -> int:
    version_file = pathlib.Path("VERSION").read_text(encoding="utf-8").strip()

    manifest = json.loads(
        pathlib.Path(".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    manifest_version = manifest["version"]

    changelog = pathlib.Path("docs/CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## v(\d+\.\d+(?:\.\d+)?)", changelog, re.MULTILINE)
    if not match:
        print("CHANGELOG: cannot find latest version header")
        return 1
    changelog_version = match.group(1)

    # plugin.json may carry a patch version (1.6.0), changelog may use minor (1.6)
    def normalize(v: str) -> tuple[int, ...]:
        parts = [int(p) for p in v.split(".")]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)

    versions: dict[str, tuple[int, ...]] = {
        "VERSION": normalize(version_file),
        "plugin.json": normalize(manifest_version),
        "CHANGELOG.md": normalize(changelog_version),
    }
    for path in _SKILL_HEADER_FILES:
        header = _skill_header_version(path)
        if header is not None:
            versions[str(path)] = normalize(header)

    if len(set(versions.values())) != 1:
        print("Version mismatch:")
        for src, v in versions.items():
            print(f"  {src}: {'.'.join(map(str, v))}")
        return 1

    print(f"Version sync OK: {version_file} ({len(versions)} sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
