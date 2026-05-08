---
description: Настроить observability (structlog + Sentry + Prometheus + health + audit log)
argument-hint: "[minimal | standard | full]"
---

Добавь observability-слой. Уровень: $ARGUMENTS (по умолчанию `standard`).

Читай reference: `.claude/skills/botforge/references/observability.md`.

**Уровни:**

### `minimal` — для Lite / MVP
- structlog JSON на stdout
- request_id middleware
- Errors handler (уже есть в BotForge)
- Healthcheck endpoint

### `standard` — для Pro (по умолчанию)
- Всё из `minimal`, плюс:
- Sentry integration с scrub-ом чувствительных данных
- Audit log в БД (модель `audit_events`)
- `/metrics` endpoint (prometheus_client)
- Готовые счётчики: updates, handler latency, TG API errors, payment events

### `full` — для SaaS / enterprise
- Всё из `standard`, плюс:
- OpenTelemetry tracing (FastAPI + SQLAlchemy + httpx инструментация)
- Grafana dashboard JSON (генерируется)
- Alert rules (error rate, webhook last_error, payment success rate, broadcast stuck)
- Readiness probe с DB + Redis check
- Log retention policy в RUNBOOK

**Файлы для генерации:**
- `app/config/logging.py` — configure_logging() + configure_sentry()
- `app/middlewares/logging.py` — LoggingMiddleware с request_id bind
- `app/bot/metrics.py` — Counter/Histogram/Gauge
- `app/bot/health.py` — /healthz + /readyz
- `app/models/audit.py` — AuditEvent
- `app/services/audit_service.py` — log(actor, action, target, payload)
- `infra/grafana/*.json` — дашборды (для `full`)
- `infra/alerts.yml` — Prometheus alert rules

**Инжекция в codebase:**
- `AuditService` вызывается в: role change, ban, broadcast send, payment refund, settings update
- `request_id` логируется во всех handler-ах через middleware
- Sentry `before_send` фильтрует: `bot_token`, `api_key`, `jwt`, `password`, card numbers

**Integration notes:**
- `/metrics` НЕ публичный — bind на internal interface или basic-auth
- Sentry DSN — из `.env`, не в коде
- Если нет Sentry — skill использует только stdout, без падений

**Self-review:**
- [ ] structlog processors в правильном порядке
- [ ] sensitive-фильтр в Sentry before_send
- [ ] request_id виден в каждой log-записи
- [ ] `/metrics` закрыт от интернета
- [ ] audit_events пишутся транзакционно с действием
- [ ] log retention задокументирован

**Deploy:**
- Prometheus job на `<bot>:9090/metrics`
- Grafana data source + импорт дашборда
- Alert manager → Slack/PagerDuty
