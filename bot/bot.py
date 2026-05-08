"""
Telegram bot for kolodahearthstone.ru VIP content unlock.

Why we upload image bytes ourselves instead of passing URLs to Telegram:
the WP host blocks/throttles Telegram's downloader (sendPhoto with the raw
URL succeeds for ~13% of images and takes ~2s on average). So the bot
fetches each cover with a normal browser User-Agent and uploads the bytes
once. Telegram returns a file_id, we cache it on disk, and from then on
every render is essentially instant.

Caches (all keyed by image URL):
  PHOTO_CACHE   url -> file_id   (persisted to /data/photo_cache.json)
  IMAGE_BYTES   url -> bytes     (in memory, populated by prefetch / on demand)

Lockers list is fetched from WP once per ~5 min and shared across users.
"""
import asyncio
import html
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    BufferedInputFile,
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
DATA_DIR = Path(env("DATA_DIR", "/data", required=False))

CAPTION_LIMIT = 1024
SUB_CACHE_TTL = 60.0
LOCKERS_CACHE_TTL = 300.0
IMAGE_FETCH_UA = "Mozilla/5.0 (compatible; KolodaHearthstoneBot/1.0)"
IMAGE_FETCH_TIMEOUT = 20.0
PREFETCH_CONCURRENCY = 8
PHOTO_CACHE_FILE = DATA_DIR / "photo_cache.json"

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
SHARED_LOCKERS_LOCK: asyncio.Lock | None = None

SUB_CACHE: dict[int, tuple[bool, float]] = {}

PHOTO_CACHE: dict[str, str] = {}              # url -> file_id (persisted)
IMAGE_BYTES: dict[str, bytes] = {}            # url -> bytes (in memory)
IMAGE_FETCH_LOCKS: dict[str, asyncio.Lock] = {}

ALLOWED_STATUSES = {"member", "administrator", "creator"}


# =====================================================
#  Persistent photo cache
# =====================================================

def _load_photo_cache() -> None:
    try:
        if PHOTO_CACHE_FILE.exists():
            with PHOTO_CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                PHOTO_CACHE.update({str(k): str(v) for k, v in data.items()})
                log.info("photo cache loaded: %d entries", len(PHOTO_CACHE))
    except Exception:
        log.exception("photo cache load failed")


def _save_photo_cache() -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = PHOTO_CACHE_FILE.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(PHOTO_CACHE, f, ensure_ascii=False)
        tmp.replace(PHOTO_CACHE_FILE)
    except Exception:
        log.exception("photo cache save failed")


def _store_file_id(url: str, sent: Any) -> None:
    if not url or not isinstance(sent, Message) or not sent.photo:
        return
    file_id = sent.photo[-1].file_id
    if PHOTO_CACHE.get(url) != file_id:
        PHOTO_CACHE[url] = file_id
        _save_photo_cache()


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
            return SHARED_LOCKERS
        if isinstance(data, list):
            SHARED_LOCKERS = data
            SHARED_LOCKERS_TS = now
        return SHARED_LOCKERS


# =====================================================
#  Image fetching
# =====================================================

async def _fetch_image_bytes(url: str) -> bytes | None:
    if not url:
        return None
    lock = IMAGE_FETCH_LOCKS.setdefault(url, asyncio.Lock())
    async with lock:
        if url in IMAGE_BYTES:
            return IMAGE_BYTES[url]
        try:
            async with httpx.AsyncClient(
                timeout=IMAGE_FETCH_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": IMAGE_FETCH_UA},
            ) as client:
                r = await client.get(url)
            if r.status_code != 200:
                log.warning("image fetch %s: %d", url, r.status_code)
                return None
            ctype = r.headers.get("content-type", "")
            if "image" not in ctype.lower():
                log.warning("image fetch %s: non-image content-type=%s", url, ctype)
                return None
            IMAGE_BYTES[url] = r.content
            return r.content
        except Exception as e:
            log.warning("image fetch %s: err=%s", url, e)
            return None


def _filename_from_url(url: str) -> str:
    name = url.rsplit("/", 1)[-1].split("?", 1)[0] or "cover"
    if "." not in name:
        name += ".jpg"
    return name


async def _photo_payload(url: str) -> tuple[Any, str] | tuple[None, None]:
    """
    Returns (payload, kind) where kind is one of 'file_id' / 'bytes'.
    Tries cached file_id first, then locally cached bytes, then on-demand fetch.
    """
    file_id = PHOTO_CACHE.get(url)
    if file_id:
        return file_id, "file_id"

    img_bytes = IMAGE_BYTES.get(url)
    if img_bytes is None:
        img_bytes = await _fetch_image_bytes(url)
    if img_bytes:
        return BufferedInputFile(img_bytes, filename=_filename_from_url(url)), "bytes"

    return None, None


# =====================================================
#  Photo send/edit primitives
# =====================================================

def _is_not_modified(err: TelegramBadRequest) -> bool:
    return "not modified" in (err.message or "").lower()


async def send_photo_cached(
    msg: Message,
    image_url: str,
    caption: str,
    kb: InlineKeyboardMarkup | None,
) -> bool:
    if not image_url:
        return False

    payload, kind = await _photo_payload(image_url)
    if payload is None:
        return False
    try:
        sent = await msg.answer_photo(payload, caption=caption, reply_markup=kb)
        _store_file_id(image_url, sent)
        return True
    except TelegramBadRequest as e:
        log.warning("answer_photo (%s) url=%s err=%s", kind, image_url, e.message)
        if kind == "file_id":
            PHOTO_CACHE.pop(image_url, None)
            _save_photo_cache()
            payload2, kind2 = await _photo_payload(image_url)
            if payload2 is None or kind2 == "file_id":
                return False
            try:
                sent = await msg.answer_photo(payload2, caption=caption, reply_markup=kb)
                _store_file_id(image_url, sent)
                return True
            except TelegramBadRequest as e2:
                log.warning("answer_photo retry url=%s err=%s", image_url, e2.message)
    return False


async def edit_to_photo_cached(
    msg: Message,
    image_url: str,
    caption: str,
    kb: InlineKeyboardMarkup | None,
) -> bool:
    if not image_url:
        return False

    payload, kind = await _photo_payload(image_url)
    if payload is None:
        return False
    try:
        result = await msg.edit_media(
            media=InputMediaPhoto(media=payload, caption=caption, parse_mode=ParseMode.HTML),
            reply_markup=kb,
        )
        if isinstance(result, Message):
            _store_file_id(image_url, result)
        return True
    except TelegramBadRequest as e:
        if _is_not_modified(e):
            return True
        log.info("edit_media (%s) url=%s err=%s", kind, image_url, e.message)
        if kind == "file_id":
            PHOTO_CACHE.pop(image_url, None)
            _save_photo_cache()
            payload2, kind2 = await _photo_payload(image_url)
            if payload2 is None or kind2 == "file_id":
                return False
            try:
                result = await msg.edit_media(
                    media=InputMediaPhoto(media=payload2, caption=caption, parse_mode=ParseMode.HTML),
                    reply_markup=kb,
                )
                if isinstance(result, Message):
                    _store_file_id(image_url, result)
                return True
            except TelegramBadRequest as e2:
                log.info("edit_media retry url=%s err=%s", image_url, e2.message)
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
#  Welcome / subscribe
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
        log.exception("welcome: get_lockers failed")

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

    if image and not is_photo_msg:
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass
        if await send_photo_cached(msg, image, caption, kb):
            return
        await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)
        return

    if not image and is_photo_msg:
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass
        await msg.answer(caption, reply_markup=kb, disable_web_page_preview=True)
        return

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
    asyncio.create_task(_prefetch_image_bytes())  # fire-and-forget refresh
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
    await render_card(target, item=item, idx=idx, total=len(lockers), edit=edit_message is not None)


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

async def _prefetch_image_bytes() -> None:
    lockers = await get_lockers()
    urls = [
        l["image"] for l in lockers
        if l.get("image") and l["image"] not in PHOTO_CACHE and l["image"] not in IMAGE_BYTES
    ]
    if not urls:
        log.info(
            "image prefetch: %d cached as file_id, %d in memory — nothing to fetch",
            len([1 for l in lockers if l.get("image") in PHOTO_CACHE]),
            len([1 for l in lockers if l.get("image") in IMAGE_BYTES]),
        )
        return

    log.info("image prefetch: %d to fetch", len(urls))
    sem = asyncio.Semaphore(PREFETCH_CONCURRENCY)

    async def fetch(u: str) -> None:
        async with sem:
            await _fetch_image_bytes(u)

    await asyncio.gather(*[fetch(u) for u in urls], return_exceptions=True)
    ok = sum(1 for u in urls if u in IMAGE_BYTES)
    log.info("image prefetch done: %d/%d bytes ready", ok, len(urls))


async def main() -> None:
    global SHARED_LOCKERS_LOCK
    SHARED_LOCKERS_LOCK = asyncio.Lock()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _load_photo_cache()

    me = await bot.get_me()
    log.info("starting bot @%s id=%s data=%s", me.username, me.id, DATA_DIR)
    log.info("WP base: %s", WP_BASE_URL)

    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="catalog", description="Каталог VIP-статей"),
        BotCommand(command="help", description="Помощь"),
    ])

    asyncio.create_task(_warmup())

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def _warmup() -> None:
    try:
        await get_lockers(force=True)
        log.info("lockers warmup: %d cached", len(SHARED_LOCKERS))
        await _prefetch_image_bytes()
    except Exception:
        log.exception("warmup failed")


if __name__ == "__main__":
    asyncio.run(main())
