# 03 — Lead-gen Bot (planned)

> Scaffold planned for BotForge v1.8 (additional examples pack). See [Roadmap](../../wiki/Roadmap.md).

## Planned features

- FSM: `Lead.name → phone → goal → confirm`
- Phone validation via regex
- Confirmation → транзакция: insert в `leads` + append в Google Sheets + admin-notify
- **Outbox pattern** для частичных сбоев интеграций
- UTM-трекинг через deep-links (`t.me/<bot>?start=<base64url-signed>`)
- A/B-тест приветственных сообщений
- AmoCRM integration (optional)

## Data model

```
leads(id, tg_id, name, phone, goal, utm_source, utm_medium, utm_campaign,
      variant, status, created_at)
outbox_events(id, aggregate_id, event_type, payload, attempts, processed_at)
```

## How to generate today

```
/botforge-new Pro
Задача: лидген-бот для онлайн-школы.
FSM: имя → телефон → цель → подтверждение.
Записывает в Postgres + Google Sheets + уведомляет админа в Telegram.
UTM из deep-link. Outbox pattern.
Хостинг: Railway, webhook.
```

## Contribute

See [CONTRIBUTING.md](../../CONTRIBUTING.md). Target: full working scaffold.
