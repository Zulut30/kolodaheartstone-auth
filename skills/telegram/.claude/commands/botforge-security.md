---
description: Полный security-аудит Telegram-бота по чеклисту BotForge
argument-hint: "[область: all | auth | payments | miniapp | data]"
---

Проведи security-аудит текущего бота. Область: $ARGUMENTS (по умолчанию `all`).

**Формат findings:**
```
[critical|high|medium|low] category — file:line
  Угроза: ...
  Эксплуатация: ...
  Правка: ...
```

**Проверь:**

### Secrets & Config (`all`)
- [ ] Нет `BOT_TOKEN`, `API_KEY`, `SECRET` в коде (grep: `sk_`, `eyJ`, `token\s*=\s*["']`)
- [ ] `.env` в `.gitignore`
- [ ] `.env.example` без реальных значений
- [ ] Логи не содержат секретов, card numbers, эл. почт пользователей

### Auth (`auth`, `all`)
- [ ] Admin-команды за `AdminFilter`/`RoleFilter`
- [ ] `tg_id` берётся из update, не из message text
- [ ] Ban-check ДО бизнес-логики
- [ ] Rate limit на чувствительные команды (auth, payment, promo)

### Mini App (`miniapp`, `all`)
- [ ] initData проверяется HMAC на сервере (НЕ доверять `initDataUnsafe`)
- [ ] `auth_date` не старше 1 часа
- [ ] JWT TTL ≤ 12 ч
- [ ] HTTPS обязателен
- [ ] CORS whitelist — только webapp origin, никаких `*`
- [ ] CSP headers на фронте
- [ ] X-Frame-Options / frame-ancestors настроены

### Payments (`payments`, `all`)
- [ ] Webhook signature проверяется (HMAC / Stripe-Signature / IP-whitelist)
- [ ] Idempotency по `external_id` — двойная обработка невозможна
- [ ] `order_id` создаётся в вашей БД ДО вызова провайдера
- [ ] Суммы — `Decimal`, не `float`
- [ ] Grant access ТОЛЬКО при `status == "succeeded"`
- [ ] Refunds обрабатываются
- [ ] Нет логирования card/token

### Data (`data`, `all`)
- [ ] SQL только параметризованный (ORM или `text(...)` с bind-params)
- [ ] User input санитизирован перед `parse_mode=HTML/Markdown`
- [ ] Файлы от пользователей валидируются (size, mime)
- [ ] `CallbackData`-фабрики, не сырые строки
- [ ] `parse_mode` контролируется администратором для рассылок

### Infra (`all`)
- [ ] Webhook `secret_token` включён
- [ ] Dockerfile: non-root user, минимальный base
- [ ] Зависимости закреплены (lockfile)
- [ ] Нет уязвимостей в deps (`pip-audit` / `safety check` / GitHub Dependabot)
- [ ] Healthcheck отвечает только 200, не утекает инфа

### Ops (`all`)
- [ ] Token ротировался хотя бы раз за 6 месяцев
- [ ] DB-бэкап работает и проверен восстановлением
- [ ] Sentry / error tracking подключён
- [ ] Алерты на аномальные события (массовые ошибки, всплеск register)

**В конце:**
- Сводка: X critical, Y high, Z medium, W low
- Вердикт: **SAFE / FIX BEFORE PROD / CRITICAL HOLD**
- Top-3 приоритет исправлений
- Рекомендация: что автоматизировать в CI (pip-audit, gitleaks, bandit)
