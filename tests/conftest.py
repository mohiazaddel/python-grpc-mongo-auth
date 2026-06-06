from __future__ import annotations

import pytest
import mongomock

from auth_service.config import Settings
from auth_service.infrastructure.database import MongoStore
from auth_service.infrastructure.repositories import OtpRepository, RefreshTokenRepository, UserRepository


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        mongo_uri="mongodb://unused",
        mongo_db="test_auth",
        jwt_secret="test-jwt-secret",
        otp_pepper="test-otp-pepper",
        otp_resend_cooldown_seconds=0,
        otp_ttl_seconds=120,
        otp_max_attempts=3,
    )


@pytest.fixture()
def store(settings: Settings) -> MongoStore:
    return MongoStore(settings, client=mongomock.MongoClient())


@pytest.fixture()
def users(store: MongoStore) -> UserRepository:
    return UserRepository(store)


@pytest.fixture()
def otps(store: MongoStore) -> OtpRepository:
    return OtpRepository(store)


@pytest.fixture()
def refresh_tokens(store: MongoStore) -> RefreshTokenRepository:
    return RefreshTokenRepository(store)
