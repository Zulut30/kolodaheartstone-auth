# Bot API 9.6 — Spec summary

BotForge enforces the official Telegram Bot API 9.6 (April 2026). This page is a fast-lookup; full: [`references/telegram-api-spec.md`](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/telegram-api-spec.md).

## Rate limits

| Scope | Limit | Source |
|---|---|---|
| Per user (private chat) | **1 msg/sec** | bots/faq |
| Per group | **20 msg/min** | bots/faq |
| Broadcast to different users | **~30 msg/sec** | bots/faq |
| Paid broadcast | up to **1000 msg/sec** | bots/faq |

**BotForge throttles broadcasts to 25 msg/s** (safety margin under 30).

## Error handling

| Code | aiogram exception | Action |
|---|---|---|
| 400 | `TelegramBadRequest` | No retry, fix input |
| 401 | `TelegramUnauthorizedError` | Alert, rotate token |
| 403 | `TelegramForbiddenError` | Mark blocked, never retry |
| 404 | `TelegramNotFound` | Fix, no retry |
| 409 | `TelegramConflictError` | Remove webhook or stop polling |
| 429 | `TelegramRetryAfter` | `sleep(e.retry_after)`, retry once |
| 5xx | `TelegramServerError` | tenacity retry + backoff |

## Webhook

```python
await bot.set_webhook(
    url="https://example.com/tg/webhook",
    secret_token="A-Za-z0-9_-{1,256}",
    max_connections=40,          # 1..100
    allowed_updates=[
        "message", "callback_query",
        "pre_checkout_query", "successful_payment",
        "my_chat_member", "chat_member",
        "chat_join_request",
    ],
    drop_pending_updates=True,
)
```

HTTPS only; ports 443, 80, 88, 8443.

## Length limits

| Field | Limit |
|---|---|
| Message text | 4096 UTF-16 code units |
| Caption | 1024 |
| `callback_data` | **64 bytes** — use `CallbackData` factories |
| `answerCallbackQuery.text` | 200 chars |
| Deep-link payload | 64 chars `[A-Za-z0-9_-]` |
| Invoice `title` | 1..32 |
| Invoice `description` | 1..255 |
| Invoice `payload` | 1..128 bytes |

## MarkdownV2 escape

Characters that must be `\`-escaped in MarkdownV2:
```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

Inside code (backticks) and pre-blocks: only `` ` `` and `\` escape.

BotForge helper:
```python
_ESCAPE = r"_*[]()~`>#+-=|{}.!"
def md2_escape(text: str) -> str:
    return "".join(f"\\{c}" if c in _ESCAPE else c for c in text)
```

## Deep links

| URL | Sent to bot |
|---|---|
| `t.me/<bot>?start=<payload>` | `/start <payload>` (private) |
| `t.me/<bot>?startgroup=<payload>` | group select + `/start@<bot> <payload>` |
| `t.me/<bot>?startapp=<payload>` | Mini App with `start_param=<payload>` |

**Payload**: max 64 chars, `[A-Za-z0-9_-]`. For binary data — base64url encode + HMAC sign.

## Telegram Stars (XTR)

- `currency = "XTR"`
- `provider_token = ""` (empty string, not null)
- Methods: `createInvoiceLink`, `sendInvoice`, `refundStarPayment`
- Only digital goods (Apple/Google store policy)
- Handlers: `pre_checkout_query` (answer `ok=True` within 10s) → `successful_payment`
- Subscription: `subscription_period` in `createInvoiceLink`

## Mini App initData

```
secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
calc_hash = hex(HMAC_SHA256(key=secret_key, msg=data_check_string))
valid = hmac.compare_digest(calc_hash, received_hash)
```

Reject if `auth_date` older than 3600 seconds. Never trust `initDataUnsafe` on the client.

## `setMyCommands` scopes

- `BotCommandScopeDefault` — fallback
- `BotCommandScopeAllPrivateChats`
- `BotCommandScopeAllGroupChats`
- `BotCommandScopeAllChatAdministrators`
- `BotCommandScopeChat(chat_id)`
- `BotCommandScopeChatAdministrators(chat_id)`
- `BotCommandScopeChatMember(chat_id, user_id)` — per-user menu

Command: 1..32 chars `[a-z0-9_]`. Description: 1..256 chars. Max 100 commands per scope.
