from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery

from app.integrations.payments.stars import StarsProvider
from app.repositories.payment_repo import PaymentRepo
from app.repositories.subscription_repo import SubscriptionRepo
from app.services.payment_service import PaymentService
from app.services.subscription_service import SubscriptionService

router = Router(name="payment")


def _build_service(bot, session) -> PaymentService:  # type: ignore[no-untyped-def]
    return PaymentService(
        provider=StarsProvider(bot),
        payments=PaymentRepo(session),
        subscriptions=SubscriptionService(SubscriptionRepo(session)),
    )


@router.callback_query(F.data == "vip:buy")
async def on_vip_buy(call: CallbackQuery, session, user) -> None:  # type: ignore[no-untyped-def]
    if call.message is None or call.bot is None:
        await call.answer()
        return
    service = _build_service(call.bot, session)
    pay_url = await service.start_vip_purchase(user.id)
    await call.message.answer(f"Оплатить: {pay_url}")
    await call.answer()


@router.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery) -> None:
    await q.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message, session) -> None:  # type: ignore[no-untyped-def]
    sp = message.successful_payment
    if sp is None or message.bot is None:
        return
    service = _build_service(message.bot, session)
    await service.on_successful_payment(
        order_id=sp.invoice_payload,
        external_id=sp.telegram_payment_charge_id,
        amount_units=sp.total_amount,
    )
    await message.answer("✅ VIP активирован. Спасибо!")
