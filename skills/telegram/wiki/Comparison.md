# Comparison

Full document: [docs/COMPARISON.md](https://github.com/Zulut30/telegram-skills/blob/main/docs/COMPARISON.md).

## Quick table

| | Plain LLM prompt | cookiecutter-aiogram | no-code (BotFather templates) | BotForge |
|---|---|---|---|---|
| Architecture | Monolith | Fixed template | Locked platform | Layered, enforced |
| Secrets handling | Hardcoded | .env | Platform | .env + pydantic-settings |
| Database | Usually none | SQLAlchemy | Managed opaque | SQLAlchemy async + Alembic |
| Payments | Free-form | Mostly ЮKassa only | Platform-limited | Unified 5 providers |
| Rate limits | Ignored | Usually correct | N/A | Enforced (25 msg/s) |
| Mini Apps | Insecure HMAC | Rarely covered | Rare | First-class + JWT |
| Extendability | Breaks at 3rd feature | Requires manual | UI-limited | Diff-aware |
| Code ownership | Yours | Yours | Platform | Yours |
| Vendor lock-in | None | None | High | None |

## vs python-telegram-bot

BotForge defaults to aiogram 3, but choice is orthogonal.

| | python-telegram-bot | aiogram 3 (BotForge default) |
|---|---|---|
| Async model | Since v20 | Async-first day one |
| Router / Blueprint | Application + handlers | First-class Router |
| FSM | External persistence | Built-in (Redis/Memory/Mongo) |
| Middleware | TypeHandler + JobQueue | Dedicated pipeline |
| Typing | Improving | Strict throughout |
| CallbackData | Manual string parsing | Pydantic-like factories |
| Community size | Largest | Second, RU-heavy, fast-growing |

Use PTB if: existing PTB codebase, need rich JobQueue, team expertise.
Use BotForge+aiogram if: new project, strong typing matters, FastAPI mental model.

BotForge **can** generate PTB code — must be justified in ADR stage.

## When NOT to use BotForge

- One-off toy bot, never deployed
- Bot with <10 users, no payments
- Team has proprietary Telegram framework
- Non-Python stack (Node / Go / Rust)
