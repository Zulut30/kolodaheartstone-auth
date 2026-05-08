"""
Telegram bot for kolodahearthstone.ru VIP content unlock.

UI:
  /start            welcome card with cover, "Latest article" / catalog CTAs
  /catalog          card-style article browser (1 article per screen)
  Navigation        ◀ / ▶ between articles
  "Latest article"  one tap to issue link for the freshest post

Performance:
  Lockers list is shared across users with a 5-min cache + a startup
  prefetch. Photos are sent by URL the first time, then re-used by file_id
  on subsequent renders — that's what makes ◀▶ feel instant after warmup.
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

CAPTION_LIMIT = 1024
SUB_CACHE_TTL = 60.0
LOCKERS_CACHE_TTL = 300.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("vipbot")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ----- Caches -----
SHARED_LOCKERS: list[dict[str, Any]] = []
SHARED_LOCKERS_TS: float = 0.0
SHARED_LOCKERS_LOCK: asyncio.Lock | None = None  # created in main()

SUB_CACHE: dict[int, tuple[bool, float]] = {}

# image URL -> Telegram file_id (file_id is per-bot, valid forever)
PHOTO_CACHE: dict[str, str] = {}

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


async def get_lockers(*, force: bool = False) -> list[dict[str, Any]]:
    """Single shared cache for all users."""
    global SHARED_LOCKERS, SHARED_LOCKERS_TS
    assert SHARED_LOCKERS_LOCK is not None
    now = time.monotonic()
    async with SHARED_LOCKERS_LOCK:
        if not force and SHARED_LOCKERS and (now - SHARED_LOCKERS_TS) < LOCKERS_CACHE_TTL:
            return SHARED_LOCKERS
        try:
            data = await wp_get("/wp-json/vip/v1/lockers")
        except Exception:
            log.exception("get_lockers: WP request failed")
            return SHARED_LOCKERS  # serve stale rather than empty
        if isinstance(data, list):
            SHARED_LOCKERS = data
            SHARED_LOCKERS_TS = now
        return SHARED_LOCKERS


# =====================================================
#  Photo cache helpers (file_id reuse for instant re-renders)
# =====================================================

def _media_for(url: str) -> str:
    return PHOTO_CACHE.get(url, url)


def _store_file_id(url: str, sent: Any) -> None:
    if not url or not isinstance(sent, Message) or not sent.photo:
        return
    PHOTO_CACHE[url] = sent.photo[-1].file_id


async def send_photo_cached(
    msg: Message,
    image_url: str,
    caption: str,
    kb: InlineKeyboardMarkup | None,
) -> bool:
    if not image_url:
        return False
    media = _media_for(image_url)
    try:
        sent = await msg.answer_photo(media, caption=caption, reply_markup=kb)
        _store_file_id(image_url, sent)
        return True
    except TelegramBadRequest as e:
        if media != image_url:
            PHOTO_CACHE.pop(image_url, None)
            try:
                sent = await msg.answer_photo(image_url, caption=caption, reply_markup=kb)
                _store_file_id(image_url, sent)
                return True
            except TelegramBadRequest as e2:
                log.warning("answer_photo retry url=%s err=%s", image_url, e2.message)
        else:
            log.warning("answer_photo url=%s err=%s", image_url, e.message)
    return False


async def edit_to_photo_cached(
    msg: Message,
    image_url: str,
    caption: str,
    kb: InlineKeyboardMarkup | None,
) -> bool:
    if not image_url:
        return False
    media = _media_for(image_url)
    try:
        result = await msg.edit_media(
            media=InputMediaPhoto(media=media, caption=caption, parse_mode=ParseMode.HTML),
            reply_markup=kb,
        )
        if isinstance(result, Message):
            _store_file_id(image_url, result)
        return True
    except TelegramBadRequest as e:
        if _is_not_modified(e):
            return True
        if media != image_url:
            PHOTO_CACHE.pop(image_url, None)
            try:
                result = await msg.edit_media(
                    media=InputMediaPhoto(media=image_url, caption=caption, parse_mode=ParseMode.HTML),
                    reply_markup=kb,
                )
                if isinstance(result, Message):
                    _store_file_id(image_url, result)
                return True
            except TelegramBadRequest as e2:
                log.info("edit_media retry url=%s err=%s", image_url, e2.message)
        else:
            log.info("edit_media url=%s err=%s", image_url, e.message)
    return False


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
        [InlineKeyboardButton(text="🔥 Последняя статья", callback_data="latest")],
        [InlineKeyboardButton(text="📚 Каталог статей", callback_data="catalog:0")],
        [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="help")],
    ])


async def send_welcome_screen(msg: Message) -> None:
    cover_url = ""
    try:
        lockers = await get_lockers()
        for l in lockers:
            if l.get("image"):
                cover_url = l["image"]
                break
    except Exception:
        log.exception("welcome: get_lockers failed; falling back to text")

    kb = welcome_keyboard()
    if cover_url and await send_photo_cached(msg, cover_url, WELCOME_TEXT, kb):
        return
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

    body_budget = max(0, CAPTION_LIMIT - len(head_plain) - 50)
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

    if not edit:
        if image and await send_photo_cached(msg, image, caption, kb):
            return
        await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)
        return

    is_photo_msg = bool(getattr(msg, "photo", None))
    log.info(
        "render_card idx=%s total=%s image=%s prev=%s",
        idx, total, "yes" if image else "no",
        "photo" if is_photo_msg else "text",
    )

    # Cross-type: text->photo means we must drop and resend
    if image and not is_photo_msg:
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass
        if await send_photo_cached(msg, image, caption, kb):
            return
        await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)
        return

    # Cross-type: photo->text — drop the photo card
    if not image and is_photo_msg:
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass
        await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)
        return

    # Same type — edit in place
    if image:
        if await edit_to_photo_cached(msg, image, caption, kb):
            return
    else:
        try:
            await msg.edit_text(caption, reply_markup=kb, disable_web_page_preview=True)
            return
        except TelegramBadRequest as e:
            if _is_not_modified(e):
                return
            log.info("edit_text failed: %s", e.message)

    # Last resort: drop and resend
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass
    if image and await send_photo_cached(msg, image, caption, kb):
        return
    await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)


# =====================================================
#  Issue link (shared by /art:N and /latest)
# =====================================================

async def issue_link_for(q: CallbackQuery, item: dict[str, Any], idx: int) -> None:
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
#  Handlers
# =====================================================

@dp.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    log.info("/start user=%s", msg.from_user.id)
    if not await is_subscribed(msg.from_user.id):
        await send_subscribe_screen(msg)
        return
    await send_welcome_screen(msg)


@dp.message(Command("catalog"))
async def cmd_catalog(msg: Message) -> None:
    if not await is_subscribed(msg.from_user.id):
        await send_subscribe_screen(msg)
        return
    await open_catalog(msg, idx=0, edit_message=None)


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
        await q.answer("✅ Подписка подтверждена")
        try:
            await q.message.delete()
        except TelegramBadRequest:
            pass
        await send_welcome_screen(q.message)
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
    await q.answer("Обновляю каталог…")
    await get_lockers(force=True)
    await open_catalog(q.message, idx=0, edit_message=q.message)


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
    await open_catalog(q.message, idx=idx, edit_message=q.message)


@dp.callback_query(F.data == "latest")
async def cb_latest(q: CallbackQuery) -> None:
    if not await is_subscribed(q.from_user.id):
        await q.answer("Подписка не подтверждена.", show_alert=True)
        return
    lockers = await get_lockers()
    if not lockers:
        await q.answer("Пока нет VIP-статей.", show_alert=True)
        return
    await issue_link_for(q, lockers[0], idx=0)


async def open_catalog(
    msg: Message,
    *,
    idx: int,
    edit_message: Message | None,
) -> None:
    try:
        lockers = await get_lockers()
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
            "📭 Пока нет VIP-статей.\nЗагляните позже — авторы публикуют новые материалы регулярно.",
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
    if not await is_subscribed(q.from_user.id):
        await q.answer("Подписка не подтверждена.", show_alert=True)
        return
    lockers = await get_lockers()
    if idx < 0 or idx >= len(lockers):
        await q.answer("Каталог обновился, нажмите /catalog.", show_alert=True)
        return
    await issue_link_for(q, lockers[idx], idx=idx)


# =====================================================
#  Lifecycle
# =====================================================

async def main() -> None:
    global SHARED_LOCKERS_LOCK
    SHARED_LOCKERS_LOCK = asyncio.Lock()

    me = await bot.get_me()
    log.info("starting bot @%s id=%s", me.username, me.id)
    log.info("WP base: %s", WP_BASE_URL)

    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="catalog", description="Каталог VIP-статей"),
        BotCommand(command="help", description="Помощь"),
    ])

    # Pre-fetch the catalog so the first /start hits a warm cache.
    asyncio.create_task(_prefetch_lockers())

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def _prefetch_lockers() -> None:
    try:
        await get_lockers(force=True)
        log.info("prefetch: %d lockers cached", len(SHARED_LOCKERS))
    except Exception:
        log.exception("prefetch failed")


if __name__ == "__main__":
    asyncio.run(main())
