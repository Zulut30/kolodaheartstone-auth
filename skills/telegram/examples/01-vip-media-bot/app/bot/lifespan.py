from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)

from app.config.settings import settings


async def on_startup(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск"),
            BotCommand(command="help", description="Помощь"),
        ],
        scope=BotCommandScopeDefault(),
    )
    admin_cmds = [
        BotCommand(command="start", description="Запуск"),
        BotCommand(command="stats", description="Статистика"),
    ]
    for admin_id in settings.admin_ids:
        await bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=admin_id))

    if settings.webhook_url and settings.webhook_secret:
        await bot.set_webhook(
            url=f"{settings.webhook_url}{settings.webhook_path}",
            secret_token=settings.webhook_secret,
            allowed_updates=[
                "message",
                "callback_query",
                "pre_checkout_query",
                "successful_payment",
            ],
            drop_pending_updates=True,
        )


async def on_shutdown(bot: Bot) -> None:
    await bot.session.close()
