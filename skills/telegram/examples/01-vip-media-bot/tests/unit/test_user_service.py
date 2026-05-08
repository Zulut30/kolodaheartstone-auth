from unittest.mock import MagicMock

import pytest

from app.repositories.user_repo import UserRepo
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_ensure_user_creates_new(session):
    service = UserService(UserRepo(session))
    tg_user = MagicMock()
    tg_user.id = 777
    tg_user.username = "alice"
    tg_user.language_code = "en"

    user = await service.ensure_user(tg_user)

    assert user.tg_id == 777
    assert user.username == "alice"


@pytest.mark.asyncio
async def test_ensure_user_idempotent(session):
    service = UserService(UserRepo(session))
    tg_user = MagicMock()
    tg_user.id = 777
    tg_user.username = "alice"
    tg_user.language_code = "en"

    user1 = await service.ensure_user(tg_user)
    user2 = await service.ensure_user(tg_user)

    assert user1.id == user2.id


@pytest.mark.asyncio
async def test_ensure_user_updates_username(session):
    service = UserService(UserRepo(session))
    tg_user = MagicMock()
    tg_user.id = 777
    tg_user.username = "alice"
    tg_user.language_code = "en"

    await service.ensure_user(tg_user)

    tg_user.username = "alice_new"
    user = await service.ensure_user(tg_user)

    assert user.username == "alice_new"
