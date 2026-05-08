from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis.asyncio import Redis


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, rate_seconds: int = 1) -> None:
        self._redis = redis
        self._rate = rate_seconds

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        uid = getattr(getattr(event, "from_user", None), "id", None)
        if uid is None:
            return await handler(event, data)
        key = f"thr:{uid}"
        if await self._redis.set(key, "1", ex=self._rate, nx=True):
            return await handler(event, data)
        return None
