# 02 — AI Assistant Bot (planned)

> Scaffold planned for BotForge v1.8 (additional examples pack). See [Roadmap](../../wiki/Roadmap.md).

## Planned features

- OpenAI / Anthropic API integration via `integrations/openai_client.py` (httpx + tenacity)
- 3 tariffs: Free / Pro / Ultra with token limits in Redis (monthly window)
- Dialog history in `messages(user_id, role, content, tokens, created_at)`
- Streaming responses via `edit_message_text` (batch every 200 tokens)
- Upsell screen on limit breach
- `pgvector` RAG for premium knowledge-base queries
- Voice → text via Whisper API

## How to generate today (DIY)

Until we ship the reference implementation, generate your own:

```
/botforge-new SaaS
Задача: AI-ассистент на OpenAI API с тремя тарифами.
Лимиты токенов по месяцам. История диалогов в Postgres.
Оплата через ЮKassa. Хостинг: Fly.io, webhook.
```

Then:
```
/botforge-extend добавь стриминг ответа через edit_message_text, батч по 200 токенов
/botforge-extend добавь pgvector RAG для Ultra-тарифа
```

## Contribute

Want to land this example? See [CONTRIBUTING.md](../../CONTRIBUTING.md). Target: full working code mirroring `examples/01-vip-media-bot/` structure.
