---
description: Сгенерировать test suite для бота (unit + integration + aiogram mocks)
argument-hint: "[unit | integration | all | path/to/module]"
---

Сгенерируй тесты для бота. Область: $ARGUMENTS (по умолчанию `all`).

**Стек:**
- `pytest` + `pytest-asyncio`
- `aiogram-tests` или `aiosend` mock bot
- `pytest-postgresql` или testcontainers для реальной БД в integration
- `fakeredis` для unit
- `respx` или `httpx-mock` для интеграций

**Структура:**
```
tests/
  conftest.py              # фикстуры: session, redis, bot, dispatcher, client
  unit/
    test_user_service.py
    test_subscription_service.py
    test_payment_service.py
    test_broadcast_service.py
    test_channel_check_service.py
    test_filters.py
    integrations/
      test_yookassa_client.py
      test_webapp_auth.py
  integration/
    test_start_flow.py
    test_subscription_flow.py
    test_payment_webhook.py
    test_admin_broadcast.py
```

**Правила:**
1. Тестируем **services**, не handlers. Handlers тонкие — через integration-тест всей цепочки.
2. Используем реальную Postgres в integration (через testcontainers), не SQLite.
3. Redis — `fakeredis` в unit, реальный в integration.
4. Внешние API — `respx` для httpx (ЮKassa, CryptoBot).
5. Telegram Bot — `MockedBot` из `aiogram_tests` либо ручной stub.
6. `conftest.py` содержит `pytest_asyncio` event loop + `session` фикстуру с откатом транзакции.

**Coverage target:** ≥ 70% для services, ≥ 50% общий.

**Примеры:**

### Unit (service)
```python
# tests/unit/test_subscription_service.py
import pytest
from datetime import datetime, timedelta, UTC

@pytest.mark.asyncio
async def test_activate_extends_existing(subscription_service, sub_repo_fake):
    user_id = 42
    future = datetime.now(UTC) + timedelta(days=10)
    sub_repo_fake.set_active(user_id, expires_at=future)

    await subscription_service.activate(user_id, plan="vip", days=30)

    sub = await sub_repo_fake.active_for(user_id)
    assert sub.expires_at == future + timedelta(days=30)
```

### Integration (webhook)
```python
# tests/integration/test_payment_webhook.py
import pytest

@pytest.mark.asyncio
async def test_yookassa_webhook_grants_vip(client, yookassa_payload, user_with_pending_order):
    r = await client.post("/webhooks/yookassa", json=yookassa_payload)
    assert r.status_code == 200

    # access granted
    sub = await sub_repo.active_for(user_with_pending_order.id)
    assert sub and sub.plan == "vip"

    # idempotent: second call no-op
    r2 = await client.post("/webhooks/yookassa", json=yookassa_payload)
    assert r2.status_code == 200
    # access not duplicated
```

**CI:**
```yaml
# .github/workflows/test.yml
- run: uv sync
- run: ruff check .
- run: mypy app tests
- run: pytest --cov=app --cov-fail-under=70
```

**Обязательно покрыть:**
- Payment webhook idempotency
- `parse_and_verify_init_data` — happy path + bad sig + expired
- `RoleFilter` — allow/deny
- `ChannelCheckService` — cache hit/miss
- `BroadcastService` — RetryAfter handling
- `TelegramForbiddenError` — пометка blocked без ретрая
