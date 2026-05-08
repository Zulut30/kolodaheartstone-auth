# BotForge for Zed

Zed supports Claude Code skills natively. Two setup options:

## Option 1: via Claude Code integration

If you use Claude Code from Zed's Assistant:

```bash
cp -r <telegram-skills>/.claude/skills/botforge ~/.claude/skills/
cp <telegram-skills>/.claude/commands/*.md ~/.claude/commands/
```

Claude Code inside Zed will pick up the skill automatically.

## Option 2: as system prompt in Zed Assistant

Add a custom assistant role:

1. Open Zed → Assistant panel → Settings
2. Create a new role `BotForge`
3. Paste contents of [`system_prompt.txt`](../system_prompt.txt) as the system prompt
4. Select this role when you want to build Telegram bots

## Workspace settings

The `.zed/settings.json` in this repo sets Anthropic Opus as default,
associates `.mdc` files (Cursor MDC rules) with markdown, and configures
Python formatting for contributors.
