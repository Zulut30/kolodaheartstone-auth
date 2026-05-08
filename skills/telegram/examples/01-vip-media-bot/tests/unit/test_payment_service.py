from decimal import Decimal

import pytest

from app.integrations.payments.stars import StarsProvider
from app.repositories.payment_repo import PaymentRepo
from app.repositories.subscription_repo import SubscriptionRepo
from app.repositories.user_repo import UserRepo
from app.services.payment_service import PaymentService
from app.services.subscription_service import SubscriptionService
from tests.conftest import get_only_payment


@pytest.mark.asyncio
async def test_start_vip_purchase_creates_pending_payment(session, bot_mock):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    service = PaymentService(
        provider=StarsProvider(bot_mock),
        payments=PaymentRepo(session),
        subscriptions=SubscriptionService(SubscriptionRepo(session)),
    )

    pay_url = await service.start_vip_purchase(user.id)

    assert pay_url == "https://t.me/invoice/abc123"
    bot_mock.create_invoice_link.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_successful_payment_activates_subscription(session, bot_mock):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    payments = PaymentRepo(session)
    subs = SubscriptionService(SubscriptionRepo(session))
    service = PaymentService(StarsProvider(bot_mock), payments, subs)

    await service.start_vip_purchase(user.id)
    pending = await get_only_payment(session)

    await service.on_successful_payment(
        order_id=pending.order_id,
        external_id="tg-charge-123",
        amount_units=100,
    )

    assert await subs.is_vip(user.id) is True


@pytest.mark.asyncio
async def test_duplicate_webhook_is_idempotent(session, bot_mock):
    """Payments with the same external_id must not double-activate subscriptions."""
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    payments = PaymentRepo(session)
    subs = SubscriptionService(SubscriptionRepo(session))
    service = PaymentService(StarsProvider(bot_mock), payments, subs)

    await service.start_vip_purchase(user.id)
    pending = await get_only_payment(session)

    await service.on_successful_payment(pending.order_id, "charge-1", 100)
    first_sub = await SubscriptionRepo(session).active_for(user.id)

    await service.on_successful_payment(pending.order_id, "charge-1", 100)
    second_sub = await SubscriptionRepo(session).active_for(user.id)

    assert first_sub is not None and second_sub is not None
    assert first_sub.id == second_sub.id


@pytest.mark.asyncio
async def test_amount_stored_as_decimal(session, bot_mock):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    service = PaymentService(
        StarsProvider(bot_mock),
        PaymentRepo(session),
        SubscriptionService(SubscriptionRepo(session)),
    )
    await service.start_vip_purchase(user.id)

    payment = await get_only_payment(session)
    assert isinstance(payment.amount, Decimal)
    assert payment.currency == "XTR"
