from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config.settings import settings
from app.handlers import router as app_router
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.throttling import ThrottlingMiddleware


def build_dispatcher(redis: Redis) -> Dispatcher:
    dp = Dispatcher(storage=RedisStorage(redis))

    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(AuthMiddleware())
    dp.message.middleware(ThrottlingMiddleware(redis))
    dp.callback_query.middleware(ThrottlingMiddleware(redis))

    dp.include_router(app_router)
    return dp


def build_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=False)
