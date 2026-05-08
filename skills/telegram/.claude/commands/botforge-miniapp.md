---
description: Подключить Telegram Mini App (Web App) к существующему боту
argument-hint: "[описание Mini App: каталог / профиль / dashboard / …]"
---

Подключи к текущему боту **Telegram Mini App** по стандартам BotForge.

**Запрос:** $ARGUMENTS

Используй полный reference: `.claude/skills/botforge/references/miniapp.md`.

**План:**

1. **ADR-дополнение** — обоснуй, почему Mini App лучше FSM для этой задачи (≤100 слов).
2. **Структура** — предложи дерево:
   ```
   api/          FastAPI backend
     routers/
     security.py
     deps.py
   webapp/       frontend (Vite + React/Vue/Svelte — уточни у юзера)
     src/
     package.json
   app/integrations/webapp_auth.py   initData HMAC validation
   ```
3. **Backend** — сгенерируй:
   - `app/integrations/webapp_auth.py` — HMAC-проверка initData (`WebAppData` secret)
   - `api/security.py` — JWT issue/verify (TTL ≤12ч)
   - `api/routers/auth.py` — `POST /auth/telegram` обменивает initData на JWT
   - `api/deps.py` — `Depends(current_user_id)`
4. **Frontend** — минимальный scaffold:
   - `webapp/src/sdk.ts` — обёртка над `@twa-dev/sdk`
   - `webapp/src/api.ts` — fetch wrapper с auto-login через initData
   - `webapp/src/main.*` — роутинг + главная страница
   - `vite.config.*` + `package.json`
5. **Bot side** — кнопка запуска Mini App:
   - `app/keyboards/inline/miniapp.py` с `WebAppInfo(url=...)`
   - Handler `/app` → отправка кнопки
6. **Infra** — обнови `docker-compose.yml`:
   - Сервис `api` (FastAPI, uvicorn)
   - Сервис `webapp` (nginx + static)
   - CORS whitelist на `settings.webapp_url`
7. **Security checklist** — прогон по security-чеклисту из miniapp.md.
8. **Deploy** — HTTPS обязателен, инструкция для Fly.io/VPS с Caddy/nginx TLS.

**Hard bans:**
- Не доверять `initDataUnsafe` на клиенте — только подписанный initData на сервере.
- JWT secret в `.env`, не в коде.
- CORS без `*`.
- Платежи из Mini App — через Telegram (`openInvoice`), НЕ через свой checkout.
