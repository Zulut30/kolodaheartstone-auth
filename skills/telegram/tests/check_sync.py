"""Verify that the skill prompt stays in sync across its four distribution formats.

Files that must express the same core rules:
  1. .claude/skills/botforge/SKILL.md
  2. system_prompt.txt
  3. cursor/.cursor/rules/botforge.mdc
  4. cursor/.cursorrules
  5. codex/AGENTS.md

The check looks for key canonical phrases (hard bans, rate limits, critical
constraints). If one file drops a phrase the others still carry, drift is
detected and exit code is 1.

This is structural, not exact — wording can differ slightly, but every file
must mention the key concept.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Windows consoles default to cp1251/cp866 and choke on ✓/× in our output.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent

TARGETS = {
    "SKILL": ROOT / ".claude" / "skills" / "botforge" / "SKILL.md",
    "system_prompt": ROOT / "system_prompt.txt",
    "cursor_mdc": ROOT / "cursor" / ".cursor" / "rules" / "botforge.mdc",
    "cursor_legacy": ROOT / "cursor" / ".cursorrules",
    "codex": ROOT / "codex" / "AGENTS.md",
}

# Canonical concepts every file MUST mention (case-insensitive substring match).
REQUIRED_CONCEPTS: list[tuple[str, list[str]]] = [
    ("aiogram 3", ["aiogram"]),
    ("Python 3.12+", ["3.12"]),
    ("layered architecture — handlers layer", ["handlers"]),
    ("layered architecture — services layer", ["services"]),
    ("layered architecture — repositories layer", ["repositor"]),
    ("hard ban on blocking requests", ["requests"]),
    ("hard ban on secrets in code", ["secret"]),
    ("rate limit 25/s broadcast", ["25"]),
    ("rate limit 1/sec per user", ["1 msg/sec", "1/sec", "1 msg/s"]),
    ("callback_data 64 bytes", ["64"]),
    ("Telegram Bot API version reference", ["9.6", "Bot API"]),
    ("Mini App initData HMAC", ["initData", "WebAppData"]),
    ("Telegram Stars XTR currency", ["XTR"]),
    ("TelegramRetryAfter handling", ["RetryAfter", "retry_after"]),
    ("TelegramForbiddenError handling", ["Forbidden", "blocked"]),
    ("six-stage workflow", ["brief", "ADR", "self-review"]),
    ("mode keyword Pro", ["Pro"]),
    ("mode keyword Lite", ["Lite"]),
    ("mode keyword SaaS", ["SaaS"]),
    ("mode keyword Media", ["Media"]),
    ("bypass protocol", ["bypass"]),
    ("override protocol", ["override"]),
    ("recovery protocol", ["recovery"]),
    ("version header v1.7", ["v1.7", "1.7.0"]),
]


def load(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").lower()


def main() -> int:
    contents = {name: load(p) for name, p in TARGETS.items()}
    missing_files = [n for n, c in contents.items() if not c]
    if missing_files:
        for n in missing_files:
            print(f"✗ file missing: {TARGETS[n]}")
        return 1

    errors: list[str] = []
    for concept_name, needles in REQUIRED_CONCEPTS:
        for file_name, text in contents.items():
            if not any(n.lower() in text for n in needles):
                errors.append(f"{file_name}: missing concept '{concept_name}'")

    if errors:
        print("Four-format sync drift detected:\n")
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n{len(errors)} drift(s). Fix files listed in docs/SYNC-CHECKLIST.md")
        return 1

    print(f"✓ Four-format sync OK ({len(REQUIRED_CONCEPTS)} concepts × {len(TARGETS)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
