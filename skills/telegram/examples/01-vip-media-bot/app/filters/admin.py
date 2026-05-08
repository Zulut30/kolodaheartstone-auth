from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from app.config.settings import settings


class AdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        uid = getattr(getattr(event, "from_user", None), "id", None)
        return uid in settings.admin_ids
