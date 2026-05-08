---
description: Создать новый Telegram-бот с нуля через BotForge (полный workflow)
argument-hint: "[Lite|Pro|Media|SaaS] описание бота"
---

Активируй skill **BotForge** и пройди полный 6-stage workflow для нового Telegram-бота.

**Запрос пользователя:** $ARGUMENTS

Следуй точно по стадиям:

1. **Business Brief** — задай до 5 уточняющих вопросов (purpose / monetization / audience / integrations / hosting). Если всё указано в запросе — пропусти.
2. **ADR** — Architecture Decision Record в пределах 250 слов: стек + обоснование, модель данных, модульная раскладка, зависимости, деплой, риски, точки расширения.
3. **Project Tree** — полное дерево проекта до любых файлов.
4. **File Generation** — в строгом порядке зависимостей: `config → db → models → schemas → repositories → integrations → services → filters → middlewares → keyboards → states → handlers → dispatcher → entrypoint → infra (Dockerfile, compose, Alembic, .env.example, Makefile, README)`.
5. **Self-Review** — checkbox-аудит по checklist из `.claude/skills/botforge/references/checklists.md`.
6. **Deployment Instructions** — конкретные команды для выбранной платформы.

Режим по умолчанию — **Pro**. Если пользователь указал Lite/Media/SaaS — применяй его особенности.

Соблюдай hard bans: никакой бизнес-логики в handlers, никакого ORM вне repositories, никаких секретов в коде, никакого `requests`, никакого монолита.
