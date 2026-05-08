<p align="center">
  <img src="assets/logo/logo.svg" width="128" alt="BotForge logo" />
</p>

<h1 align="center">BotForge</h1>

<p align="center">
  <b>The Telegram Bot Engineering Skill for AI</b><br/>
  Production-ready skill pack for Claude Code, Codex, Cursor, and any LLM.
</p>

<p align="center">
  <b>English</b> · <a href="docs/ru/README.md">Русский</a> · <a href="docs/pl/README.md">Polski</a>
</p>

<p align="center">
  <a href="https://zulut30.github.io/telegram-skills/"><b>Website</b></a> ·
  <a href="https://github.com/Zulut30/telegram-skills/wiki"><b>Wiki</b></a> ·
  <a href="docs/QUICKSTART.md">Quickstart</a> ·
  <a href="docs/INSTALL.md">Install</a> ·
  <a href="docs/USAGE.md">Usage</a> ·
  <a href="docs/COMPARISON.md">Compare</a> ·
  <a href="docs/SHOWCASE.md">Showcase</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-compatible-8A2BE2" alt="Claude Code"/></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-rules-000000" alt="Cursor"/></a>
  <a href="https://openai.com"><img src="https://img.shields.io/badge/Codex-AGENTS.md-10A37F" alt="Codex"/></a>
  <a href="https://docs.aiogram.dev/"><img src="https://img.shields.io/badge/aiogram-3.x-2CA5E0" alt="aiogram"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB" alt="Python"/></a>
  <a href="https://core.telegram.org/bots/api"><img src="https://img.shields.io/badge/Bot%20API-9.6-0088CC" alt="Bot API"/></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"/></a>
</p>

---

BotForge turns an AI assistant into a senior Telegram bot engineer. Instead of a one-shot `main.py` with 800 lines of tangled code, the AI designs and builds a **modular, scalable, production-ready Telegram bot** — with architecture, database, migrations, admin panel, payments, broadcasts, Docker, and deployment.

## Three promises

1. **No monoliths.** Layered architecture (handlers / services / repositories / integrations) by default.
2. **No drafts.** Docker + Postgres + Alembic + `.env` + deployment instructions in the very first generation.
3. **No breakage.** The fifth feature is as easy to add as the first.

## Why it works

- **Grounded in the official Telegram Bot API 9.6.** Rate limits (1/sec, 20/min, 30/sec broadcast), MarkdownV2 escape rules, Mini App initData HMAC validation, 64-byte `CallbackData` limit — every constraint cites `core.telegram.org`.
- **Mandatory 6-stage workflow.** Brief → ADR → Tree → Files → Self-review → Deploy. The AI cannot skip straight to code.
- **Hard bans enforced by skill rules.** Secrets in code, `requests`, SQL in handlers, monoliths — blocked at the skill level, not by style.
- **Provider-agnostic payments.** Switching ЮKassa → Stripe is a one-line DI change.

## Quick start

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cp -r telegram-skills/.claude/skills/botforge ~/.claude/skills/
cp -r telegram-skills/.claude/commands ~/.claude/
```

In Claude Code:
```
/botforge-new SaaS
Task: course marketplace bot with VIP access for 499 RUB/month
Hosting: VPS, Docker Compose, webhook
```

The AI will ask up to 5 clarifying questions, produce an ADR, render the project tree, generate every file, run a self-review checklist, and give you deployment commands.

## 19 slash commands

```
Build & evolve:      /botforge-new /botforge-extend /botforge-review /botforge-refactor
Modules:             /botforge-miniapp /botforge-auth /botforge-payments
                     /botforge-broadcast /botforge-admin /botforge-admin-web
                     /botforge-scheduler /botforge-inline /botforge-i18n
Operations:          /botforge-test /botforge-deploy /botforge-security
                     /botforge-botfather /botforge-observability /botforge-help
```

## Working example

[`examples/01-vip-media-bot/`](examples/01-vip-media-bot/) — a VIP bot on Telegram Stars, 25 Python files, everything the skill prescribes.

```bash
cd examples/01-vip-media-bot
cp .env.example .env   # set BOT_TOKEN, ADMIN_IDS
make up
```

## Four modes

| Mode | When | Differences |
|---|---|---|
| **Lite** | MVP in an evening | SQLite, polling, no Docker |
| **Pro** (default) | Commercial bot | Full production standard |
| **Media** | Content / channels | + CMS sync, segmented broadcasts, UTM |
| **SaaS** | Subscriptions / VIP | + billing, multi-provider payments, admin metrics |

## What's in the box

| File | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Full skill document — manifest, system prompt, rules, patterns, examples |
| [`system_prompt.txt`](system_prompt.txt) | Raw system prompt for any LLM |
| [`.claude/skills/botforge/`](.claude/skills/botforge/) | **Claude Code** Agent Skill with 23 references |
| [`.claude/commands/`](.claude/commands/) | 19 slash commands |
| [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) | Plugin manifest |
| [`cursor/.cursor/rules/botforge.mdc`](cursor/.cursor/rules/botforge.mdc) | **Cursor** rules (modern MDC) |
| [`codex/AGENTS.md`](codex/AGENTS.md) | **Codex / Aider / Continue** |
| [`.vscode/`](.vscode/) | VS Code snippets (`bf-new`, `bf-extend`, …) |
| [`.zed/`](.zed/) | Zed configuration |
| [`tests/golden/`](tests/golden/) | Eval harness: structural assertions on AI output |
| [`examples/`](examples/) | Working bot examples |

## Documentation

- [QUICKSTART](docs/QUICKSTART.md) — 5 minutes from zero to bot
- [INSTALL](docs/INSTALL.md) — detailed per-tool setup
- [USAGE](docs/USAGE.md) — modes, prompt formats, session lifecycle
- [COMPARISON](docs/COMPARISON.md) — vs plain prompts, cookiecutter, no-code, generic agents
- [SHOWCASE](docs/SHOWCASE.md) — bots built with BotForge
- [CHANGELOG](docs/CHANGELOG.md) — version history and roadmap

## Reference library

23 deep reference documents covering every aspect of Telegram bot engineering: architecture, 12 reusable patterns, Mini Apps, auth (roles / initData / OAuth / API keys), payments (5 providers), official Bot API 9.6 constraints, BotFather setup, i18n, observability, scheduled tasks, recurring subscriptions, inline mode, groups/channels/forums, media handling, anti-spam, GDPR compliance, analytics, anti-patterns, performance, admin panel, FAQ.

## License

MIT. Use freely in commercial projects.

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md). Pull requests welcome.
