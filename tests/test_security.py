from __future__ import annotations

import pytest

from auth_service.errors import InvalidCredentials, RateLimited
from auth_service.domain.auth import OtpService, TokenService
from auth_service.domain.security import hash_secret, normalize_phone


def test_phone_normalization_accepts_e164_like_numbers() -> None:
    assert normalize_phone("+98 912-345-6789") == "+989123456789"


def test_phone_normalization_rejects_invalid_numbers() -> None:
    with pytest.raises(InvalidCredentials):
        normalize_phone("123")


def test_otp_is_hashed_and_single_use(settings, store, otps) -> None:
    service = OtpService(otps, settings)
    otp = service.create_otp("+989123456789")

    saved = store.otps.find_one({"phone": "+989123456789"})
    assert saved["otp_hash"] != otp
    assert saved["otp_hash"] == hash_secret(otp, settings.otp_pepper)

    assert service.verify_otp("+989123456789", otp) is True
    with pytest.raises(InvalidCredentials):
        service.verify_otp("+989123456789", otp)


def test_otp_attempt_limit(settings, otps) -> None:
    service = OtpService(otps, settings)
    service.create_otp("+989123456789")

    for _ in range(settings.otp_max_attempts):
        with pytest.raises(InvalidCredentials):
            service.verify_otp("+989123456789", "000000")

    with pytest.raises(InvalidCredentials):
        service.verify_otp("+989123456789", "111111")


def test_otp_resend_cooldown(settings, store, otps) -> None:
    settings = settings.__class__(**{**settings.__dict__, "otp_resend_cooldown_seconds": 45})
    service = OtpService(otps, settings)
    service.create_otp("+989123456789")

    with pytest.raises(RateLimited):
        service.create_otp("+989123456789")


def test_refresh_token_rotation(settings, users, refresh_tokens) -> None:
    user = users.get_or_create_by_phone("+989123456789", "user")
    tokens = TokenService(users, refresh_tokens, settings)

    first = tokens.issue_pair(user)
    second = tokens.refresh(first["refresh_token"])

    assert second["refresh_token"] != first["refresh_token"]
    with pytest.raises(InvalidCredentials):
        tokens.refresh(first["refresh_token"])


def test_admin_role_required(settings, users, refresh_tokens) -> None:
    user = users.get_or_create_by_phone("+989123456789", "user")
    tokens = TokenService(users, refresh_tokens, settings)
    pair = tokens.issue_pair(user)

    with pytest.raises(Exception):
        tokens.verify_access(f"Bearer {pair['access_token']}", required_role="admin")
    assert tokens.verify_access(f"Bearer {pair['access_token']}")["role"] == "user"
