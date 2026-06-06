from __future__ import annotations

import hashlib
import hmac
import re

from auth_service.errors import InvalidCredentials

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

