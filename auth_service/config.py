from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db: str = os.getenv("MONGO_DB", "auth_service")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
    sms_queue: str = os.getenv("SMS_QUEUE", "sms.otp")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    otp_pepper: str = os.getenv("OTP_PEPPER", "change-me-too")
    kavenegar_api_key: str = os.getenv("KAVENEGAR_API_KEY", "")
    kavenegar_sender: str = os.getenv("KAVENEGAR_SENDER", "10008663")
    grpc_host: str = os.getenv("GRPC_HOST", "[::]")
    grpc_port: int = int(os.getenv("GRPC_PORT", "50051"))
    access_token_ttl_seconds: int = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900"))
    refresh_token_ttl_seconds: int = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "2592000"))
    otp_ttl_seconds: int = int(os.getenv("OTP_TTL_SECONDS", "120"))
    otp_max_attempts: int = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    otp_resend_cooldown_seconds: int = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "45"))
    default_user_role: str = os.getenv("DEFAULT_USER_ROLE", "user")
    bootstrap_admin_phone: str = os.getenv("BOOTSTRAP_ADMIN_PHONE", "")


def load_settings() -> Settings:
    return Settings()
