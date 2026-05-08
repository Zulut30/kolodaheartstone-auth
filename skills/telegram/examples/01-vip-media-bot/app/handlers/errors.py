import uuid

import structlog
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router(name="errors")
log = structlog.get_logger()


@router.errors()
async def on_error(event: ErrorEvent) -> bool:
    rid = uuid.uuid4().hex[:8]
    log.exception("update.failed", request_id=rid)
    upd = event.update
    target = upd.message or (upd.callback_query.message if upd.callback_query else None)
    if target is not None:
        await target.answer(f"Что-то пошло не так. Код: {rid}")
    return True
