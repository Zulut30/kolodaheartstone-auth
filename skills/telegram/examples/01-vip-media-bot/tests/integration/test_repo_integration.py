"""Integration tests: repositories + real SQLite-in-memory schema."""

from decimal import Decimal

import pytest

from app.repositories.payment_repo import PaymentRepo
from app.repositories.user_repo import UserRepo


@pytest.mark.asyncio
async def test_payment_lifecycle_pending_to_succeeded(session):
    user = await UserRepo(session).upsert(tg_id=1, username=None, lang=None)
    repo = PaymentRepo(session)

    payment = await repo.create(
        order_id="order-1",
        user_id=user.id,
        provider="stars",
        amount=Decimal("100"),
        currency="XTR",
    )
    assert payment.status == "pending"

    confirmed = await repo.mark_succeeded("order-1", external_id="charge-abc")

    assert confirmed is not None
    assert confirmed.status == "succeeded"
    assert confirmed.external_id == "charge-abc"


@pytest.mark.asyncio
async def test_is_processed_prevents_double_processing(session):
    user = await UserRepo(session).upsert(tg_id=1, username=None, lang=None)
    repo = PaymentRepo(session)
    await repo.create("order-1", user.id, "stars", Decimal("100"), "XTR")
    await repo.mark_succeeded("order-1", "charge-abc")

    assert await repo.is_processed("charge-abc") is True
    assert await repo.is_processed("unknown-charge") is False


@pytest.mark.asyncio
async def test_user_count_reflects_inserts(session):
    repo = UserRepo(session)
    assert await repo.count() == 0

    await repo.upsert(tg_id=1, username="a", lang=None)
    await repo.upsert(tg_id=2, username="b", lang=None)
    await repo.upsert(tg_id=1, username="a-updated", lang=None)  # upsert same

    assert await repo.count() == 2
