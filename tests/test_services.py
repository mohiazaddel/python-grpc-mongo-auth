from __future__ import annotations

from unittest.mock import Mock

from auth_service.config import Settings
from auth_service.application.auth import AuthApplicationService
from auth_service.application.ports import SmsMessage
from auth_service.domain.auth import OtpService, TokenService


def test_request_otp_queues_sms(settings, users, otps, refresh_tokens) -> None:
    sms = Mock()
    service = AuthApplicationService(
        settings,
        users,
        OtpService(otps, settings),
        TokenService(users, refresh_tokens, settings),
        sms,
    )

    service.request_otp("+989123456789")

    message = sms.publish.call_args.args[0]
    assert isinstance(message, SmsMessage)
    assert message.phone == "+989123456789"
    assert "verification code" in message.text


def test_bootstrap_admin_phone_gets_admin_role(settings, users, otps, refresh_tokens) -> None:
    admin_settings = Settings(**{**settings.__dict__, "bootstrap_admin_phone": "+989123456789"})
    otp_service = OtpService(otps, admin_settings)
    token_service = TokenService(users, refresh_tokens, admin_settings)
    service = AuthApplicationService(admin_settings, users, otp_service, token_service, Mock())

    otp = otp_service.create_otp("+989123456789")
    pair = service.verify_otp("+989123456789", otp)

    assert pair["role"] == "admin"
