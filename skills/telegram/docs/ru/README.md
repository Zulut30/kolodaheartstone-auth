<p align="center">
  <img src="../../assets/logo/logo.svg" width="128" alt="BotForge logo" />
</p>

<h1 align="center">BotForge</h1>

<p align="center">
  <b>Инженерный skill для AI, создающий production-ready Telegram-боты</b><br/>
  Готовый пакет для Claude Code, Codex, Cursor и любого LLM.
</p>

<p align="center">
  <a href="../../README.md">English</a> · <b>Русский</b> · <a href="../pl/README.md">Polski</a>
</p>

<p align="center">
  <a href="../QUICKSTART.md">Быстрый старт</a> ·
  <a href="../INSTALL.md">Установка</a> ·
  <a href="../USAGE.md">Использование</a> ·
  <a href="../COMPARISON.md">Сравнение</a> ·
  <a href="../SHOWCASE.md">Примеры</a>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-compatible-8A2BE2" alt="Claude Code"/></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-rules-000000" alt="Cursor"/></a>
  <a href="https://openai.com"><img src="https://img.shields.io/badge/Codex-AGENTS.md-10A37F" alt="Codex"/></a>
  <a href="https://docs.aiogram.dev/"><img src="https://img.shields.io/badge/aiogram-3.x-2CA5E0" alt="aiogram"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB" alt="Python"/></a>
  <a href="https://core.telegram.org/bots/api"><img src="https://img.shields.io/badge/Bot%20API-9.6-0088CC" alt="Bot API"/></a>
</p>

---

BotForge превращает AI-ассистента в senior-инженера Telegram-ботов. Вместо одноразового `main.py` на 800 строк AI проектирует и собирает **модульного, масштабируемого, production-ready Telegram-бота** — с архитектурой, БД, миграциями, админкой, платежами, рассылками, Docker и деплоем.

## Три обещания

1. **Не монолит.** Слоёная архитектура (handlers / services / repositories / integrations) из коробки.
2. **Не черновик.** Docker + Postgres + Alembic + `.env` + инструкции деплоя в первой же генерации.
3. **Не разваливается.** Пятую фичу добавляете так же легко, как первую.

## Почему это работает

- **Опирается на официальную документацию Telegram Bot API 9.6.** Rate limits (1/сек, 20/мин, 30/сек broadcast), правила экранирования MarkdownV2, Mini App initData HMAC-валидация, 64-байтный лимит `CallbackData` — каждое ограничение цитируется из `core.telegram.org`.
- **Обязательный 6-stage workflow.** Brief → ADR → Tree → Files → Self-review → Deploy. AI не может «срезать» сразу к коду.
- **Hard bans на уровне правил skill.** Секреты в коде, `requests`, SQL в handlers, монолит — блокируются самим skill, а не стилем.
- **Платежи — provider-agnostic.** Смена ЮKassa → Stripe = замена одной строки DI.

## Быстрый старт

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cp -r telegram-skills/.claude/skills/botforge ~/.claude/skills/
cp -r telegram-skills/.claude/commands ~/.claude/
```

В Claude Code:
```
/botforge-new SaaS
Задача: бот-витрина онлайн-курсов с VIP-доступом за 499 ₽/мес
Хостинг: VPS, Docker Compose, webhook
```

AI задаст до 5 уточняющих вопросов, предложит ADR, построит дерево проекта, сгенерирует все файлы, прогонит self-review и выдаст команды деплоя.

## 19 slash-команд

```
Создание и развитие:  /botforge-new /botforge-extend /botforge-review /botforge-refactor
Модули:               /botforge-miniapp /botforge-auth /botforge-payments
                      /botforge-broadcast /botforge-admin /botforge-admin-web
                      /botforge-scheduler /botforge-inline /botforge-i18n
Операции:             /botforge-test /botforge-deploy /botforge-security
                      /botforge-botfather /botforge-observability /botforge-help
```

## Рабочий пример

[`examples/01-vip-media-bot/`](../../examples/01-vip-media-bot/) — VIP-бот на Telegram Stars, 25 Python-файлов, всё по стандарту skill.

```bash
cd examples/01-vip-media-bot
cp .env.example .env   # заполните BOT_TOKEN, ADMIN_IDS
make up
```

## Четыре режима

| Режим | Когда | Особенности |
|---|---|---|
| **Lite** | MVP за вечер | SQLite, polling, без Docker |
| **Pro** (default) | Коммерческий бот | Полный production-стандарт |
| **Media** | Контент/каналы | + CMS-sync, сегментированные рассылки, UTM |
| **SaaS** | Подписки/VIP | + billing, multi-provider payments, admin-метрики |

## Что внутри

| Файл | Назначение |
|---|---|
| [`SKILL.md`](../../SKILL.md) | Полный skill-документ — манифест, system prompt, правила, паттерны |
| [`system_prompt.txt`](../../system_prompt.txt) | Голый system prompt для любого LLM |
| [`.claude/skills/botforge/`](../../.claude/skills/botforge/) | **Claude Code** Agent Skill с 23 references |
| [`.claude/commands/`](../../.claude/commands/) | 19 slash-команд |
| [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) | Plugin manifest |
| [`cursor/.cursor/rules/botforge.mdc`](../../cursor/.cursor/rules/botforge.mdc) | **Cursor** правила (современный MDC) |
| [`codex/AGENTS.md`](../../codex/AGENTS.md) | **Codex / Aider / Continue** |
| [`.vscode/`](../../.vscode/) | VS Code snippets (`bf-new`, `bf-extend`, …) |
| [`.zed/`](../../.zed/) | Конфигурация Zed |
| [`tests/golden/`](../../tests/golden/) | Eval harness: структурные assert-ы на output AI |
| [`examples/`](../../examples/) | Рабочие примеры ботов |

## Документация

- [QUICKSTART](../QUICKSTART.md) — 5 минут от нуля до бота
- [INSTALL](../INSTALL.md) — установка под каждый инструмент
- [USAGE](../USAGE.md) — режимы, форматы промптов, сессии
- [COMPARISON](../COMPARISON.md) — vs plain prompts, cookiecutter, no-code, generic agents
- [SHOWCASE](../SHOWCASE.md) — боты, сделанные через BotForge
- [CHANGELOG](../CHANGELOG.md) — история версий и roadmap

## Reference-библиотека

23 глубоких ссылочных документа по всем аспектам инженерии Telegram-ботов: архитектура, 12 переиспользуемых паттернов, Mini Apps, auth (роли / initData / OAuth / API keys), платежи (5 провайдеров), официальные ограничения Bot API 9.6, BotFather setup, i18n, observability, scheduled-таски, recurring-подписки, inline-режим, группы/каналы/форумы, работа с медиа, anti-spam, GDPR compliance, analytics, anti-patterns, performance, admin panel, FAQ.

## Лицензия

MIT. Используйте в коммерческих проектах без ограничений.

## Контрибьюции

См. [CONTRIBUTING](../../CONTRIBUTING.md) и [SECURITY](../../SECURITY.md). PR приветствуются.
