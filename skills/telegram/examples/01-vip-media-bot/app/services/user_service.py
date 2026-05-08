from aiogram.types import User as TgUser

from app.models.user import User
from app.repositories.user_repo import UserRepo


class UserService:
    def __init__(self, user_repo: UserRepo) -> None:
        self._users = user_repo

    async def ensure_user(self, tg_user: TgUser) -> User:
        return await self._users.upsert(
            tg_id=tg_user.id,
            username=tg_user.username,
            lang=tg_user.language_code,
        )
