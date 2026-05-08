from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline.main_menu import main_menu_kb

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать! Выберите раздел:",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "menu:main")
async def show_main_menu(call: CallbackQuery) -> None:
    if call.message is None:
        await call.answer()
        return
    await call.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await call.answer()
