from __future__ import annotations

import pytest

from auth_service.config import Settings, load_settings
from auth_service.errors import ConfigurationError


def test_load_settings_reads_environment_at_call_time(monkeypatch) -> None:
    monkeypatch.setenv("GRPC_PORT", "6000")
    monkeypatch.setenv("DEFAULT_USER_ROLE", "admin")

    settings = load_settings()

    assert settings.grpc_port == 6000
    assert settings.default_user_role == "admin"


def test_settings_rejects_invalid_role() -> None:
    with pytest.raises(ConfigurationError):
        Settings(default_user_role="owner")


def test_production_requires_strong_secrets() -> None:
    with pytest.raises(ConfigurationError):
        Settings(app_env="production")
