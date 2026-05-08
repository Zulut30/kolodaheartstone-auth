from decimal import Decimal
from uuid import uuid4

from app.config.settings import settings
from app.integrations.payments.base import InvoiceRequest, PaymentProvider
from app.repositories.payment_repo import PaymentRepo
from app.services.subscription_service import SubscriptionService


class PaymentService:
    def __init__(
        self,
        provider: PaymentProvider,
        payments: PaymentRepo,
        subscriptions: SubscriptionService,
    ) -> None:
        self._provider = provider
        self._payments = payments
        self._subs = subscriptions

    async def start_vip_purchase(self, user_id: int) -> str:
        order_id = uuid4().hex
        amount = Decimal(settings.vip_price_stars)
        await self._payments.create(
            order_id=order_id,
            user_id=user_id,
            provider=self._provider.name,
            amount=amount,
            currency="XTR",
        )
        result = await self._provider.create_invoice(
            InvoiceRequest(
                amount=amount,
                currency="XTR",
                description=f"VIP access for {settings.vip_duration_days} days",
                user_id=user_id,
                order_id=order_id,
                metadata={"plan": "vip"},
            )
        )
        return result.pay_url or ""

    async def on_successful_payment(
        self, order_id: str, external_id: str, amount_units: int
    ) -> None:
        if await self._payments.is_processed(external_id):
            return
        payment = await self._payments.mark_succeeded(order_id, external_id)
        if payment is None:
            return
        await self._subs.activate(
            user_id=payment.user_id,
            plan="vip",
            days=settings.vip_duration_days,
        )
