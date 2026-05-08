from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.filters.admin import AdminFilter
from app.repositories.user_repo import UserRepo

router = Router(name="admin")
router.message.filter(AdminFilter())


@router.message(Command("stats"))
async def cmd_stats(message: Message, session) -> None:  # type: ignore[no-untyped-def]
    total = await UserRepo(session).count()
    await message.answer(f"📊 Всего пользователей: <b>{total}</b>", parse_mode="HTML")
