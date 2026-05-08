# Showcase — bots built with BotForge

Production deployments using BotForge. Submit yours via [feature request issue](https://github.com/Zulut30/telegram-skills/issues/new?template=feature_request.md).

## Reference implementations in this repo

### [01 — VIP Media Bot](../examples/01-vip-media-bot/) ✅
Telegram Stars VIP-подписка для кино-канала. Gated content через проверку подписки на канал, админка, рассылки, Docker-деплой. **~25 Python-файлов, полностью рабочий.**

### 02 — AI Assistant (planned)
OpenAI-бот с 3 тарифами (Free / Pro / Ultra), лимиты токенов, история диалогов, pgvector RAG.

### 03 — Lead-gen Bot (planned)
FSM-сбор заявок → Google Sheets → уведомление админу. Outbox pattern, UTM-трекинг из deep-links.

---

## Community bots

_Хочешь попасть в этот список? Открой PR с ссылкой на бот + кратким описанием._

Формат:
- **Name** (@bot_username) — 1-sentence description. Stack highlight. Submitted by [@user](https://github.com/user).

_(awaiting first contributions)_

---

## Submit yours

1. Deploy a bot built with BotForge.
2. Open a PR editing this file, adding a row under **Community bots**.
3. Confirm:
   - [ ] Uses BotForge-style layered architecture (handlers/services/repositories)
   - [ ] Не монолит на 800 строк
   - [ ] You want public attribution
4. Approved by maintainer — usually within 7 days.
