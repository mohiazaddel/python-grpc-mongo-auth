from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from auth_service.application.ports import SmsMessage
from auth_service.config import Settings
from auth_service.errors import MessagingError
from auth_service.infrastructure.kavenegar import KavenegarClient


def test_kavenegar_requires_api_key(settings) -> None:
    client = KavenegarClient(settings)

    with pytest.raises(MessagingError):
        client.send_sms(SmsMessage(phone="+989123456789", text="code 123456"))


def test_kavenegar_wraps_request_errors(settings) -> None:
    settings = Settings(**{**settings.__dict__, "kavenegar_api_key": "test-key"})
    session = Mock()
    session.post.side_effect = requests.Timeout()
    client = KavenegarClient(settings, session=session)

    with pytest.raises(MessagingError):
        client.send_sms(SmsMessage(phone="+989123456789", text="code 123456"))


def test_kavenegar_wraps_rejected_response(settings) -> None:
    settings = Settings(**{**settings.__dict__, "kavenegar_api_key": "test-key"})
    response = Mock()
    response.json.return_value = {"return": {"status": 401}}
    session = Mock()
    session.post.return_value = response
    client = KavenegarClient(settings, session=session)

    with pytest.raises(MessagingError):
        client.send_sms(SmsMessage(phone="+989123456789", text="code 123456"))
