from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pymongo.errors import DuplicateKeyError

from .clock import utcnow
from .database import MongoStore


class UserRepository:
    def __init__(self, store: MongoStore) -> None:
        self.collection = store.users

    def get_by_id(self, user_id: Any) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": user_id})

    def get_or_create_by_phone(self, phone: str, role: str) -> dict[str, Any]:
        user = self.collection.find_one({"phone": phone})
        if user:
            return user
        now = utcnow()
        doc = {"phone": phone, "role": role, "created_at": now, "updated_at": now}
        try:
            result = self.collection.insert_one(doc)
        except DuplicateKeyError:
            existing = self.collection.find_one({"phone": phone})
            if existing:
                return existing
            raise
        doc["_id"] = result.inserted_id
        return doc


class OtpRepository:
    def __init__(self, store: MongoStore) -> None:
        self.collection = store.otps

    def latest_for_phone(self, phone: str) -> dict[str, Any] | None:
        return self.collection.find_one({"phone": phone}, sort=[("created_at", -1)])

    def latest_active_for_phone(self, phone: str, now: datetime) -> dict[str, Any] | None:
        return self.collection.find_one(
            {"phone": phone, "used_at": None, "expires_at": {"$gt": now}},
            sort=[("created_at", -1)],
        )

    def create(self, phone: str, otp_hash: str, ttl_seconds: int) -> None:
        now = utcnow()
        self.collection.insert_one(
            {
                "phone": phone,
                "otp_hash": otp_hash,
                "attempts": 0,
                "used_at": None,
                "created_at": now,
                "expires_at": now + timedelta(seconds=ttl_seconds),
            }
        )

    def increment_attempts(self, otp_id: Any) -> None:
        self.collection.update_one({"_id": otp_id}, {"$inc": {"attempts": 1}})

    def mark_used(self, otp_id: Any, used_at: datetime) -> None:
        self.collection.update_one({"_id": otp_id}, {"$set": {"used_at": used_at}})


class RefreshTokenRepository:
    def __init__(self, store: MongoStore) -> None:
        self.collection = store.refresh_tokens

    def create(self, user_id: Any, token_hash: str, ttl_seconds: int) -> None:
        now = utcnow()
        self.collection.insert_one(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "created_at": now,
                "expires_at": now + timedelta(seconds=ttl_seconds),
                "revoked_at": None,
            }
        )

    def find_active(self, token_hash: str, now: datetime) -> dict[str, Any] | None:
        return self.collection.find_one(
            {"token_hash": token_hash, "revoked_at": None, "expires_at": {"$gt": now}}
        )

    def revoke(self, token_id: Any, revoked_at: datetime) -> None:
        self.collection.update_one({"_id": token_id}, {"$set": {"revoked_at": revoked_at}})
