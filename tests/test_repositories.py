from __future__ import annotations

from auth_service.database import utcnow


def test_user_repository_get_or_create_keeps_existing_role(users) -> None:
    first = users.get_or_create_by_phone("+989123456789", "admin")
    second = users.get_or_create_by_phone("+989123456789", "user")

    assert first["_id"] == second["_id"]
    assert second["role"] == "admin"


def test_refresh_token_repository_create_find_and_revoke(refresh_tokens) -> None:
    refresh_tokens.create("user-id", "token-hash", ttl_seconds=60)
    stored = refresh_tokens.find_active("token-hash", utcnow())

    assert stored is not None
    refresh_tokens.revoke(stored["_id"], utcnow())
    assert refresh_tokens.find_active("token-hash", utcnow()) is None

