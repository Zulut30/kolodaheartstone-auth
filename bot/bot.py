"""
Telegram bot for kolodahearthstone.ru VIP content unlock.

UI:
  /start            welcome card (with first article cover) + CTAs
  /catalog          card-style article browser (1 article per screen)
  Navigation        ◀ / ▶ between articles, "Получить доступ" issues link
  Subscription      "I subscribed" callback re-checks membership

Flow:
  membership in CHANNEL_ID or GROUP_ID -> /lockers from WP -> on tap,
  POST /issue -> short magic-link URL the user clicks to unlock browser.
"""
import asyncio
import html
import logging
import os
import sys
import time
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

CAPTION_LIMIT = 1024     # Telegram photo caption hard limit
SUB_CACHE_TTL = 60.0     # seconds — how long to trust a positive/negative subscription check
LOCKERS_CACHE_TTL = 300  # seconds — auto-refresh /lockers in background

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("vipbot")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Per-user state
USER_LOCKERS: dict[int, tuple[list[dict[str, Any]], float]] = {}
SUB_CACHE: dict[int, tuple[bool, float]] = {}

ALLOWED_STATUSES = {"member", "administrator", "creator"}


# =====================================================
#  WordPress / Telegram helpers
# =====================================================

async def is_subscribed(user_id: int, *, force: bool = False) -> bool:
    now = time.monotonic()
    if not force:
        cached = SUB_CACHE.get(user_id)
        if cached and (now - cached[1]) < SUB_CACHE_TTL:
            return cached[0]

    result = False
    for chat_id in (CHANNEL_ID, GROUP_ID):
        try:
            m = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        except Exception as e:
            log.warning("getChatMember failed for chat=%s user=%s: %s", chat_id, user_id, e)
            continue
        status = m.status
        if status in ALLOWED_STATUSES:
            result = True
            break
        if status == "restricted" and getattr(m, "is_member", False):
            result = True
            break

    SUB_CACHE[user_id] = (result, now)
    return result


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
    now = time.monotonic()
    if not force:
        cached = USER_LOCKERS.get(user_id)
        if cached and (now - cached[1]) < LOCKERS_CACHE_TTL:
            return cached[0]
    data = await wp_get("/wp-json/vip/v1/lockers")
    if not isinstance(data, list):
        data = []
    USER_LOCKERS[user_id] = (data, now)
    return data


# =====================================================
#  Static UI strings
# =====================================================

WELCOME_TEXT = (
    "✨ <b>VIP-доступ Колоды Hearthstone</b>\n\n"
    "Этот бот выдаёт одноразовые ссылки разблокировки статей сайта "
    "<a href=\"https://kolodahearthstone.ru\">kolodahearthstone.ru</a> "
    "для подписчиков канала и группы.\n\n"
    "🃏 Выбираете статью\n"
    "🔓 Получаете персональную ссылку\n"
    "💎 Открываете в браузере — доступ сохраняется на 7 дней"
)

HELP_TEXT = (
    "<b>Как это работает</b>\n\n"
    "1. Бот проверяет вашу подписку на канал и группу.\n"
    "2. Вы выбираете статью в каталоге — бот выдаёт одноразовую ссылку.\n"
    "3. Открываете её <i>в обычном браузере</i> — ссылка автоматически разблокирует контент и сжигается.\n"
    "4. Доступ к статье сохраняется в браузере на 7 дней.\n\n"
    "<b>⚠️ Важно</b>\n"
    "Открывайте ссылку в системном браузере (Safari, Chrome, Edge), а не во встроенном Telegram-просмотрщике — "
    "иначе cookie разблокировки сохранится только в нём.\n\n"
    "<b>Команды</b>\n"
    "/start — главное меню\n"
    "/catalog — каталог статей\n"
    "/help — эта справка"
)


def parse_subscribe_links() -> list[tuple[str, str]]:
    """Each entry is either 'Name|URL' or just 'URL'."""
    items: list[tuple[str, str]] = []
    for entry in SUBSCRIBE_LINKS.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if "|" in entry:
            name, _, url = entry.partition("|")
            name, url = name.strip(), url.strip()
        else:
            url = entry
            name = "Подписаться"
        if url:
            items.append((name, url))
    return items


SUBSCRIBE_BUTTONS = parse_subscribe_links()


# =====================================================
#  Welcome / subscribe screens
# =====================================================

def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Каталог статей", callback_data="catalog:0")],
        [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="help")],
    ])


async def send_welcome_screen(msg: Message, user_id: int) -> None:
    cover_url = ""
    try:
        lockers = await load_lockers(user_id)
        for l in lockers:
            if l.get("image"):
                cover_url = l["image"]
                break
    except Exception:
        log.exception("welcome: lockers prefetch failed; falling back to text")

    kb = welcome_keyboard()
    if cover_url:
        try:
            await msg.answer_photo(cover_url, caption=WELCOME_TEXT, reply_markup=kb)
            return
        except TelegramBadRequest as e:
            log.warning("welcome cover failed (%s); falling back to text", e.message)

    await msg.answer(WELCOME_TEXT, reply_markup=kb, disable_web_page_preview=True)


async def send_subscribe_screen(msg: Message) -> None:
    text = (
        "🔒 <b>Доступ только для подписчиков</b>\n\n"
        "Чтобы получить VIP-ссылки, вступите в наш канал или группу. "
        "Затем нажмите <b>«Я подписался»</b> — проверим заново."
    )
    rows: list[list[InlineKeyboardButton]] = []
    for name, url in SUBSCRIBE_BUTTONS:
        rows.append([InlineKeyboardButton(text=f"➡️ {name}", url=url)])
    rows.append([InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")])
    await msg.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        disable_web_page_preview=True,
    )


# =====================================================
#  Catalog cards
# =====================================================

def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def card_caption(item: dict[str, Any], idx: int, total: int) -> str:
    title = _truncate((item.get("title") or "(без названия)").strip(), 200)
    excerpt = (item.get("excerpt") or "").strip()

    head_plain = f"{title}\n📖 Статья {idx + 1} из {total}"
    head_html = f"<b>{html.escape(title)}</b>\n<i>📖 Статья {idx + 1} из {total}</i>"

    if not excerpt:
        return head_html

    # Truncate raw excerpt before escaping so we never split a HTML entity.
    body_budget = max(0, CAPTION_LIMIT - len(head_plain) - 50)  # safety margin for entity expansion
    excerpt = _truncate(excerpt, body_budget)

    return f"{head_html}\n\n{html.escape(excerpt)}"


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


def _is_not_modified(err: TelegramBadRequest) -> bool:
    return "not modified" in (err.message or "").lower()


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
            if _is_not_modified(e):
                return
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
        await send_subscribe_screen(msg)
        return
    await send_welcome_screen(msg, user_id)


@dp.message(Command("catalog"))
async def cmd_catalog(msg: Message) -> None:
    if not await is_subscribed(msg.from_user.id):
        await send_subscribe_screen(msg)
        return
    await open_catalog(msg, msg.from_user.id, idx=0, edit_message=None)


@dp.message(Command("help"))
async def cmd_help(msg: Message) -> None:
    await msg.answer(HELP_TEXT, disable_web_page_preview=True)


@dp.callback_query(F.data == "help")
async def cb_help(q: CallbackQuery) -> None:
    await q.answer()
    await q.message.answer(HELP_TEXT, disable_web_page_preview=True)


@dp.callback_query(F.data == "noop")
async def cb_noop(q: CallbackQuery) -> None:
    await q.answer()


@dp.callback_query(F.data == "check_sub")
async def cb_check_sub(q: CallbackQuery) -> None:
    SUB_CACHE.pop(q.from_user.id, None)
    if await is_subscribed(q.from_user.id, force=True):
        await q.answer("✅ Подписка подтверждена", show_alert=False)
        try:
            await q.message.delete()
        except TelegramBadRequest:
            pass
        await send_welcome_screen(q.message, q.from_user.id)
    else:
        await q.answer(
            "Не вижу вашу подписку. Подпишитесь и попробуйте ещё раз через 10–20 секунд.",
            show_alert=True,
        )


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
    await q.answer()
    await open_catalog(q.message, q.from_user.id, idx=idx, edit_message=q.message)


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
        await msg.answer(f"⚠️ Сервер вернул HTTP {e.response.status_code}. Попробуйте позже.")
        return
    except Exception:
        log.exception("lockers failed")
        await msg.answer("⚠️ Не удалось загрузить каталог. Попробуйте позже.")
        return

    if not lockers:
        await msg.answer(
            "📭 Пока нет VIP-статей.\n"
            "Загляните позже — авторы публикуют новые материалы регулярно.",
            disable_web_page_preview=True,
        )
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

    cached = USER_LOCKERS.get(q.from_user.id)
    lockers = cached[0] if cached else []
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
        if e.response.status_code in (401, 503):
            await q.message.answer("⚠️ Сервер не принял авторизацию бота. Сообщите админу.")
        else:
            await q.message.answer(
                f"⚠️ Не удалось выдать ссылку (код {e.response.status_code}). Попробуйте позже."
            )
        return
    except Exception:
        log.exception("issue failed")
        await q.message.answer("⚠️ Не удалось выдать ссылку. Попробуйте позже.")
        return

    url = res.get("url")
    ttl = int(res.get("ttl") or 900)
    minutes = max(1, ttl // 60)
    title = item.get("title") or "статья"

    if not url:
        await q.message.answer("Сервер не вернул ссылку. Попробуйте позже.")
        return

    open_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть в браузере", url=url)],
        [InlineKeyboardButton(text="📚 Назад в каталог", callback_data=f"catalog:{idx}")],
    ])

    text = (
        f"🔓 <b>{html.escape(title)}</b>\n\n"
        f"⏱ Действует <b>{minutes} мин</b> · одноразовая\n"
        f"💎 После активации доступ сохранится в браузере на 7 дней\n\n"
        f"<b>Ссылка</b> (нажмите, чтобы скопировать):\n"
        f"<code>{html.escape(url)}</code>\n\n"
        f"<i>💡 Откройте её в обычном браузере (Safari, Chrome, Edge). "
        f"Если открыть встроенным просмотрщиком Telegram — cookie сохранится только в нём.</i>"
    )

    await q.message.answer(text, reply_markup=open_kb, disable_web_page_preview=True)


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
