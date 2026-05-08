# Installation

BotForge ships for six tools. Each has the same underlying skill prompt + references, packaged in the format the tool expects.

## Claude Code (recommended)

### One-liner (global)
```bash
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash
```
Copies to `~/.claude/skills/botforge/` and `~/.claude/commands/`.

### Per-project
```bash
cd <your-project>
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- claude-project .
```
Also copies `.claude-plugin/plugin.json` so the project declares the plugin.

### Via plugin marketplace (when available)
```
/plugin install github:Zulut30/telegram-skills
```

## Cursor

```bash
cd <your-project>
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- cursor .
```
Copies `.cursor/rules/botforge.mdc` (modern MDC format).

Legacy: `.cursorrules` is also copied if it doesn't exist, for older Cursor versions.

## Codex / Codex CLI / Aider / Continue

```bash
cd <your-project>
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- codex .
```
Copies `AGENTS.md` to project root. Any tool that reads `AGENTS.md` picks it up.

## VS Code (without Claude Code)

Snippets-only approach:
```bash
mkdir -p <your-project>/.vscode
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/.vscode/botforge-snippets.code-snippets \
  -o <your-project>/.vscode/botforge-snippets.code-snippets
```

Then type `bf-new`, `bf-extend`, `bf-review`, `bf-miniapp`, `bf-pay` in any markdown buffer.

## Zed

Two paths: use Claude Code inside Zed, or copy the system prompt into Zed's Assistant role.
See [`.zed/README.md`](https://github.com/Zulut30/telegram-skills/blob/main/.zed/README.md).

## Anthropic / OpenAI API direct

Raw system prompt:
```bash
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- system-prompt .
```

Then in Python:
```python
from anthropic import Anthropic

client = Anthropic()
with open("botforge_system_prompt.txt") as f:
    system_prompt = f.read()

resp = client.messages.create(
    model="claude-opus-4-7",
    system=system_prompt,
    max_tokens=8000,
    messages=[{"role": "user", "content": "BotForge: Pro\nTask: ..."}],
)
```

## ChatGPT Custom GPT

1. Create new GPT → Configure → Instructions
2. Paste contents of [`system_prompt.txt`](https://github.com/Zulut30/telegram-skills/blob/main/system_prompt.txt)
3. Knowledge → upload `SKILL.md` + relevant `references/*.md`

## Verification

Send a test request:
```
BotForge: Pro
Task: simple echo bot to verify the skill is loaded.
```

If loaded correctly, the response starts with Stage 1 (Business Brief) or Stage 2 (ADR) — **not** with a `main.py` code block.

## Uninstall

```bash
rm -rf ~/.claude/skills/botforge
rm ~/.claude/commands/botforge-*.md
```
