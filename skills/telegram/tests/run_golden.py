"""Golden-output test harness for BotForge.

Runs each prompt against a BotForge-configured LLM and asserts structural
properties of the output. Exits non-zero on any failure.

Requires: ANTHROPIC_API_KEY (or OPENAI_API_KEY). Skips gracefully if neither set.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("Install pyyaml: pip install pyyaml")
    sys.exit(2)


ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "tests" / "golden" / "prompts"
ASSERTIONS_DIR = ROOT / "tests" / "golden" / "assertions"
SYSTEM_PROMPT_FILE = ROOT / "system_prompt.txt"


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")


def call_anthropic(system: str, user: str) -> str:
    import anthropic  # type: ignore[import-not-found]

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.environ.get("BOTFORGE_MODEL", "claude-opus-4-5"),
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if hasattr(block, "text"))


def call_openai(system: str, user: str) -> str:
    from openai import OpenAI  # type: ignore[import-not-found]

    client = OpenAI()
    resp = client.chat.completions.create(
        model=os.environ.get("BOTFORGE_MODEL", "gpt-5"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""


def call_llm(system: str, user: str) -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return call_anthropic(system, user)
    if os.environ.get("OPENAI_API_KEY"):
        return call_openai(system, user)
    raise RuntimeError("No ANTHROPIC_API_KEY or OPENAI_API_KEY in env")


def check_assertions(output: str, spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for section in spec.get("contains_sections") or []:
        if section.lower() not in output.lower():
            errors.append(f"missing section: '{section}'")

    for pattern in spec.get("required_patterns") or []:
        if not re.search(pattern, output, flags=re.IGNORECASE):
            errors.append(f"missing required pattern: {pattern!r}")

    for pattern in spec.get("forbidden_patterns") or []:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            errors.append(f"forbidden pattern present: {pattern!r} ({match.group()!r})")

    min_blocks = spec.get("min_code_blocks")
    if min_blocks is not None:
        count = output.count("```") // 2
        if count < min_blocks:
            errors.append(f"code blocks: got {count}, need ≥ {min_blocks}")

    for mode in spec.get("mentions_modes") or []:
        if mode.lower() not in output.lower():
            errors.append(f"output does not mention mode: {mode}")

    return errors


def run() -> int:
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        print("⏭  No API key in env — skipping golden tests.")
        return 0

    system = load_system_prompt()
    failed: list[str] = []
    total = 0

    for prompt_file in sorted(PROMPTS_DIR.glob("*.txt")):
        total += 1
        name = prompt_file.stem
        spec_file = ASSERTIONS_DIR / f"{name}.yml"
        if not spec_file.exists():
            print(f"⚠  {name}: no assertion file, skipping")
            continue
        spec = yaml.safe_load(spec_file.read_text(encoding="utf-8"))

        print(f"▶  {name} — {spec.get('name', '')}")
        try:
            output = call_llm(system, prompt_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"   ✗ LLM call failed: {e}")
            failed.append(name)
            continue

        errors = check_assertions(output, spec)
        if errors:
            print(f"   ✗ FAIL ({len(errors)} errors):")
            for err in errors:
                print(f"     · {err}")
            failed.append(name)
        else:
            print("   ✓ PASS")

    print()
    print(f"Results: {total - len(failed)}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
