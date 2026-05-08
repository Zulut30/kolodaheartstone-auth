# Architecture Reference

## Full project tree

```
my_bot/
├── app/
│   ├── __main__.py              # entrypoint: python -m app
│   ├── bot/
│   │   ├── dispatcher.py        # create_dispatcher() assembles routers + middlewares
│   │   └── lifespan.py          # startup/shutdown hooks (bot.set_my_commands, engine.dispose)
│   ├── config/
│   │   ├── settings.py          # pydantic-settings BaseSettings
│   │   ├── logging.py           # structlog / dictConfig
│   │   └── constants.py         # magic numbers, default TTLs, page sizes
│   ├── db/
│   │   ├── engine.py            # async engine + session factory
│   │   └── uow.py               # unit-of-work helper
│   ├── models/
│   │   ├── base.py              # DeclarativeBase + timestamps mixin
│   │   ├── user.py
│   │   ├── subscription.py
│   │   └── payment.py
│   ├── schemas/                 # pydantic DTOs for service boundaries
│   ├── repositories/
│   │   ├── base.py              # BaseRepo(session)
│   │   ├── user_repo.py
│   │   ├── subscription_repo.py
│   │   └── payment_repo.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── subscription_service.py
│   │   ├── payment_service.py
│   │   ├── broadcast_service.py
│   │   └── channel_check_service.py
│   ├── integrations/
│   │   ├── yookassa_client.py
│   │   ├── openai_client.py
│   │   ├── sheets_client.py
│   │   └── wordpress_client.py
│   ├── middlewares/
│   │   ├── db_session.py        # injects AsyncSession into handler data
│   │   ├── throttling.py        # Redis-based rate limit per user
│   │   ├── auth.py              # loads User into data
│   │   ├── i18n.py
│   │   └── logging.py           # request_id, structured logs
│   ├── filters/
│   │   ├── admin.py
│   │   └── subscription.py
│   ├── keyboards/
│   │   ├── inline/
│   │   │   ├── main_menu.py
│   │   │   └── subscription.py
│   │   └── reply/
│   │       └── admin.py
│   ├── states/
│   │   ├── broadcast.py
│   │   └── onboarding.py
│   ├── handlers/
│   │   ├── __init__.py          # Router(); include all sub-routers
│   │   ├── common.py            # /start, /help
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── broadcast.py
│   │   │   ├── users.py
│   │   │   └── stats.py
│   │   └── errors.py            # global error handler
│   └── utils/
│       ├── retry.py
│       └── time.py
├── migrations/                  # alembic
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docs/
│   ├── ADR/
│   └── RUNBOOK.md
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── pyproject.toml
├── alembic.ini
├── Makefile
└── README.md
```

## Layer responsibilities

| Layer | Allowed | Forbidden |
|---|---|---|
| `handlers/` | parse update, validate callback_data, call service, send reply | SQL/ORM, business rules, external API calls |
| `services/` | orchestration, business rules, call repos + integrations | direct SQL, Telegram API calls outside passed Bot |
| `repositories/` | SQLAlchemy queries, transactions | HTTP calls, Telegram API |
| `integrations/` | HTTP/gRPC clients to external services, retry logic | SQL, Telegram API |
| `models/` | ORM declarations, Mapped typed fields | behavior beyond __repr__ |
| `middlewares/` | cross-cutting concerns: DI, auth, throttling, i18n, logging | business logic |

## Dependency flow

```
handler → service → repository → model
                 → integration → external API
```

Never handler → repository. Never service → handler. Never model → service.
