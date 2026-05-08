# Examples

Reference implementations generated through BotForge. All code is in the [`examples/`](https://github.com/Zulut30/skills/tree/main/examples) directory of the main repo.

## 01 — VIP Media Bot ✅

**Status:** fully working, with tests.
**Location:** [`examples/01-vip-media-bot/`](https://github.com/Zulut30/telegram-skills/tree/main/examples/01-vip-media-bot)

A VIP bot for a media channel: gated content by channel subscription, VIP tier via Telegram Stars, admin `/stats`, rate-limited broadcasts.

**Stack:**
- aiogram 3.x, SQLAlchemy 2 async, Alembic
- PostgreSQL 16, Redis 7, Docker Compose
- Telegram Stars (XTR) payments
- Webhook mode

**Files:** ~25 Python modules + Docker + migrations + tests (pytest + aiosqlite).

**Tests cover:**
- SubscriptionService activation and extension
- PaymentService idempotent webhook handling
- ChannelCheckService with Redis cache
- UserService upsert idempotency
- Full repository lifecycle

**Run it:**
```bash
cd examples/01-vip-media-bot
cp .env.example .env   # set BOT_TOKEN, ADMIN_IDS, REQUIRED_CHANNELS
make up
make logs
```

## 02 — AI Assistant (planned)

**Status:** stub + DIY-guide in [`examples/02-ai-assistant/`](https://github.com/Zulut30/telegram-skills/tree/main/examples/02-ai-assistant)

Planned features: OpenAI/Anthropic integration with 3 tariffs (Free / Pro / Ultra), token limits per month in Redis, dialog history in Postgres, streaming responses, pgvector RAG for premium queries.

Generate your own today:
```
/botforge-new SaaS
Task: AI assistant on OpenAI with three tariffs, token limits per month,
dialog history in Postgres. Payment via ЮKassa. Host on Fly.io.
```

## 03 — Lead-gen Bot (planned)

**Status:** stub + DIY-guide in [`examples/03-lead-gen/`](https://github.com/Zulut30/telegram-skills/tree/main/examples/03-lead-gen)

Planned: FSM lead collection (name → phone → goal → confirm), Postgres + Google Sheets sync, admin notification, outbox pattern, UTM-tracking via signed deep-links, A/B welcome variants.

## Community showcase

Built a bot with BotForge? Submit via the [show-and-tell template](https://github.com/Zulut30/telegram-skills/discussions/new?category=show-and-tell) or open a PR editing [`docs/SHOWCASE.md`](https://github.com/Zulut30/telegram-skills/blob/main/docs/SHOWCASE.md).

## How the reference bot was generated

Single command in Claude Code with BotForge installed:

```
/botforge-new SaaS
Task: VIP bot for a cinema Telegram channel.
Gated content by channel subscription. VIP for 100 Stars / month.
Admin: stats + broadcasts. Hosting: VPS, Docker Compose, webhook.
```

The AI:
1. Asked 2 clarifying questions (skipped 3 that were answered)
2. Produced ADR — stack, data model, risks
3. Rendered the directory tree
4. Generated every file in dependency order
5. Ran self-review checklist
6. Gave deployment commands

Time: ~8 minutes of LLM output + manual review.
