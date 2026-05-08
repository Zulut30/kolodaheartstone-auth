---
description: Добавить scheduled tasks (APScheduler / arq / cron) для рассылок, expire, напоминаний
argument-hint: "[apscheduler | arq | cron] [task: expire-subs | reminders | broadcasts | stats | custom]"
---

Добавь scheduler в текущий бот. Инструмент + задача: $ARGUMENTS (по умолчанию `arq reminders,expire-subs`).

Читай reference: `.claude/skills/botforge/references/scheduler.md`.

**Выбор инструмента:**
- **APScheduler** — для Lite/Pro, до 100 job/сутки, single-instance
- **arq** (Redis) — для Pro/SaaS, масштабируется, retry + priority
- **cron + CLI** — простейшие ежедневные, минимум кода

**Типовые задачи:**

### `expire-subs`
Каждые 15 мин — пометить `status=expired` у подписок с `expires_at < now`. За 3 дня / 1 день — отправить уведомление пользователю.

### `reminders`
Time-based триггеры. `_defer_until=datetime` в arq или `DateTrigger` в APScheduler. Сервис `ReminderService.schedule(user_id, text, at)` делает enqueue.

### `broadcasts`
Отложенные рассылки. Воркер раз в минуту опрашивает `broadcasts.find_ready(now)` и диспатчит.

### `stats`
Раз в час — агрегация `daily_stats(date, new_users, active, revenue)`. Упрощает админ-дашборд.

### `custom`
Спросите у пользователя, что планировать, и создайте задачу.

**Файлы:**
- Для APScheduler: `app/scheduler/setup.py`, `app/scheduler/tasks.py`, регистрация в `on_startup`
- Для arq: `app/workers/worker.py` (WorkerSettings), `app/workers/tasks.py`, сервис `app/workers/context.py` с DI
- Для cron: `app/cli/tasks.py` с `click`-группой, crontab-инструкция в README

**Docker:**
- Для arq — отдельный сервис в `docker-compose.yml`: `worker: command: arq app.workers.worker.WorkerSettings`
- Для APScheduler — дополнительный setup не нужен (in-process)

**Idempotency:**
Все периодические задачи должны быть idempotent. Для «once per event» — advisory locks или `SELECT FOR UPDATE SKIP LOCKED`.

**Observability:**
- Prometheus: `scheduler_job_duration_seconds{name}`, `scheduler_job_errors_total{name}`
- Logs: `job_name`, `duration_ms`, `result`
- Alert: job не выполнялась >2× ожидаемого интервала

**Self-review:**
- [ ] Все задачи idempotent
- [ ] Timeouts заданы на каждой
- [ ] Retry с dead-letter очередью, не infinite loop
- [ ] Graceful shutdown: worker дожидается current job
- [ ] Логи не содержат секретов в payload
