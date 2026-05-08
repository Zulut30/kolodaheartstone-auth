from aiogram.types import InlineKeyboardButton as B
from aiogram.types import InlineKeyboardMarkup as K


def main_menu_kb() -> K:
    return K(
        inline_keyboard=[
            [B(text="📚 Контент", callback_data="menu:content")],
            [
                B(text="💎 VIP", callback_data="menu:vip"),
                B(text="👤 Профиль", callback_data="menu:profile"),
            ],
        ]
    )


def vip_buy_kb(stars: int) -> K:
    return K(
        inline_keyboard=[
            [B(text=f"Купить VIP за {stars} ⭐", callback_data="vip:buy")],
            [B(text="← Назад", callback_data="menu:main")],
        ]
    )
