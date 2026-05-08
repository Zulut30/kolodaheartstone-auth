---
description: Сгенерировать BotFather setup-инструкцию и тексты для бота
argument-hint: "[описание бота или имя бренда]"
---

Подготовь полный **BotFather setup checklist** для бота: $ARGUMENTS

Читай reference: `.claude/skills/botforge/references/botfather-setup.md`.

**Выдай:**

### 1. Настройки BotFather (пошагово)
- `/setdescription` — сгенерируй текст 0–512 символов под задачу
- `/setabouttext` — сгенерируй краткое 0–120 символов
- `/setuserpic` — опиши, какая картинка нужна (стиль, цвета)
- `/setprivacy` — рекомендация (ENABLED / DISABLED) с обоснованием
- `/setjoingroups` — рекомендация с обоснованием
- `/setinline` — нужен ли inline-режим + placeholder
- `/setcommands` — список команд в формате BotFather (`cmd - описание`)

### 2. Команды бота (синхронные с `setMyCommands`)
- Default scope — для обычных пользователей
- Admin scope — для `BotCommandScopeChat(admin_id)`
- Если Mini App — `/setmenubutton` с URL

### 3. Tokens & providers
- BOT_TOKEN → в `.env`
- Если платежи: какие провайдеры подключить через `/mybots` → Payments
- Для Stars — `provider_token=""` (провайдер не нужен)

### 4. Три env
Сгенерируй таблицу для dev / staging / prod ботов — отдельные BOT_TOKEN, отдельные webhook URL, отдельные secret_token.

### 5. Legal
- Privacy Policy URL — **обязателен**, если собираете данные / принимаете платежи
- Terms of Service URL — **обязателен** для платежей
- Предложи короткий скелет PP и ToS (или ссылку на шаблон).

### 6. Pre-launch checklist
Полный checklist с чекбоксами из botfather-setup.md.

### 7. Ротация токена
Процедура ротации BOT_TOKEN (каждые 90 дней или при утечке).
