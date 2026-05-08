# Quickstart

From zero to a production-ready Telegram bot in 5 minutes.

## Prerequisites

- Claude Code / Cursor / Codex / any LLM tool
- Python 3.12+
- Docker + Docker Compose
- Telegram `BOT_TOKEN` from [@BotFather](https://t.me/BotFather) (`/newbot`)

## 1. Install the skill

**One-liner (any target):**
```bash
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash
```

Targets: `claude` (default, global), `claude-project`, `cursor`, `codex`, `system-prompt`.

**Self-test before installing:**
```bash
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- --check
```

## 2. Try the reference bot (no AI needed)

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cd telegram-skills/examples/01-vip-media-bot
cp .env.example .env
# edit .env: BOT_TOKEN, ADMIN_IDS=[<your tg_id>]
make up
make logs
```

Send `/start` to your bot in Telegram.

## 3. Generate your own bot with AI

In Claude Code / Cursor / Codex:

```
/botforge-new SaaS
Task: course marketplace bot with VIP access for 499 RUB/month
Hosting: VPS, Docker Compose, webhook
```

The skill enforces the 6-stage workflow:
1. **Brief** — up to 5 clarifying questions
2. **ADR** — architecture decision record (<250 words)
3. **Project tree** — full directory before any file content
4. **Files** — in dependency order
5. **Self-review** — checkbox audit
6. **Deploy** — concrete commands

## 4. Extend

```
/botforge-extend add referral program with 20% discount
```

## 5. Deploy

```
/botforge-deploy fly webhook
```

## Next

- [Commands Reference](Commands-Reference) — all 19 slash commands
- [Architecture](Architecture) — why layered design, what's banned
- [Examples](Examples) — working bots
