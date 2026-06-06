from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from typing import Any

import jwt

from .config import Settings
from .database import utcnow
from .errors import InvalidCredentials, PermissionDenied, RateLimited
from .repositories import OtpRepository, RefreshTokenRepository, UserRepository

PHONE_RE = re.compile(r"^\+?[1-9]\d{7,14}$")


def normalize_phone(phone: str) -> str:
    value = re.sub(r"[\s\-()]", "", phone or "")
    if not PHONE_RE.fullmatch(value):
        raise InvalidCredentials("invalid phone number")
    return value


def hash_secret(secret: str, pepper: str) -> str:
    return hmac.new(pepper.encode(), secret.encode(), hashlib.sha256).hexdigest()


def constant_time_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


class OtpService:
    def __init__(self, otps: OtpRepository, settings: Settings) -> None:
        self.otps = otps
        self.settings = settings

    def create_otp(self, phone: str) -> str:
        phone = normalize_phone(phone)
        now = utcnow()
        last = self.otps.latest_for_phone(phone)
        if last and (now - last["created_at"]).total_seconds() < self.settings.otp_resend_cooldown_seconds:
            raise RateLimited("otp recently requested")

        otp = f"{secrets.randbelow(1_000_000):06d}"
        self.otps.create(phone, hash_secret(otp, self.settings.otp_pepper), self.settings.otp_ttl_seconds)
        return otp

    def verify_otp(self, phone: str, otp: str) -> bool:
        phone = normalize_phone(phone)
        if not re.fullmatch(r"\d{6}", otp or ""):
            raise InvalidCredentials("invalid otp")
        now = utcnow()
        doc = self.otps.latest_active_for_phone(phone, now)
        if not doc:
            raise InvalidCredentials("otp expired or not found")
        if doc["attempts"] >= self.settings.otp_max_attempts:
            raise InvalidCredentials("too many otp attempts")

        self.otps.increment_attempts(doc["_id"])
        expected = hash_secret(otp, self.settings.otp_pepper)
        if not constant_time_equal(expected, doc["otp_hash"]):
            raise InvalidCredentials("invalid otp")

        self.otps.mark_used(doc["_id"], now)
        return True


class TokenService:
    def __init__(self, users: UserRepository, refresh_tokens: RefreshTokenRepository, settings: Settings) -> None:
        self.users = users
        self.refresh_tokens = refresh_tokens
        self.settings = settings

    def issue_pair(self, user: dict[str, Any]) -> dict[str, Any]:
        now = utcnow()
        access_expires = now + timedelta(seconds=self.settings.access_token_ttl_seconds)
        access_payload = {
            "sub": str(user["_id"]),
            "phone": user["phone"],
            "role": user["role"],
            "iat": int(now.timestamp()),
            "exp": int(access_expires.timestamp()),
            "typ": "access",
        }
        access_token = jwt.encode(access_payload, self.settings.jwt_secret, algorithm="HS256")
        refresh_token = secrets.token_urlsafe(48)
        self.refresh_tokens.create(
            user["_id"],
            hash_secret(refresh_token, self.settings.jwt_secret),
            self.settings.refresh_token_ttl_seconds,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.settings.access_token_ttl_seconds,
            "role": user["role"],
        }

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        now = utcnow()
        token_hash = hash_secret(refresh_token or "", self.settings.jwt_secret)
        stored = self.refresh_tokens.find_active(token_hash, now)
        if not stored:
            raise InvalidCredentials("invalid refresh token")
        user = self.users.get_by_id(stored["user_id"])
        if not user:
            raise InvalidCredentials("user not found")
        self.refresh_tokens.revoke(stored["_id"], now)
        return self.issue_pair(user)

    def verify_access(self, authorization: str | None, required_role: str | None = None) -> dict[str, Any]:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise InvalidCredentials("missing bearer token")
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, self.settings.jwt_secret, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise InvalidCredentials("invalid access token") from exc
        if payload.get("typ") != "access":
            raise InvalidCredentials("invalid token type")
        if required_role and payload.get("role") != required_role:
            raise PermissionDenied("insufficient role")
        return payload
