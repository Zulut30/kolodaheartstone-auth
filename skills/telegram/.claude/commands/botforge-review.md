---
description: Code review существующего Telegram-бота по стандартам BotForge
argument-hint: "[путь к файлу/директории или описание что ревьюить]"
---

Проведи code review по стандартам **BotForge** для: $ARGUMENTS

Если аргумент пустой — ревьюй весь проект, начиная с `app/`.

**Формат ответа:**

Каждая находка в формате:
```
[blocker|major|minor|nit] path/to/file.py:LINE — краткое описание
  Проблема: ...
  Правка: ...
```

**Проверь минимум:**

1. Handlers тонкие (≤20 строк, без бизнес-логики, без SQL)
2. ORM только в `repositories/`
3. DB session через middleware, не импортом
4. Секреты только в `.env`
5. Все I/O async, никакого `requests`
6. Внешние API: timeout + tenacity retry
7. Логи structlog/JSON, никакого print
8. Type hints на публичных функциях
9. Payment webhooks idempotent по `external_id`
10. Admin-команды за `RoleFilter`/`AdminFilter`
11. `CallbackData`-фабрики вместо сырых строк
12. Throttling middleware активен
13. Нет логирования чувствительных данных

**В конце:**
- Сводка: X blocker, Y major, Z minor, W nit
- Вердикт: **SHIP / FIX / REWORK**
- Приоритизированный список правок (top-3)

Не переписывай код без спроса — только предлагай diff-и.
