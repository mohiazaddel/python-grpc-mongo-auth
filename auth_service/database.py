from __future__ import annotations

from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING, MongoClient

from .config import Settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MongoStore:
    def __init__(self, settings: Settings, client: MongoClient | None = None) -> None:
        self.client = client or MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[settings.mongo_db]
        self.users = self.db["users"]
        self.otps = self.db["otps"]
        self.refresh_tokens = self.db["refresh_tokens"]

    def ensure_indexes(self) -> None:
        self.users.create_index("phone", unique=True)
        self.otps.create_index([("phone", ASCENDING), ("created_at", DESCENDING)])
        self.otps.create_index("expires_at", expireAfterSeconds=0)
        self.refresh_tokens.create_index("token_hash", unique=True)
        self.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
        self.refresh_tokens.create_index([("user_id", ASCENDING), ("revoked_at", ASCENDING)])
