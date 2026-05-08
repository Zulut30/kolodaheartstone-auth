# Architecture

BotForge enforces a layered architecture. Not a suggestion — a hard rule inside the skill prompt.

## Layers

```
bot/          entrypoint, dispatcher, middlewares wiring
handlers/     Telegram-facing ONLY: parse update → call service → send reply
services/     business logic (framework-agnostic where possible)
repositories/ data access — the ONLY place ORM lives
models/       SQLAlchemy ORM declarations
schemas/      pydantic DTOs for service boundaries
keyboards/    inline + reply keyboard builders
states/       FSM state groups
middlewares/  auth, throttling, i18n, db-session injection
filters/      custom aiogram filters
integrations/ external API clients (OpenAI, Sheets, WordPress, payments)
config/       settings, logging, constants
utils/        pure helpers, no framework imports
migrations/   alembic
tests/
```

## Dependency flow

```
handler → service → repository → model
                 → integration → external API
```

**Never:**
- handler → repository
- service → handler
- model → service
- integration → handler or service

## Why this matters

### Handlers stay thin
Each handler is ≤ 20 lines. Its job is transport: unpack the update, call a service, send a reply. Every line of business logic in a handler is a blocker-level finding in `/botforge-review`.

### Services are testable without Telegram
A service doesn't know about `aiogram.types.Message`. It takes primitive inputs and returns primitive outputs. You can unit-test every business rule without mocking the Telegram client.

### Repositories are the ORM boundary
Want to swap SQLAlchemy for SQLModel? One layer to change. Raw SQL outside `repositories/` is a blocker.

### Integrations are provider-agnostic
`PaymentProvider` is an ABC. `StarsProvider`, `YookassaProvider`, `StripeProvider` implement it. Switching = one DI line.

## Hard bans

Things the skill refuses to generate:

- Business logic inside handlers
- Direct ORM / SQL outside `repositories/`
- Secrets or tokens in code
- `requests` or any blocking I/O
- Global mutable singletons beyond dispatcher/bot/engine
- Single-file bots (>80 lines except `bot/__main__.py`)
- `TODO: add later` stubs in a production scaffold
- Invented Telegram or aiogram 3 API

## Technical stack (Pro mode)

- Python 3.12+
- aiogram 3.x
- SQLAlchemy 2.x async + Alembic
- PostgreSQL (SQLite only in Lite mode)
- Redis for FSM, throttling, caches
- pydantic-settings
- structlog (JSON) or stdlib JSON logging
- httpx (NEVER `requests`)
- tenacity for retries
- Docker multi-stage + docker-compose
- pytest + pytest-asyncio
- ruff + mypy --strict

## Extension protocol

When you ask `/botforge-extend`:
1. Skill identifies the target layer(s).
2. Proposes a change surface (files to touch + new files).
3. Verifies no public interface breaks.
4. Implements + generates migration if data model changes.
5. Updates README if operator behavior changes.
6. Runs self-review.

## Review protocol

When you ask `/botforge-review`:
- Each finding classified: `[blocker] [major] [minor] [nit]`.
- Cited by `file:line`.
- Never silently rewritten.
- Summary: verdict `SHIP / FIX / REWORK` + top-3 priority fixes.

## See also

- [Reference Library](Reference-Library) — 21 deep-dive modules
- [Bot API spec](Bot-API-Spec) — official constraints enforced
- [Examples](Examples) — reference implementations
