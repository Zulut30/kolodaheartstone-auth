from aiogram import Bot
from redis.asyncio import Redis


class ChannelCheckService:
    def __init__(self, bot: Bot, redis: Redis, channels: list[int]) -> None:
        self._bot = bot
        self._redis = redis
        self._channels = channels

    async def is_subscribed(self, user_id: int) -> bool:
        if not self._channels:
            return True
        key = f"subcheck:{user_id}"
        cached = await self._redis.get(key)
        if cached is not None:
            return cached == b"1"
        for chat_id in self._channels:
            member = await self._bot.get_chat_member(chat_id, user_id)
            if member.status in {"left", "kicked"}:
                await self._redis.set(key, "0", ex=600)
                return False
        await self._redis.set(key, "1", ex=600)
        return True
