# Growth Kit — seeded issues and discussions

Ready-to-post content to kickstart community engagement. Copy–paste into GitHub.

## Issues to seed (good first issue)

### Issue 1 — Add /botforge-webhook troubleshooter
**Labels:** `good first issue`, `enhancement`, `command`

> Add `/botforge-webhook` slash command that diagnoses webhook setup: calls `getWebhookInfo`, checks `last_error_date`/`last_error_message`, verifies HTTPS, secret_token presence.
>
> **Files:** `.claude/commands/botforge-webhook.md`, update `plugin.json`, help.md.

### Issue 2 — Add Stripe subscription example to examples/
**Labels:** `good first issue`, `example`

> Implement full Stripe subscription flow as `examples/02-saas-stripe/` — mirror `01-vip-media-bot/` structure but replace Telegram Stars with Stripe. Use `subscriptions.md` reference.

### Issue 3 — Translate /botforge-help into PL/RU
**Labels:** `good first issue`, `docs`, `i18n`

> Currently `botforge-help.md` is in Russian/English mixed. Decide primary language (EN), translate to RU (`docs/ru/`) and PL (`docs/pl/`). See `i18n.md` reference for consistency rules.

### Issue 4 — Add `/botforge-channel-post` command
**Labels:** `help wanted`, `command`

> Bot that posts to channels from a managed interface. Build on `groups-and-channels.md` reference. Include scheduling via `scheduler.md`.

### Issue 5 — VS Code extension for BotForge
**Labels:** `help wanted`, `enhancement`, `ide`

> Package `.vscode/botforge-snippets.code-snippets` as a proper VS Code extension, publishable to the marketplace.

### Issue 6 — Business API reference
**Labels:** `help wanted`, `reference`

> Document Telegram Business API integration as `references/business-api.md`. Requires actual Business account to verify behavior. See Bot API 9.x docs.

### Issue 7 — Golden test: add `/botforge-refactor` case
**Labels:** `good first issue`, `testing`

> Add `tests/golden/prompts/04-refactor-monolith.txt` + assertions. Prompt should pass a messy monolith and check output lists blockers, proposes atomic PR plan, preserves public commands.

### Issue 8 — Reference: A/B testing framework
**Labels:** `enhancement`, `reference`

> Expand `analytics.md` with a dedicated section/file on A/B experiments: bucketing, variant exposure events, statistical significance guidance.

### Issue 9 — Document cost of bot generation
**Labels:** `docs`, `help wanted`

> Add `docs/COST.md` estimating token spend per bot generation: small (`/botforge-extend`), medium (`/botforge-new`), large (SaaS full scaffold). Update as models change.

### Issue 10 — Improve logo
**Labels:** `design`, `help wanted`

> Current `assets/logo/logo.svg` is a placeholder checkmark. Design brief: combine Telegram paper-plane motif with forge/engineering cue (anvil/hammer). Keep SVG source + export PNGs.

## Discussions to seed

### 🎉 v1.7 released — here's what's new
**Category:** Announcements

> Long-form post: recap the releases that got us here (1.0 → 1.7).
> Link to CHANGELOG, SHOWCASE, QUICKSTART. Ask for feedback on v1.8 priorities.

### What are you building with BotForge?
**Category:** Show and tell

> Seed with a description of the reference `examples/01-vip-media-bot/`, invite submissions.

### Poll: which payment provider should we deepen next?
**Category:** Polls

> Options: CryptoBot, Stripe subscriptions, Tribute, Ozon Pay, WaaS.
> Drives roadmap.

### Do you prefer the 6-stage workflow to feel lighter for small changes?
**Category:** Ideas

> Opens debate on the "escape hatch" gap identified in audits.

### Tips and tricks — share your favorite BotForge workflows
**Category:** Tips

> Seed with 3 power-user patterns: chaining commands, reusing ADRs across bots, review-then-refactor loops.

## Social post templates

### Twitter/X launch

> Just shipped BotForge v1.7 🛠️
>
> A skill that turns Claude Code / Cursor / Codex into a senior Telegram bot engineer.
>
> • 19 slash commands
> • 23 reference modules
> • Grounded in Bot API 9.6
> • Working example with tests
> • MIT, no lock-in
>
> https://github.com/Zulut30/telegram-skills

### Telegram channel announcement

> **BotForge v1.7 — AI делает production-ready Telegram-ботов**
>
> Skill для Claude Code, Cursor и Codex. Вместо одноразового main.py — слоёная архитектура, Postgres, Docker, платежи (Stars/ЮKassa/Stripe), Mini Apps.
>
> • 19 slash-команд
> • 23 reference-модулей
> • Опирается на официальный Bot API 9.6
> • Tested example bot
>
> **Документация:** github.com/Zulut30/telegram-skills
> **Quickstart:** 5 минут от нуля до бота

### Reddit r/TelegramBots

> **Title:** [Project] BotForge — a Claude Code skill that builds production-ready aiogram 3 bots
>
> After my third handmade Telegram bot turned into an 800-line main.py, I built a skill that forces an AI assistant to produce layered architecture, Docker, Alembic, payments, and deployment — in one generation.
>
> Grounded in Bot API 9.6. Supports Telegram Stars, ЮKassa, Stripe, CryptoBot. MIT.
>
> Would love feedback on the architecture choices in the reference modules.
>
> https://github.com/Zulut30/telegram-skills
