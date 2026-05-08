# Quickstart — 5 minutes to a bot

## 0. Prerequisites

- Claude Code / Cursor / Codex (any one)
- Python 3.12+
- Docker + Docker Compose
- Telegram BOT_TOKEN (@BotFather → `/newbot`)

## 1. Install the skill

### Claude Code (recommended)
```bash
git clone https://github.com/Zulut30/telegram-skills.git
mkdir -p ~/.claude/skills
cp -r telegram-skills/.claude/skills/botforge ~/.claude/skills/
cp -r telegram-skills/.claude/commands ~/.claude/
```

### Cursor
```bash
cp telegram-skills/cursor/.cursor/rules/botforge.mdc <your-project>/.cursor/rules/
```

### Codex / Codex CLI
```bash
cp telegram-skills/codex/AGENTS.md <your-project>/AGENTS.md
```

## 2. Try the example (без AI)

```bash
cd telegram-skills/examples/01-vip-media-bot
cp .env.example .env
# edit: BOT_TOKEN=..., ADMIN_IDS=[123456789]
make up
make logs
```

Send `/start` to your bot in Telegram. Send `/stats` from an admin account.

## 3. Generate your own bot (with AI)

In Claude Code / Cursor / Codex:

```
/botforge-new SaaS
Задача: бот-витрина онлайн-курсов с VIP-доступом за 499 ₽/мес через ЮKassa.
Интеграции: WordPress (каталог курсов).
Хостинг: VPS, Docker Compose, webhook.
```

The AI will:
1. Ask up to 5 clarifying questions (skip if already specified)
2. Produce an ADR (stack, data model, risks)
3. Render the full project tree
4. Generate all files in dependency order
5. Run self-review checklist
6. Give deployment commands

## 4. Extend it

```
/botforge-extend добавь реферальную программу со скидкой 20%
```

## 5. Deploy

```
/botforge-deploy fly webhook
```

Follow the commands. First deploy — ~10 minutes.

---

## What's next

- [Full usage guide](USAGE.md) — modes, prompt formats, session lifecycle
- [Install details](INSTALL.md) — Claude Projects, API direct, VS Code
- [FAQ](../.claude/skills/botforge/references/faq.md) — troubleshooting
- [Examples](../examples/) — more working bots (coming soon)
