# Examples

Краткие бизнес-кейсы ботов, которые BotForge генерирует из брифа.
Полные ADR, дерево и ключевые файлы для каждого — в [`.claude/skills/botforge/references/examples.md`](../.claude/skills/botforge/references/examples.md).

## 01 — VIP media bot (кино-канал)
Gated-контент по подписке на канал + VIP за 299 ₽/мес + админка + рассылки.
Stack: aiogram 3 + PostgreSQL + Redis + Docker. Webhook за nginx.
Payments: Telegram Stars + ЮKassa. Broadcast 25 msg/s.

## 02 — AI assistant с тарифами
OpenAI-бот, 3 плана (Free/Pro/Ultra), лимиты токенов, история диалогов.
Redis для счётчиков, upsell при переполнении лимита.
Streaming ответов через `edit_message_text`.

## 03 — Lead-gen bot (онлайн-школа)
FSM-сбор заявки → Google Sheets → уведомление админу.
Outbox pattern на случай частичных сбоев интеграций.
UTM-трекинг через deep-links, A/B приветствий.

---

Хотите увидеть полный код? Попросите BotForge сгенерировать:

```
BotForge: Media
Задача: VIP-бот для кино-канала (пример №1 из BotForge examples).
Развернуть полностью: ADR, дерево, все файлы, деплой.
```
