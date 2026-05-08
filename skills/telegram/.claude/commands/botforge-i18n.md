---
description: Добавить в бота мультиязычность (gettext + Babel + middleware)
argument-hint: "[список языков: ru,en,uk,...]"
---

Добавь i18n в текущий бот. Языки: $ARGUMENTS (по умолчанию `ru,en`).

Читай reference: `.claude/skills/botforge/references/i18n.md`.

**План:**

### 1. Утилиты
- `app/utils/i18n.py` — gettext wrapper с ContextVar-ом для текущего языка
- `_()` и `ngettext()` как публичные функции

### 2. Middleware
- `app/middlewares/i18n.py` — определяет язык по приоритету: `user.lang` > `from_user.language_code` > default
- Регистрируется ПОСЛЕ `AuthMiddleware` (нужен `user` в data)

### 3. Структура локалей
```
app/locales/
  messages.pot
  ru/LC_MESSAGES/bot.po + bot.mo
  en/LC_MESSAGES/bot.po + bot.mo
```

### 4. Babel config
- Добавить `Babel` в dev deps
- `babel.cfg` — extraction rules для Python файлов
- `pyproject.toml`: `[tool.babel]` секция
- Makefile targets:
  ```
  i18n-extract: pybabel extract -o app/locales/messages.pot app/
  i18n-update:  pybabel update -i ... -d app/locales -D bot
  i18n-compile: pybabel compile -d app/locales -D bot
  ```

### 5. Миграция существующих строк
- Найти все литералы, отправляемые пользователю (handlers, keyboards)
- Обернуть в `_("...")`
- Запустить `make i18n-extract` → получить `messages.pot`
- Инициализировать языки: `pybabel init -i ... -l ru -l en`
- Заполнить `.po` файлы

### 6. Плюрализация
- Русский: 3 формы (один день / 2 дня / 5 дней)
- Убедись, что `Plural-Forms:` в `.po` правильный для каждого языка

### 7. Хранение выбора пользователя
- Добавить команду `/lang` для переключения
- `SetLangCallback` — inline-кнопки с флагами
- Сохранять в `users.lang`
- Alembic-миграция на поле `lang: Mapped[str | None]`

### 8. CI check
- Добавить step: `pybabel extract --no-location -o /tmp/new.pot app/ && diff app/locales/messages.pot /tmp/new.pot` — падение, если есть неизвлечённые строки

### 9. Tests
- Unit-тесты: `set_lang("ru"); assert _("welcome") == "Привет"`
- Проверка fallback при неизвестном языке

### Anti-patterns (напомни):
- ❌ Перевод в models / services — только в presentation layer
- ❌ `text = x if lang == "ru" else y` — не масштабируется
- ❌ БД как хранилище переводов
- ❌ Google Translate в рантайме

### Deploy:
- `.mo` файлы должны попасть в Docker-образ (не `.gitignore`)
- Либо собирать в Dockerfile: `RUN pybabel compile -d app/locales -D bot`
