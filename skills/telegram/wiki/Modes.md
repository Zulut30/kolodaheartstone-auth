# Modes

Four modes cover the spectrum from weekend MVP to enterprise SaaS.

Set mode as the first line of your prompt: `BotForge: SaaS`. Default is `Pro`.

## Lite — MVP per evening

**When:** Proof-of-concept, throwaway bot, 1-2 features, no payment.

**Stack:**
- SQLite (aiosqlite)
- Polling (no webhook)
- No Docker
- No Alembic (auto-create tables)
- Minimal layers: handlers, services, repos, optional middlewares

**Time to first message:** ~30 minutes

**Trade-offs:**
- Cannot scale beyond one instance
- Migrating data later is manual
- No production-grade error handling

**Good for:**
- Hackathons
- Internal tools for a team of <10
- Testing a business idea

## Pro — Commercial bot (default)

**When:** Paying client, public product, long-term maintenance.

**Stack:**
- Python 3.12+
- aiogram 3.x
- PostgreSQL + SQLAlchemy async + Alembic
- Redis for FSM, throttling, caches
- Docker multi-stage + docker-compose
- webhook at HTTPS
- structlog JSON + errors handler

**Time to first message:** ~2-3 hours (setup + BotFather + deploy)

**Expected lifetime:** Years. Adding new features doesn't require rewrites.

**Good for:**
- Most commercial bots
- Growing audiences (10k+ MAU)
- Client work

## Media — Content & channels

**On top of Pro, adds:**
- CMS sync (WordPress, Notion, Airtable)
- Segmented broadcasts (by lang, tier, behavior)
- UTM tracking via signed deep-links
- Scheduled publishing
- Media group helpers
- Reactions and polls

**When:**
- Bot distributes content from your channel
- VIP tier inside Telegram
- Content gated by channel subscription

**Example:** Cinema review channel with VIP picks, weekly broadcasts, interactive polls.

## SaaS — Subscriptions & VIP

**On top of Pro, adds:**
- Plans (Free / Pro / Ultra)
- Trials with expiration
- Proration on upgrade/downgrade
- Multi-provider payments (Stars + ЮKassa + Stripe + CryptoBot)
- Dunning (failed-payment retry ladder)
- Admin metrics dashboard (MRR, churn, LTV)
- Invite-link rotation for closed channels
- Feature flags

**When:**
- Recurring revenue
- Access control to a closed group/channel
- Metrics-driven business

**Example:** Paid community access, online course subscription, B2B SaaS with Telegram dashboard.

## How modes interact with commands

Most slash commands work across all modes, but outputs differ:

| Command | Lite output | Pro output | SaaS output |
|---|---|---|---|
| `/botforge-new` | SQLite, polling, no Docker | Postgres + Redis + Docker | + billing engine + plans |
| `/botforge-payments` | Stars only | Stars + one provider | Multi-provider unified |
| `/botforge-admin` | `/stats` inline | Full inline panel | Mini App panel with metrics |
| `/botforge-observability` | Stdout logs | structlog + Sentry | + Prometheus + Grafana |

## Switching modes mid-project

Not automatic. Upgrading Lite → Pro is a meaningful refactor — use `/botforge-refactor` and it'll produce a PR-sequence plan.

Going Pro → SaaS is usually additive: add plans table, payment provider abstraction, billing service. Use `/botforge-extend`.
