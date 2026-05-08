# 01 — VIP Media Bot

Полностью рабочий пример, сгенерированный через BotForge. Production-ready: слоёная архитектура, Postgres, Redis, Docker, Alembic, webhook.

## Фичи

- `/start` — приветствие + проверка подписки на канал
- `/vip` — покупка VIP-доступа (Telegram Stars)
- `/content` — выдача контента (free / channel / vip tier)
- `/profile` — статус подписки
- Админка: `/stats`, `/broadcast`
- Rate-limited broadcast (25 msg/s)
- Redis-кэш `getChatMember` (10 мин TTL)
- Idempotent payment handlers

## Стек

- Python 3.12 • aiogram 3.x • SQLAlchemy 2 async • Alembic
- PostgreSQL 16 • Redis 7 • Docker Compose

## Структура

```
app/
├── __main__.py
├── config/settings.py
├── db/engine.py
├── models/ (base, user, subscription, payment, content)
├── repositories/ (base, user, subscription, payment, content)
├── services/ (user, subscription, payment, broadcast, channel_check, content)
├── integrations/payments/ (base, stars)
├── middlewares/ (db_session, auth, throttling, logging)
├── filters/ (admin, subscription)
├── keyboards/inline/ (main_menu, subscription)
├── states/ (broadcast)
├── handlers/ (common, subscription, payment, admin, errors)
└── utils/ (markdown, time)
migrations/
docker/
docker-compose.yml
.env.example
pyproject.toml
alembic.ini
Makefile
```

## Quickstart

```bash
cp .env.example .env
# edit BOT_TOKEN, ADMIN_IDS, REQUIRED_CHANNELS

make up           # postgres + redis + migrations + bot
make logs
```

Открой `@your_bot` в Telegram, отправь `/start`.

## Переменные окружения

| Key | Description |
|---|---|
| `BOT_TOKEN` | из @BotFather |
| `ADMIN_IDS` | JSON-массив, e.g. `[123456789]` |
| `REQUIRED_CHANNELS` | JSON-массив chat_id, e.g. `[-1001234567890]` |
| `DATABASE_URL` | `postgresql+asyncpg://...` |
| `REDIS_URL` | `redis://redis:6379/0` |
| `WEBHOOK_URL` | опционально, HTTPS; если пусто — polling |
| `WEBHOOK_SECRET` | 1..256 chars `[A-Za-z0-9_-]` |
| `LOG_LEVEL` | `INFO` / `DEBUG` / `WARNING` |

## Деплой

См. [`docs/DEPLOY.md`](docs/DEPLOY.md) для Fly.io / Railway / VPS инструкций.

## Как был сгенерирован

Один запрос к Claude Code с установленным BotForge skill:

```
/botforge-new SaaS
Задача: VIP-бот для Telegram-канала о кино.
Gated-контент через проверку подписки на канал.
VIP-доступ за 100 Stars/мес к premium подборкам.
Админка: статистика + рассылки.
Хостинг: Docker Compose на VPS, webhook.
```

Результат — этот репозиторий.
