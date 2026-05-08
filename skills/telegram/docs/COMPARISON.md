# Comparison — BotForge vs alternatives

## vs plain prompt to ChatGPT / Claude

| | Plain prompt | BotForge |
|---|---|---|
| Architecture | Monolith, 1 file | Layered (handlers/services/repos) |
| Secrets | Hardcoded in code | `.env` + pydantic-settings |
| Database | Often none / raw SQL | SQLAlchemy async + Alembic |
| Payments | Free-form snippets | Unified `PaymentProvider` (5 providers) |
| Rate limits | Ignored | 25 msg/s broadcast, 1/sec per user |
| Error handling | bare `try/except` | Differentiated for `RetryAfter`/`Forbidden`/`BadRequest` |
| Webhook | Polling by default | Webhook + `secret_token` + `allowed_updates` |
| Docker | Sometimes | Always multi-stage + compose with healthchecks |
| Extendability | Break on 3rd feature | Stable through 5+ iterations |
| Output consistency | Depends on luck | 6-stage workflow enforced |

## vs cookiecutter-aiogram / bot-templates

| | cookiecutter / templates | BotForge |
|---|---|---|
| Customization | Fixed template | AI adapts per business brief |
| Mini Apps | Rarely covered | First-class: initData HMAC + JWT + React skeleton |
| Payments | Usually ЮKassa only | Stars / ЮKassa / CryptoBot / Stripe / Tribute unified |
| Scheduled tasks | Manual | `/botforge-scheduler` (APScheduler / arq / cron) |
| i18n | Not included | `/botforge-i18n` with gettext + Babel |
| Observability | No | `/botforge-observability` — structlog / Sentry / Prometheus |
| Extension | Manual refactor | `/botforge-extend` — diff-aware |
| Code review | — | `/botforge-review` with `[blocker]/[major]/[minor]/[nit]` |
| Starts from | Empty template | Business brief + ADR |

## vs BotFather bot templates / constructor services

| | BotFather / no-code | BotForge |
|---|---|---|
| Code ownership | Locked in platform | Your repo, your infra |
| Extensibility | Limited UI features | Unlimited (Python code) |
| DB | Managed, opaque | Your Postgres, your schema |
| Integrations | Platform-limited | Anything Python can call |
| Hosting | Platform | VPS / Fly / Railway / any |
| Payments | Platform fees | Direct to your account |
| Custom domain | Rare | Always yours |
| Vendor lock-in | High | None |

## vs "just use GPT Engineer / AutoGPT" for bots

| | Generic agents | BotForge |
|---|---|---|
| Domain knowledge | General coding | Telegram Bot API 9.6 specific |
| Rate limit awareness | No | Yes (1/sec, 20/min, 30/sec) |
| MarkdownV2 escape | Maybe | Enforced |
| Mini App HMAC | Usually missing / insecure | Official spec from `core.telegram.org` |
| Provider-agnostic payments | No | Yes |
| Self-review | Freeform | Structured checklist |

## vs python-telegram-bot (PTB)

The most popular Python framework worldwide. BotForge defaults to aiogram 3, but the choice is orthogonal: you can pick PTB if you need to, BotForge will still enforce layered architecture.

| | python-telegram-bot | aiogram 3 (BotForge default) |
|---|---|---|
| Async model | Async since v20 | Async-first from day one |
| Router/Blueprint | `Application` + handlers | First-class `Router` with includes |
| FSM | External persistence | Built-in (Redis/Mongo/Memory) |
| Middleware | `TypeHandler`, JobQueue | Dedicated pipeline (FastAPI-like) |
| Type hints | Improving, historically lax | Strict, every method typed |
| CallbackData | Manual string parsing | Pydantic-like factories |
| Community size | Largest | Second, fast-growing, RU-heavy |
| Breaking-change cadence | Conservative | Faster (3.x had major jumps) |

**When to stay on PTB:**
- Existing PTB codebase; don't rewrite just for aiogram.
- You need rich `JobQueue` out-of-box (PTB ships more here).
- Team expertise is deeply PTB.

**When BotForge + aiogram is better:**
- New project, no legacy.
- You want modern async patterns mirroring FastAPI mental model.
- Strong typing matters to your team.

**Can BotForge generate PTB code?** Yes, non-default. The ADR stage must justify PTB choice; layer structure (handlers / services / repositories) is identical — only framework-specific bits change.

## When NOT to use BotForge

- One-off toy bot, never deployed — `/botforge-new Lite` is still overkill; write a 50-line script.
- Bot with <10 users and no payments — Lite mode is enough, Pro is overhead.
- Team already has a proprietary Telegram framework in production — BotForge's philosophy may not match.
- Non-Python stack (Node / Go / Rust) — BotForge is aiogram-focused. Principles transfer, code doesn't.
