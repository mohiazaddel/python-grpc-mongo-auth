from __future__ import annotations

from pymongo.errors import DuplicateKeyError

from auth_service.infrastructure.clock import utcnow


def test_user_repository_get_or_create_keeps_existing_role(users) -> None:
    first = users.get_or_create_by_phone("+989123456789", "admin")
    second = users.get_or_create_by_phone("+989123456789", "user")

    assert first["_id"] == second["_id"]
    assert second["role"] == "admin"


def test_user_repository_returns_existing_user_after_duplicate_insert(users, monkeypatch) -> None:
    existing = {"_id": "existing-id", "phone": "+989123456780", "role": "admin"}
    calls = 0

    def find_one(query):
        nonlocal calls
        calls += 1
        if calls == 1:
            return None
        return existing

    monkeypatch.setattr(users.collection, "find_one", find_one)
    monkeypatch.setattr(users.collection, "insert_one", lambda _doc: (_ for _ in ()).throw(DuplicateKeyError("race")))

    second = users.get_or_create_by_phone("+989123456780", "user")

    assert second == existing


def test_refresh_token_repository_create_find_and_revoke(refresh_tokens) -> None:
    refresh_tokens.create("user-id", "token-hash", ttl_seconds=60)
    stored = refresh_tokens.find_active("token-hash", utcnow())

    assert stored is not None
    refresh_tokens.revoke(stored["_id"], utcnow())
    assert refresh_tokens.find_active("token-hash", utcnow()) is None
