---
description: Добавить auth слой (роли, фильтры, Mini App initData, внешний OAuth)
argument-hint: "[roles | miniapp | oauth | api-keys | all]"
---

Добавь auth-слой в текущий бот. Профиль: $ARGUMENTS (по умолчанию — `roles`).

Читай reference: `.claude/skills/botforge/references/auth.md`.

**Профили:**

### `roles` — ролевая модель
- Добавь `Role` enum и поле `role` в `User` model
- Alembic-миграция
- `AuthMiddleware` — upsert user + `data["user"]`
- `BanMiddleware` — ранний отброс забаненных
- `RoleFilter(*roles)` — для handlers
- Admin-команды: `/grant_role`, `/ban`, `/unban` (за `RoleFilter(Role.admin)`)
- Audit log в `audit_events`

### `miniapp` — initData + JWT
- `app/integrations/webapp_auth.py` — HMAC check
- `api/security.py` — JWT issue/verify
- `api/routers/auth.py` — `POST /auth/telegram`
- `api/deps.py` — `current_user_id`
- Секреты в `.env`: `BOT_TOKEN`, `JWT_SECRET`
См. `references/miniapp.md`.

### `oauth` — bridging Telegram ↔ Google/Github
- `app/integrations/oauth_bridge.py` — signed state
- `api/routers/oauth.py` — `/oauth/start`, `/oauth/callback`
- Связь `tg_id ↔ external_account_id` в новой таблице `external_accounts`
- После callback — бот шлёт пользователю «Успешно связано»

### `api-keys` — bot ↔ backend
- `INTERNAL_API_KEY` в `.env`
- Middleware на FastAPI: сверка `X-Internal-Key` через `hmac.compare_digest`
- Документация ротации ключей в RUNBOOK

### `all` — все четыре

**Обязательно:**
1. Self-review по Auth Security Checklist
2. Обнови `.env.example`
3. Обнови README: секция «Auth»
4. Добавь unit-тесты на `RoleFilter`, `parse_and_verify_init_data`, `sign_state/verify_state`
