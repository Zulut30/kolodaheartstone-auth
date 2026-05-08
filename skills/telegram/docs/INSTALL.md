# Installation

## Claude Code Plugin (recommended, one-click)

BotForge ships as a Claude Code plugin. Once plugin marketplaces land in your Claude Code build:

```
/plugin install github:Zulut30/telegram-skills
```

Or add to `.claude.json` → `plugins`:
```json
{
  "plugins": [
    { "source": "github:Zulut30/telegram-skills" }
  ]
}
```

## Claude Code (manual)

BotForge is packaged as a [Claude Code Agent Skill](https://docs.claude.com/claude-code) with YAML frontmatter. Claude will auto-load it when the user describes a Telegram-bot task.

### Global (available in every project)
```bash
git clone https://github.com/Zulut30/telegram-skills.git
mkdir -p ~/.claude/skills
cp -r telegram-skills/.claude/skills/botforge ~/.claude/skills/
```

### Per-project
```bash
cd <your-project>
git clone https://github.com/Zulut30/telegram-skills.git /tmp/tg-skills
mkdir -p .claude/skills
cp -r /tmp/tg-skills/.claude/skills/botforge .claude/skills/
```

Invoke: Claude auto-selects the skill when you describe a Telegram-bot task, or explicitly: `/skill botforge`.

## Claude Projects / Claude.ai

1. Open your Project → Settings → Project Instructions.
2. Paste contents of [`system_prompt.txt`](../system_prompt.txt).
3. Optionally upload `SKILL.md` and the `references/*.md` files to Project Knowledge.

## Cursor

```bash
cp telegram-skills/cursor/.cursorrules <your-project>/.cursorrules
```

Cursor automatically picks up `.cursorrules` from the project root. For newer Cursor versions using `.cursor/rules/*.mdc` format, create `.cursor/rules/botforge.mdc` with the same content plus YAML frontmatter:

```yaml
---
description: BotForge — Telegram bot engineering skill
globs: ["**/*.py"]
alwaysApply: true
---
```

## Zed

See [`.zed/README.md`](../.zed/README.md) — two paths: via Claude Code integration inside Zed, or as a custom Assistant role.

## VS Code (without Claude Code)

```bash
mkdir -p <your-project>/.vscode
cp telegram-skills/.vscode/botforge-snippets.code-snippets <your-project>/.vscode/
```

Type `bf-new`, `bf-extend`, `bf-review`, `bf-miniapp`, `bf-pay` in any markdown/plaintext buffer for structured BotForge prompts.

## OpenAI Codex / Codex CLI / Aider / Continue

Any tool that respects `AGENTS.md`:

```bash
cp telegram-skills/codex/AGENTS.md <your-project>/AGENTS.md
```

For ChatGPT Custom GPT:
1. Create GPT → Configure → Instructions
2. Paste [`system_prompt.txt`](../system_prompt.txt)
3. Knowledge → upload `SKILL.md`

## Anthropic / OpenAI API (custom integrations)

Use [`system_prompt.txt`](../system_prompt.txt) as the `system` message.

```python
from anthropic import Anthropic

client = Anthropic()
with open("system_prompt.txt") as f:
    system_prompt = f.read()

response = client.messages.create(
    model="claude-opus-4-7",
    system=system_prompt,
    max_tokens=8000,
    messages=[{"role": "user", "content": "BotForge: Pro\nЗадача: ..."}],
)
```

## Verification

After install, send a test request:

```
BotForge: Pro
Задача: простой бот-эхо для проверки установки.
```

If the skill is loaded correctly, the response will start with Stage 1 (Business Brief) or Stage 2 (ADR), NOT with a `main.py` code block.
