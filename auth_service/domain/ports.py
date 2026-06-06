from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol


class UserRepository(Protocol):
    def get_by_id(self, user_id: Any) -> dict[str, Any] | None:
        ...

    def get_or_create_by_phone(self, phone: str, role: str) -> dict[str, Any]:
        ...


class OtpRepository(Protocol):
    def latest_for_phone(self, phone: str) -> dict[str, Any] | None:
        ...

    def latest_active_for_phone(self, phone: str, now: datetime) -> dict[str, Any] | None:
        ...

    def create(self, phone: str, otp_hash: str, ttl_seconds: int) -> None:
        ...

    def increment_attempts(self, otp_id: Any) -> None:
        ...

    def mark_used(self, otp_id: Any, used_at: datetime) -> None:
        ...


class RefreshTokenRepository(Protocol):
    def create(self, user_id: Any, token_hash: str, ttl_seconds: int) -> None:
        ...

    def find_active(self, token_hash: str, now: datetime) -> dict[str, Any] | None:
        ...

    def revoke(self, token_id: Any, revoked_at: datetime) -> None:
        ...

