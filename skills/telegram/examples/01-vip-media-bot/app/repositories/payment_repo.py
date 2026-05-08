from decimal import Decimal

from sqlalchemy import select

from app.models.payment import Payment, PaymentStatus
from app.repositories.base import BaseRepo


class PaymentRepo(BaseRepo):
    async def create(
        self,
        order_id: str,
        user_id: int,
        provider: str,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            provider=provider,
            amount=amount,
            currency=currency,
            status=PaymentStatus.pending,
        )
        self.session.add(payment)
        await self.session.commit()
        return payment

    async def mark_succeeded(self, order_id: str, external_id: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            return None
        if payment.status == PaymentStatus.succeeded:
            return payment  # idempotent no-op
        payment.status = PaymentStatus.succeeded
        payment.external_id = external_id
        await self.session.commit()
        return payment

    async def is_processed(self, external_id: str) -> bool:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.external_id == external_id)
            .where(Payment.status == PaymentStatus.succeeded)
        )
        return result.scalar_one_or_none() is not None
