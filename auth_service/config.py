from __future__ import annotations

import os
from dataclasses import dataclass

from auth_service.errors import ConfigurationError


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc


def env_str(name: str, default: str) -> str:
    return os.getenv(name, default)


DEFAULT_JWT_SECRET = "change-me-in-production"
DEFAULT_OTP_PEPPER = "change-me-too"


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "auth_service"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/%2F"
    sms_queue: str = "sms.otp"
    jwt_secret: str = DEFAULT_JWT_SECRET
    otp_pepper: str = DEFAULT_OTP_PEPPER
    kavenegar_api_key: str = ""
    kavenegar_sender: str = "10008663"
    grpc_host: str = "[::]"
    grpc_port: int = 50051
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 2592000
    otp_ttl_seconds: int = 120
    otp_max_attempts: int = 5
    otp_resend_cooldown_seconds: int = 45
    default_user_role: str = "user"
    bootstrap_admin_phone: str = ""
    app_env: str = "development"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mongo_uri=env_str("MONGO_URI", cls.mongo_uri),
            mongo_db=env_str("MONGO_DB", cls.mongo_db),
            rabbitmq_url=env_str("RABBITMQ_URL", cls.rabbitmq_url),
            sms_queue=env_str("SMS_QUEUE", cls.sms_queue),
            jwt_secret=env_str("JWT_SECRET", cls.jwt_secret),
            otp_pepper=env_str("OTP_PEPPER", cls.otp_pepper),
            kavenegar_api_key=env_str("KAVENEGAR_API_KEY", cls.kavenegar_api_key),
            kavenegar_sender=env_str("KAVENEGAR_SENDER", cls.kavenegar_sender),
            grpc_host=env_str("GRPC_HOST", cls.grpc_host),
            grpc_port=env_int("GRPC_PORT", cls.grpc_port),
            access_token_ttl_seconds=env_int("ACCESS_TOKEN_TTL_SECONDS", cls.access_token_ttl_seconds),
            refresh_token_ttl_seconds=env_int("REFRESH_TOKEN_TTL_SECONDS", cls.refresh_token_ttl_seconds),
            otp_ttl_seconds=env_int("OTP_TTL_SECONDS", cls.otp_ttl_seconds),
            otp_max_attempts=env_int("OTP_MAX_ATTEMPTS", cls.otp_max_attempts),
            otp_resend_cooldown_seconds=env_int(
                "OTP_RESEND_COOLDOWN_SECONDS",
                cls.otp_resend_cooldown_seconds,
            ),
            default_user_role=env_str("DEFAULT_USER_ROLE", cls.default_user_role),
            bootstrap_admin_phone=env_str("BOOTSTRAP_ADMIN_PHONE", cls.bootstrap_admin_phone),
            app_env=env_str("APP_ENV", cls.app_env),
        )

    def __post_init__(self) -> None:
        positive_values = {
            "grpc_port": self.grpc_port,
            "access_token_ttl_seconds": self.access_token_ttl_seconds,
            "refresh_token_ttl_seconds": self.refresh_token_ttl_seconds,
            "otp_ttl_seconds": self.otp_ttl_seconds,
            "otp_max_attempts": self.otp_max_attempts,
        }
        for name, value in positive_values.items():
            if value <= 0:
                raise ConfigurationError(f"{name} must be positive")
        if self.otp_resend_cooldown_seconds < 0:
            raise ConfigurationError("otp_resend_cooldown_seconds cannot be negative")
        if self.default_user_role not in {"admin", "user"}:
            raise ConfigurationError("default_user_role must be admin or user")
        if self.app_env == "production":
            if self.jwt_secret == DEFAULT_JWT_SECRET or len(self.jwt_secret) < 32:
                raise ConfigurationError("JWT_SECRET must be a strong production secret")
            if self.otp_pepper == DEFAULT_OTP_PEPPER or len(self.otp_pepper) < 32:
                raise ConfigurationError("OTP_PEPPER must be a strong production secret")


def load_settings() -> Settings:
    return Settings.from_env()
