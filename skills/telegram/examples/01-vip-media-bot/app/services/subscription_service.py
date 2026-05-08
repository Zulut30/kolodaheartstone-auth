from datetime import UTC, datetime, timedelta

from app.models.subscription import Subscription
from app.repositories.subscription_repo import SubscriptionRepo


class SubscriptionService:
    def __init__(self, sub_repo: SubscriptionRepo) -> None:
        self._repo = sub_repo

    async def is_vip(self, user_id: int) -> bool:
        sub = await self._repo.active_for(user_id)
        if sub is None:
            return False
        return sub.expires_at > datetime.now(UTC)

    async def activate(self, user_id: int, plan: str, days: int) -> Subscription:
        now = datetime.now(UTC)
        existing = await self._repo.active_for(user_id)
        starts_at = existing.expires_at if existing and existing.expires_at > now else now
        expires_at = starts_at + timedelta(days=days)
        return await self._repo.create(
            user_id=user_id,
            plan=plan,
            started_at=starts_at,
            expires_at=expires_at,
        )
