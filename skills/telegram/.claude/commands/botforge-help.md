---
description: Справка по командам BotForge
---

# BotForge — команды

Установленные slash-команды для работы с Telegram-ботами через BotForge.

## Создание и развитие

| Команда | Назначение |
|---|---|
| `/botforge-new [Lite\|Pro\|Media\|SaaS] <описание>` | Создать новый бот с нуля (полный 6-stage workflow) |
| `/botforge-extend <описание фичи>` | Добавить фичу в существующий бот без слома архитектуры |
| `/botforge-refactor <контекст>` | Рефакторинг монолита в слоёную архитектуру |
| `/botforge-review [путь]` | Code review по стандартам BotForge (blocker/major/minor/nit) |

## Модули

| Команда | Назначение |
|---|---|
| `/botforge-miniapp <описание>` | Подключить Telegram Mini App (FastAPI + React/Vue + JWT) |
| `/botforge-auth [roles\|miniapp\|oauth\|api-keys\|all]` | Auth-слой: роли, initData, OAuth bridging, API keys |
| `/botforge-payments [provider] <продукт>` | Платежи: Stars / ЮKassa / CryptoBot / Stripe / Tribute |
| `/botforge-broadcast [simple\|segmented\|ab-test\|scheduled]` | Рассылки с rate limit и admin FSM |
| `/botforge-admin [inline\|webapp\|both]` | Admin-панель с метриками и audit log |
| `/botforge-test [unit\|integration\|all]` | Test suite: pytest + aiogram mocks + testcontainers |

## Операции

| Команда | Назначение |
|---|---|
| `/botforge-deploy [docker\|fly\|railway\|vps] [polling\|webhook]` | Подготовить деплой |
| `/botforge-security [all\|auth\|payments\|miniapp\|data]` | Security-аудит с приоритизацией |
| `/botforge-botfather <описание бота>` | BotFather setup + тексты description/about/commands |
| `/botforge-i18n <ru,en,...>` | Мультиязычность через gettext + Babel |
| `/botforge-observability [minimal\|standard\|full]` | Logging, Sentry, Prometheus, audit, alerts |
| `/botforge-scheduler [apscheduler\|arq\|cron] [task]` | Scheduled tasks: рассылки, expire, напоминания |
| `/botforge-inline <описание>` | Inline-режим (@botname query) |
| `/botforge-admin-web <описание>` | Beautiful web admin panel (React + Tailwind + shadcn/ui) |

## Типичные сценарии

**Новый коммерческий бот с подписками:**
```
/botforge-new SaaS бот-витрина онлайн-курсов с VIP-доступом
/botforge-payments yookassa подписка 499/мес
/botforge-miniapp каталог курсов + личный кабинет
/botforge-admin webapp
/botforge-deploy fly webhook
/botforge-security all
```

**Расширение существующего бота:**
```
/botforge-review
/botforge-extend реферальная программа со скидкой 20%
/botforge-test unit
```

**Рефакторинг legacy:**
```
/botforge-refactor текущий main.py на 800 строк
/botforge-deploy docker webhook
```

## Больше

- Полная документация: `SKILL.md`
- System prompt: `system_prompt.txt`
- Reference-паттерны: `.claude/skills/botforge/references/`
- Установка в другие инструменты: `docs/INSTALL.md`
