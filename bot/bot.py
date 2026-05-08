"""
Telegram bot for kolodahearthstone.ru VIP content unlock.

UI:
  /start          welcome card with brand intro and a single CTA
  /catalog        card-style article browser (1 article per screen)
  Navigation      ◀ / ▶ between articles, "Получить доступ" issues link

Flow:
  membership in CHANNEL_ID or GROUP_ID -> /lockers from WP -> on tap,
  POST /issue -> short magic-link URL the user clicks to unlock browser.
"""
import asyncio
import html
import logging
import os
import sys
from typing import Any

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)


def env(name: str, default: str | None = None, *, required: bool = True) -> str:
    val = os.environ.get(name, default)
    if required and not val:
        sys.exit(f"missing required env var: {name}")
    return val or ""


BOT_TOKEN = env("BOT_TOKEN")
WP_BASE_URL = env("WP_BASE_URL").rstrip("/")
WP_BEARER = env("WP_BEARER")
CHANNEL_ID = int(env("CHANNEL_ID"))
GROUP_ID = int(env("GROUP_ID"))
SUBSCRIBE_LINKS = env("SUBSCRIBE_LINKS", "", required=False)
HTTP_TIMEOUT = float(env("HTTP_TIMEOUT", "10", required=False))

CAPTION_LIMIT = 1024  # Telegram photo caption hard limit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("vipbot")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

USER_LOCKERS: dict[int, list[dict[str, Any]]] = {}

ALLOWED_STATUSES = {"member", "administrator", "creator"}


# =====================================================
#  WordPress / Telegram helpers
# =====================================================

async def is_subscribed(user_id: int) -> bool:
    for chat_id in (CHANNEL_ID, GROUP_ID):
        try:
            m = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        except Exception as e:
            log.warning("getChatMember failed for chat=%s user=%s: %s", chat_id, user_id, e)
            continue
        status = m.status
        if status in ALLOWED_STATUSES:
            return True
        if status == "restricted" and getattr(m, "is_member", False):
            return True
    return False


async def wp_get(path: str) -> Any:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(
            f"{WP_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {WP_BEARER}"},
        )
        r.raise_for_status()
        return r.json()


async def wp_post(path: str, payload: dict) -> Any:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.post(
            f"{WP_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {WP_BEARER}"},
            json=payload,
        )
        r.raise_for_status()
        return r.json()


async def load_lockers(user_id: int, *, force: bool = False) -> list[dict[str, Any]]:
    if not force and user_id in USER_LOCKERS:
        return USER_LOCKERS[user_id]
    data = await wp_get("/wp-json/vip/v1/lockers")
    if not isinstance(data, list):
        data = []
    USER_LOCKERS[user_id] = data
    return data


# =====================================================
#  UI builders
# =====================================================

WELCOME_TEXT = (
    "✨ <b>VIP-доступ Колоды Hearthstone</b>\n\n"
    "Этот бот выдаёт одноразовые ссылки разблокировки статей "
    "сайта <a href=\"https://kolodahearthstone.ru\">kolodahearthstone.ru</a> "
    "для подписчиков канала и группы.\n\n"
    "🃏 Выбираете статью\n"
    "🔓 Получаете персональную ссылку\n"
    "💎 Открываете контент в браузере — доступ сохраняется на 7 дней"
)


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Каталог статей", callback_data="catalog:0")],
        [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="help")],
    ])


def build_subscribe_text() -> str:
    text = (
        "🔒 <b>Доступ только для подписчиков</b>\n\n"
        "Чтобы получить VIP-ссылки, вступите в наш канал или группу. "
        "Затем нажмите /start ещё раз."
    )
    if SUBSCRIBE_LINKS:
        items = [x.strip() for x in SUBSCRIBE_LINKS.split(",") if x.strip()]
        if items:
            text += "\n\n" + "\n".join(f"• {x}" for x in items)
    return text


def card_caption(item: dict[str, Any], idx: int, total: int) -> str:
    title = (item.get("title") or "(без названия)").strip()
    excerpt = (item.get("excerpt") or "").strip()

    head = f"<b>{html.escape(title)}</b>\n<i>📖 Статья {idx + 1} из {total}</i>"
    if not excerpt:
        return head

    body = html.escape(excerpt)
    text = f"{head}\n\n{body}"
    if len(text) <= CAPTION_LIMIT:
        return text

    overflow = len(text) - CAPTION_LIMIT + 1
    body = body[: max(0, len(body) - overflow)].rstrip() + "…"
    return f"{head}\n\n{body}"


def card_keyboard(idx: int, total: int) -> InlineKeyboardMarkup:
    nav: list[InlineKeyboardButton] = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"catalog:{idx - 1}"))
    nav.append(InlineKeyboardButton(text=f"{idx + 1} / {total}", callback_data="noop"))
    if idx < total - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"catalog:{idx + 1}"))

    rows: list[list[InlineKeyboardButton]] = [nav]
    rows.append([InlineKeyboardButton(text="🔓 Получить доступ", callback_data=f"art:{idx}")])
    rows.append([
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh"),
        InlineKeyboardButton(text="🏠 В начало", callback_data="catalog:0"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# =====================================================
#  Card rendering: edit existing message in place when we can,
#  otherwise delete and post a fresh one.
# =====================================================

async def render_card(
    msg: Message,
    *,
    item: dict[str, Any],
    idx: int,
    total: int,
    edit: bool,
) -> None:
    caption = card_caption(item, idx, total)
    kb = card_keyboard(idx, total)
    image = (item.get("image") or "").strip()

    if edit:
        try:
            if image:
                await msg.edit_media(
                    media=InputMediaPhoto(media=image, caption=caption, parse_mode=ParseMode.HTML),
                    reply_markup=kb,
                )
            else:
                await msg.edit_text(caption, reply_markup=kb, disable_web_page_preview=True)
            return
        except TelegramBadRequest as e:
            log.info("edit fallback (%s); sending fresh card", e.message)
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass

    if image:
        try:
            await msg.answer_photo(image, caption=caption, reply_markup=kb)
            return
        except TelegramBadRequest as e:
            log.warning("answer_photo failed for %s: %s — falling back to text", image, e.message)

    await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)


# =====================================================
#  Handlers
# =====================================================

@dp.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    user_id = msg.from_user.id
    log.info("/start user=%s", user_id)
    if not await is_subscribed(user_id):
        await msg.answer(build_subscribe_text(), disable_web_page_preview=True)
        return
    await msg.answer(WELCOME_TEXT, reply_markup=welcome_keyboard(), disable_web_page_preview=True)


@dp.message(Command("catalog"))
async def cmd_catalog(msg: Message) -> None:
    if not await is_subscribed(msg.from_user.id):
        await msg.answer(build_subscribe_text(), disable_web_page_preview=True)
        return
    await open_catalog(msg, msg.from_user.id, idx=0, edit_message=None)


@dp.message(Command("help"))
async def cmd_help(msg: Message) -> None:
    await msg.answer(
        "<b>Как это работает</b>\n\n"
        "1. Бот проверяет вашу подписку на канал/группу.\n"
        "2. Вы выбираете статью в каталоге — бот выдаёт одноразовую ссылку.\n"
        "3. Открываете её в браузере — ссылка автоматически разблокирует контент и «сжигается».\n"
        "4. Доступ сохраняется в браузере на 7 дней.\n\n"
        "<b>Команды</b>\n"
        "/start — главное меню\n"
        "/catalog — каталог статей\n"
        "/help — эта справка",
        disable_web_page_preview=True,
    )


@dp.callback_query(F.data == "help")
async def cb_help(q: CallbackQuery) -> None:
    await cmd_help(q.message)
    await q.answer()


@dp.callback_query(F.data == "noop")
async def cb_noop(q: CallbackQuery) -> None:
    await q.answer()


@dp.callback_query(F.data == "refresh")
async def cb_refresh(q: CallbackQuery) -> None:
    if not await is_subscribed(q.from_user.id):
        await q.answer("Подписка не подтверждена.", show_alert=True)
        return
    USER_LOCKERS.pop(q.from_user.id, None)
    await q.answer("Обновляю каталог…")
    await open_catalog(q.message, q.from_user.id, idx=0, edit_message=q.message)


@dp.callback_query(F.data.startswith("catalog:"))
async def cb_catalog(q: CallbackQuery) -> None:
    if not await is_subscribed(q.from_user.id):
        await q.answer("Подписка не подтверждена.", show_alert=True)
        return
    try:
        idx = int(q.data.split(":", 1)[1])
    except ValueError:
        await q.answer("Неверный шаг.", show_alert=True)
        return
    await open_catalog(q.message, q.from_user.id, idx=idx, edit_message=q.message)
    await q.answer()


async def open_catalog(
    msg: Message,
    user_id: int,
    *,
    idx: int,
    edit_message: Message | None,
) -> None:
    try:
        lockers = await load_lockers(user_id)
    except httpx.HTTPStatusError as e:
        log.error("lockers HTTP %s: %s", e.response.status_code, e.response.text[:300])
        await msg.answer(f"Не удалось загрузить каталог: HTTP {e.response.status_code}")
        return
    except Exception as e:
        log.exception("lockers failed")
        await msg.answer(f"Не удалось загрузить каталог: {e}")
        return

    if not lockers:
        await msg.answer("📭 Пока нет VIP-статей. Попробуйте позже.")
        return

    idx = max(0, min(len(lockers) - 1, idx))
    item = lockers[idx]
    target = edit_message or msg
    await render_card(
        target,
        item=item,
        idx=idx,
        total=len(lockers),
        edit=edit_message is not None,
    )


@dp.callback_query(F.data.startswith("art:"))
async def cb_article(q: CallbackQuery) -> None:
    try:
        idx = int(q.data.split(":", 1)[1])
    except ValueError:
        await q.answer("Неверный выбор.", show_alert=True)
        return

    lockers = USER_LOCKERS.get(q.from_user.id) or []
    if idx < 0 or idx >= len(lockers):
        await q.answer("Каталог устарел, нажмите /catalog.", show_alert=True)
        return

    if not await is_subscribed(q.from_user.id):
        await q.answer("Подписка не подтверждена.", show_alert=True)
        return

    item = lockers[idx]
    await q.answer("Готовлю ссылку…")

    try:
        res = await wp_post(
            "/wp-json/vip/v1/issue",
            {
                "post_id": item["post_id"],
                "code": item["code"],
                "telegram_user_id": q.from_user.id,
            },
        )
    except httpx.HTTPStatusError as e:
        log.error("issue HTTP %s: %s", e.response.status_code, e.response.text[:300])
        await q.message.answer(f"Не удалось выдать ссылку: HTTP {e.response.status_code}")
        return
    except Exception as e:
        log.exception("issue failed")
        await q.message.answer(f"Не удалось выдать ссылку: {e}")
        return

    url = res.get("url")
    ttl = int(res.get("ttl") or 900)
    minutes = max(1, ttl // 60)
    title = item.get("title") or "статья"

    if not url:
        await q.message.answer("Сервер не вернул ссылку. Попробуйте позже.")
        return

    open_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть статью", url=url)],
        [InlineKeyboardButton(text="📚 Назад в каталог", callback_data=f"catalog:{idx}")],
    ])

    await q.message.answer(
        f"🔓 <b>{html.escape(title)}</b>\n\n"
        f"Ссылка одноразовая и действует <b>{minutes} мин</b>.\n"
        f"После открытия доступ к статье сохранится в браузере на 7 дней.",
        reply_markup=open_kb,
        disable_web_page_preview=True,
    )


# =====================================================
#  Lifecycle
# =====================================================

async def main() -> None:
    me = await bot.get_me()
    log.info("starting bot @%s id=%s", me.username, me.id)
    log.info("WP base: %s", WP_BASE_URL)

    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="catalog", description="Каталог VIP-статей"),
        BotCommand(command="help", description="Помощь"),
    ])

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
