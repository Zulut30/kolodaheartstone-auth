---
description: Добавить систему сегментированных рассылок (admin flow + worker + rate limit)
argument-hint: "[simple | segmented | ab-test | scheduled]"
---

Добавь в бот систему рассылок. Профиль: $ARGUMENTS (по умолчанию `segmented`).

**Файлы:**

### Модели
```
broadcasts(id, text, media_file_id, segment, scheduled_at, status,
           created_by, started_at, finished_at, total, ok, failed, blocked)
broadcast_targets(broadcast_id, user_id, status, attempts, error)  -- только для больших рассылок
```

### Сервисы
- `app/services/broadcast_service.py` — создание, планирование, отправка
- Rate limit: **25 msg/s** (жёсткий лимит Telegram для ботов)
- Обработка ошибок:
  - `TelegramRetryAfter` → `asyncio.sleep(e.retry_after)` и повтор
  - `TelegramForbiddenError` (user blocked bot) → пометить `blocked`, не ретраить
  - прочее → 1 retry, дальше `failed`

### Admin FSM (`app/states/broadcast.py`)
```
Broadcast.text → media (опционально) → segment → preview → confirm
```
- `/broadcast` — старт (за `RoleFilter(Role.admin)`)
- Preview: отправить админу то же сообщение, что пойдёт юзерам
- Confirm: inline-кнопки «Отправить / Отменить»

### Сегментация (если `segmented`)
Query builder сегмента:
- All users
- Active (последняя активность < N дней)
- VIP / Free
- По языку
- По тегам (если введены)

В handler: `segment` как pydantic model, репозиторий её применяет.

### Scheduled (если `scheduled`)
- `scheduled_at: datetime` в модели
- Worker (`app/workers/broadcast_worker.py`) или cron-скрипт каждую минуту:
  ```python
  async def tick() -> None:
      jobs = await repo.find_ready(now=datetime.now(UTC))
      for j in jobs:
          await service.dispatch(j.id)
  ```
- В compose — отдельный сервис `worker: ... command: python -m app.workers.broadcast_worker`

### A/B test (если `ab-test`)
- Два варианта текста
- Split 50/50 по `user_id % 2`
- Метрики: CTR на inline-кнопку
- `broadcast_variants(broadcast_id, variant, text, shown, clicked)`

### Безопасность
- `parse_mode` выбирает админ (HTML рекомендуется)
- Текст санитизирован перед сохранением (если HTML — валидный HTML)
- Подтверждение перед отправкой (особенно для «All users»)
- Audit log: кто, когда, что, скольким

### Мониторинг
- Прогресс в админ-чат: `Sent 1500/10000 (ok=1450, blocked=30, failed=20)` каждые 30 сек
- При завершении — финальная сводка

### Self-review
- [ ] 25 msg/s соблюдается
- [ ] `RetryAfter` обрабатывается
- [ ] Заблокированные пользователи помечаются, не ретраятся
- [ ] Admin-only доступ
- [ ] Preview перед отправкой
- [ ] Scheduled worker не пересекается с ручной отправкой (advisory-lock)
