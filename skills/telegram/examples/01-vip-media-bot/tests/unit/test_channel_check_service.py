from unittest.mock import MagicMock

import pytest

from app.services.channel_check_service import ChannelCheckService


@pytest.mark.asyncio
async def test_empty_channels_always_subscribed(bot_mock, redis_mock):
    service = ChannelCheckService(bot_mock, redis_mock, channels=[])
    assert await service.is_subscribed(user_id=42) is True


@pytest.mark.asyncio
async def test_cached_yes_returns_true(bot_mock, redis_mock):
    redis_mock.get.return_value = b"1"
    service = ChannelCheckService(bot_mock, redis_mock, channels=[-100])

    assert await service.is_subscribed(user_id=42) is True
    bot_mock.get_chat_member.assert_not_called()


@pytest.mark.asyncio
async def test_cached_no_returns_false(bot_mock, redis_mock):
    redis_mock.get.return_value = b"0"
    service = ChannelCheckService(bot_mock, redis_mock, channels=[-100])

    assert await service.is_subscribed(user_id=42) is False
    bot_mock.get_chat_member.assert_not_called()


@pytest.mark.asyncio
async def test_miss_calls_api_and_caches_positive(bot_mock, redis_mock):
    member = MagicMock()
    member.status = "member"
    bot_mock.get_chat_member.return_value = member
    service = ChannelCheckService(bot_mock, redis_mock, channels=[-100])

    assert await service.is_subscribed(user_id=42) is True
    bot_mock.get_chat_member.assert_awaited_once_with(-100, 42)
    redis_mock.set.assert_awaited_with("subcheck:42", "1", ex=600)


@pytest.mark.asyncio
async def test_miss_calls_api_and_caches_negative_on_kicked(bot_mock, redis_mock):
    member = MagicMock()
    member.status = "kicked"
    bot_mock.get_chat_member.return_value = member
    service = ChannelCheckService(bot_mock, redis_mock, channels=[-100])

    assert await service.is_subscribed(user_id=42) is False
    redis_mock.set.assert_awaited_with("subcheck:42", "0", ex=600)
