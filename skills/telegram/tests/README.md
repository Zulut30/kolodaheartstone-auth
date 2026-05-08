# Golden-output tests

Tests that verify the skill produces outputs matching its promise: layered architecture, no monoliths, no secrets in code, proper rate limits.

## How it works

1. Each test case in `tests/golden/prompts/` is a user prompt directed at a BotForge-enabled LLM.
2. The expected structural properties are declared in `tests/golden/assertions/` as YAML.
3. The runner (`run_golden.py`) calls an LLM with the BotForge system prompt + the user prompt, then checks the output against assertions.

Assertions are **structural**, not exact-match — the LLM can vary wording but must produce:
- Specific section headings (ADR, Tree, Self-review)
- Forbidden patterns must be absent (`import requests`, `session.execute` inside handlers/, etc.)
- Required patterns must be present (`pydantic-settings`, `alembic`, `async def`)

## Run locally

```bash
pip install anthropic pyyaml
export ANTHROPIC_API_KEY=sk-...
python tests/run_golden.py
```

Exit code 0 if all cases pass, 1 otherwise.

## Assertion types

| Type | Meaning |
|---|---|
| `contains_sections` | Headers/phrases that must appear |
| `forbidden_patterns` | Regex patterns that must NOT appear |
| `required_patterns` | Regex patterns that must appear |
| `min_code_blocks` | Minimum fenced code blocks |
| `mentions_modes` | Output mentions the requested mode keyword |

## Adding a new case

1. `tests/golden/prompts/<name>.txt` — the user prompt
2. `tests/golden/assertions/<name>.yml` — expectations

Keep prompts self-contained (no prior-session context needed).

## CI

Runs on PRs to `main` via `.github/workflows/golden.yml` (opt-in: requires `ANTHROPIC_API_KEY` repo secret). Skips gracefully if secret absent.
