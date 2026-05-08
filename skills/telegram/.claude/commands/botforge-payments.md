---
description: Подключить платёжную систему (Stars / ЮKassa / CryptoBot / Stripe / Tribute)
argument-hint: "[stars | yookassa | cryptobot | stripe | tribute | multi] описание продукта"
---

Подключи платежи к текущему боту. Провайдер + продукт: $ARGUMENTS

Читай reference: `.claude/skills/botforge/references/payments.md`.

**Workflow:**

1. **Brief (если не указано):**
   - Что продаём: digital / физ. товар / подписка / VIP-доступ
   - Аудитория: РФ / мир / крипто
   - Сумма и валюта
   - Одноразовая оплата или recurring

2. **Выбор провайдера (если `multi` или не задан):**
   | Кейс | Провайдер |
   |---|---|
   | Digital + TG-только | **Stars** (0% комиссии) |
   | РФ, карты/СБП | **ЮKassa** |
   | Международка, крипто | **CryptoBot** |
   | Global, карты/subscriptions | **Stripe** |
   | Каналы РФ с подпиской | **Tribute** |

3. **Файлы:**
   - `app/integrations/payments/base.py` — `PaymentProvider` ABC, `InvoiceRequest`, `InvoiceResult`, `PaymentEvent`
   - `app/integrations/payments/<provider>.py` — реализация
   - `app/services/payment_service.py` — провайдер-агностик логика
   - `app/repositories/payment_repo.py` — с `is_processed(external_id)` для idempotency
   - `app/models/payment.py` — order_id, external_id, status, amount (Decimal!), currency, metadata
   - Alembic-миграция
   - Для HTTP-провайдеров (ЮKassa/Stripe/CryptoBot): `api/routers/payments.py` с `/webhooks/{provider}`
   - Для Stars: handlers `pre_checkout_query` + `successful_payment` в `app/handlers/payment.py`

4. **DI:**
   - В `bot/dispatcher.py` или `api/deps.py` — создать провайдера из settings
   - Заменить провайдера = одна строка, бизнес-слой не трогаем

5. **Idempotency:**
   - При создании инвойса: сохранить `order_id` в БД ДО вызова провайдера
   - При вебхуке: `if await repo.is_processed(external_id): return`
   - `Idempotence-Key` = `order_id` (для ЮKassa, Stripe)

6. **Grant access:**
   - Доступ / VIP / подписка выдаётся ТОЛЬКО при `status == "succeeded"`
   - Логируй `order_id`, НЕ логируй card/token

7. **Self-review по Payments Security Checklist:**
   - [ ] Webhook signature verified
   - [ ] Idempotent по external_id
   - [ ] Amount = Decimal
   - [ ] Refunds через тот же handle_webhook
   - [ ] Тайм-ауты + retry
   - [ ] `.env.example` содержит все ключи провайдера

8. **Deploy notes:**
   - Публичный webhook URL (HTTPS)
   - Для ЮKassa — IP whitelist
   - Для Stripe — `STRIPE_WEBHOOK_SECRET` в `.env`
   - Для Stars — дополнительных endpoint'ов не нужно

9. **README section** — «Payments: как тестировать» (тестовый магазин ЮKassa, Stripe test keys, CryptoBot testnet).
