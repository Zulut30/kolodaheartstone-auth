from aiogram import Bot
from aiogram.types import LabeledPrice

from app.integrations.payments.base import (
    InvoiceRequest,
    InvoiceResult,
    PaymentProvider,
)


class StarsProvider(PaymentProvider):
    name = "stars"

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def create_invoice(self, req: InvoiceRequest) -> InvoiceResult:
        stars = int(req.amount)
        link = await self._bot.create_invoice_link(
            title=req.description[:32],
            description=req.description[:255],
            payload=req.order_id,
            currency="XTR",
            prices=[LabeledPrice(label=req.description[:32], amount=stars)],
            provider_token="",
        )
        return InvoiceResult(
            provider=self.name,
            external_id=req.order_id,
            pay_url=link,
            raw={"link": link},
        )
