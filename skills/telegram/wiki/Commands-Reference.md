# Commands Reference

19 slash commands covering the full lifecycle of a Telegram bot.

## Build & evolve

### `/botforge-new [Lite|Pro|Media|SaaS] <description>`
Create a new bot from scratch. Full 6-stage workflow.

**Example:**
```
/botforge-new SaaS
Task: subscription bot for a course marketplace, ЮKassa payments
Hosting: Fly.io, webhook
```

### `/botforge-extend <feature description>`
Add a feature to an existing bot without breaking architecture.

**Example:**
```
/botforge-extend add referral program — 20% discount for inviter after friend's first payment
```

### `/botforge-review [path]`
Code review using `[blocker] [major] [minor] [nit]` classification.

**Example:**
```
/botforge-review app/services/payment_service.py
```

### `/botforge-refactor <context>`
Turn a monolith into layered architecture. Produces PR-sequence plan with zero-downtime migration.

## Modules

### `/botforge-miniapp <description>`
Add a Telegram Mini App: FastAPI backend + React/Vue frontend + initData HMAC + JWT.

### `/botforge-auth [roles|miniapp|oauth|api-keys|all]`
Add an auth layer: roles, ban, initData validation, OAuth bridging, internal API keys.

### `/botforge-payments [stars|yookassa|cryptobot|stripe|tribute] <product>`
Wire up a payment provider via the unified `PaymentProvider` interface.

### `/botforge-broadcast [simple|segmented|ab-test|scheduled]`
Broadcast system with admin FSM, rate-limiting (25 msg/s), error-tolerant delivery.

### `/botforge-admin [inline|webapp|both]`
Admin panel: stats, user management, broadcasts, settings, audit log.

### `/botforge-admin-web`
Full web admin dashboard: React 19 + Vite + Tailwind + shadcn/ui frontend,
FastAPI backend sharing code with the bot, JWT auth with roles, SSE real-time
updates for payments and broadcast progress.

### `/botforge-scheduler [apscheduler|arq|cron] [task]`
Scheduled tasks: expire subscriptions, reminders, deferred broadcasts, hourly stats.

### `/botforge-inline <description>`
Inline mode (`@botname query`) with pagination and `chosen_inline_result` analytics.

### `/botforge-i18n <ru,en,pl,...>`
Multi-language via gettext + Babel. Language detection priority: user choice → `language_code` → default.

## Operations

### `/botforge-test [unit|integration|all|path]`
Test suite: pytest + aiogram mocks + testcontainers for real Postgres in integration.

### `/botforge-deploy [docker|fly|railway|vps] [polling|webhook]`
Deployment preparation: Dockerfile, compose, fly.toml, Caddyfile, healthchecks, rollback.

### `/botforge-security [all|auth|payments|miniapp|data]`
Security audit with `[critical|high|medium|low]` findings.

### `/botforge-botfather <bot description>`
BotFather setup checklist + generated `description`, `about`, commands, privacy mode recommendation.

### `/botforge-observability [minimal|standard|full]`
Logging, Sentry, Prometheus metrics, health probes, audit log, alert rules.

### `/botforge-help`
Show this list.

## Composing commands

Build a full SaaS bot in one session:

```
/botforge-new SaaS course marketplace with VIP
/botforge-payments yookassa 499 RUB/month subscription
/botforge-miniapp catalog + profile page
/botforge-admin webapp
/botforge-observability standard
/botforge-test unit
/botforge-deploy fly webhook
/botforge-security all
```

Each command is diff-aware — new ones add to the project without breaking what existed.

## Tips

- **Set mode explicitly** as the first line: `BotForge: SaaS` — the AI defaults to Pro.
- **Answer the brief in one message** to skip to ADR faster.
- **Use `/botforge-review` liberally** — it's cheaper than a broken production.
- **Save the ADR** to `docs/ADR/` in your bot's repo — it's your contract with future-you.
