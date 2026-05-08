---
description: Подготовить деплой бота (Docker / Fly.io / Railway / VPS) + webhook
argument-hint: "[docker | fly | railway | vps] [polling | webhook]"
---

Подготовь деплой текущего бота. Платформа + режим: $ARGUMENTS (по умолчанию `docker webhook`).

**1. Audit перед деплоем:**
- [ ] `.env.example` актуален, все переменные на месте
- [ ] Alembic миграции без конфликтов (`alembic check`)
- [ ] `Dockerfile` multi-stage, non-root user
- [ ] `docker-compose.yml` с healthchecks
- [ ] Логи в stdout (JSON)
- [ ] Sentry подключён (опционально, но рекомендовано)

**2. Polling → Webhook (если webhook):**
- `bot/__main__.py`: заменить `dp.start_polling(bot)` на aiohttp-app с `SimpleRequestHandler(dp, bot, secret_token=settings.webhook_secret)`
- `api/app.py` или `bot/web.py`: `AIOHTTPServer`
- `.env`: `WEBHOOK_URL`, `WEBHOOK_SECRET`, `WEBHOOK_PATH`
- nginx (если VPS): TLS + reverse-proxy на bot:8080

**3. Платформенные файлы:**

### Docker (любая VPS с Docker)
- `docker/Dockerfile` multi-stage
- `docker/entrypoint.sh`: `alembic upgrade head && exec python -m app`
- `docker-compose.prod.yml`
- Makefile targets: `deploy`, `logs`, `down`, `rollback`

### Fly.io
- `fly.toml`: app name, region, [[services]] с portами, http_checks
- `Dockerfile` (тот же, что и для Docker)
- Deploy-команда: `fly launch && fly secrets set ... && fly deploy`
- Volumes для Postgres (fly postgres attach)

### Railway
- `railway.toml` или UI config
- Секреты через Railway Dashboard
- Postgres + Redis plugins
- Webhook URL из `RAILWAY_PUBLIC_DOMAIN`

### VPS (Ubuntu + Docker + Caddy)
- `Caddyfile`: автоматический TLS, reverse-proxy на bot
- `systemd` unit для `docker compose up` (опционально)
- Инструкция: `git pull && docker compose pull && docker compose up -d`

**4. Migrations на проде:**
- Отдельный шаг перед стартом: `alembic upgrade head`
- Rollback: `alembic downgrade -1` задокументирован в RUNBOOK

**5. Backup strategy:**
- `pg_dump` cron или hoster-snapshots
- `.env` — храни в password manager, не в git

**6. Post-deploy verification:**
```
curl -X POST https://<domain>/tg/webhook -H "X-Telegram-Bot-Api-Secret-Token: $WEBHOOK_SECRET"
# должен вернуть 401 на невалидный body, но НЕ 502/504
```
Плюс: отправь `/start` в бот, проверь логи.

**7. RUNBOOK.md** — если нет, создай раздел:
- «Бот не отвечает» → проверить webhook (`getWebhookInfo`)
- «Платежи не проходят» → проверить webhook провайдера и idempotency
- «Рассылка застряла» → поднять воркер, очистить Redis-ключи
- «Миграция сломана» → `alembic downgrade <rev>` + восстановление из backup

**8. Итог:**
Выдай пошаговые команды деплоя для выбранной платформы и URL, который нужно заtg-setWebhook'нуть.
