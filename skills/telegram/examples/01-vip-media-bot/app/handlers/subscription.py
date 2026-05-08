from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.config.settings import settings
from app.keyboards.inline.main_menu import vip_buy_kb
from app.models.user import User
from app.repositories.subscription_repo import SubscriptionRepo
from app.services.subscription_service import SubscriptionService

router = Router(name="subscription")


@router.callback_query(F.data == "menu:vip")
async def show_vip(call: CallbackQuery) -> None:
    if call.message is None:
        await call.answer()
        return
    text = (
        f"💎 <b>VIP-доступ</b>\n\n"
        f"— Закрытые подборки\n"
        f"— Эксклюзивные материалы\n\n"
        f"Цена: <b>{settings.vip_price_stars} ⭐</b> / "
        f"{settings.vip_duration_days} дней"
    )
    await call.message.edit_text(
        text, reply_markup=vip_buy_kb(settings.vip_price_stars), parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "menu:profile")
async def show_profile(call: CallbackQuery, user: User, session) -> None:  # type: ignore[no-untyped-def]
    if call.message is None:
        await call.answer()
        return
    service = SubscriptionService(SubscriptionRepo(session))
    is_vip = await service.is_vip(user.id)
    status = "💎 VIP активен" if is_vip else "Обычный пользователь"
    await call.message.edit_text(f"Ваш статус: <b>{status}</b>", parse_mode="HTML")
    await call.answer()
