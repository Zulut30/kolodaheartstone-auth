# BotForge — Skill Overview

**Version:** 1.7.1
**Released:** 2026-04-20
**License:** MIT

> **Note.** This file is a high-level overview of the skill for human readers.
> The **canonical skill prompt** consumed by Claude Code lives at
> [`.claude/skills/botforge/SKILL.md`](.claude/skills/botforge/SKILL.md).
> The raw prompt for other LLMs lives at [`system_prompt.txt`](system_prompt.txt).
> If this file and the canonical skill disagree, the canonical skill wins.

---

## Содержание

1. [Манифест](#1-манифест)
2. [System Prompt](#2-system-prompt)
3. [Rules & Guardrails](#3-rules--guardrails)
4. [Шаблоны ответов AI](#4-шаблоны-ответов-ai)
5. [Reference-архитектура](#5-reference-архитектура)
6. [Reusable Patterns Library](#6-reusable-patterns-library)
7. [Примеры ботов](#7-примеры-ботов)
8. [Инструкция по использованию](#8-инструкция-по-использованию)
9. [Чек-листы](#9-чек-листы)
10. [Changelog & Roadmap](#10-changelog--roadmap)

---

## 1. Манифест

**Главный тезис:** AI генерирует код. BotForge заставляет AI инженерить **продукты**.

**Что делает skill:**
- Вынуждает уточнить бизнес-задачу перед кодом
- Навязывает слоёную архитектуру
- Выдаёт дерево проекта до генерации файлов
- Запрещает монолит, хардкод, `requests`, секреты в коде
- Автоматически добавляет Docker, Alembic, логи, retry, self-review
- Поддерживает инкрементальное расширение без слома архитектуры

**Ценность:**
- −15 часов скаффолдинга на каждом боте
- Единый стандарт для команды
- Output сразу коммерческого качества
- Меньше технического долга

---

## 2. System Prompt

Полный system prompt вынесен в [`system_prompt.txt`](system_prompt.txt). Вставляется как есть в:
- Claude Projects / Claude Code
- Cursor rules
- Custom GPT Instructions
- OpenAI / Anthropic API `system` message
- Любой LLM-агент

---

## 3. Rules & Guardrails

### 3.1 Architectural (blocker-level)
1. Handler = transport-слой. Только: парсинг update → вызов service → отправка ответа.
2. ORM/SQL — исключительно в `repositories/`.
3. DB session инжектится `DbSessionMiddleware`, не импортом.
4. FSM-группы — в `states/`, не inline.
5. Клавиатуры — фабрики `build_*_kb()` в `keyboards/`.
6. Внешние API — `integrations/<vendor>_client.py` с `httpx.AsyncClient`, timeout ≤ 10s, `tenacity` retry (3 попытки, exp. backoff).
7. Конфиг — `pydantic_settings.BaseSettings`, source of truth — `.env`.

### 3.2 Code Style
- `ruff` + `mypy --strict` зелёные
- Публичные функции: полные type hints
- Никаких `print`
- Magic numbers → `config/constants.py`
- Одна ответственность на модуль

### 3.3 Error Handling
- Глобальный `ErrorsMiddleware`: traceback + user_id + update_type + `request_id`
- Внешние API: `tenacity.retry(stop=stop_after_attempt(3), wait=wait_exponential())` + graceful fallback
- БД: `async with session.begin():`, rollback автоматический
- User-errors (валидация) ≠ system-errors
- Пользователю — никогда traceback

### 3.4 Security
- Секреты только в `.env`; `.env.example` без значений
- Админы через `ADMIN_IDS` + `AdminFilter`
- Webhook `secret_token` обязателен
- `CallbackData`-фабрики везде
- Throttling через Redis
- Idempotency keys для payment webhooks

### 3.5 Deployment
- Dockerfile multi-stage, non-root user
- `docker-compose.yml`: bot + postgres + redis + nginx (при webhook)
- Healthchecks у всех сервисов
- Alembic `upgrade head` в entrypoint.sh
- Логи в stdout (JSON)
- `Makefile`: `run`, `test`, `lint`, `migrate`, `up`, `down`, `logs`, `deploy`

### 3.6 Documentation
- `README.md`: что это / stack / local run / env / deploy / архитектура
- `docs/ADR/NNNN-title.md` для крупных решений
- `docs/RUNBOOK.md` для инцидентов

---

## 4. Шаблоны ответов AI

### 4.1 «Создай Telegram-бота …»
```
### 1. Бизнес-брифинг
(5 вопросов или пропуск)

### 2. ADR
Стек, модель данных, зависимости, деплой, риски, точки расширения.

### 3. Дерево проекта
<tree>

### 4. Файлы (в порядке зависимости)
<config → … → infra>

### 5. Self-review
- [x] ...

### 6. Запуск
<deploy commands>
```

### 4.2 «Добавь фичу X»
```
### План изменений
Слои: ...
Новые файлы: ...
Изменяемые: ...
Обратная совместимость: сохраняется.

### Миграция (если нужно)

### Код (только затронутые файлы)

### Self-review дельты
```

### 4.3 «Review мой код»
```
[blocker] app/handlers/payment.py:42 — прямой SQL; вынести в PaymentRepo.create()
[major]   app/services/broadcast.py:88 — нет retry на bot.send_message
[minor]   app/keyboards/main.py:12 — inline-клавиатура собирается в handler
[nit]     app/config/settings.py:5 — отсутствует docstring
```

### 4.4 «Рефакторинг монолита»
```
### Инвентаризация
### План миграции (по шагам, без простоя)
### Порядок PR-ов (атомарные шаги)
### Риски и откат
```

### 4.5 «Переведи на webhook / деплой»
```
### Режим (polling → webhook)
### Изменения (bot/__main__.py, nginx, compose, env)
### Деплой (конкретные команды)
### Откат
```

---

## 5. Reference-архитектура

```
my_bot/
├── app/
│   ├── __main__.py
│   ├── bot/
│   │   ├── dispatcher.py
│   │   └── lifespan.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── constants.py
│   ├── db/
│   │   ├── engine.py
│   │   └── uow.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── subscription.py
│   │   └── payment.py
│   ├── schemas/
│   ├── repositories/
│   │   ├── base.py
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
│   │   ├── db_session.py
│   │   ├── throttling.py
│   │   ├── auth.py
│   │   ├── i18n.py
│   │   └── logging.py
│   ├── filters/
│   │   ├── admin.py
│   │   └── subscription.py
│   ├── keyboards/
│   │   ├── inline/
│   │   └── reply/
│   ├── states/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── admin/
│   │   └── errors.py
│   └── utils/
├── migrations/
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

---

## 6. Reusable Patterns Library

### 6.1 Settings
```python
# app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    admin_ids: list[int]
    required_channels: list[int] = []
    database_url: str
    redis_url: str = "redis://redis:6379/0"

    webhook_url: str | None = None
    webhook_secret: str | None = None
    webhook_path: str = "/tg/webhook"

    yookassa_shop_id: str | None = None
    yookassa_secret_key: str | None = None
    openai_api_key: str | None = None

    log_level: str = "INFO"

settings = Settings()
```

### 6.2 DB engine
```python
# app/db/engine.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.config.settings import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

### 6.3 DB Session Middleware
```python
# app/middlewares/db_session.py
from aiogram import BaseMiddleware
from app.db.engine import session_factory

class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with session_factory() as session:
            data["session"] = session
            return await handler(event, data)
```

### 6.4 Repository Base
```python
# app/repositories/base.py
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
```

### 6.5 User Service
```python
# app/services/user_service.py
from aiogram.types import User as TgUser
from app.repositories.user_repo import UserRepo

class UserService:
    def __init__(self, user_repo: UserRepo) -> None:
        self._users = user_repo

    async def ensure_user(self, tg_user: TgUser) -> None:
        await self._users.upsert(
            tg_id=tg_user.id,
            username=tg_user.username,
            lang=tg_user.language_code,
        )
```

### 6.6 Channel Subscription Check (Redis-cached)
```python
# app/services/channel_check_service.py
from aiogram import Bot
from redis.asyncio import Redis

class ChannelCheckService:
    def __init__(self, bot: Bot, redis: Redis, channels: list[int]) -> None:
        self._bot, self._redis, self._channels = bot, redis, channels

    async def is_subscribed(self, user_id: int) -> bool:
        key = f"subcheck:{user_id}"
        if (cached := await self._redis.get(key)) is not None:
            return cached == b"1"
        for chat_id in self._channels:
            m = await self._bot.get_chat_member(chat_id, user_id)
            if m.status in {"left", "kicked"}:
                await self._redis.set(key, "0", ex=600)
                return False
        await self._redis.set(key, "1", ex=600)
        return True
```

### 6.7 Throttling Middleware
```python
# app/middlewares/throttling.py
from aiogram import BaseMiddleware
from redis.asyncio import Redis

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, rate: float = 1.0) -> None:
        self._redis, self._rate = redis, rate

    async def __call__(self, handler, event, data):
        uid = getattr(event.from_user, "id", None)
        if uid is None:
            return await handler(event, data)
        key = f"thr:{uid}"
        if await self._redis.set(key, "1", ex=int(self._rate), nx=True):
            return await handler(event, data)
```

### 6.8 Admin Filter
```python
# app/filters/admin.py
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from app.config.settings import settings

class AdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        uid = getattr(event.from_user, "id", None)
        return uid in settings.admin_ids
```

### 6.9 Broadcast Service (rate-limited)
```python
# app/services/broadcast_service.py
import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError

class BroadcastService:
    def __init__(self, bot: Bot, rps: int = 25) -> None:
        self._bot, self._sem = bot, asyncio.Semaphore(rps)

    async def send_to(self, user_ids: list[int], text: str) -> dict[str, int]:
        ok = blocked = failed = 0
        async def _one(uid: int) -> None:
            nonlocal ok, blocked, failed
            async with self._sem:
                try:
                    await self._bot.send_message(uid, text)
                    ok += 1
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    await self._bot.send_message(uid, text); ok += 1
                except TelegramForbiddenError:
                    blocked += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(1 / 25)
        await asyncio.gather(*[_one(u) for u in user_ids])
        return {"ok": ok, "blocked": blocked, "failed": failed}
```

### 6.10 FSM State Group
```python
# app/states/onboarding.py
from aiogram.fsm.state import State, StatesGroup

class Onboarding(StatesGroup):
    waiting_name = State()
    waiting_email = State()
    confirm = State()
```

### 6.11 Inline Keyboard Factory
```python
# app/keyboards/inline/main_menu.py
from aiogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as K

def main_menu_kb() -> K:
    return K(inline_keyboard=[
        [B(text="Каталог", callback_data="menu:catalog")],
        [B(text="VIP", callback_data="menu:vip"),
         B(text="Профиль", callback_data="menu:profile")],
    ])
```

### 6.12 Errors Handler
```python
# app/handlers/errors.py
import logging, uuid
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router(name="errors")
log = logging.getLogger(__name__)

@router.errors()
async def on_error(event: ErrorEvent) -> bool:
    rid = uuid.uuid4().hex[:8]
    log.exception("update failed", extra={"request_id": rid})
    upd = event.update
    target = upd.message or (upd.callback_query.message if upd.callback_query else None)
    if target:
        await target.answer(f"Что-то пошло не так. Код: {rid}")
    return True
```

---

## 7. Примеры ботов

### 7.1 VIP-бот медиа-канала о кино
**Запрос:** gated-контент + VIP за 299 ₽/мес + рассылки + админка.
Stack: aiogram 3 + PostgreSQL + Redis + Docker. Webhook за nginx. Telegram Stars + ЮKassa. Кэш `getChatMember` 10 мин. Broadcast 25 msg/s.
Модель: `users, subscriptions(plan, status, expires_at), payments(provider, ext_id), content_items(tier)`.

### 7.2 AI-ассистент с тарифами
**Запрос:** OpenAI-бот, 3 тарифа, лимиты токенов, история диалогов.
OpenAI через `integrations/openai_client.py` (httpx + tenacity). История в `messages`. Счётчики лимитов в Redis. Переполнение → upsell.

### 7.3 Лидген-бот для онлайн-школы
**Запрос:** FSM-сбор заявки → Google Sheets → уведомление админу.
FSM: `Lead.name → phone → goal → confirm`. Валидация regex. Транзакция: insert в `leads` + append в Sheets + admin-notify. Outbox-pattern на случай частичных сбоев.

Полные реализации см. в [`examples/`](examples/).

---

## 8. Инструкция по использованию

### 8.1 Куда вставлять system prompt
- **Claude Projects:** Project Instructions
- **Claude Code:** `.claude/skills/botforge/SKILL.md`
- **Cursor:** `.cursorrules`
- **Codex / Codex CLI:** `AGENTS.md`
- **Custom GPT:** Instructions
- **API:** `system` message

### 8.2 Формат запроса
```
BotForge: [Lite|Pro|Media|SaaS]
Задача: <бизнес-описание>
Ограничения: <бюджет/хостинг/сроки>
Ответы на брифинг (опционально): 1)... 2)...
```

### 8.3 Типичная сессия
1. Пользователь: `BotForge: Pro. Бот-витрина курсов с оплатой ЮKassa`
2. AI: 5 вопросов → пользователь отвечает
3. AI: ADR + tree + файлы + self-review + deploy
4. Пользователь: «добавь рефералку»
5. AI: план дельты + diff + миграция
6. Пользователь: `review app/services/payment_service.py`
7. AI: список нарушений с тегами

---

## 9. Чек-листы

### 9.1 Self-Review (AI прогоняет после генерации)
- [ ] Нет секретов в коде
- [ ] Handlers ≤ 20 строк, без бизнес-логики
- [ ] SQL/ORM только в `repositories/`
- [ ] DB session через middleware
- [ ] Все I/O async
- [ ] Внешние API: timeout + retry
- [ ] Логи structlog/JSON
- [ ] Type hints на публичных функциях
- [ ] `.env.example` полный
- [ ] Dockerfile multi-stage, non-root
- [ ] docker-compose с healthchecks
- [ ] Alembic baseline создан
- [ ] README с 6 разделами
- [ ] `ruff` и `mypy --strict` зелёные

### 9.2 Deploy Checklist
- [ ] `.env` на сервере, не в репо
- [ ] `BOT_TOKEN` свежий
- [ ] Webhook URL HTTPS, secret задан
- [ ] DB бэкап настроен
- [ ] Sentry подключён
- [ ] Healthcheck отвечает
- [ ] Rate limits протестированы
- [ ] RUNBOOK актуален

### 9.3 Security Checklist
- [ ] Admin-команды за `AdminFilter`
- [ ] Webhook `secret_token` включён
- [ ] `CallbackData`-фабрики везде
- [ ] Payment webhooks idempotent
- [ ] SQL только параметризованный
- [ ] User input санитизирован
- [ ] Throttling активен
- [ ] Нет логирования чувствительных данных

---

## 10. Changelog & Roadmap

| Версия | Статус | Содержание |
|---|---|---|
| **v1.7.1** | released | web admin panel (React + FastAPI + SSE), `/botforge-admin-web` command, 23 references |
| v1.7 | released | stability protocols (Bypass / Override / Recovery), anti-patterns, naming contract |
| v1.6 | released | admin panel reference, analytics, GDPR compliance, anti-spam |
| v1.5 | released | performance, groups & channels, media, inline mode deep-dives |
| v1.4 | released | observability (structlog / Sentry / Prometheus), scheduler, i18n, subscriptions |
| v1.3 | released | Mini Apps, auth (initData HMAC / OAuth / API keys / roles) |
| v1.2 | released | unified payments (Stars / ЮKassa / CryptoBot / Stripe / Tribute) |
| v1.1 | released | examples pack, four-format sync, golden tests |
| v1.0 Pro | released | core skill, aiogram 3, Postgres, Redis, Docker, Alembic, admin, broadcast, channel-check |
| v1.8 Factory | planned | CLI `botforge new <name>`, multitenancy |
| v2.0 Studio | vision | UI-конструктор → экспорт проекта |

Подробности релизов — в [`docs/CHANGELOG.md`](docs/CHANGELOG.md).
