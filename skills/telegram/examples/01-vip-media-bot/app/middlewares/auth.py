from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.repositories.user_repo import UserRepo
from app.services.user_service import UserService


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = getattr(event, "from_user", None)
        if tg_user is None or data.get("session") is None:
            return await handler(event, data)

        service = UserService(UserRepo(data["session"]))
        user = await service.ensure_user(tg_user)
        if user.is_banned:
            return None

        data["user"] = user
        return await handler(event, data)
