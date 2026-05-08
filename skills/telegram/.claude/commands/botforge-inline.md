---
description: Добавить inline-режим (@botname query) с результатами и пагинацией
argument-hint: "[описание что искать: каталог / контент / юзеры / custom]"
---

Подключи inline-режим к боту. Контент: $ARGUMENTS

Читай reference: `.claude/skills/botforge/references/inline-mode.md`.

**Шаги:**

### 1. BotFather
Напомни пользователю: `/setinline` → placeholder (например, `поиск фильмов`). Опционально `/setinlinefeedback` для аналитики выбора.

### 2. Handler
`app/handlers/inline.py` с `@router.inline_query()`:
- Парсинг `query.query`
- Вызов `CatalogService.search(q, limit=20, offset=int(query.offset or 0))`
- Сборка `InlineQueryResultArticle` / `Photo` / `Video`
- `query.answer(results, cache_time=300, is_personal=False, next_offset=...)`

### 3. Service
`app/services/catalog_service.py` (или аналог под домен) с `search(q, limit, offset)`. ORM-запросы — в repo.

### 4. Throttle
`app/middlewares/inline_throttle.py` — Redis, 1 query/sec per user. Иначе при печати летят 10+ inline-queries за секунду.

### 5. Chosen inline result (опционально)
Если включён feedback — `@router.chosen_inline_result()` пишет аналитику в БД.

### 6. allowed_updates
Обнови список в `on_startup`:
```python
allowed_updates = [..., "inline_query", "chosen_inline_result"]
```

### 7. Constraints (official)
- Max 50 results per response
- Query string ≤ 256 chars
- next_offset ≤ 64 bytes
- cache_time: 300s (5 мин) — public, 0 для personal

### 8. Security
- Экранирование user input в SQL (ORM-параметры) и HTML (при вставке в `input_message_content`)
- `is_personal=True` если результаты зависят от пользователя — иначе кэш испортит UX
- Не кладите секреты в `result_id` — они логируются в `chosen_inline_result`

### 9. Self-review
- [ ] `inline_query` в `allowed_updates`
- [ ] Throttle middleware активен
- [ ] BD-запросы с LIMIT 50
- [ ] `cache_time` выставлен
- [ ] `next_offset` для пагинации
- [ ] Результаты персональны при необходимости
