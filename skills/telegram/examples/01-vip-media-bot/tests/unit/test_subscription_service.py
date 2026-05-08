from datetime import UTC, datetime, timedelta

import pytest

from app.repositories.subscription_repo import SubscriptionRepo
from app.repositories.user_repo import UserRepo
from app.services.subscription_service import SubscriptionService


@pytest.mark.asyncio
async def test_is_vip_false_when_no_subscription(session):
    service = SubscriptionService(SubscriptionRepo(session))
    assert await service.is_vip(user_id=1) is False


@pytest.mark.asyncio
async def test_activate_creates_new_subscription(session):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    service = SubscriptionService(SubscriptionRepo(session))

    sub = await service.activate(user_id=user.id, plan="vip", days=30)

    assert sub.user_id == user.id
    assert sub.plan == "vip"
    assert (sub.expires_at - sub.started_at).days == 30


@pytest.mark.asyncio
async def test_activate_extends_existing_active_subscription(session):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    service = SubscriptionService(SubscriptionRepo(session))

    first = await service.activate(user.id, "vip", 30)
    second = await service.activate(user.id, "vip", 30)

    assert second.started_at >= first.expires_at


@pytest.mark.asyncio
async def test_is_vip_true_for_active_subscription(session):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    service = SubscriptionService(SubscriptionRepo(session))
    await service.activate(user.id, "vip", 30)

    assert await service.is_vip(user.id) is True


@pytest.mark.asyncio
async def test_is_vip_false_for_expired_subscription(session):
    user = await UserRepo(session).upsert(tg_id=100, username="u", lang="en")
    repo = SubscriptionRepo(session)
    past = datetime.now(UTC) - timedelta(days=30)
    await repo.create(
        user_id=user.id,
        plan="vip",
        started_at=past - timedelta(days=30),
        expires_at=past,
    )
    service = SubscriptionService(repo)

    assert await service.is_vip(user.id) is False
