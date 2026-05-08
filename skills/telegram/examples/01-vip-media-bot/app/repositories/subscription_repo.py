from datetime import datetime

from sqlalchemy import select

from app.models.subscription import Subscription, SubStatus
from app.repositories.base import BaseRepo


class SubscriptionRepo(BaseRepo):
    async def active_for(self, user_id: int) -> Subscription | None:
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == SubStatus.active)
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: int,
        plan: str,
        started_at: datetime,
        expires_at: datetime,
    ) -> Subscription:
        sub = Subscription(
            user_id=user_id,
            plan=plan,
            status=SubStatus.active,
            started_at=started_at,
            expires_at=expires_at,
        )
        self.session.add(sub)
        await self.session.commit()
        return sub
